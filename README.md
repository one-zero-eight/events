# Events API | InNoHassle ecosystem

> https://api.innohassle.ru/events

[![GitHub Actions pre-commit](https://img.shields.io/github/actions/workflow/status/one-zero-eight/InNoHassle-Events/pre-commit.yaml?label=pre-commit)](https://github.com/one-zero-eight/InNoHassle-Events/actions)

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-Events&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-Events)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-Events&metric=bugs)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-Events)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-Events&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-Events)

## Table of contents

Did you know that GitHub supports table of
contents [by default](https://github.blog/changelog/2021-04-13-table-of-contents-support-in-markdown-files/) 🤔

## About

This is the API for events service in InNoHassle ecosystem.

### Features

- 📅 Event Aggregation
    - 📚 [Core and Elective Courses](https://eduwiki.innopolis.university/index.php/All:Schedule)
    - 🏋️ [Sports Classes](https://sport.innopolis.university)
    - 🧹 [Dorm Cleaning](https://hotel.innopolis.university/studentaccommodation/)
    - 🎵 [Music Room Booking](https://innohassle.ru/music-room)
    - 📖 [Moodle Events](https://moodle.innopolis.university/) _(in progress)_
- 🌟 Personalized Schedule
    - ⭐ Favorites Management
    - 👀 Hide/Unhide Groups
    - 🆔 Automatically add schedule based on your identity
- 🔄 Schedule Export
    - 🗓️ Schedule in [.ics format](https://icalendar.org/) to import into your calendar app

### Technologies

- [Python 3.11](https://www.python.org/downloads/release/python-3117/) & [Poetry](https://python-poetry.org/docs/)
- [FastAPI](https://fastapi.tiangolo.com/) & [Pydantic](https://docs.pydantic.dev/latest/)
- Database and ORM: [PostgreSQL](https://www.postgresql.org/), [SQLAlchemy](https://www.sqlalchemy.org/),
  [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- Formatting and linting: [Ruff](https://docs.astral.sh/ruff/), [pre-commit](https://pre-commit.com/)
- Deployment: [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/),
  [GitHub Actions](https://github.com/features/actions)

## Development

### Getting started

1. Install [Python 3.11+](https://www.python.org/downloads/release/python-3117/)
2. Install [Poetry](https://python-poetry.org/docs/)
3. Install project dependencies with [Poetry](https://python-poetry.org/docs/cli/#options-2).
   ```bash
   poetry install --no-root --with code-style
   ```
4. Set up [pre-commit](https://pre-commit.com/) hooks:

   ```bash
   poetry run pre-commit install --install-hooks -t pre-commit -t commit-msg
   ```
5. Set up project settings file (check [settings.schema.yaml](settings.schema.yaml) for more info).
   ```bash
   cp settings.example.yaml settings.yaml
   ```
   Edit `settings.yaml` according to your needs.
6. Set up a [PostgreSQL](https://www.postgresql.org/) database instance.
   <details>
    <summary>Using docker container</summary>

    - Set up database settings for [docker-compose](https://docs.docker.com/compose/) container
      in `.env` file:х
      ```bash
      cp .env.example .env
      ```
    - Set up a network for music room service if you have not done it yet.
      ```bash
      docker network create music-room
      ```
    - Run the database instance:
      ```bash
      docker compose up -d db
      ```
    - Make sure to set up the actual database connection in `settings.yaml`, for example:
      ```yaml
      db_url: postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
      ```

   </details>
   <details>
    <summary>Using pgAdmin</summary>

    - Connect to the PostgreSQL server using pgAdmin
    - Set up a new database in the server: `Edit > New Object > New database`
    - Use the database name in `settings.yaml` file, for example `innohassle-events`:
      ```yaml
      db_url: postgresql+asyncpg://postgres:your_password@localhost:5432/innohassle-events
      ```
   </details>

**Set up PyCharm integrations**

1. Ruff ([plugin](https://plugins.jetbrains.com/plugin/20574-ruff)).
   It will lint and format your code. Make sure to enable `Use ruff format` option in plugin settings.
2. Pydantic ([plugin](https://plugins.jetbrains.com/plugin/12861-pydantic)). It will fix PyCharm issues with
   type-hinting.
3. Conventional commits ([plugin](https://plugins.jetbrains.com/plugin/13389-conventional-commit)). It will help you
   to write [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Run for development

1. Run the database if you have not done it yet
2. Upgrade the database schema using [alembic](https://alembic.sqlalchemy.org/en/latest/):
   ```bash
   poetry run alembic upgrade head
   ```
3. Run the ASGI server
   ```bash
   poetry run python -m src.api
   ```
   OR using uvicorn directly
   ```bash
   poetry run uvicorn src.api.app:app --use-colors --proxy-headers --forwarded-allow-ips=*
   ```

Now the API is running on http://localhost:8000. Good job!

### Deployment

We use Docker with Docker Compose plugin to run the website on servers.

1. Copy the file with environment variables: `cp .env.example .env`
2. Change environment variables in the `.env` file
3. Copy the file with settings: `cp settings.example.yaml settings.yaml`
4. Change settings in the `settings.yaml` file according to your needs
   (check [settings.schema.yaml](settings.schema.yaml) for more info)
5. Install Docker with Docker Compose
6. Deploy [Music room service](https://github.com/one-zero-eight/InNoHassle-MusicRoom)
   > Or just create a network for the music room service: `docker network create music-room`
7. Build a Docker image: `docker compose build --pull`
8. Run the container: `docker compose up --detach`
9. Check the logs: `docker compose logs -f`

## FAQ

### How to update dependencies?

Project dependencies

1. Run `poetry update` to update all dependencies
2. Run `poetry show --outdated` to check for outdated dependencies
3. Run `poetry add <package>@latest` to add a new dependency if needed

Pre-commit hooks

1. Run `poetry run pre-commit autoupdate`

## Contributing

We are open to contributions of any kind.
You can help us with code, bugs, design, documentation, media, new ideas, etc.
If you are interested in contributing, please read our [contribution guide](https://github.com/one-zero-eight/.github/blob/main/CONTRIBUTING.md).
