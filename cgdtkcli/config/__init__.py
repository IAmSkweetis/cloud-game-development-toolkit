from __future__ import annotations

from pathlib import Path
from typing import List

import tomli_w
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from cgdtkcli.config.project import ProjectConfig
from cgdtkcli.constants import DEFAULT_CGDTK_PATH
from cgdtkcli.exceptions import CgdtkConfigFileExistsError
from cgdtkcli.models import LogFormat, LogLevel
from cgdtkcli.utils import get_repo_root


class LoggingConfig(BaseModel):
    enabled: bool = True
    default_level: LogLevel = LogLevel.DEBUG
    root_path: Path = Field(default_factory=get_repo_root)

    file_enable: bool = False
    file_path: Path = Field(default_factory=lambda: get_repo_root() / "logs" / "cgdtkcli.lo")
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
        env_file=".env",
        env_prefix="CGDTK_",
        env_nested_delimiter="_",
        env_nested_max_split=1,
        toml_file=DEFAULT_CGDTK_PATH / "config.toml",
    )

    aws_region: str = "us-west-2"
    aws_profile: str = "default"

    path: Path = Field(default_factory=get_repo_root)

    logging: LoggingConfig = LoggingConfig()
    projects: List[ProjectConfig] = []

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
        )

    @model_validator(mode="after")
    def propegate_root_path(self) -> CgdtkConfig:
        self.logging.root_path = self.path

        for project in self.projects:
            project.root_path = self.path

        return self


def write_config(
    config: CgdtkConfig,
    config_file: Path = DEFAULT_CGDTK_PATH / "config.toml",
    overwrite: bool = True,
) -> None:
    # Check to see if the config_file parent exists. If not, we'll need to create the path.
    if not config_file.parent.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)

    # If the config file exists, we want to error unless we receive option to overwrite.
    if not overwrite and config_file.exists():
        raise CgdtkConfigFileExistsError(config_file.as_posix())

    # Write the config file.
    with config_file.open("wb") as f:
        tomli_w.dump(config.model_dump(mode="json"), f)


# Global config object
cgdtk_config = CgdtkConfig()
