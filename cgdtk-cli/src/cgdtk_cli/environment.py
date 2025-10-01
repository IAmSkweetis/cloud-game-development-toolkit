from typing import List, Tuple, override

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from cgdtk_cli.exceptions import CgdtkConfigError
from cgdtk_cli.utils import CGDTK_REPO_ROOT


class Environment(BaseModel):
    name: str


class EnvironmentConfig(BaseSettings):
    environments: List[Environment] = Field(default_factory=list)
    model_config = SettingsConfigDict()

    @classmethod
    @override
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        env_config_file = CGDTK_REPO_ROOT.joinpath("environments/config.yaml")

        return (
            YamlConfigSettingsSource(
                settings_cls,
                yaml_file=env_config_file,
                yaml_file_encoding="utf-8",
            ),
        )


ENVIRONMENT_CONFIG = EnvironmentConfig()
