import atexit
import logging.config
import logging.handlers
import sys
from json import load
from os import mkdir
from pathlib import Path

logger = logging.getLogger('log/main')


def setup_logging():
    config_file = Path(__file__).parent.parent / 'configs' / 'logconfig.json'
    with open(config_file) as f_in:
        config = load(f_in)

    if log_file := config.get('handlers', {}).get('file_json', {}).get('filename', ''):
        log_dir = Path(log_file).parent
        if not log_dir.exists():
            mkdir(log_dir)
        if not log_dir.is_dir():
            log_dir.unlink()
            mkdir(log_dir)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def main():
    setup_logging()
    logging.basicConfig(level="DEBUG")
    logger.debug("debug message", extra={"x": "hello"})
    logger.info("info message %s", 123)
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.error(e, exc_info=True, stack_info=True)


if __name__ == "__main__":
    main()
