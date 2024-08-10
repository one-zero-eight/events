from src.modules.event_groups.routes import router as router_event_groups
from src.modules.ics.routes import router as router_ics
from src.modules.parse.routes import router as router_parse
from src.modules.predefined.routes import router as router_predefined
from src.modules.tags.routes import router as router_tags
from src.modules.users.routes import router as router_users

routers = [router_users, router_event_groups, router_tags, router_ics, router_parse, router_predefined]

__all__ = ["routers", *routers]
