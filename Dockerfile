# Based on https://github.com/svx/poetry-fastapi-docker/blob/main/Dockerfile

###########################################################
# Base Python image. Set shared environment variables.
FROM python:3.12-slim-bullseye AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_INSTALLER_MAX_WORKERS=10 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


###########################################################
# Builder stage. Build dependencies.
FROM base AS builder
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential \
        curl \
        netcat \
        vim \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry. Respects $POETRY_VERSION and $POETRY_HOME
ENV POETRY_VERSION=1.8.3
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sS https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python3 - --version ${POETRY_VERSION} && \
    chmod a+x /opt/poetry/bin/poetry

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-interaction


###########################################################
# Production stage. Copy only runtime deps that were installed in the Builder stage.
FROM base AS production

COPY --from=builder $VENV_PATH $VENV_PATH

COPY --chmod=755 ./deploy/docker-entrypoint.sh /

# Create user with the name poetry
RUN groupadd -g 1500 poetry && \
    useradd -m -u 1500 -g poetry poetry

COPY --chown=poetry:poetry . /code
USER poetry
WORKDIR /code

EXPOSE 8000
ENTRYPOINT [ "/docker-entrypoint.sh" ]
CMD [ "gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "1", "src.api.app:app" ]
