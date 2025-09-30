from typing import TYPE_CHECKING

from boto3 import Session
from botocore.exceptions import NoCredentialsError

from cgdtk_cli.exceptions import CgdtkConfigError
from cgdtk_cli.tools.base import ToolABC

if TYPE_CHECKING:
    from mypy_boto3_sts.client import STSClient


class ToolAwsCli(ToolABC):
    def __init__(self) -> None:
        super().__init__(
            name="aws-cli",
            executable_name="aws",
            install_url=(
                "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
            ),
        )

    def get_tool_version(self) -> str:
        if not self.is_installed:
            return "Unknown"
        
        return self._extract_version(self.exec(["--version"]))

    def configuration_check(self) -> bool:
        session = Session()
        client: "STSClient" = session.client("sts")  # type: ignore

        try:
            response = client.get_caller_identity()
        except NoCredentialsError as err:
            raise CgdtkConfigError(
                "AWS credentials not configured. Use the environment variables AWS_PROFILE and/or"
                " AWS_REGION."
            ) from err
        finally:
            client.close()

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return True

        return False
