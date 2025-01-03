"""music room sports moodle hidden

Revision ID: 6f44af938cdf
Revises: cba1388a6e8f
Create Date: 2024-02-13 05:37:56.186458

"""

# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6f44af938cdf"
down_revision: str | None = "cba1388a6e8f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("music_room_hidden", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )
    op.add_column("users", sa.Column("sports_hidden", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("users", sa.Column("moodle_hidden", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "moodle_hidden")
    op.drop_column("users", "sports_hidden")
    op.drop_column("users", "music_room_hidden")
    # ### end Alembic commands ###
