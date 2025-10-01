from typing import cast

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated

from cgdtk_cli.module import TERRAFORM_MODULES, TerraformModule

modules_cli_group = typer.Typer(help="Manage modules", no_args_is_help=True)


def module_callback(module_name: str) -> TerraformModule:
    for module in TERRAFORM_MODULES:
        if module.name == module_name:
            return module
    raise typer.BadParameter(f"Module {module_name} not found")


@modules_cli_group.command(name="list", help="List all modules")
def list_modules() -> None:
    print("List all modules")

    module_table = Table("Name", "Path", "Variables")
    for module in TERRAFORM_MODULES:
        module_table.add_row(module.name, module.path.as_posix(), str(len(module.variables)))

    rprint(module_table)


@modules_cli_group.command(name="show", help="Show the details of a module")
def show_module(
    name: Annotated[
        str, typer.Argument(help="Name of the module to show", callback=module_callback)
    ],
) -> None:

    # Cast the module to TerraformModule for proper type hints
    module = cast(TerraformModule, name)

    print(f"Module: {module.name}")
    print(f"Path: {module.path}")
    print(f"Variables: {len(module.variables)}")


# Module Variables subcommand group.
variables_subcommand = typer.Typer(help="Manage variables", no_args_is_help=True)


@variables_subcommand.command(name="list", help="List all the variables of a module")
def list_module_variables(
    name: Annotated[
        str, typer.Argument(help="Name of the module to list variables", callback=module_callback)
    ],
    details: Annotated[
        bool,
        typer.Option(
            help=(
                "Show full details of the variable. Otherwise, only list the names and types of "
                "the variables."
            )
        ),
    ] = False,
) -> None:
    module = cast(TerraformModule, name)

    if len(module.variables) == 0:
        print(f"No variables found for module {module.name}")
        return

    console = Console(width=100)

    if details:
        for i, var in enumerate(module.variables):
            console.clear()
            console.print(var)
            console.print()
            if i < len(module.variables) - 1:
                console.input("\nPress Enter for next variable (or Ctrl+C to exit)...")
    else:
        var_table = Table(
            title=f"[bold]Variables for [bold cyan]{module.name}[/bold cyan][/bold]",
            box=None,
            width=100,
        )
        var_table.add_column(
            "Variable",
            style="cyan",
            no_wrap=True,
            min_width=max(len(v.name) for v in module.variables),
        )
        var_table.add_column("Type", style="magenta", min_width=10)
        var_table.add_column("Default", style="green", min_width=10, overflow="fold")

        for var in module.variables:
            var_table.add_row(var.name, var.type, var.default)

        console.print(var_table)


@variables_subcommand.command(name="show", help="Show the details of a variable")
def show_module_variable(
    module_name: Annotated[
        str, typer.Argument(help="Name of the module to show", callback=module_callback)
    ],
    variable_name: Annotated[str, typer.Argument(help="Name of the variable to show")],
) -> None:
    module = cast(TerraformModule, module_name)

    console = Console(width=100)

    if len(module.variables) == 0:
        console.print(f"No variables found for module {module.name}")
        return

    for var in module.variables:
        if var.name == variable_name:
            console.clear()
            console.print(var)
            return

    console.print(f"Variable {variable_name} not found in module {module.name}")


modules_cli_group.add_typer(variables_subcommand, name="variables")
