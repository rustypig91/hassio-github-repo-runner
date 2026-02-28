#!/usr/bin/env sh

set -e

. /app/venv/bin/activate

exec python3 -u /app/run.py \
    --poll-interval-seconds 30 \
    --repo-url "https://github.com/ubc/flask-sample-app.git" \
    --branch "main" \
    --github-token "" \
    --setup-command "pip install -r requirements.txt" \
    --start-command "flask run --host=0.0.0.0 --port=5000" \
    --checkout-dir /app/checkout