#!/bin/sh

export CONFIG_FILE=/nevermined-compute-api/config.ini
envsubst < /nevermined-compute-api/config.ini.template > /nevermined-compute-api/config.ini

gunicorn -b ${COMPUTE_API_URL#*://} -w ${COMPUTE_API_WORKERS} -t ${COMPUTE_API_TIMEOUT} nevermined_compute_api.run:app
tail -f /dev/null
