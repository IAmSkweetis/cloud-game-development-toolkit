import os
import re
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, HttpUrl, computed_field, field_validator

from cgdtk_cli.exceptions import CgdtkException


class ToolABC(BaseModel, ABC):
    name: str
    executable_name: str
    install_url: str = Field(default="http://localhost:8000")

    @field_validator("install_url")
    @classmethod
    def validate_install_url(cls, v: str) -> str:
        HttpUrl(v)
        return v

    def _extract_version(self, output: str) -> str:
        """Attempts to extract a string that looks like a semver."""
        # TODO: Is there a better pattern for this?
        semver_patterns = [
            r"v?(\d+\.\d+\.\d+)",  # 1.2.3 or v1.2.3
            r"version\s+v?(\d+\.\d+\.\d+)",  # "version 1.2.3"
            r"(\d+\.\d+)",  # 1.2 (fallback)
        ]

        for pattern in semver_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)

        return "Unknown"

    @abstractmethod
    def get_tool_version(self) -> str:
        """Override this method to provide a way for the tool to be tested."""
        pass

    @computed_field
    @property
    def exec_version(self) -> str:
        return self.get_tool_version()

    @computed_field
    @property
    def executable_path(self) -> Path | None:
        which_path = shutil.which(self.executable_name)
        return Path(which_path) if which_path else None

    @computed_field()
    @property
    def is_installed(self) -> bool:
        return self.executable_path is not None

    @computed_field()
    @property
    def is_executable(self) -> bool:
        return (
            self.executable_path is not None
            and self.executable_path.is_file()
            and os.access(self.executable_path, os.X_OK)
        )

    @abstractmethod
    def configuration_check(self) -> bool:
        """Override this method to provide a way for the tool to be tested."""
        pass

    @computed_field()
    @property
    def is_configured(self) -> bool:
        # If the tool isn't installed or executable, we assume it is not configured.
        if not self.is_installed or not self.is_executable:
            return False

        # We'll check if the tool is configured by runnint the self.__configuration_check() method.
        # This method should be implemented on any subclass.
        if not self.configuration_check():
            return False

        return True

    # TODO: Consider breaking down the exec into common actions of "show", "apply", etc
    def exec(self, command_args: List[str], cwd: Path = Path.cwd()) -> str:
        if self.executable_path is None:
            raise CgdtkException(f"Tool {self.name} not found in PATH")

        command = [self.executable_path] + command_args

        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)

        if result.returncode != 0:
            raise CgdtkException(f"Problem running tool {self.name}")
        return result.stdout.strip()


class ToolBasic(ToolABC):
    """A basic tool that can be used if there is not any customized logic for configuration checks."""

    def get_tool_version(self) -> str:
        """The genericised get_tool_version method in ToolBasic is implemented to provide a
        check against the common ways to version. If the tool you want to implement does not
        provide a version with "--version", "-v" or "version", implement a new Tool from
        ToolABC.

        Returns:
            str: A string value of the tools version or "Unknown"
        """

        tool_version = "Unknown"

        if not self.is_installed:
            return tool_version

        version_argument_variants = ["--version", "-v", "version"]

        for variant in version_argument_variants:
            try:
                tool_version = self.exec([variant])
                break
            except CgdtkException:
                continue

        # Try to extract a semver from the output
        tool_version = self._extract_version(tool_version)

        return tool_version

    def configuration_check(self) -> bool:
        return True
