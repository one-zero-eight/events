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

This is the API for events service in InNoHassle ecosystem. Lets...

### Features

- 📅 Event Aggregation
    - 📚 [Core and Elective Courses](https://eduwiki.innopolis.university/index.php/All:Schedule)
    - 🏋️ [Sports Classes](https://sport.innopolis.university)
    - 🧹 [Dorm Cleaning](https://hotel.innopolis.university/studentaccommodation/)
    - 🎵 [Music Room Booking](https://innohassle.ru/music-room)
    - 📖 [Moodle Events](https://moodle.innopolis.university/)
- 🌟 Personalized Schedule
    - ⭐ Favorites Management
    - 👀 Hide/Unhide Groups
    - 🆔 Automatically add schedule based on your identity
- 🔄 Schedule Export
    - 🗓️ Schedule in [.ics format](https://icalendar.org/) to import into your calendar app

### Technologies

- [Python 3.12](https://www.python.org/downloads/) & [Poetry](https://python-poetry.org/docs/)
- [FastAPI](https://fastapi.tiangolo.com/)
- Database and ORM: [PostgreSQL](https://www.postgresql.org/), [SQLAlchemy](https://www.sqlalchemy.org/),
  [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- Formatting and linting: [Ruff](https://docs.astral.sh/ruff/), [pre-commit](https://pre-commit.com/)
- Deployment: [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/),
  [GitHub Actions](https://github.com/features/actions)

## Development

### Set up for development

1. Install [Python 3.12+](https://www.python.org/downloads/), [Poetry](https://python-poetry.org/docs/),
   [Docker](https://docs.docker.com/engine/install/)
2. Install project dependencies with [Poetry](https://python-poetry.org/docs/cli/#options-2).
   ```bash
   poetry install
   ```
3. Start development server:
   ```bash
   poetry run python -m src.api --reload
   ```
   > Follow provided instructions if needed
4. Open in the browser: http://localhost:8000
   > The api will be reloaded when you edit the code

> [!IMPORTANT]
> For endpoints requiring authorization click "Authorize" button in Swagger UI

> [!TIP]
> Edit `settings.yaml` according to your needs, you can view schema in
> [config_schema.py](src/config_schema.py) and in [settings.schema.yaml](settings.schema.yaml)

**Set up PyCharm integrations**

1. Run configurations ([docs](https://www.jetbrains.com/help/pycharm/run-debug-configuration.html#createExplicitly)).
   Right-click the `__main__.py` file in the project explorer, select `Run '__main__'` from the context menu.
2. Ruff ([plugin](https://plugins.jetbrains.com/plugin/20574-ruff)).
   It will lint and format your code. Make sure to enable `Use ruff format` option in plugin settings.
3. Pydantic ([plugin](https://plugins.jetbrains.com/plugin/12861-pydantic)). It will fix PyCharm issues with
   type-hinting.
4. Conventional commits ([plugin](https://plugins.jetbrains.com/plugin/13389-conventional-commit)). It will help you
   to write [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/).

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
If you are interested in contributing, please read
our [contribution guide](https://github.com/one-zero-eight/.github/blob/main/CONTRIBUTING.md).
