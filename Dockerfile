FROM python:3.8-slim-buster
LABEL maintainer="Keyko <root@keyko.io>"

ARG VERSION

RUN apt-get update \
    && apt-get install gcc gettext-base -y \
    && apt-get clean

COPY . /nevermined-compute-api
WORKDIR /nevermined-compute-api

RUN pip install .

# config.ini configuration file variables
ENV COMPUTE_API_URL='http://0.0.0.0:8050'

# docker-entrypoint.sh configuration file variables
ENV COMPUTE_API_WORKERS='1'
ENV COMPUTE_API_TIMEOUT='9000'
ENV ALGO_POD_TIMEOUT='3600'
ENV ALLOWED_PROVIDERS=""
ENV SIGNATURE_REQUIRED=0

ENTRYPOINT ["/nevermined-compute-api/docker-entrypoint.sh"]

EXPOSE 8050
