from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import DataTable

from cgdtkcli.tools import INFRA_TOOLS


class ToolsContainer(VerticalScroll):

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        tool_table = self.query_one(DataTable[str])
        tool_table.add_columns("Name", "Version", "Path", "Installed", "Executable", "Configured")

        for tool in INFRA_TOOLS.values():
            tool_table.add_row(
                tool.name,
                tool.exec_version,
                tool.executable_path.as_posix() if tool.executable_path else "😭",
                "🎉" if tool.is_installed else "😭",
                "🎉" if tool.is_executable else "😭",
                "🎉" if tool.is_configured else "😭",
                key=tool.name,
            )
