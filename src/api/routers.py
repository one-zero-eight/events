from src.api.users import router as router_users
from src.api.event_groups import router as router_event_groups
from src.api.tags import router as router_tags
from src.api.ics import router as router_ics
from src.api.root import router as router_root
from src.api.parse.routes import router as router_parse

routers = [router_users, router_event_groups, router_tags, router_root, router_ics, router_parse]

__all__ = ["routers", *routers]
