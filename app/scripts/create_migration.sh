#!/usr/bin/env bash

# Script for creating an automatic DB migrations. Generates the migration
in a running container and extracts the migration file
# execute from scripts directory

if [ "$#" -ne 1 ]; then
    echo "Usage:    ./create_migration.sh <MIGRATION_NAME>"
    return 1
fi

docker exec fastapi-backend bash -c "python3 -m alembic revision --autogenerate -m \"$1\""
docker cp fastapi-backend:$(docker exec fastapi-backend bash -c "ls -rt /app/migrations/versions/*.py | tail -1") ../migrations/versions/