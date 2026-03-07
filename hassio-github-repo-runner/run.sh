#!/usr/bin/with-contenv bashio

set -e

. /app/venv/bin/activate

export DATA_DIR=/media/hassio-github-repo-runner
mkdir -p "$DATA_DIR"

export SHARE_DIR=/share/hassio-github-repo-runner
mkdir -p "$SHARE_DIR"

environment_variables=$(bashio::config 'environment_variables')


if [ -n "$environment_variables" ]; then
    for pair in $(echo "$environment_variables" | tr ',' '\n'); do
        pair=$(echo "$pair" | xargs) # trim whitespace
        [ -z "$pair" ] && continue
        eval "echo \"Setting environment variable: $pair\""
        eval "export $pair"
    done
fi

exec python3 -u /app/run.py --checkout-dir /app/checkout \
    --poll-interval-seconds $(bashio::config 'poll_interval_seconds') \
    --repo-url "$(bashio::config 'repo_url')" \
    --branch "$(bashio::config 'branch')" \
    --github-token "$(bashio::config 'github_token')" \
    --setup-command "$(bashio::config 'setup_command')" \
    --start-command "$(bashio::config 'start_command')"
