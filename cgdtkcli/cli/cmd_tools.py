from typing import cast

import typer
from rich import print
from rich.table import Table
from typing_extensions import Annotated

from cgdtkcli.tools import INFRA_TOOLS, ToolABC

tools_cli_group = typer.Typer(
    help="Commands to interact directly with tools.", no_args_is_help=True
)

def tool_callback(tool_name: str) -> ToolABC:
    if tool_name not in INFRA_TOOLS:
        raise typer.BadParameter(f"Tool {tool_name} not found.")
    return INFRA_TOOLS[tool_name]

@tools_cli_group.command(name="list", help="List the tools.")
def list_tools() -> None:
    """List the tools."""

    tool_table = Table(title="Tools")
    tool_table.add_column("Name", justify="left", no_wrap=True)
    tool_table.add_column("Version", justify="left", no_wrap=True)
    tool_table.add_column("Path", justify="left", no_wrap=True)
    tool_table.add_column("Installed", justify="center", no_wrap=True)
    tool_table.add_column("Executable", justify="center", no_wrap=True)
    tool_table.add_column("Configured", justify="center", no_wrap=True)

    # Generate the table from the INFRA_TOOLS dictionary
    for tool in INFRA_TOOLS.values():
        tool_table.add_row(
            tool.name,
            tool.exec_version,
            tool.executable_path.as_posix() if tool.executable_path else "😭",
            "🎉" if tool.is_installed else "😭",
            "🎉" if tool.is_executable else "😭",
            "🎉" if tool.is_configured else "😭",
        )
        

    print(tool_table)


@tools_cli_group.command(name="test", help="Test a tool")
def verify_tool(tool: Annotated[str, typer.Argument(help="The tool to test", callback=tool_callback)]) -> None:

    # We use the tool_callback to validate that the tool is in the list and to retrieve the tool
    # from the configured tools in the INFRA_TOOLS dictionary. We recast the tool into infra_tool 
    # for proper type hints.
    infra_tool = cast(ToolABC, tool)

    print(f"Testing tool: {infra_tool.name}")
    print(f"Tool is installed: {infra_tool.is_installed}")
    print(f"Tool is executable: {infra_tool.is_executable}")
    print(f"Tool is configured: {infra_tool.is_configured}")
    print(f"Tool version: {infra_tool.exec_version}")
