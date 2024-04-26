# -*- coding: utf-8 -*-
import asyncio
import atexit
import errno
import logging
import os
from concurrent.futures import Future
from enum import Enum
from pathlib import Path
from shutil import rmtree
from typing import override, Callable, Coroutine, Literal, TextIO, TypeAlias

from utils import AsyncThread

log = logging.getLogger(__name__)

_PIPE_BUF = 64 * 1024

_access_mode: TypeAlias = Literal['r', 'w']


class _State(Enum):
    CREATED = 'created'
    OPENED = 'opened'
    CLOSED = 'closed'


class Fifo:
    def __init__(self, path: os.PathLike, mode: _access_mode) -> None:
        self.path: Path = Path(path)
        self.mode: _access_mode = mode

        self._state: _State = _State.CREATED
        self.fd: int | None = None

        if self.mode not in ('r', 'w'):
            raise TypeError('mode must be "r" or "w"')

        self.open()

    def __del__(self) -> None:
        self.close()

    def _create_fifo_file(self) -> None:
        fifo_file = self.path

        if not fifo_file.exists():
            pass
        elif fifo_file.is_fifo():
            return
        elif fifo_file.is_dir():
            log.warning('有名管道文件 %s 被占用，将删除旧文件夹', fifo_file.absolute())
            rmtree(fifo_file)
        else:
            log.warning('有名管道文件 %s 被占用，将删除旧文件', fifo_file.absolute())
            fifo_file.unlink()
        os.mkfifo(fifo_file)

    def close(self) -> None:
        if self._state is _State.OPENED:
            os.close(self.fd)
            self._state = _State.CLOSED

    def open(self) -> None:
        if self._state is _State.OPENED:
            return

        # 允许重新打开
        # if self._state is _State.CLOSED:
        #     raise RuntimeError('fifo is already closed')

        self._create_fifo_file()

        if self.mode == 'r':
            self.fd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
        elif self.mode == 'w':
            # 写端需要管道有读端才可以打开，所以先读再写避免阻塞
            readfd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
            self.fd = os.open(self.path, os.O_WRONLY | os.O_NONBLOCK)
            os.close(readfd)
        else:
            assert 'mode must be "r" or "w"'

        self._state = _State.OPENED

    def read(self, size: int = _PIPE_BUF) -> bytes:
        try:
            return os.read(self.fd, size)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                # 写端未打开或为空
                return b''
            raise e

    def write(self, data: bytes) -> int:
        try:
            return os.write(self.fd, data)
        except OSError as e:
            if e.errno == errno.EPIPE:
                # 读端未打开
                return 0
            raise e


class AsyncFifo(Fifo):
    def __init__(self, path: os.PathLike, mode: _access_mode, async_thread: AsyncThread) -> None:
        super().__init__(path, mode)
        self._async_thread = async_thread
        self._stream_reader: asyncio.StreamReader | None = None
        self._stream_writer: asyncio.StreamWriter | None = None
        self._listen_future: Future | None = None

    @override
    def close(self) -> None:
        if self._state is _State.OPENED:
            if self._stream_writer is not None:
                self._stream_writer.close()
                self._stream_writer = None
            elif self._stream_reader is not None:
                os.close(self.fd)
                self._stream_reader = None

            self._state = _State.CLOSED

    def register_coroutine(self, coroutine: Coroutine) -> Future:
        return self._async_thread.add_coroutine(coroutine)

    @override
    async def read(self, size: int = _PIPE_BUF) -> bytes:
        if self._state is not _State.OPENED:
            raise RuntimeError('fifo is not opened')
        if self._stream_reader is None:
            if self.mode != 'r':
                raise RuntimeError('read operate need mode is "r"')
            operation = os.fdopen(self.fd, self.mode)
            self._stream_reader = self.register_coroutine(self.get_areader(operation)).result()

        return await self._stream_reader.read(size)

    @override
    async def write(self, data: bytes) -> None:
        if self._state is not _State.OPENED:
            raise RuntimeError('fifo is not opened')
        if self._stream_writer is None:
            if self.mode != 'w':
                raise RuntimeError('write operate need mode is "w"')
            operation = os.fdopen(self.fd, self.mode)
            self._stream_reader = self.register_coroutine(self.get_areader(operation)).result()

        self._stream_writer.write(data)
        await self._stream_writer.drain()

    def listen(self, callback: Callable = None) -> Future:
        if callback is None:
            callback = print

        self._listen_future = self._async_thread.add_coroutine(self._listen_helper(callback))
        atexit.register(self.cancel_listen)
        return self._listen_future

    async def _listen_helper(self, callback: Callable) -> None:
        operation = os.fdopen(self.fd, self.mode)
        reader = await self.get_areader(operation)
        while True:
            if reader.at_eof():
                self.close()
                self.open()
                operation = os.fdopen(self.fd, self.mode)
                reader = await self.get_areader(operation)
            if data := await reader.readline():
                callback(data)

    def cancel_listen(self) -> None:
        atexit.unregister(self.cancel_listen)
        if self._listen_future is not None:
            self._listen_future.cancel()
            self._listen_future = None

    @staticmethod
    async def get_areader(reader: TextIO) -> asyncio.StreamReader:
        loop = asyncio.get_running_loop()
        areader = asyncio.StreamReader(loop=loop)
        r_protocol = asyncio.StreamReaderProtocol(areader, loop=loop)
        await loop.connect_read_pipe(lambda: r_protocol, reader)
        return areader

    @staticmethod
    async def get_awriter(writer: TextIO) -> asyncio.StreamWriter:
        loop = asyncio.get_running_loop()
        # asyncio.streams.py 26
        # StreamReaderProtocol 实现了对 StreamWriter.wait_closed 的支持
        # 其父类 FlowControlMixin 实现了对 StreamWriter.drain 的支持
        # 所以需要实例化 StreamWriter 需要 StreamReaderProtocol 作为参数
        # noinspection PyTypeChecker
        w_protocol = asyncio.StreamReaderProtocol(None, loop=loop)
        w_transport, _ = await loop.connect_write_pipe(lambda: w_protocol, writer)
        awriter = asyncio.StreamWriter(w_transport, w_protocol, None, loop)
        return awriter


def test():
    at = AsyncThread()
    t = AsyncFifo(Path().home() / 'fd3', 'r', at)
    t.listen()
    import time
    time.sleep(100)
    # t.close()
    # time.sleep(5)


if __name__ == '__main__':
    test()
