# GitHub Repo Runner - Home Assistant Add-on

Home Assistant add-on that clones a Git repository and runs your custom start command.

## Features

- User-configured `repo_url` and `start_command`
- Clones repo into persistent add-on storage (`/data/checkout`)
- Optional pull on startup before launching your app
- Continuous remote update checks with automatic app restart when changes are found
- Runs your command as the main add-on process

## Install (Local Add-on Repository)

1. Put this repository somewhere Home Assistant can access.
2. In Home Assistant, go to **Settings → Add-ons → Add-on Store → ⋮ → Repositories**.
3. Add the repository URL/path for this repo.
4. Install **GitHub Repo Runner** and start it.
5. Configure the options (repo URL + start command), then start the add-on.

## Configuration

Example options:

```yaml
repo_url: https://github.com/example/my-app.git
branch: main
app_subdir: ""
start_command: flask run --host 0.0.0.0 --port 5000
poll_interval_seconds: 30
github_token: ""
```

- `repo_url` (required): Git repository to clone
- `branch`: branch to checkout and pull (default `main`)
- `app_subdir`: optional subfolder inside the repo to run from
- `start_command` (required): command to run after clone/pull
- `github_token`: optional GitHub Personal Access Token for private GitHub repos (used with `https://github.com/...` URLs)
- `poll_interval_seconds`: how often to check `origin/<branch>` for updates (default `30`, minimum `5`)

### Private GitHub repositories

For private repos, use an HTTPS GitHub URL and set `github_token` to a PAT that has repository read access.

Example:

```yaml
repo_url: https://github.com/your-user/your-private-repo.git
branch: main
github_token: ghp_xxx
start_command: python app.py
```

The token is used for clone/fetch and is masked in startup logs.

After startup, the add-on keeps running as a supervisor process. It checks the remote branch on the configured interval and, when a new commit is detected, pulls the update and restarts your app process automatically.

To access your app from outside the container, your `start_command` must bind to `0.0.0.0` (not `127.0.0.1`/`localhost`) and use an exposed port.

This add-on exposes `5000/tcp` by default.

This add-on does not provide its own API or web server. The process started by `start_command` is the app that runs.

