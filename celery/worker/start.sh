#!/bin/bash

set -o errexit
set -o nounset

celery -A app.core.celery worker --loglevel=info
