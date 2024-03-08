import copy
import logging
import logging.handlers
from datetime import datetime
from json import dumps
from typing import override

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class IgnoreExcFormatter(logging.Formatter):
    """不在消息末尾添加错误信息"""
    @override
    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        return self.formatMessage(record)


class KeepExcInfoQueueHandler(logging.handlers.QueueHandler):
    @override
    def prepare(self, record):
        msg = self.format(record)
        record = copy.copy(record)
        record.message = msg
        record.msg = msg
        record.args = None
        record.exc_info = None

        # 保留错误信息，根据参考，清空这两项是为了防止二次记录，但在搭配 IgnoreExcFormatter 时，不会有这个问题，所以保留方便自定义格式化
        # https://github.com/python/cpython/issues/75267
        # record.exc_text = None
        # record.stack_info = None
        return record


class MyJSONFormatter(logging.Formatter):
    def __init__(
            self,
            *,
            fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict:
        always_fields = {
            "message": record.getMessage(),
            "time": datetime.fromtimestamp(record.created).astimezone().isoformat(),
        }

        if record.exc_info is not None:
            if record.exc_text is None:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text is not None:
            always_fields["exc_info"] = record.exc_text

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class InfoOnlyFilter(logging.Filter):

    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno == logging.INFO
