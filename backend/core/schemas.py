"""
Core schemas infrastructure.

Contains shared Pydantic base classes used across all domains.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CoreBaseModel(BaseModel):
    """Base Pydantic model for the project."""
    model_config = ConfigDict()


class ORMBaseModel(CoreBaseModel):
    """Base model for ORM-backed schemas."""
    model_config = ConfigDict(from_attributes=True)


class StrictBaseModel(CoreBaseModel):
    """Base model with strict extra field validation."""
    model_config = ConfigDict(extra="forbid")


class ORMStrictBaseModel(StrictBaseModel):
    """Base model for ORM-backed schemas with strict extra validation."""
    model_config = ConfigDict(from_attributes=True, extra="forbid")


__all__ = [
    "CoreBaseModel",
    "ORMBaseModel",
    "StrictBaseModel",
    "ORMStrictBaseModel",
]