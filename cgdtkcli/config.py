from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from cgdtkcli.models import LogFormat, LogLevel


def __find_env_file() -> Path | None:
    current_dir = Path.cwd()
    while True:
        env_file = current_dir / ".env"
        if env_file.exists():
            return env_file
        if current_dir == current_dir.parent:
            return None
        current_dir = current_dir.parent


ENV_FILE = __find_env_file()


class LoggingConfig(BaseModel):
    enabled: bool = True
    default_level: LogLevel = LogLevel.DEBUG

    file_enable: bool = False
    file_path: Path = Path().home() / ".aws" / "cgdtkcli.log"
    file_level: LogLevel = LogLevel.DEBUG
    file_format: LogFormat = LogFormat.STD

    console_enable: bool = True
    console_level: LogLevel = LogLevel.DEBUG
    console_format: LogFormat = LogFormat.STD

    tui_enable: bool = False
    tui_level: LogLevel = LogLevel.DEBUG
    tui_format: LogFormat = LogFormat.TUI


class CgdtkConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="CGDTK_",
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )

    aws_region: str = "us-west-2"
    aws_profile: str = "default"

    logging: LoggingConfig = LoggingConfig()


cgdtk_config = CgdtkConfig()
