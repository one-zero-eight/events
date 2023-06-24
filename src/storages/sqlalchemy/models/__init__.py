from src.storages.sqlalchemy.models.users import User, Group
from src.storages.sqlalchemy.models.base import Base

all_models = [User, Group]

__all__ = [*all_models, Base]
