ARG BUILD_FROM=python:3.12-alpine
FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache git


COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY app /app/app
COPY run.sh /run.sh

RUN mkdir -p /data
COPY default-options.yaml /data/options.yaml

RUN chmod +x /run.sh

CMD [ "/run.sh" ]
