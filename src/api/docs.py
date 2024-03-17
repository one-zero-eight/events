# Website url
import re

from fastapi.routing import APIRoute

WEBSITE_URL = "https://innohassle.ru"

# API version
VERSION = "0.1.0"

# Info for OpenAPI specification
TITLE = "InNoHassle Events API"
SUMMARY = "Browse and create schedules at Innopolis University."

DESCRIPTION = """
### About this project

This is the API for Events project in InNoHassle ecosystem developed by one-zero-eight community.

Using this API you can browse, view, create and edit schedules at Innopolis University.

Backend is developed using FastAPI framework on Python.

Note: API is unstable. Endpoints and models may change in the future.

Useful links:
- [Backend source code](https://github.com/one-zero-eight/InNoHassle-Events)
- [Frontend source code](https://github.com/one-zero-eight/InNoHassle-Website)
- [Website](https://innohassle.ru/schedule)
"""

CONTACT_INFO = {
    "name": "one-zero-eight (Telegram)",
    "url": "https://t.me/one_zero_eight",
}
LICENSE_INFO = {
    "name": "MIT License",
    "identifier": "MIT",
}

TAGS_INFO = [
    {
        "name": "Event Groups",
        "description": (
            "Groups consisting of multiple events. It can represent a schedule of one academic group or club."
        ),
    },
    {
        "name": "ICS",
        "description": "Generate .ics to import them into calendar app.",
    },
    {
        "name": "Tags",
        "description": "Topics or categories of event groups.",
    },
    {
        "name": "Users",
        "description": "User data and linking users with event groups.",
    },
]


def generate_unique_operation_id(route: APIRoute) -> str:
    # Better names for operationId in OpenAPI schema.
    # It is needed because clients generate code based on these names.
    # Requires pair (tag name + function name) to be unique.
    # See fastapi.utils:generate_unique_id (default implementation).
    operation_id = f"{route.tags[0]}_{route.name}".lower()
    operation_id = re.sub(r"\W+", "_", operation_id)
    return operation_id
