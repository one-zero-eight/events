# Events API in InNoHassle ecosystem

> Trust the system more than the memory

## Table of contents

- [Description](#description)
- [How to use](#how-to-use)

## Description

This is the API for events in InNoHassle ecosystem. It is written in Python 3.10 using [FastAPI](https://fastapi.tiangolo.com/).


## How to use

1. Install dependencies with [poetry](https://python-poetry.org/docs/).
    ```bash
    poetry install
    ```
2. Setup environment variables in `.env.local` file.
    ```bash
    cp .env.example .env.local
    ```
3. Run the ASGI server using src/dev.py script
    ```bash
    poetry shell
    python -m src.dev
    ```
    OR using uvicorn directly
    ```bash
    poetry run uvicorn src.main:app --reload
    ```
    OR using 'Dev server' configuration in PyCharm.
