from enum import StrEnum
from typing import Any, TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storages.sql.models import Base

if TYPE_CHECKING:
    from src.storages.sql.models.users import User


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    type: Mapped[str] = mapped_column(nullable=True)
    satellite: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)

    ownership_association: Mapped[list["TagOwnership"]] = relationship(
        "TagOwnership", back_populates="tag", cascade="all, delete-orphan", lazy="selectin"
    )


class OwnershipEnum(StrEnum):
    default = "default"
    moderator = "moderator"
    owner = "owner"


class TagOwnership(Base):
    __tablename__ = "tags_ownership"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    user: Mapped["User"] = relationship("User")
    tag: Mapped["Tag"] = relationship("Tag")

    ownership_enum: Mapped[OwnershipEnum] = mapped_column(
        SQLAlchemyEnum(OwnershipEnum, name="ownership_type"), default=OwnershipEnum.default
    )


class EventGroupXTag(Base):
    __tablename__ = "event_group_x_tag"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)

    event_group: Mapped["EventGroup"] = relationship("EventGroup", back_populates="tags_association")
    tag: Mapped["Tag"] = relationship(lazy="joined")


from src.storages.sql.models.event_groups import EventGroup  # noqa: E402
