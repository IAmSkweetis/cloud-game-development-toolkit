from typing import List, cast

import typer
from rich.console import Console
from rich.prompt import Confirm
from typing_extensions import Annotated

from cgdtk_cli.environment import (
    CgdtkEnvironment,
    CgdtkEnvironmentsConfig,
    CgdtkEnvironmentType,
    render_environment_from_template,
)
from cgdtk_cli.module import VALID_MODULE_NAMES
from cgdtk_cli.tools import INFRA_TOOLS

environment_cli_group = typer.Typer(
    help="Commands to manage a CGD Environments", no_args_is_help=True
)


def environment_exists(environment_name: str) -> CgdtkEnvironment:
    """
    Check if an environment exists.
    """

    cgdtk_env_config = CgdtkEnvironmentsConfig()

    if environment_name not in cgdtk_env_config.environments:
        raise typer.BadParameter(f"Environment {environment_name} does not exist.")

    return cgdtk_env_config.environments[environment_name]


@environment_cli_group.command(name="list", help="List all environments.")
def list_environments() -> None:
    """
    List all environments.
    """
    cgdtk_env_config = CgdtkEnvironmentsConfig()

    if not cgdtk_env_config.environments:
        raise typer.BadParameter("No environments found.")

    print("Environments:")
    for env, _ in cgdtk_env_config.environments.items():
        print(f"  {env}")


@environment_cli_group.command(name="show", help="Show the config for a given environment.")
def show_environment(
    environment_name: Annotated[
        str, typer.Option(help="The environment to show", callback=environment_exists)
    ],
) -> None:
    environment = cast(CgdtkEnvironment, environment_name)

    console = Console(width=100)
    console.print(environment)


def split_and_process_terraform_modules(
    terraform_modules: List[str],
) -> List[str]:
    """
    Split a comma seperated list into a list of strings and verify that it is a valid module.
    """
    processed_modules = [module.strip() for item in terraform_modules for module in item.split(",")]

    invalid_modules = [m for m in processed_modules if m not in VALID_MODULE_NAMES]
    if invalid_modules:
        raise typer.BadParameter(f"Module(s) {', '.join(invalid_modules)} do not exist.")

    return processed_modules


@environment_cli_group.command(name="create", help="Create a new environment in config.")
def create_environment(
    environment_name: Annotated[
        str,
        typer.Option(help="The name of the environment to create"),
    ],
    environment_type: Annotated[
        CgdtkEnvironmentType,
        typer.Option(help="The type of environment to create"),
    ] = CgdtkEnvironmentType.TERRAFORM,
    terraform_modules: Annotated[
        List[str],
        typer.Option(
            help=(
                "The terraform modules to include in the environment. Multiple "
                "`--terraform-modules` can be provided. Alternatively, use a comma seperated list."
            ),
            callback=split_and_process_terraform_modules,
        ),
    ] = [],
    vpc_id: Annotated[
        str,
        typer.Option(help="VPC ID of the environment..."),
    ] = "",
    overwrite: Annotated[
        bool,
        typer.Option(help="Overwrite an existing environment"),
    ] = False,
    yes_im_sure: Annotated[
        bool,
        typer.Option(help="If you are really sure you want to overwrite the environment..."),
    ] = False,
) -> None:

    console = Console(width=100)

    # Instantiate the config.
    cgdtk_env_config = CgdtkEnvironmentsConfig()

    # Check if the environment exists.
    if environment_name in cgdtk_env_config.environments and not overwrite:
        raise typer.BadParameter(
            f"Environment {environment_name} already exists. Use --overwrite to overwrite."
        )

    # Even if the user provides the overwrite flag, we REALLY want to verify.
    if overwrite and not yes_im_sure:
        overwrite_confirm = Confirm.ask(
            "Proceeding will delete [red bold]EVERYTHING[/red bold] in "
            f"[cyan]{cgdtk_env_config.environments[environment_name].path}[/cyan]. \n\n"
            "[yellow italic]Are you absolutely sure you want to proceed?",
            console=console,
        )

        if not overwrite_confirm:
            raise typer.Abort()

    # Let's create our environment object.
    console.print("[purple]Creating environment...")
    environment = CgdtkEnvironment(
        name=environment_name,
        environment_type=environment_type,
        terraform_modules=terraform_modules,
    )
    cgdtk_env_config.environments[environment_name] = environment

    # Write the config to file.
    console.print("[purple]Writing config to file...")
    cgdtk_env_config.write_to_file()

    # Create the environment directory.
    render_environment_from_template(
        environment=environment, console=console, vpc_id=vpc_id, overwrite=overwrite
    )

    # print out the environment to console
    console.print(f"[purple]Environment {environment.name} created successfully...")
    console.print(environment)

    # Run a terraform init on the environment.
    console.rule("Begin [purple i]terraform init")
    console.print(f"[purple]Initializing environment {environment.name}...")

    # Check if terraform is installed.
    if not INFRA_TOOLS["terraform"].is_ready:
        raise typer.BadParameter("Terraform is not installed.")

    # Execute the terraform init command.
    console.print("[purple]Running terraform init...")
    INFRA_TOOLS["terraform"].exec(
        command_args=["init"], cwd=environment.path / "terraform", console=console
    )
    console.rule("End [purple i]terraform init")

    # We're done!
    console.print(
        "\n\n[green]Review the generated configuration and the CGD Docs on how to continue."
    )


@environment_cli_group.command(name="init", help="Runs a terraform init on a given environment.")
def init_environment(
    environment_name: Annotated[
        str,
        typer.Option(help="The environment to init", callback=environment_exists),
    ],
) -> None:
    environment = cast(CgdtkEnvironment, environment_name)

    console = Console()
    console.print(f"[purple]Initializing environment {environment.name}...")

    # Check if terraform is installed.
    if not INFRA_TOOLS["terraform"].is_ready:
        raise typer.BadParameter("Terraform is not installed.")

    # Execute the terraform init command.
    console.print("[purple]Running terraform init...")
    INFRA_TOOLS["terraform"].exec(
        command_args=["init"], cwd=environment.path / "terraform", console=console
    )
