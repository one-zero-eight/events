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


class UserXFavoriteEventGroup(Base):
    __tablename__ = "users_x_favorite_groups"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("event_groups.id"), primary_key=True)
    hidden: Mapped[bool] = mapped_column(default=False)
    predefined: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship("User", back_populates="favorites_association")
    event_group: Mapped[EventGroup] = relationship(lazy="joined")
