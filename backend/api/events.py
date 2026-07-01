"""
DEPRECATO — il router vive in `backend.domains.events.router`.

`populate_event_category_name` resta esportato qui per retro-compatibilità
(usato da `backend.api.sync` finché anche sync non sarà migrato).
"""
from backend.domains.events.router import router  # noqa: F401
from backend.domains.events.service import populate_category_name as populate_event_category_name  # noqa: F401
