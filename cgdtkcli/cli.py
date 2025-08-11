import typer

from cgdtkcli.project.cli import project_cli_group

cgdtkcli_entry = typer.Typer(help="AWS Cloud Game Development Toolkit CLI", no_args_is_help=True)

cgdtkcli_entry.add_typer(project_cli_group, name="project")
