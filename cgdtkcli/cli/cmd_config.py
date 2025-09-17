import typer
from rich.pretty import pprint

from cgdtkcli.config import cgdtk_config
from cgdtkcli.logging import LOG

config_cli_group = typer.Typer(help="Commands to interact with CGDTK config.", no_args_is_help=True)


@config_cli_group.command(name="show", help="Show the CGDTK config.")
def show_config() -> None:
    """Show the CGDTK config."""
    env_file = cgdtk_config.model_config.get('env_file')
    LOG.info(f"Reading config from {env_file or 'environment variables'}")
    pprint(cgdtk_config.model_dump())
