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


@modules_cli_group.command(name="variables", help="List all the variables of a module")
def list_module_variables(
    name: Annotated[
        str, typer.Argument(help="Name of the module to show", callback=module_callback)
    ],
) -> None:
    module = cast(TerraformModule, name)

    if len(module.variables) == 0:
        print(f"No variables found for module {module.name}")
        return

    console = Console()

    with console.pager():
        for var in module.variables:
            console.print("-" * 20)
            console.print(f"Variable: {var.name}")
            console.print(f"Type: {var.type.value}")
            console.print(f"Default: {var.default}")
            console.print(f"Description:\n{var.description}\n\n")
            console.print()
