#!/usr/bin/env sh

set -ex

docker build -t webhoster:latest .
docker stop webhoster-container > /dev/null || true 
docker rm webhoster-container > /dev/null || true
# docker run -it --entrypoint /bin/sh -p 5000:5000 --name webhoster-container webhoster:latest 
docker run -p 5000:5000 --entrypoint /app/run-test.sh --name webhoster-container webhoster:latest 
