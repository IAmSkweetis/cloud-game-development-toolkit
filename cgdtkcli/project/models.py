import uuid
from pathlib import Path

from pydantic import UUID4, BaseModel, DirectoryPath, Field, StrictStr

DEFAULT_PROJECTS_ROOT = Path.home() / ".aws-cgdtk"


class Project(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, frozen=True)
    name: StrictStr = Field(default="my-game-infra", max_length=64)
    path: DirectoryPath = Field(default_factory=lambda data: DEFAULT_PROJECTS_ROOT / data["name"])
