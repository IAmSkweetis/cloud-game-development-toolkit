from pathlib import Path

from git import Repo

from cgdtk_cli.exceptions import CgdtkRepoError


def get_repo_root() -> Path:
    repo = Repo(__file__, search_parent_directories=True)
    if repo.working_tree_dir is None:
        raise CgdtkRepoError(f"Unable to find root of repo from {__file__}")

    return Path(repo.working_tree_dir)


CGDTK_REPO_ROOT = get_repo_root()
