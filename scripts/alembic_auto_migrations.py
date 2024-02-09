import sys
import pathlib

import alembic.config

if len(sys.argv) == 2:
    print("Reading commit message from", sys.argv[1])
    message_path = sys.argv[1]
else:
    message_path = ".git/COMMIT_EDITMSG"
message = pathlib.Path(message_path).read_text()

commit_name = message.splitlines()[0]

# auto-generate the migrations
alembic_args = [
    # "--raiseerr",
    "revision",
    "--autogenerate",
    "-m",
    commit_name,
]

alembic.config.main(argv=alembic_args)
