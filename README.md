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
|   .env.example  # Example of environment variables for local development
|   (.env.local)  # Environment variables for local development
|   .gitignore
|   LICENSE
|   poetry.lock
|   pyproject.toml   # Poetry project configuration
|   README.md
|
+---.run
|       Dev server.run.xml    # PyCharm run configuration for local development
|
\---src
    |   config.py       # Configuration module for the application (using ENV variables)
    |   dev.py          # Script for local development
    |   exceptions.py   # Custom exceptions
    |   main.py         # Represents ASGI application and initializes FastAPI application
    |
    +---app       # Represents FastAPI application with routers, dependencies, schemas, etc.
    |   |   dependencies.py      # Includes FastAPI dependencies for dependency injection
    |   |   routers.py           # Includes FastAPI routers for API endpoints
    |   |   schemas.py           # Includes Pydantic schemas for API request and response bodies
    |   |
    |   +---auth              # Module for authentication and authorization
    |   |   |   common.py
    |   |   |   dependencies.py
    |   |   |   dev.py
    |   |   |   innopolis.py
    |   |   \---jwt.py
    |   |
    |   +---event_groups      # Module for event groups
    |   |   |   routes.py        # Includes API endpoints for event group-related operations
    |   |   |   schemas.py       # Includes Pydantic schemas for event group-related operations
    |   +---users             # Module for users
    |   |   |   routes.py
    |   |   \---schemas.py
    |
    +---repositories # Represents repositories layer for data access and manipulation
    |   |
    |   +---event_groups
    |   |   |   abc.py  # Abstract base class for event group repository
    |   |   \---repository.py # SQLAlchemy repository for event group connected methods
    |   |
    |   +---users
    |   |   |   abc.py  # Abstract base class for user repository
    |   |   |   json_repository.py  # JSON repository for predefined groups and users
    |   |   |   sql_repository.py   # SQLAlchemy repository for user connected methods
    |   |   |   (predefined_groups.json)  # Predefined groups data
    |   |   \---(innopolis_user_data.json) # Innopolis users data
    \---storages  # Represents data storage such as databases, third-party APIs, etc.
        |
        \---sql   # SQLAlchemy storage
            |   storage.py    # SQLAlchemy session factory
            |
            \---models  # SQLAlchemy ORM models representing database tables

```
