from typing import Dict

from cgdtk_cli.tools.awscli import ToolAwsCli
from cgdtk_cli.tools.base import ToolABC, ToolBasic

INFRA_TOOLS: Dict[str, ToolABC] = {
    "tfenv": ToolBasic(
        name="tfenv",
        executable_name="tfenv",
        install_url="https://github.com/tfutils/tfenv",
    ),
    "packer": ToolBasic(
        name="packer",
        executable_name="packer",
        install_url="https://developer.hashicorp.com/packer/tutorials/docker-get-started/get-started-install-cli",
    ),
    "aws-cli": ToolAwsCli(),
    "ansible": ToolBasic(
        name="ansible",
        executable_name="ansible",
        install_url="https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html",
    ),
    "terraform": ToolBasic(
        name="terraform",
        executable_name="terraform",
        install_url="https://developer.hashicorp.com/terraform/install",
    ),
    "tgenv": ToolBasic(
        name="tgenv", executable_name="tgenv", install_url="https://github.com/tgenv/tgenv"
    ),
    "terragrunt": ToolBasic(
        name="terragrunt",
        executable_name="terragrunt",
        install_url="https://terragrunt.gruntwork.io/docs/getting-started/install/",
    ),
}
