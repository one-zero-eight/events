"""upgrade empty to HEAD

Revision ID: 8ff07476cbc4
Revises:
Create Date: 2024-02-10 23:52:03.482605

"""

# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8ff07476cbc4"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "event_groups",
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("satellite", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias"),
        sa.UniqueConstraint("path"),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tags",
        sa.Column("alias", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("satellite", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias", "type"),
    )
    op.create_table(
        "users",
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "event_groups_x_ownerships",
        sa.Column("object_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_alias", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["object_id"],
            ["event_groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("object_id", "user_id"),
    )
    op.create_table(
        "event_groups_x_tags",
        sa.Column("object_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["object_id"], ["event_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("object_id", "tag_id"),
    )
    op.create_table(
        "event_patches",
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("dtstart", sa.DateTime(), nullable=False),
        sa.Column("dtend", sa.DateTime(), nullable=False),
        sa.Column("rrule", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["events.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "events_x_event_groups",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("event_group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_group_id"],
            ["event_groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
        ),
        sa.PrimaryKeyConstraint("event_id", "event_group_id"),
    )
    op.create_table(
        "events_x_ownerships",
        sa.Column("object_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_alias", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["object_id"],
            ["events.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("object_id", "user_id"),
    )
    op.create_table(
        "linked_calendars",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("color", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "alias", name="unique_user_id_alias"),
    )
    op.create_table(
        "tags_x_ownerships",
        sa.Column("object_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_alias", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["object_id"],
            ["tags.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("object_id", "user_id"),
    )
    op.create_table(
        "users_x_favorite_groups",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False),
        sa.Column("predefined", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["event_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "group_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users_x_favorite_groups")
    op.drop_table("tags_x_ownerships")
    op.drop_table("linked_calendars")
    op.drop_table("events_x_ownerships")
    op.drop_table("events_x_event_groups")
    op.drop_table("event_patches")
    op.drop_table("event_groups_x_tags")
    op.drop_table("event_groups_x_ownerships")
    op.drop_table("users")
    op.drop_table("tags")
    op.drop_table("events")
    op.drop_table("event_groups")
    # ### end Alembic commands ###
