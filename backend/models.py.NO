"""
DEPRECATED: Central models module - use domain-specific models instead.

This file exists for backward compatibility only.
For new code, import directly from the domain modules.
"""
from __future__ import annotations

from backend.core.database import Base  # noqa: F401

from backend.domains.audit.models import SharedActivityLog  # noqa: F401
from backend.domains.categories.models import CategoryGenre, UserCategory  # noqa: F401
from backend.domains.config import Config, ConfigCode  # noqa: F401
from backend.domains.countdowns.models import Countdown  # noqa: F401
from backend.domains.events.models import Event  # noqa: F401
from backend.domains.habits.models import Habit, HabitLog, HabitPeriod  # noqa: F401
from backend.domains.notifications.models import Notification  # noqa: F401
from backend.domains.planning.models import DailyEntry  # noqa: F401
from backend.domains.shopping.models import (  # noqa: F401
    InventoryBatch,
    ShoppingGroup,
    ShoppingGroupMember,
    ShoppingList,
    ShoppingListItem,
    ShoppingProduct,
    ShoppingSupplier,
)
from backend.domains.tasks.models import PrioritaEnum, Task  # noqa: F401
from backend.domains.users.models import User  # noqa: F401

__all__ = [
    "Base",
    "Config",
    "ConfigCode",
    "User",
    "UserCategory",
    "CategoryGenre",
    "Task",
    "PrioritaEnum",
    "Event",
    "ShoppingGroup",
    "ShoppingGroupMember",
    "ShoppingList",
    "ShoppingListItem",
    "ShoppingProduct",
    "ShoppingSupplier",
    "InventoryBatch",
    "SharedActivityLog",
    "Notification",
    "DailyEntry",
    "Countdown",
    "Habit",
    "HabitPeriod",
    "HabitLog",
]