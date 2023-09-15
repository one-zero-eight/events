import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.storages.sql.models.__mixin__ import IdMixin, NameMixin, OwnershipsMixinFactory
from src.storages.sql.models.base import Base

if TYPE_CHECKING:
    from src.storages.sql.models.users import User


class Workshop(Base, IdMixin, NameMixin, OwnershipsMixinFactory("workshops", Base)):
    __tablename__ = "workshops"
    #
    alias: Mapped[str] = mapped_column(unique=True)
    date: Mapped[datetime.date] = mapped_column()
    speaker: Mapped[str] = mapped_column(nullable=True)
    capacity: Mapped[int] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(nullable=True)
    location: Mapped[str] = mapped_column(nullable=True)

    timeslots: Mapped[list["Timeslot"]] = relationship(
        "Timeslot",
        back_populates="workshop",
        cascade="all, delete-orphan",
    )

    checkins: Mapped[list["CheckIn"]] = relationship("CheckIn", back_populates="workshop", cascade="all, delete-orphan")


class Timeslot(Base):
    __tablename__ = "timeslots"

    workshop_id: Mapped[int] = mapped_column(ForeignKey("workshops.id"))
    sequence: Mapped[int] = mapped_column(primary_key=True)
    start: Mapped[datetime.time] = mapped_column()
    end: Mapped[datetime.time] = mapped_column()

    workshop: Mapped[Workshop] = relationship("Workshop", back_populates="timeslots")


class CheckIn(Base):
    __tablename__ = "workshop_checkins"

    workshop_id: Mapped[int] = mapped_column(ForeignKey("workshops.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    timeslot_sequence: Mapped[int] = mapped_column(primary_key=True)
    dtstamp: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    workshop: Mapped[Workshop] = relationship("Workshop", back_populates="checkins")
    user: Mapped["User"] = relationship("User", backref="checkins")
