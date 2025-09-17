from typing import TYPE_CHECKING

from boto3 import Session

from cgdtkcli.config import cgdtk_config
from cgdtkcli.tools.tool import ToolABC

if TYPE_CHECKING:
    from mypy_boto3_sts.client import STSClient


class ToolAwsCli(ToolABC):
    def __init__(self) -> None:
        super().__init__(
            name="aws-cli",
            executable_name="aws",
            install_url="https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html",
        )

    def get_tool_version(self) -> str:
        if not self.is_installed:
            return "Unknown"

        return self.exec(["--version"])

    def configuration_check(self) -> bool:
        session = Session(
            profile_name=cgdtk_config.aws_profile, region_name=cgdtk_config.aws_region
        )
        client: "STSClient" = session.client("sts")  # type: ignore

        response = client.get_caller_identity()

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return True

        return False
