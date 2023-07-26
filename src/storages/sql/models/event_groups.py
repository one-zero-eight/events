__all__ = ["EventGroup", "UserXFavoriteEventGroup"]

from typing import Any, TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storages.sql.__mixin__ import TagsMixinFactory
from src.storages.sql.models import Base

if TYPE_CHECKING:
    from src.storages.sql.models.users import User


class EventGroup(Base, TagsMixinFactory("event_groups", Base)):
    __tablename__ = "event_groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text(), nullable=True)
    satellite: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)

    tags_association: Mapped["EventGroupXTag"] = relationship(
        "EventGroupXTag", back_populates="event_group", cascade="all, delete-orphan"
    )


class UserXFavorite(Base):
    __tablename__ = "users_x_favorites"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    hidden: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship("User", back_populates="favorites_association")
    group: Mapped[EventGroup] = relationship(lazy="joined")


class UserXGroup(Base):
    __tablename__ = "users_x_groups"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    hidden: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship("User", back_populates="groups_association")
    group: Mapped[EventGroup] = relationship(lazy="joined")


from src.storages.sql.models.tags import EventGroupXTag  # noqa: E402
