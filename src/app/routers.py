from src.app.schemas_registry import router as router_schemas_registry
from src.app.users import router as router_users
from src.app.event_groups import router as router_event_groups
from src.app.auth import router as router_auth

routers = [router_users, router_event_groups, router_schemas_registry, router_auth]

__all__ = ["routers", *routers]
