from sqlalchemy import Column, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.storages.sqlalchemy.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(nullable=True)

    email: Mapped[str] = mapped_column(primary_key=True, unique=True)

    status: Mapped[str] = mapped_column(nullable=True)
    favorites: Mapped[list["Group"]] = relationship(secondary="user_favorites")
    groups: Mapped[list["Group"]] = relationship(secondary="user_x_group")


class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column(nullable=True)


user_x_favorites = Table(
    "user_x_favorites",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("group_id", ForeignKey("groups.id")),
    Column("hidden", Boolean),
)

user_x_group = Table(
    "user_x_group",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("group_id", ForeignKey("groups.id")),
    Column("hidden", Boolean),
)
