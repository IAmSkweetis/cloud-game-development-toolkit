from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, List

from pydantic import (UUID4, BaseModel, DirectoryPath, Field, computed_field,
                      model_validator)

from cgdtkcli.config.environment import EnvironmentConfig
from cgdtkcli.constants import DEFAULT_CGDTK_PATH


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
