"""
Central model registry for SQLAlchemy.

Importa esplicitamente tutti i modelli di dominio così che SQLAlchemy
possa risolvere correttamente relationship e mapper string-based.
"""
from __future__ import annotations


def import_all_models() -> None:
    import backend.domains.audit.models  # noqa: F401
    import backend.domains.categories.models  # noqa: F401
    import backend.domains.config.models  # noqa: F401
    import backend.domains.countdowns.models  # noqa: F401
    import backend.domains.events.models  # noqa: F401
    import backend.domains.habits.models  # noqa: F401
    import backend.domains.monthly_entries.models  # noqa: F401
    import backend.domains.notifications.models  # noqa: F401
    import backend.domains.planning.models  # noqa: F401
    import backend.domains.shopping.models  # noqa: F401
    import backend.domains.tasks.models  # noqa: F401
    import backend.domains.users.models  # noqa: F401


__all__ = ["import_all_models"]