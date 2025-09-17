from textual.widgets import Log

class LogsContainer(Log):

    def on_mount(self) -> None:
        self.border_title = "Logs"
