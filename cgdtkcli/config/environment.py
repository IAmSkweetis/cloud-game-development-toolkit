import uuid
from pathlib import Path

from pydantic import UUID4, BaseModel, DirectoryPath, Field, computed_field

from cgdtkcli.constants import DEFAULT_CGDTK_PATH


class EnvironmentConfig(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    name: str = "dev"
    project_name: str = "my-game-infra"
    project_path: Path = DEFAULT_CGDTK_PATH / "projects" / project_name

    @computed_field
    @property
    def path(self) -> DirectoryPath:
        return self.project_path / self.name
