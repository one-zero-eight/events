# Events API in InNoHassle ecosystem

> Trust the system more than the memory

[![GitHub Actions pytest](https://img.shields.io/github/actions/workflow/status/one-zero-eight/InNoHassle-Events/pytest.yml?label=pytest)](https://github.com/one-zero-eight/InNoHassle-Events/actions)
[![GitHub Actions pre-commit](https://img.shields.io/github/actions/workflow/status/one-zero-eight/InNoHassle-Events/pre-commit.yml?label=pre-commit)](https://github.com/one-zero-eight/InNoHassle-Events/actions)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ArtemSBulgakov/075e30f7e4a7e9a28e40aa614db5445e/raw/pytest-coverage-comment__main.json)](https://github.com/one-zero-eight/InNoHassle-Events/actions)

## Table of contents

- [Project Description](#project-description)
- [How to use](#how-to-use)
- [Features list](#features-list)
- [Project Installation](#project-installation)
- [Project Structure](#project-structure)

## Project Description

This is the API for events in InNoHassle ecosystem. It is written in Python 3.11
using [FastAPI](https://fastapi.tiangolo.com/).

## Demo

You can test our product here [InNoHassle](https://innohassle.ru/schedule).

The background part of our API:

https://github.com/one-zero-eight/InNoHassle-Events/assets/104205787/8e519e69-7a2e-4507-9087-6b4e81e5266d

## How to use

1. Run the ASGI server(see [Project Installation](#project-installation)) or use our
   deployed [version](https://api.innohassle.ru/events/v0/auth/innopolis/login?return_to=/events/v0/docs).
2. Go to Swagger UI, read the docs, and try API endpoints(`/events/v0/docs`).
3. Enjoy using our API.

## Features list

1. Import any events to your calendar
    - Easily import events from various sources and add them to your personal calendar
    - Supports popular calendar file format .ics for easy integration with different applications
    - Intuitive import process with step-by-step instruction
2. Integrated Calendar Dashboard
    - View your events in the integrated calendar within the dashboard and schedule
    - Choose between day, week, or month views to suit your preference
3. Group Visibility Control
    - Hide or unhide your groups based on your preference
    - Hidden groups are not visible in the dashboard calendar
4. Favourites Management
    - Add events to your favorites for easy tracking and quick access
    - Delete outdated events from you favourites list
    - Effortlessly manage your favorite events and keep track of them

## Project Installation

1. Install dependencies with [poetry](https://python-poetry.org/docs/).
    ```bash
    poetry install
    ```
2. Set up pre-commit hooks:

    ```bash
    poetry shell
    pre-commit install
    pre-commit run --all-files
    ```
3. Setup environment variables in `.env.local` file.
    ```bash
    cp .env.example .env.local
    ```
4. Run the ASGI server using src/dev.py script
    ```bash
    poetry shell
    python -m src.dev
    ```
   OR using uvicorn directly
    ```bash
    poetry run uvicorn src.main:app --reload
    ```
   OR using 'Dev server' configuration in PyCharm.

Set up PyCharm integrations:

1. Black formatter ([docs](https://black.readthedocs.io/en/stable/integrations/editors.html#pycharm-intellij-idea)).
2. Ruff ([docs](https://beta.ruff.rs/docs/editor-integrations/#pycharm-unofficial)).

## Project Structure

```
*
| - LICENSE
| - README.md
| - docker-compose.yml
| - poetry.lock
| - pyproject.toml   # dependencies and configuration
+-- deploy           # deployment scripts and dockerfile
|   - Dockerfile
|   - docker-entrypoint.sh
+-- src                 # all source code
|   - config.py         # configuration for the project
|   - dev.py            # run development server
|   - exceptions.py     # custom exceptions
|   - main.py           # entrypoint for the FastAPI
|   +-- app             # FastAPI application
|   |   - dependencies.py  # dependencies for the application (Depends)
|   |   - routers.py       # include all routers for the API
|   |   +-- auth           # authentication module
|   |   |   - common.py
|   |   |   - dependencies.py # dependencies to extract user data from token
|   |   |   - dev.py          # auth routes for development
|   |   |   - innopolis.py    # auth routes for Innopolis SSO
|   |   |   - jwt.py
|   |   +-- event_groups   # event groups module
|   |   |   - routes.py       # routes for event groups router
|   |   +-- users          # users module
|   |       - routes.py       # routes for users router
|   +-- repositories    # repositories for data access layer
|   |   +-- event_groups   # event groups repository
|   |   |   - abc.py          # abstract base class for event groups repository
|   |   |   - repository.py   # repository implementation for event groups
|   |   |
|   |   +-- users       # users repository
|   |       - abc.py       # abstract base class for users repository
|   |       - sql_repository.py        # repository implementation for users
|   |       - json_repository.py       # temporary repository to extract user data from jsons
|   |       - (innopolis_user_data.json) # predefined user data from Innopolis official lists
|   |       - (predefined_groups.json)   # predefined groups for users
|   +-- schemas         # domain models for the application (pydantic models)
|   |   - event_groups.py  # schemas for event groups and related models
|   |   - users.py         # schemas for users
|   +-- storages        # data access layer
|       +-- sql            # SQL storages
|           - storage.py   # class for SQL storage
|           +-- models        # SQLAlchemy models
|               - base.py     # base class for SQLAlchemy models
|               - event_groups.py
|               - users.py
+-- tests               # tests for the project
    +-- app
    |   - test_app_configuration.py
    +-- repositories
        - test_event_groups.py
        - test_users.py
```
