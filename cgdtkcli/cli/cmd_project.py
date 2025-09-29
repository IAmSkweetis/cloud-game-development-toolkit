import typer
from rich import print

from cgdtkcli.config import cgdtk_config

project_cli_group = typer.Typer(help="Project related commands", no_args_is_help=True)


@project_cli_group.command(name="list", help="List all projects.")
def list_projects() -> None:
    """List all projects."""

    print("Projects:")
    for project in cgdtk_config.projects:
        print(f"  - {project.name}: [cyan]{project.path}[/cyan]")
        if project.environments:
            for env in project.environments:
                print(f"      - {env.name}")
