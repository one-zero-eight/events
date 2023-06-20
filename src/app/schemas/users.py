from ._base import BaseSchema
from ._mixins import HasIdMixin, CollectConfigMeta, ORMMixin


class BaseUser(BaseSchema):
    """
    Represents a user.
    """


class CreateUser(BaseUser):
    ...


class ViewUser(BaseUser, HasIdMixin, ORMMixin, metaclass=CollectConfigMeta):
    ...
