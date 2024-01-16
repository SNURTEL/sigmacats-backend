FROM python:3.11.6-slim-bullseye

# Dockerfile for backend and celery

# "production", "development", "test"
ARG BUILD_ENV=development

WORKDIR /app/

# POETRY_VERSION should match `"poetry--core=="<VERSION>"` in `pyproject.toml`
ENV BUILD_ENV=${BUILD_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.5.0

# copy the dependencies file beforehand prevent discarding cached dependencies if any file in ./app changes
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

# Install poetry
RUN pip install --no-cache-dir --upgrade poetry==${POETRY_VERSION}

# Install python dependencies
RUN poetry config virtualenvs.create false \
&& poetry install \
$(test "$BUILD_ENV" = "production" && echo "--no-dev") \
$(test "$BUILD_ENV" = "test" && echo "--with test") \
$(test "$BUILD_ENV" = "development" && echo "--with test") \
--no-interaction --no-ansi

COPY ./app /app

COPY start.sh start-backend.sh
RUN chmod +x start-backend.sh

COPY celery/worker/start.sh start-worker.sh
RUN chmod +x start-worker.sh

COPY celery/beat/start.sh start-beat.sh
RUN chmod +x start-beat.sh

COPY celery/flower/start.sh start-flower.sh
RUN chmod +x start-flower.sh