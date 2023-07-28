__all__ = ["User"]

from typing import TYPE_CHECKING

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, mapped_column, Mapped

from src.storages.sql.__mixin__ import IdMixin
from src.storages.sql.models.base import Base

if TYPE_CHECKING:
    from src.storages.sql.models.event_groups import EventGroup


class User(Base, IdMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(nullable=True)

    email: Mapped[str] = mapped_column(unique=True)

    status: Mapped[str] = mapped_column(nullable=True)

    favorites_association: Mapped[list["UserXFavoriteEventGroup"]] = relationship(
        "UserXFavoriteEventGroup",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    favorites: Mapped[list["EventGroup"]] = association_proxy(
        "favorites_association",
        "event_group",
    )


from src.storages.sql.models.event_groups import UserXFavoriteEventGroup  # noqa: E402
