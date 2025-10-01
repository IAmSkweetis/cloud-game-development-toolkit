import typer

from cgdtk_cli import __version__
from cgdtk_cli.cli.cmd_environment import environment_cli_group
from cgdtk_cli.cli.cmd_modules import modules_cli_group
from cgdtk_cli.cli.cmd_tools import tools_cli_group

cli_entry = typer.Typer(
    help="AWS Cloud Game Development Toolkit CLI",
    no_args_is_help=True,
)


@cli_entry.command(name="version")
def version() -> None:
    """
    Print the version of the CLI.
    """

    typer.echo(f"AWS Cloud Game Development Toolkit CLI (cgdtk) v{__version__}")


cli_entry.add_typer(modules_cli_group, name="module")
cli_entry.add_typer(tools_cli_group, name="tools")
cli_entry.add_typer(environment_cli_group, name="environment")
