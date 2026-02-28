from typing import Optional

import yaml
import os
import sys
import shutil
from pathlib import Path
from git import Repo, InvalidGitRepositoryError


DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
OPTIONS_FILE = DATA_DIR / "options.yaml"
CHECKOUT_DIR = DATA_DIR / "checkout"


def _read_options() -> dict:
    if not OPTIONS_FILE.exists():
        raise RuntimeError(f"Missing {OPTIONS_FILE}")

    with OPTIONS_FILE.open("r", encoding="utf-8") as file:
        options = yaml.safe_load(file)

    repo_url = str(options.get("repo_url", "")).strip()
    branch = str(options.get("branch", "main")).strip() or "main"
    app_subdir = str(options.get("app_subdir", "")).strip("/")
    setup_command = str(options.get("setup_command", "")).strip()
    start_command = str(options.get("start_command", "")).strip()
    pull_on_start = bool(options.get("pull_on_start", True))

    if not repo_url:
        raise RuntimeError("Option 'repo_url' is required")
    if not start_command:
        raise RuntimeError("Option 'start_command' is required")

    return {
        "repo_url": repo_url,
        "branch": branch,
        "app_subdir": app_subdir,
        "setup_command": setup_command,
        "start_command": start_command,
        "pull_on_start": pull_on_start,
    }


def _clone_or_pull(repo_url: str, branch: str, pull_on_start: bool) -> None:
    CHECKOUT_DIR.parent.mkdir(parents=True, exist_ok=True)

    repo = None
    if not CHECKOUT_DIR.exists() or not (CHECKOUT_DIR / ".git").exists():
        print(f"Cloning {repo_url} ({branch})...")
        if CHECKOUT_DIR.exists():
            shutil.rmtree(CHECKOUT_DIR)
        repo = Repo.clone_from(repo_url,
                               to_path=CHECKOUT_DIR,
                               branch=branch)
        return

    try:
        repo = Repo(CHECKOUT_DIR)
    except InvalidGitRepositoryError:
        shutil.rmtree(CHECKOUT_DIR)
        repo = Repo.clone_from(repo_url, to_path=CHECKOUT_DIR, branch=branch)
        return

    if not pull_on_start:
        return

    origin = repo.remotes.origin
    origin.fetch()
    repo.git.checkout(branch)
    repo.git.reset('--hard', f'origin/{branch}')
    print(f"Checked out {repo_url} ({branch})")


def _resolve_workdir(app_subdir: str) -> Path:
    base = CHECKOUT_DIR.resolve()
    workdir = (base / app_subdir).resolve() if app_subdir else base
    if not str(workdir).startswith(str(base)):
        raise RuntimeError("Invalid app_subdir")
    if not workdir.exists() or not workdir.is_dir():
        raise RuntimeError("Configured app_subdir does not exist")
    return workdir


def _setup_environment(options: dict) -> None:
    setup_command = options.get("setup_command") if options else None
    if not setup_command:
        return
    print(f"Running setup command: {setup_command}")
    os.execvp("sh", ["sh", "-lc", setup_command])


def main() -> None:
    try:
        options = _read_options()
        print(f"Starting with options: {options}")
        _clone_or_pull(options["repo_url"],
                       options["branch"], options["pull_on_start"])
        workdir = _resolve_workdir(options["app_subdir"])
    except Exception as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        sys.exit(1)

    os.chdir(workdir)
    _setup_environment(options)
    os.execvp("sh", ["sh", "-lc", options["start_command"]])


if __name__ == "__main__":
    main()
