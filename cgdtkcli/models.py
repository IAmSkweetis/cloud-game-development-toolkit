import logging
from enum import Enum
from typing import Callable

from pydantic import BaseModel


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogHandler(str, Enum):
    CONSOLE = "console"
    FILE = "file"
    CLOUDWATCH = "cloudwatch"


class LogFormat(str, Enum):
    STD = "std"
    JSON = "json"
    TUI = "tui"


class LogHandlerConfig(BaseModel):
    function: Callable[[LogFormat], logging.Handler]
    enabled: bool
    log_format: LogFormat


class ToolButtonType(str, Enum):
    VERIFY = "verify"
    INSTALL = "install"
