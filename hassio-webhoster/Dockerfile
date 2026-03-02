ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-ubuntu:24.04
FROM ${BUILD_FROM}

WORKDIR /app

# Install base packages for build development
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3.12-dev \
        python3.12-venv \
        python-is-python3 \
        git \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*


RUN python3 -m venv venv

COPY requirements.txt requirements.txt

RUN source venv/bin/activate &&\
    pip install --no-cache-dir -r requirements.txt && \
    python -m ensurepip --upgrade && \
    python -m pip install --no-cache-dir --upgrade pip && \
    rm -f requirements.txt

COPY run.py run.py
COPY run.sh run.sh
RUN chmod +x run.sh
COPY run-test.sh run-test.sh
RUN chmod +x run-test.sh

RUN mkdir -p /data

CMD [ "/app/run.sh" ]
