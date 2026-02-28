# hassio-webhoster

Home Assistant add-on that clones a Git repository and runs your custom start command.

## Features

- User-configured `repo_url` and `start_command`
- Clones repo into persistent add-on storage (`/data/checkout`)
- Optional pull on startup before launching your app
- Runs your command as the main add-on process

## Install (Local Add-on Repository)

1. Put this repository somewhere Home Assistant can access.
2. In Home Assistant, go to **Settings → Add-ons → Add-on Store → ⋮ → Repositories**.
3. Add the repository URL/path for this repo.
4. Install **Git Repo Webhoster** and start it.
5. Configure the options (repo URL + start command), then start the add-on.

## Configuration

Example options:

```yaml
repo_url: https://github.com/example/my-app.git
branch: main
app_subdir: ""
start_command: npm run start
pull_on_start: true
```

- `repo_url` (required): Git repository to clone
- `branch`: branch to checkout and pull (default `main`)
- `app_subdir`: optional subfolder inside the repo to run from
- `start_command` (required): command to run after clone/pull
- `pull_on_start`: if true, fetch/reset to latest branch on start

This add-on does not provide its own API or web server. The process started by `start_command` is the app that runs.

