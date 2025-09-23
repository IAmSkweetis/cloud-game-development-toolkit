from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, List

import tomli_w
from pydantic import (UUID4, BaseModel, DirectoryPath, Field, computed_field,
                      model_validator)
from pydantic_settings import (BaseSettings, PydanticBaseSettingsSource,
                               SettingsConfigDict, TomlConfigSettingsSource)

from cgdtkcli.constants import DEFAULT_CGDTK_PATH
from cgdtkcli.exceptions import CgdtkConfigFileExistsError
from cgdtkcli.models import LogFormat, LogLevel


class LoggingConfig(BaseModel):
    enabled: bool = True
    default_level: LogLevel = LogLevel.DEBUG
    root_path: Path = DEFAULT_CGDTK_PATH

    file_enable: bool = False
    file_path: Path = root_path / "logs" / "cgdtkcli.log"
    file_level: LogLevel = LogLevel.DEBUG
    file_format: LogFormat = LogFormat.STD

    console_enable: bool = True
    console_level: LogLevel = LogLevel.DEBUG
    console_format: LogFormat = LogFormat.STD

    tui_enable: bool = False
    tui_level: LogLevel = LogLevel.DEBUG
    tui_format: LogFormat = LogFormat.TUI


class EnvironmentConfig(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str = "dev"
    project_name: str = "my-game-infra"
    project_path: Path = DEFAULT_CGDTK_PATH / "projects" / project_name

    @computed_field
    @property
    def path(self) -> DirectoryPath:
        return self.project_path / self.name


class ProjectConfig(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str = "my-game-infra"
    environments: List[EnvironmentConfig] = [EnvironmentConfig()]
    root_path: Path = DEFAULT_CGDTK_PATH

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        for env in self.environments:
            env.project_name = self.name

    @computed_field
    @property
    def path(self) -> DirectoryPath:
        return self.root_path / "projects" / self.name

    @model_validator(mode="after")
    def propegate_project_path(self) -> ProjectConfig:
        for env in self.environments:
            env.project_path = self.path

        return self


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

    path: Path = DEFAULT_CGDTK_PATH

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
