"""
Categories domain - user-scoped category management for tasks and events.
Public API re-exports for schemas and enums.
"""
from __future__ import annotations

from backend.domains.categories.models import CategoryGenre, UserCategory
from backend.domains.categories.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)

__all__ = [
    "UserCategory",
    "CategoryGenre",
    "CategoryCreate",
    "CategoryResponse",
    "CategoryUpdate",
]