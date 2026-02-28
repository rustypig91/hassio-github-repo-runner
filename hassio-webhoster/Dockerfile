ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.21
FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache git

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN . venv/bin/activate && pip3 install --no-cache-dir -r requirements.txt
RUN rm -f requirements.txt

COPY run.py run.py
COPY run.sh run.sh
RUN chmod +x run.sh
COPY run-test.sh run-test.sh
RUN chmod +x run-test.sh

RUN mkdir -p /data

CMD [ "/app/run.sh" ]
