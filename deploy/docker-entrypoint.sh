#!/bin/sh

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

# You can put other setup logic here
alembic upgrade head

# Evaluating passed command:
exec "$@"
