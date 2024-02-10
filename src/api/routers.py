from src.api.users import router as router_users
from src.api.event_groups import router as router_event_groups
from src.api.auth import router as router_auth
from src.api.tags import router as router_tags
from src.api.ics import router as router_ics

# TODO: Implement workshops
# from src.app.workshops import router as router_workshops

from src.api.root import router as router_root

routers = [router_users, router_event_groups, router_auth, router_tags, router_root, router_ics]

__all__ = ["routers", *routers]
