FROM python:3.6-alpine
LABEL maintainer="Keyko <root@keyko.io>"

ARG VERSION

RUN apk add --no-cache --update\
    build-base \
    gcc \
    gettext\
    gmp \
    gmp-dev \
    libffi-dev \
    openssl-dev \
    py-pip \
    python3 \
    python3-dev \
    postgresql-dev \
  && pip install virtualenv

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
