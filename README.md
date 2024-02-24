# Events API in InNoHassle ecosystem

> Trust the system more than the memory

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg) ](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=Python) ](https://www.python.org/downloads/release/python-3110/)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

[![GitHub Actions pytest](https://img.shields.io/github/actions/workflow/status/one-zero-eight/InNoHassle-Events/pytest.yml?label=pytest)](https://github.com/one-zero-eight/InNoHassle-Events/actions)
[![GitHub Actions pre-commit](https://img.shields.io/github/actions/workflow/status/one-zero-eight/InNoHassle-Events/pre-commit.yml?label=pre-commit)](https://github.com/one-zero-eight/InNoHassle-Events/actions)

[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-Events&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-Events)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-Events&metric=bugs)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-Events)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=one-zero-eight_InNoHassle-Events&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=one-zero-eight_InNoHassle-Events)

## Table of contents

GitHub supports table of
contents [by default](https://github.blog/changelog/2021-04-13-table-of-contents-support-in-markdown-files/).

## Project description

This is the API for events in InNoHassle ecosystem. It is written in Python 3.11
using [FastAPI](https://fastapi.tiangolo.com/).

### Features list

1. Aggregate Events from Various Sources:
    - Core courses schedule from the Google Spreadsheet table
    - Elective courses schedule from another Google Spreadsheet table
    - Sports classes schedule from the [website](https://sport.innopolis.university)
    - Dorm cleaning schedule from the [website](https://hotel.innopolis.university/studentaccommodation/)
    - [InNoHassle-MusicRoom](https://github.com/one-zero-eight/InNoHassle-MusicRoom) schedule (general and personal
      view)
    - _Moodle homework and events (in progress)_
2. Personalize your schedule
    - Favourites Management
        - Add schedules to your favorites for easy tracking and quick access
        - Effortlessly manage your favorite events and keep track of them
    - Hide or unhide your groups based on your preference
        - Hidden groups are not visible in the dashboard calendar and are not included in the schedule but can be
          easily unhidden
    - Predefined schedules based on your identity
        - Automatically include your core courses and electives
        - Automatically include your bookings
          from [InNoHassle-MusicRoom](https://github.com/one-zero-eight/InNoHassle-MusicRoom)
        - _Automatically include your sports classes checkins (in progress)_
3. Export your schedule to any calendar application
    - Supports popular calendar file format .ics for easy integration with different applications
    - Export requires key-based authentication to ensure the security of the user's data
4. User Authentication
    - Seamless user authentication flow with Innopolis University SSO
    - Secure and reliable authentication process
    - User data is stored securely and is not shared with any third-party

### Demo

You can test our product here [InNoHassle](https://innohassle.ru/schedule).
And see an api deployed
version [here](https://api.innohassle.ru/events/v0/auth/innopolis/login?return_to=/events/v0/docs).

The background part of our API:

https://github.com/one-zero-eight/InNoHassle-Events/assets/104205787/8e519e69-7a2e-4507-9087-6b4e81e5266d

## Development

### Getting started

1. Install [Python 3.11+](https://www.python.org/downloads/release/python-3117/)
2. Install [Poetry](https://python-poetry.org/docs/)
3. Install project dependencies with [poetry](https://python-poetry.org/docs/cli/#options-2).
    ```bash
    poetry install --no-root
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
    - Set up database settings for [docker-compose](https://docs.docker.com/compose/) container
      in `.env` file:х
        ```bash
        cp .env.example .env
        ```
    - Run the database instance:
        ```bash
        docker compose up -d db
        ```
    - Make sure to set up the actual database connection in `settings.yaml` before running the upgrade command.
    - Upgrade the database schema using [alembic](https://alembic.sqlalchemy.org/en/latest/):
         ```bash
         poetry run alembic upgrade head
         ```

> [!NOTE]
> You can use [pgAdmin](https://www.pgadmin.org/) to run and manage your database.

Set up PyCharm integrations:

1. Ruff ([plugin](https://plugins.jetbrains.com/plugin/20574-ruff)).
   It will lint and format your code. Make sure to enable `Use ruff format` option in plugin settings.
2. Pydantic ([plugin](https://plugins.jetbrains.com/plugin/12861-pydantic)). It will fix PyCharm issues with
   type-hinting.
3. Conventional commits ([plugin](https://plugins.jetbrains.com/plugin/13389-conventional-commit)). It will help you
   to write [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Run for development

1. Run the database if you have not done it yet
    ```bash
    docker compose up -d db
    ```
   OR do it manually
2. Run the ASGI server
    ```bash
    poetry run python -m src.api
    ```
   OR using uvicorn directly
    ```bash
    poetry run uvicorn src.api.app:app --use-colors --proxy-headers --forwarded-allow-ips=*
    ```

Now the API is running on http://localhost:8000. Good job!
