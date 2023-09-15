__all__ = ["EventGroup", "UserXFavoriteEventGroup"]

from typing import Any, TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storages.sql.models.__mixin__ import (
    TagsMixinFactory,
    IdMixin,
    NameMixin,
    DescriptionMixin,
    OwnershipsMixinFactory,
    UpdateCreateDateTimeMixin,
)
from src.storages.sql.models import Base

if TYPE_CHECKING:
    from src.storages.sql.models.users import User
    from src.storages.sql.models.events import Event


class EventGroup(
    Base,
    IdMixin,
    NameMixin,
    DescriptionMixin,
    UpdateCreateDateTimeMixin,
    TagsMixinFactory("event_groups", Base),
    OwnershipsMixinFactory("event_groups", Base),
):
    __tablename__ = "event_groups"
    alias: Mapped[str] = mapped_column(String(255), unique=True)
    path: Mapped[str] = mapped_column(nullable=True, unique=True)
    satellite: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)

    favorites_association: Mapped[list["UserXFavoriteEventGroup"]] = relationship(
        "UserXFavoriteEventGroup", back_populates="event_group", cascade="all, delete-orphan", passive_deletes=True
    )

    events: Mapped[list["Event"]] = relationship("Event", secondary="events_x_event_groups")


class UserXFavoriteEventGroup(Base):
    __tablename__ = "users_x_favorite_groups"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("event_groups.id", ondelete="CASCADE"), primary_key=True)
    hidden: Mapped[bool] = mapped_column(default=False)
    predefined: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship("User", back_populates="favorites_association")
    event_group: Mapped[EventGroup] = relationship(lazy="joined", back_populates="favorites_association")
