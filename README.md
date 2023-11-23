### Quickstart guide

#### Prerequisites
- Docker Compose to run the containers
  - [Docker](https://docs.docker.com/engine/install/)
  - [Docker compose](https://docs.docker.com/compose/install/)
  - [Poetry](https://python-poetry.org)
  - "oracle-db" host with open port 1521

#### Local environment
- Init Poetry environment:
```shell
poetry install --with test
poetry shell
```

#### Adding dependencies
Regular dependency:
```shell
poetry add <PKG_NAME>
poetry lock --no-update  # ensure lock file is valid
```
Development dependency:
```shell
poetry add <PKG_NAME> --group dev
poetry lock --no-update  # ensure lock file is valid
```
Test dependency:
```shell
poetry add <PKG_NAME> --group test
poetry lock --no-update  # ensure lock file is valid
```

#### Run
- `docker compose up` is recommended, but if you really want to, use:
```shell
chmod +x start.sh
export $(grep -v '^#' ../.env | xargs) && ./start.sh
```

#### Run `flake8`, `mypy` and `pytest`
These need to pass for you PR to be accepted
```shell
cd app
flake8
mypy .
```
Running `pytest` requires a live system:
```shell
docker compose up --build --detach
# wait for containers to spin up
docker exec fastapi-backend "pytest"
```
#### Create migrations
Check if a migration can be generated:
```shell
alembic check
# or, if running in docker container:
docker exec fastapi-backend bash -c "alembic check"
```
If any model was changed, migration will be needed (CI will also fail if there are pending migrations). Generate a 
new migration:
```shell
python -m alembic revision --autogenerate -m "<MIGRATION_NAME>"
# docker alternative:
docker exec fastapi-backend bash -c "python3 -m alembic revision --autogenerate -m \"<MIGRATION_NAME>\""
docker cp fastapi-backend:$(docker exec fastapi-backend bash -c "ls -rt /app/migrations/versions/*.py | tail -1") migrations/versions/
```
Migrations are applied automatically on backend startup.