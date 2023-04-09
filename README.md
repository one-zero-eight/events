# Events API in InNoHassle ecosystem
> Trust the system more than the memory

## Features

- Event creation and storage system
- User interest analysis
- Moderation
- Subscriptions

## Structure

    .
    ├── src                 # API implementation             
    │   ├── core                    # Main service
    │   ├── {service_name}                 # Common service
    │   ├── database                # Database configuration and models
    │   └── main.py                 # FastAPI app instance
    ├── docs                # Documentation (server, builders, templates)
    ├── tests               # Automated tests(unit)
    ├── scripts             # Scripts (f.e. migration)
    ├── alembic             # Alembic migrations 
    ├── pyproject.toml      # Project dependencies
    ├── LICENSE
    └── README.md
        