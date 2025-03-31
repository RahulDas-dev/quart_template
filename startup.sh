#!/bin/bash

source .venv/bin/activate

gunicorn --bind ${DIFY_BIND_ADDRESS:-0.0.0.0}:${DIFY_PORT:-5001} \
--workers ${SERVER_WORKER_AMOUNT:-1} \
--worker-class ${SERVER_WORKER_CLASS:-gevent} \
--worker-connections ${SERVER_WORKER_CONNECTIONS:-10} \
--timeout ${GUNICORN_TIMEOUT:-200} \
app:app