#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

# ensure db is up and properly configured
cp app/backend_pre_start.py .
python3 backend_pre_start.py

# run migrations
alembic upgrade head

# start the app
uvicorn app.main:app --proxy-headers --host 0.0.0.0 --port 80
