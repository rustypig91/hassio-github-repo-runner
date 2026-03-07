#!/usr/bin/env sh

set -ex

docker build -t github-repo-runner:latest .
docker stop github-repo-runner-container > /dev/null || true 
docker rm github-repo-runner-container > /dev/null || true
# docker run -it --entrypoint /bin/bash -p 5000:5000 --name github-repo-runner-container github-repo-runner:latest 
docker run -p 5000:5000 --entrypoint /app/run-test.sh --name github-repo-runner-container github-repo-runner:latest 
