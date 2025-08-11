from typing import Dict

import typer
from rich.prompt import Confirm
from rich.table import Table
from typing_extensions import Annotated

from cgdtkcli.console import cgdtkcli_console
from cgdtkcli.project.models import DEFAULT_PROJECTS_ROOT, Project
from cgdtkcli.tools import INFRA_TOOLS, is_aws_configured

project_cli_group = typer.Typer(help="Project related commands", no_args_is_help=True)


@project_cli_group.command(help="Checks that the system is ready to run the CLI")
def system_check() -> bool:
    """Checks that the system is ready to run the CLI. We'll ensure we have the following tools installed:

    - Terraform
    - Packer
    - Ansible
    - AWS CLI

    """
    # Used to capture the overall results of any system check. We'll use this to determine if the
    # overall system check passed or not.
    system_check_results: Dict[str, bool] = {}

    # Used to capture the results and provide a summarized view of the checks.
    system_check_results_table: Table = Table(title="System Check Results")
    system_check_results_table.add_column("Tool", justify="left", style="cyan")
    system_check_results_table.add_column("Status", justify="left")
    system_check_results_table.add_column("Info", justify="left", style="green")

    cgdtkcli_console.print("Verifying if system is ready to use the CGD Toolkit...")

    # Check infra tools
    cgdtkcli_console.rule("[bold cyan]Infra Tools Check")

    tool_check = 0
    for tool in INFRA_TOOLS:
        cgdtkcli_console.print(f"Checking for [bold cyan]{tool.name}[/bold cyan]...")
        if tool.executable_path is None:
            cgdtkcli_console.print(
                f"[red]Tool [bold cyan]{tool.name}[/bold cyan] is not found in PATH[/red]"
            )
            system_check_results_table.add_row(tool.name, "[red]Not Found")
        else:
            cgdtkcli_console.print(
                f"Tool [bold cyan]{tool.name}[/bold cyan] is found in PATH at {tool.executable_path}"
            )
            system_check_results_table.add_row(
                tool.name, "[green]Found", f"Path: {str(tool.executable_path)}"
            )
            tool_check += 1

        system_check_results["tool_check"] = tool_check == 4

    # Check AWS CLI configuration
    cgdtkcli_console.rule("[bold cyan]AWS CLI Configuration Check")
    cgdtkcli_console.print("Checking if [bold cyan]aws-cli[/bold cyan] is configured...")
    if not is_aws_configured():
        cgdtkcli_console.print(
            "[red]Tool [bold cyan]aws-cli[/bold cyan] is not configured. Please run [bold]aws "
            "configure[/bold] to configure it.[/red]"
        )
        system_check_results_table.add_row("aws-cli", "[red]Not configured")
        system_check_results["aws_configured"] = False
    else:
        cgdtkcli_console.print("Tool [bold cyan]aws-cli[/bold cyan] has a valid configuration")
        system_check_results_table.add_row("aws-cli", "[green]Configured")
        system_check_results["aws_configured"] = True

    # Print our summary table
    cgdtkcli_console.rule("[bold cyan]System Check Summary")
    cgdtkcli_console.print(system_check_results_table, new_line_start=True)

    # If any of the checks failed, we'll return False and notify the user.
    if not all(system_check_results.values()):
        cgdtkcli_console.print(
            "[red]System check failed!!![/red]\n"
            "Check the docs for requirements: "
            "https://aws-games.github.io/cloud-game-development-toolkit/latest/docs/"
            "getting-started.html",
            new_line_start=True,
        )

        return False

    # If all is well, return True.
    cgdtkcli_console.print("[green]System check passed![/green]", new_line_start=True)
    return True


@project_cli_group.command(help="Initializes a new project")
def init(
    project_name: Annotated[
        str, typer.Option(help="Name of the cgdtk infrastructure project.")
    ] = "my-game-infra",
) -> None:
    """
    Initializes a new project and walks a user through the initial configuration.
    """

    # We'll run a system check before init. This is used as a safety measure.
    cgdtkcli_console.print("Running system check before initializing a new project...")

    if not system_check():
        raise typer.Exit(code=1)

    cgdtkcli_console.print(
        f"System check passed. Initializing project [bold cyan]{project_name}[/bold cyan]..."
    )

    cgdtkcli_console.rule("[bold cyan]Creating project folder")
    cgdtkcli_console.print(f"Checking if [bold cyan]{DEFAULT_PROJECTS_ROOT}[/bold cyan] exists...")
    if not DEFAULT_PROJECTS_ROOT.exists():
        cgdtkcli_console.print(
            f"[bold cyan]{DEFAULT_PROJECTS_ROOT}[/bold cyan] does not exist. Creating it..."
        )
        DEFAULT_PROJECTS_ROOT.mkdir(parents=True)
    else:
        cgdtkcli_console.print(
            f"[bold cyan]{DEFAULT_PROJECTS_ROOT}[/bold cyan] exists. Moving on..."
        )

    cgdtkcli_console.print(
        f"Creating project directory for [bold cyan]{project_name}[/bold cyan]..."
    )
    project = Project(name=project_name)
    try:
        project.path.mkdir(parents=True)
    except FileExistsError:
        cgdtkcli_console.print(
            f"[red]Project directory for [bold cyan]{project_name}[/bold cyan] already exists.[/red]"
        )
        proj_dir_overwrite: bool = Confirm.ask(
            "Do you want to overwrite the existing project directory? This will delete "
            f"any existing data at {project.path.as_posix()}"
        )

        if proj_dir_overwrite:
            cgdtkcli_console.print(
                f"Overwriting project directory for [bold cyan]{project_name}[/bold cyan]..."
            )
            project.path.rmdir()
            project.path.mkdir(parents=True)

    cgdtkcli_console.print(
        f"Project directory for [bold cyan]{project_name}[/bold cyan] created at [bold cyan]{project.path}[/bold cyan]"
    )
