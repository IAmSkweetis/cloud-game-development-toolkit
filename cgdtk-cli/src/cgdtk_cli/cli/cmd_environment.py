import typer

from cgdtk_cli.environment import ENVIRONMENT_CONFIG

environment_cli_group = typer.Typer(
    help="Commands to manage a CGD Environments", no_args_is_help=True
)


@environment_cli_group.command(name="list", help="List all environments.")
def list_environments() -> None:
    """
    List all environments.
    """

    print("Environments:")    

    for env in ENVIRONMENT_CONFIG.environments:
        print(f" - {env.name}")
