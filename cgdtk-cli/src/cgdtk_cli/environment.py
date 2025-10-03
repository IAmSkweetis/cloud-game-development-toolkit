import shutil
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple, override

import yaml
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field, computed_field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.panel import Panel
from rich.tree import Tree

from cgdtk_cli.utils import CGDTK_REPO_ROOT

CGDTK_ENVIRONMENTS_PATH = CGDTK_REPO_ROOT.joinpath("environments")


# TODO: Is it even useful to define an EnvironmentType? My reasoning for having this is if there
# was desire to have two different flows. I'm leaving it in, but TERRAGRUNT commented out.
class CgdtkEnvironmentType(str, Enum):
    TERRAFORM = "terraform"
    # TERRAGRUNT = "terragrunt"


class CgdtkEnvironment(BaseModel):
    name: str
    environment_type: CgdtkEnvironmentType = CgdtkEnvironmentType.TERRAFORM
    terraform_modules: List[str] = Field(default_factory=list)

    @computed_field
    @property
    def path(self) -> Path:
        return CGDTK_ENVIRONMENTS_PATH / self.name

    @computed_field
    @property
    def initialized(self) -> bool:
        return self.path.joinpath("terraform.tfstate").exists()

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:

        main_panel = Panel(
            f"[bold]Name:[/] {self.name}\n"
            f"[bold]Type:[/] {self.environment_type.value}\n"
            f"[bold]Path:[/] {self.path.as_posix()}\n"
            f"[bold]Initialized:[/] {self.initialized}",
            title="[white bold]Info",
            title_align="left",
            border_style="blue",
            expand=False,
        )

        module_panel = Panel(
            (
                f"[bold]Modules:[/]\n - " + "\n - ".join(self.terraform_modules)
                if self.terraform_modules
                else "[bold]Modules:[/] None"
            ),
            title="[white bold]Terraform Modules",
            title_align="left",
            border_style="blue",
            expand=False,
        )

        environment_tree = Tree(self.path.as_posix())
        self._add_tree_nodes(environment_tree, self.path)

        tree_panel = Panel(
            environment_tree,
            title="[white bold]Directory",
            title_align="left",
            border_style="blue",
            expand=False,
        )

        env_panel_group = Group(main_panel, module_panel, tree_panel)

        yield Panel(
            env_panel_group,
            title=f"[white bold]{self.name}",
            title_align="left",
            border_style="blue",
            expand=False,
        )

    def _add_tree_nodes(self, tree_node: Tree, path: Path) -> None:
        for item in path.iterdir():
            if item.is_dir():
                dir_node = tree_node.add(item.name)
                self._add_tree_nodes(dir_node, item)
            else:
                tree_node.add(item.name, style="dim")


class CgdtkEnvironmentsConfig(BaseSettings):
    environments: Dict[str, CgdtkEnvironment] = Field(default_factory=dict)
    model_config = SettingsConfigDict()

    @classmethod
    @override
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        env_config_file = CGDTK_ENVIRONMENTS_PATH / "config.yaml"

        return (
            YamlConfigSettingsSource(
                settings_cls,
                yaml_file=env_config_file,
                yaml_file_encoding="utf-8",
            ),
        )

    def write_to_file(self) -> None:
        env_config_file = CGDTK_ENVIRONMENTS_PATH / "config.yaml"

        with open(env_config_file, "w", encoding="utf-8") as fp:
            yaml.dump(self.model_dump(mode="json"), fp, allow_unicode=True)


def render_environment_from_template(
    environment: CgdtkEnvironment, console: Console, vpc_id: str, overwrite: bool = False
) -> None:

    templates_path = CGDTK_ENVIRONMENTS_PATH / "templates"

    j2_env = Environment(
        loader=FileSystemLoader(templates_path),
        keep_trailing_newline=True,
    )

    if environment.path.exists() and not overwrite:
        raise FileExistsError(f"Environment {environment.name} already exists.")
    else:
        console.print(f"[red]Deleting {environment.path}...")
        shutil.rmtree(environment.path, ignore_errors=True)

    # Template funtimes...
    for template_file in templates_path.rglob("*"):
        if template_file.is_dir():
            output_dir = environment.path / template_file.relative_to(templates_path)
            output_dir.mkdir(parents=True, exist_ok=True)
        # Render out the template files.
        if template_file.is_file():
            template = j2_env.get_template(str(template_file.relative_to(templates_path)))
            output_file = environment.path / template_file.relative_to(templates_path).with_suffix(
                ""
            )
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(
                template.render(
                    environment_name=environment.name,
                    terraform_modules=environment.terraform_modules,
                    vpc_id=vpc_id,
                )
            )
