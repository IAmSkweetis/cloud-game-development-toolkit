from enum import Enum
from pathlib import Path
from typing import List

from git import Repo
from hcl2.api import load as hcl2_load
from pydantic import BaseModel, computed_field

from cgdtk_cli.exceptions import CgdtkConfigError


class TerraformVariableType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOL = "bool"
    LIST = "list"
    MAP = "map"
    OBJECT = "object"
    TUPLE = "tuple"
    SET = "set"
    NULL = "null"


class TerraformVariable(BaseModel):
    name: str
    type: TerraformVariableType = TerraformVariableType.STRING
    default: str = ""
    description: str = ""


class TerraformModule(BaseModel):
    name: str
    path: Path

    @computed_field
    @property
    def variables(self) -> List[TerraformVariable]:
        variables_list = []
        variables_tf_path = self.path.joinpath("variables.tf")

        if not variables_tf_path.exists():
            return []

        with variables_tf_path.open("r") as f:
            variables_tf = hcl2_load(f)

        if "variable" not in variables_tf:
            return []

        for var_dict in variables_tf["variable"]:
            for var_name, var_config in var_dict.items():
                try:
                    var_type = TerraformVariableType(var_config.get("type", "string"))
                except ValueError:
                    var_temp = var_config.get("type", "string")
                    if var_temp.startswith("${list("):
                        var_type = TerraformVariableType.LIST
                    elif var_temp.startswith("${map("):
                        var_type = TerraformVariableType.MAP
                    elif var_temp.startswith("${object("):
                        var_type = TerraformVariableType.OBJECT
                    elif var_temp.startswith("${tuple("):
                        var_type = TerraformVariableType.TUPLE
                    elif var_temp.startswith("${set("):
                        var_type = TerraformVariableType.SET
                    else:
                        var_type = TerraformVariableType.STRING
                default = var_config.get("default", "")
                description = var_config.get("description", "")

                variables_list.append(
                    TerraformVariable(
                        name=var_name,
                        type=var_type,
                        default=str(default) if default is not None else "",
                        description=description,
                    )
                )

        return variables_list


def get_tf_modules() -> List[TerraformModule]:
    """Find all modules in the current repo.

    Returns:
        List[CgdtkModule]: A list of CgdtkModule objects.
    """
    repo = Repo(Path.cwd(), search_parent_directories=True)
    if repo.working_tree_dir is None:
        raise CgdtkConfigError(f"Unable to find root of repo from {Path.cwd()}")

    tf_module_path = Path(repo.working_tree_dir) / "modules"
    tf_modules = []
    skip_dirs = {"assets", "examples", "tests"}

    def _has_tf_files(path: Path) -> bool:
        return any(f.suffix == ".tf" for f in path.iterdir() if f.is_file())

    def _find_tf_modules(path: Path, parent_name: str = "") -> None:
        if path.name in skip_dirs:
            return

        if _has_tf_files(path):
            module_name = f"{parent_name}/{path.name}" if parent_name else path.name
            tf_modules.append(TerraformModule(name=module_name, path=path))

        for subdir in path.iterdir():
            if subdir.is_dir():
                current_parent = f"{parent_name}/{path.name}" if parent_name else path.name
                _find_tf_modules(subdir, current_parent)

    for module_path in tf_module_path.iterdir():
        if module_path.is_dir():
            _find_tf_modules(module_path)

    return tf_modules


TERRAFORM_MODULES = get_tf_modules()
