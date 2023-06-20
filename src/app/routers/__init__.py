from .auth import router as router_auth
from .users import router as router_users
from .search import router as router_search
from .event_chains import router as router_event_chains
from .event_groups import router as router_event_groups
from .webhooks import router as router_webhooks

routers = [
    router_auth,
    router_users,
    router_search,
    router_event_chains,
    router_event_groups,
    router_webhooks,
]

__all__ = ["routers", *routers]
