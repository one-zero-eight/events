__all__ = ["Event"]

import datetime

from sqlalchemy import ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storages.sql.__mixin__ import IdMixin
from src.storages.sql.models import Base


class Event(Base, IdMixin):
    __tablename__ = "events"

    patches: Mapped[list["EventPatch"]] = relationship(
        "EventPatch", back_populates="parent", cascade="all, delete-orphan", lazy="selectin"
    )


class EventPatch(Base, IdMixin):
    __tablename__ = "event_patches"

    parent_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    parent: Mapped[Event] = relationship("Event", back_populates="patches", lazy="joined")
    type = mapped_column(String(255), nullable=False, default="create")

    # --- .ics fields --- #
    summary: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=True)

    dtstart: Mapped[datetime.datetime] = mapped_column()
    dtend: Mapped[datetime.datetime] = mapped_column()

    rrule: Mapped[str] = mapped_column()
