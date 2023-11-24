#!/usr/bin/env bash

# execute from scripts directory

if [ "$#" -ne 1 ]; then
    echo "Usage:    ./create_migration.sh <MIGRATION_NAME>"
    return 1
fi

docker exec fastapi-backend bash -c "python3 -m alembic revision --autogenerate -m \"$1\""
docker cp fastapi-backend:$(docker exec fastapi-backend bash -c "ls -rt /app/migrations/versions/*.py | tail -1") ../migrations/versions/