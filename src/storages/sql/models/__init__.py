from src.storages.sql.models.users import (
    User,
    EventGroup,
    UserXFavorite,
    UserXGroup,
)
from src.storages.sql.models.base import Base

all_models = [User, EventGroup]

__all__ = [*all_models, Base, UserXFavorite, UserXGroup]
