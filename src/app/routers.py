from src.app.users import router as router_users
from src.app.event_groups import router as router_event_groups
from src.app.auth import router as router_auth
from src.app.tags import router as router_tags
from src.app.workshops import router as router_workshops

from src.app.ics import router as router_ics

routers = [router_users, router_event_groups, router_auth, router_tags, router_ics]

__all__ = ["routers", *routers]
