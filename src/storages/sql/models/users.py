__all__ = ["User", "UserScheduleKeys"]

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.storages.sql.models.__mixin__ import IdMixin
from src.storages.sql.models.base import Base

if TYPE_CHECKING:
    from src.storages.sql.models.event_groups import EventGroup
    from src.storages.sql.models.event_groups import UserXFavoriteEventGroup
    from src.storages.sql.models.linked import LinkedCalendar


class User(Base, IdMixin):
    __ownerships_tables__ = dict()
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(nullable=True)

    email: Mapped[str] = mapped_column(unique=True)

    status: Mapped[str] = mapped_column(nullable=True)

    favorites_association: Mapped[list["UserXFavoriteEventGroup"]] = relationship(
        "UserXFavoriteEventGroup",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    favorites: Mapped[list["EventGroup"]] = association_proxy(
        "favorites_association",
        "event_group",
    )

    linked_calendars: Mapped[list["LinkedCalendar"]] = relationship(
        "LinkedCalendar",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserScheduleKeys(Base, IdMixin):
    __tablename__ = "user_schedule_keys"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    access_key: Mapped[str] = mapped_column(nullable=False, index=True)
    resource_path: Mapped[str] = mapped_column(nullable=False)
