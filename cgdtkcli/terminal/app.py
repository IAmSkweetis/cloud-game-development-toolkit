from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Button, ContentSwitcher, Footer, Header, Static

from cgdtkcli.logging import LOG, logger_factory
from cgdtkcli.terminal.logs import LogsContainer
from cgdtkcli.terminal.tools import ToolsContainer


class HomeContainer(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Static("Home", id="home")


class CgdtkApp(App[None]):
    CSS_PATH = "cgdtk.tcss"

    BINDINGS = [Binding(key="m", action="focus('sidebar-menu')", description="Menu")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # TODO: Replace this with something.
        with VerticalScroll(id="main-screen"):
            with Vertical(classes="box", id="sidebar-menu"):
                yield Button("Home", id="home")
                yield Button("Tools", id="tools")

            with ContentSwitcher(initial="home", classes="box", id="main-area"):
                yield HomeContainer(id="home")
                yield ToolsContainer(id="tools")

            yield LogsContainer(classes="box", id="logs")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one(ContentSwitcher).current = event.button.id

    def on_mount(self) -> None:
        self.title = "Cloud Game Development Toolkit"
        self.sub_title = "A project by AWS for Games"

    def on_ready(self) -> None:
        log = self.query_one("#logs", LogsContainer)
        logger_factory.add_tui_handler(LOG, log)
        LOG.info("Ready!")


def start_terminal() -> None:
    # Turn off console logging.
    log_handlers = LOG.handlers.copy()
    for log_handler in log_handlers:
        if log_handler.name == "CONSOLE":
            LOG.removeHandler(log_handler)
            break

    app = CgdtkApp()
    app.run()
