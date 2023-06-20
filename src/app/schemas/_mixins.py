# from __future__ import annotations
from typing import Union

from pydantic import Field

from ._base import BaseSchema


class HasIdMixin(BaseSchema):
    id: int = Field(..., description="Unique identifier for the object.")


class ObjectReference(HasIdMixin, BaseSchema):
    """
    Represents a reference to an object.
    """


class HasOwnerMixin(BaseSchema):
    """
    Represents the mixin for objects with an owner.
    """

    owner: Union["ObjectReference"] = Field(default_factory=list)


class HasModeratorsMixin(BaseSchema):
    """
    Represents the mixin for objects with moderators.
    """

    moderators: list["ObjectReference"] = Field(default_factory=list)


class HasTagMixin(BaseSchema):
    tags: list["ObjectReference"] = Field(default_factory=list)


class ORMMixin(BaseSchema):
    class Config:
        orm_mode = True


class CollectConfigMeta(type(BaseSchema)):
    """
    Add nested class Config with all Config's from base classes.
    """

    def __new__(cls, name: str, bases: tuple[type(BaseSchema)], namespace: dict):
        bases_to_check = [base for base in bases if isinstance(base, BaseSchema)]
        bases_for_config = [
            base.Config for base in bases_to_check if hasattr(base, "Config")
        ]
        if "Config" in namespace:
            bases_for_config.append(namespace["Config"])
        new_config_class = type("Config", tuple(bases_for_config), {})
        namespace["Config"] = new_config_class

        return super().__new__(cls, name, bases, namespace)  # noqa
