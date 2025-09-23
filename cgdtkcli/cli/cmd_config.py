from pathlib import Path

import typer
from rich import print
from rich.pretty import pprint
from typing_extensions import Annotated

from cgdtkcli.config import cgdtk_config, write_config
from cgdtkcli.constants import DEFAULT_CGDTK_PATH
from cgdtkcli.exceptions import CgdtkConfigFileExistsError
from cgdtkcli.logging import LOG

config_cli_group = typer.Typer(help="Commands to interact with CGDTK config.", no_args_is_help=True)


@config_cli_group.command(name="show", help="Show the CGDTK config.")
def show_config() -> None:
    """Show the CGDTK config."""
    env_file = cgdtk_config.model_config.get("env_file")
    LOG.info(f"Reading config from {env_file or 'environment variables'}")
    pprint(cgdtk_config.model_dump(mode="json"))


@config_cli_group.command(name="export", help="Export the CGDTK config to file.")
def export_config(
    config_file: Annotated[
        Path, typer.Option(help="Path where the config file will be written.")
    ] = DEFAULT_CGDTK_PATH
    / "config.toml",
    overwrite: Annotated[
        bool, typer.Option(help="Overwrite the config file if it exists.")
    ] = False,
) -> None:
    """Export the CGDTK config."""
    print(f"Exporting config to {config_file}")
    try:
        write_config(cgdtk_config, config_file, overwrite)
    except CgdtkConfigFileExistsError:
        print(f"[red]Config file already exists at[/red] {config_file}")
        print("Use the --overwrite flag to overwrite the config.")
        typer.Exit(1)
