"""
DEPRECATO — il router vive in `backend.domains.tasks.router`.

`populate_task_category_name` resta esportato qui per retro-compatibilità
(usato da `backend.api.sync` finché anche sync non sarà migrato).
"""
from backend.domains.tasks.router import router  # noqa: F401
from backend.domains.tasks.service import populate_category_name as populate_task_category_name  # noqa: F401
