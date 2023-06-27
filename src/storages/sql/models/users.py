from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.storages.sql.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)

    email: Mapped[str] = mapped_column(unique=True)

    status: Mapped[str] = mapped_column(nullable=True)
    favorites_association: Mapped[list["UserXFavorite"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    favorites: Mapped[list["EventGroup"]] = association_proxy(
        "favorites_association",
        "group",
        creator=lambda group: UserXFavorite(group=group),
    )

    groups_association: Mapped[list["UserXGroup"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    groups: Mapped[list["EventGroup"]] = association_proxy(
        "groups_association", "group", creator=lambda group: UserXGroup(group=group)
    )


class EventGroup(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    type: Mapped[str] = mapped_column(nullable=True)


class UserXFavorite(Base):
    __tablename__ = "users_x_favorites"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    hidden: Mapped[bool] = mapped_column(default=False)

    user: Mapped[User] = relationship(back_populates="favorites_association")
    group: Mapped[EventGroup] = relationship(lazy="joined")


class UserXGroup(Base):
    __tablename__ = "users_x_groups"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    hidden: Mapped[bool] = mapped_column(default=False)

    user: Mapped[User] = relationship(back_populates="groups_association")
    group: Mapped[EventGroup] = relationship(lazy="joined")
