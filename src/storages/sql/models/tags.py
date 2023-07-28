__all__ = ["Tag", "TagOwnership"]

from enum import StrEnum
from typing import Any, TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Enum as SQLAlchemyEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storages.sql.__mixin__ import IdMixin
from src.storages.sql.models import Base

if TYPE_CHECKING:
    from src.storages.sql.models.users import User


class Tag(Base, IdMixin):
    __tablename__ = "tags"

    # parent_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=True)
    # parent: Mapped["Tag"] = relationship("Tag", remote_side=[id], lazy="selectin")
    # children: Mapped[list["Tag"]] = relationship("Tag", remote_side=[parent_id], lazy="selectin")

    alias: Mapped[str] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=True)
    # constraint on pair (alias, type)
    comb_alias_type_cnst = UniqueConstraint(alias, type)
    name: Mapped[str] = mapped_column(nullable=True)
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
