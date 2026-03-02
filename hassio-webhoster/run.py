import argparse
import os
import sys
import shutil
import subprocess
import signal
import time
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse
from git import Optional, Repo, InvalidGitRepositoryError

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
CHECKOUT_DIR = DATA_DIR / "checkout"

os.environ["PATH"] = f"/home/{os.getenv('USER', 'webhoster')}/.local/bin:{os.environ.get('PATH', '')}"


def _build_authenticated_repo_url(repo_url: str, github_token: Optional[str]) -> str:
    if not github_token:
        return repo_url

    parsed = urlparse(repo_url)
    if parsed.scheme != "https" or parsed.hostname not in {"github.com", "www.github.com"}:
        return repo_url

    token = quote(github_token, safe="")
    netloc = f"x-access-token:{token}@{parsed.netloc}"
    return urlunparse(parsed._replace(netloc=netloc))


class GitRepoWebhoster:
    def __init__(self, repo_url: str, branch: str, setup_command: str, start_command: str, github_token: Optional[str], poll_interval_seconds: int, checkout_dir: Path):
        self.repo_url = repo_url
        self.branch = branch
        self.setup_command = setup_command
        self.start_command = start_command
        self.github_token = github_token
        self.checkout_dir = checkout_dir
        self.poll_interval_seconds = poll_interval_seconds

        self._shutdown_requested = False

        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)

        self.repo = self._init_repo()
        self._app = None

    def run(self) -> None:
        self._supervise_application()

    def _init_repo(self) -> Repo:
        effective_repo_url = _build_authenticated_repo_url(
            self.repo_url, self.github_token)
        if not self.checkout_dir.exists() or not (self.checkout_dir / ".git").exists():
            print(
                f"Cloning {self.repo_url} ({self.branch}) into {self.checkout_dir}...")
            if self.checkout_dir.exists():
                shutil.rmtree(self.checkout_dir)
            repo = Repo.clone_from(effective_repo_url,
                                   to_path=self.checkout_dir,
                                   branch=self.branch)
        else:
            try:
                repo = Repo(self.checkout_dir)
            except InvalidGitRepositoryError:
                shutil.rmtree(self.checkout_dir)
                repo = Repo.clone_from(
                    effective_repo_url, to_path=self.checkout_dir, branch=self.branch)

        githash = repo.head.commit.hexsha[:8]
        commit_msg = repo.head.commit.message.splitlines()[0]
        print(
            f"Checked out {self.repo_url} ({self.branch}) at {githash}: {commit_msg}")
        return repo

    def _handle_shutdown_signal(self, signum, _frame) -> None:
        self._shutdown_requested = True
        print(
            f"Received signal {signum}, shutting down supervisor...")

    def _terminate_application(self) -> None:
        if self._app is None:
            return
        if self._app.poll() is not None:
            return
        self._app.terminate()
        try:
            self._app.wait(timeout=20)
        except subprocess.TimeoutExpired:
            self._app.kill()
            self._app.wait(timeout=10)

    def _supervise_application(self) -> None:
        while not self._shutdown_requested:
            self._setup_environment()
            self._app = self._start_application()
            print(f"Application started with PID {self._app.pid}")

            while not self._shutdown_requested:
                exit_code = self._app.poll()
                if exit_code is not None:
                    print(
                        f"Application exited with code {exit_code}; restarting...")
                    time.sleep(1)
                    break

                try:
                    if self._check_for_updates():
                        self._terminate_application()
                        print(
                            "Restarting application after repository update...")
                        break  # Will restart the app in the next loop iteration
                except Exception as error:
                    print(
                        f"[WARN] Update check failed: {error}", file=sys.stderr)

                time.sleep(self.poll_interval_seconds)

            if self._shutdown_requested:
                self._terminate_application()
                return

    def _setup_environment(self) -> None:
        if not self.setup_command:
            return
        print(f"Running setup command: {self.setup_command}...")
        subprocess.run(
            ["bash", "-lc", self.setup_command],
            check=True,
            cwd=self.checkout_dir,
            env=os.environ.copy()
        )
        print("Environment setup completed")

    def _start_application(self) -> subprocess.Popen:
        if not self.start_command:
            raise RuntimeError("Missing start_command")

        print(f"Running start command: {self.start_command}...")
        return subprocess.Popen(
            ["bash", "-lc", self.start_command],
            cwd=self.checkout_dir,
            env=os.environ.copy()
        )

    def _check_for_updates(self) -> bool:
        origin = self.repo.remotes.origin
        origin.fetch()

        remote_ref = f"origin/{self.branch}"
        local_sha = self.repo.head.commit.hexsha
        remote_sha = self.repo.commit(remote_ref).hexsha
        if local_sha == remote_sha:
            return False

        commit_msg = self.repo.commit(remote_ref).message.splitlines()[0]
        print(
            f"Remote update detected on {self.branch}: {local_sha[:8]} -> {remote_sha[:8]}: {commit_msg}")
        self.repo.git.checkout(self.branch)
        self.repo.git.reset("--hard", remote_ref)
        return True


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description="Git Repo Webhoster")
    parser.add_argument("--repo-url", type=str,
                        help="Git repository URL", required=True)
    parser.add_argument("--checkout-dir", type=str,
                        help="Directory to clone the repository into", required=True)
    parser.add_argument("--start-command", type=str,
                        help="Command to run to start the application", required=True)
    parser.add_argument("--branch", type=str, default="main",
                        help="Git branch to track")
    parser.add_argument("--github-token", type=str,
                        help="GitHub token for private repositories")
    parser.add_argument("--setup-command", type=str,
                        help="Command to run for environment setup (optional)")
    parser.add_argument("--poll-interval-seconds", type=int, default=30,
                        help="Interval in seconds to check for repository updates")
    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()

        webhoster = GitRepoWebhoster(
            repo_url=args.repo_url,
            branch=args.branch,
            setup_command=args.setup_command,
            start_command=args.start_command,
            github_token=args.github_token,
            poll_interval_seconds=args.poll_interval_seconds,
            checkout_dir=Path(args.checkout_dir)
        )
        webhoster.run()

    except Exception as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
