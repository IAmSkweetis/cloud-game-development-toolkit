import typer

from cgdtkcli.cli.cmd_config import config_cli_group
from cgdtkcli.cli.cmd_tools import tools_cli_group
from cgdtkcli.terminal.app import start_terminal

def main_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        start_terminal()

cgdtkcli_entry = typer.Typer(
    help="AWS Cloud Game Development Toolkit CLI",
    # NOTE: This is disabled until the commands are worked out.
    # callback=main_callback,
    no_args_is_help=True,
    invoke_without_command=True,
)

cgdtkcli_entry.add_typer(config_cli_group, name="config")
cgdtkcli_entry.add_typer(tools_cli_group, name="tools")
