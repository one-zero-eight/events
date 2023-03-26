# Events API in InNoHassle ecosystem
> Trust the system more than the memory

## Features

- Event creation and storage system
- User interest analysis
- Moderation
- Subscriptions

## Structure

    .
    ├── api                 # API implementation             
    │   ├── api                     # API server configuration, API models and routes
    │   ├── crud                    # CRUD interface over the database
    │   ├── database                # Database configuration and models
    │   ├── tests                   # Automated tests(unit)
    │   └── run.py                  # Script to run the API server
    ├── docs                # Documentation (server, builders, templates)
    ├── LICENSE
    └── README.md