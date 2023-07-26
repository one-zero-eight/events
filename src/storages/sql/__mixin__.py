from typing import TYPE_CHECKING

from sqlalchemy import Table, Column, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, declared_attr, relationship, Mapped

if TYPE_CHECKING:
    from src.storages.sql.models import Tag


def TagsMixinFactory(tablename: str, Base: type[DeclarativeBase]):
    association_table = Table(
        f"{tablename}_x_tags",
        Base.metadata,
        Column(f"{tablename.lower()}_id", Integer, ForeignKey(f"{tablename}.id", ondelete="CASCADE")),
        Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
    )

    class Mixin:
        __tags_mixin_table__ = association_table

        @declared_attr
        def tags(cls) -> Mapped[list["Tag"]]:
            return relationship("Tag", secondary=association_table, lazy="selectin")

    return Mixin
