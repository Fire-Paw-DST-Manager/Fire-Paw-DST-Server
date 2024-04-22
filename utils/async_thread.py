# -*- coding: utf-8 -*-
import asyncio
import concurrent.futures
from enum import Enum
from threading import Thread
from typing import Coroutine


class _State(Enum):
    CREATED = 'created'
    INITIALIZED = 'initialized'
    CLOSED = 'closed'


class AsyncThread:
    def __init__(self, name: str = None) -> None:
        if name is None:
            name = 'async_thread'
        self.name: str = name
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop_event: asyncio.Event | None = None
        self._thread: Thread | None = None

        self._state: _State = _State.CREATED

    def get_loop(self) -> asyncio.AbstractEventLoop:
        self._lazy_init()
        return self._loop

    def _lazy_init(self) -> None:
        if self._state is _State.CLOSED:
            raise RuntimeError("AsyncThread is closed")

        if self._state is _State.INITIALIZED:
            return

        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._stop_event: asyncio.Event = asyncio.Event()
        self._thread: Thread = Thread(
            target=self._start_loop,
            args=(self._loop, self._run_until_set(self._stop_event)),
            name=self.name,
            daemon=True)
        self._thread.start()
        self._state = _State.INITIALIZED

    def add_coroutine(self, coroutine: Coroutine) -> concurrent.futures.Future:
        self._lazy_init()
        return asyncio.run_coroutine_threadsafe(coroutine, self._loop)

    def stop(self) -> None:
        if self._state is not _State.INITIALIZED:
            return
        asyncio.run_coroutine_threadsafe(self._set_event(self._stop_event), self._loop)

        self._loop = None
        self._stop_event = None
        self._thread = None

        self._state = _State.CLOSED

    @staticmethod
    def _start_loop(loop: asyncio.AbstractEventLoop, coroutine: Coroutine) -> None:
        asyncio.set_event_loop(loop)
        asyncio.run(coroutine, loop_factory=lambda: loop)

    @staticmethod
    async def _run_until_set(event: asyncio.Event) -> None:
        await event.wait()

    @staticmethod
    async def _set_event(event: asyncio.Event) -> None:
        event.set()

    def __del__(self) -> None:
        self.stop()


async_thread = AsyncThread()
