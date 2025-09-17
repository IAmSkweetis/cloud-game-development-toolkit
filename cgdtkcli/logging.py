import logging
import time
from logging.handlers import RotatingFileHandler
from typing import Dict

from pythonjsonlogger.json import JsonFormatter
from textual.widgets import Log

from cgdtkcli.config import cgdtk_config
from cgdtkcli.exceptions import CgdtkException
from cgdtkcli.models import LogFormat, LogHandler, LogHandlerConfig


class TuiLogHandler(logging.Handler):
    def __init__(self, log_widget: Log):
        super().__init__()
        self.log_widget = log_widget

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.log_widget.write_line(msg)


class AlignedFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        record.levelname_padded = f"[{record.levelname}]{' ' * (9 - len(record.levelname))}"
        formatted = super().format(record)

        return formatted.replace(record.asctime, f"{record.asctime} {time.tzname[0]}")


class LoggerFactory:

    __json_log_format = JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    __std_log_format = AlignedFormatter("%(asctime)s %(levelname_padded)s%(message)s")
    __tui_log_format = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )

    def __init__(self):
        self._handlers: Dict[LogHandler, LogHandlerConfig] = {
            LogHandler.CONSOLE: LogHandlerConfig(
                function=self._create_console_handler,
                enabled=cgdtk_config.logging.console_enable,
                log_format=cgdtk_config.logging.console_format,
            ),
            LogHandler.FILE: LogHandlerConfig(
                function=self._create_file_handler,
                enabled=cgdtk_config.logging.file_enable,
                log_format=cgdtk_config.logging.file_format,
            ),
        }

    def _create_console_handler(self, format_type: LogFormat = LogFormat.STD) -> logging.Handler:
        handler = logging.StreamHandler()
        handler.set_name("CONSOLE")

        if format_type == LogFormat.JSON:
            handler.setFormatter(self.__json_log_format)
        elif format_type == LogFormat.STD:
            handler.setFormatter(self.__std_log_format)
        else:
            raise CgdtkException(f"Invalid log format: {format_type}")

        handler.setLevel(cgdtk_config.logging.console_level.value)

        return handler

    def _create_file_handler(self, format_type: LogFormat = LogFormat.JSON) -> logging.Handler:

        # We start a new log file on start.
        handler = RotatingFileHandler(cgdtk_config.logging.file_path, backupCount=5)
        handler.set_name("FILE")
        handler.doRollover()

        if format_type == LogFormat.JSON:
            handler.setFormatter(self.__json_log_format)
        elif format_type == LogFormat.STD:
            handler.setFormatter(self.__std_log_format)
        else:
            raise CgdtkException(f"Invalid log format: {format_type}")

        handler.setLevel(cgdtk_config.logging.file_level.value)

        return handler

    def _create_tui_handler(
        self, log_widget: Log, format_type: LogFormat = LogFormat.TUI
    ) -> logging.Handler:
        handler = TuiLogHandler(log_widget)
        handler.set_name("TUI")

        if format_type == LogFormat.TUI:
            handler.setFormatter(self.__tui_log_format)
        else:
            raise CgdtkException(f"Invalid log format: {format_type}")

        handler.setLevel(logging.DEBUG)
        return handler

    def setup_logger(self, name: str = "") -> logging.Logger:
        # If logging is disabled, we return a no-op logger.
        if not cgdtk_config.logging.enabled:
            logging.getLogger(name).addHandler(logging.NullHandler())
            return logging.getLogger(name)

        logger = logging.getLogger(name)

        # Global log level is set at debug and we'll change the level for each handler based on the
        # config.
        logger.setLevel(cgdtk_config.logging.default_level.value)

        # Clear any existing handlers.
        logger.handlers.clear()

        # Add enabled handlers.
        for _, config in self._handlers.items():
            if config.enabled:
                logger.addHandler(config.function(config.log_format))

        return logger

    def add_tui_handler(self, logger: logging.Logger, log_widget: Log) -> None:
        """Add TUI handler to existing logger"""
        tui_handler = self._create_tui_handler(log_widget)
        logger.addHandler(tui_handler)

logger_factory = LoggerFactory()
LOG = logger_factory.setup_logger("cgdtkcli")
