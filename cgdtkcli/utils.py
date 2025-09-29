from pathlib import Path

from git import Repo

from cgdtkcli.exceptions import CgdtkException


def get_repo_root() -> Path:
    # We assume we are starting where the repo was cloned.
    # We need to find the root.
    repo = Repo(Path.cwd(), search_parent_directories=True)

    if repo.working_tree_dir is None:
        raise CgdtkException("Could not find git repo root.")

    return Path(repo.working_tree_dir)
