# Website url
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
        "name": "Ics files",
        "description": "Generate .ics files for event groups to import them into calendar app.",
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
