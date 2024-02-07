# sigmacats-backend

![banner.png](.img/banner.png)

## IMPORTANT NOTE

This is the backend repository for the SIGMACATS project. Check out the [main repo](https://github.com/SNURTEL/23z-pzsp2-sigmacats) first.

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
- Starting the backend as a submodule in the main repo with **`docker compose up` is highly recommended!!!**
- If you _really_ want to, you can start the backend outside the container (bear in mind you will need to take care of all env variables, as they are normally managed by docker compose):
```shell
chmod +x start.sh
export $(grep -v '^#' ../.env | xargs) && ./start.sh
```

#### Run `flake8`, `mypy` and `pytest`
These need to pass for you PR to be accepted
```shell
cd app/app
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
docker exec fastapi-backend bash -c "alembic check"
# standalone alternative:
alembic check
```
If any model was changed, migration will be needed (CI will also fail if there are pending migrations). Generate a 
new migration:
```shell
cd scripts
./create_migration <MIGRATION_NAME>  # will be placed in `migrations` directory
# standalone alternative:
python -m alembic revision --autogenerate -m "<MIGRATION_NAME>"
```
Migrations are applied automatically on backend startup. NOTE: always check if the generated miggration includes all changes and correct if necessary. Alembic's auto-generation is usually far from perfect.