"""
Schemas for configuration options.
"""

from __future__ import annotations

from typing import List

from backend.core.schemas import StrictBaseModel


class ConfigOption(StrictBaseModel):
    """Generic option for configuration dropdowns."""

    id: int
    value: str
    label: str


class ShoppingConfigBundle(StrictBaseModel):
    """Bundle of all configuration options for the shopping UI."""

    unitOptions: List[ConfigOption]
    currencyOptions: List[ConfigOption]
    offerFlagOptions: List[ConfigOption]
    visibilityOptions: List[ConfigOption]
    listStatusOptions: List[ConfigOption]
    groupStatusOptions: List[ConfigOption]
    groupRoleOptions: List[ConfigOption]
    supplierStatusOptions: List[ConfigOption]