#!/bin/bash

set -o errexit
set -o nounset

worker_ready() {
    celery -A app.core.celery inspect ping
}

until worker_ready; do
  >&2 echo 'Celery workers not available'
  sleep 3
done
>&2 echo 'Celery workers available!'

celery -A app.core.celery  \
    --broker="${CELERY_BROKER_URL}" \
    flower
