import shutil
import subprocess
from pathlib import Path
from typing import List

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from pydantic import BaseModel, computed_field


class Tool(BaseModel):
    name: str
    executable: str

    @computed_field
    @property
    def executable_path(self) -> Path | None:
        which_path = shutil.which(self.executable)
        return Path(which_path) if which_path else None

    def run(self, command_args: List[str], cwd: Path = Path.cwd()) -> int:
        if self.executable_path is None:
            raise FileNotFoundError(f"Tool {self.name} not found in PATH")
        else:
            command = [self.executable_path] + command_args
            result = subprocess.run(command, cwd=cwd)
            return result.returncode


# TODO: Consider changing this to a dictionary. And/or need to be a config object.
INFRA_TOOLS: List[Tool] = [
    Tool(name="terraform", executable="terraform"),
    Tool(name="packer", executable="packer"),
    Tool(name="ansible", executable="ansible-playbook"),
    Tool(name="aws-cli", executable="aws"),
]


def is_aws_configured() -> bool:
    """Simple check to verify if the shell is configured to use the AWS CLI.

    Returns:
        A bool that indicates if the shell is configured.
    """
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            return False
        credentials.get_frozen_credentials()
        return True
    except (NoCredentialsError, PartialCredentialsError):
        return False
