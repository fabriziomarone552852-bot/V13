"""
Sync domain schemas.
Aggregate response models for sync endpoints.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

from backend.domains.categories.schemas import CategoryResponse
from backend.domains.countdowns.schemas import CountdownResponse
from backend.domains.events.schemas import EventResponse
from backend.domains.habits.schemas import HabitResponse
from backend.domains.planning.schemas import DailyEntryResponse
from backend.domains.shopping.schemas import ShoppingListResponse
from backend.domains.tasks.schemas import TaskResponse


class SyncDayResponse(BaseModel):
    """
    Risposta aggregata per /sync/day.
    Contiene tutti i dati necessari al frontend in una singola richiesta.
    """

    data_riferimento: date
    obiettivi: List[DailyEntryResponse] = Field(default_factory=list)
    priorita: List[DailyEntryResponse] = Field(default_factory=list)
    note: List[DailyEntryResponse] = Field(default_factory=list)
    tasks: List[TaskResponse] = Field(default_factory=list)
    events: List[EventResponse] = Field(default_factory=list)
    habits: List[HabitResponse] = Field(default_factory=list)
    categories: List[CategoryResponse] = Field(default_factory=list)
    shopping_lists: List[ShoppingListResponse] = Field(default_factory=list)
    countdowns: List[CountdownResponse] = Field(default_factory=list)


class SyncWeekResponse(BaseModel):
    start_date: date
    end_date: date
    obiettivo_settimanale: Optional[DailyEntryResponse] = None
    priorita_settimanali: List[DailyEntryResponse] = Field(default_factory=list)
    eventi_positivi: List[DailyEntryResponse] = Field(default_factory=list)
    eventi_negativi: List[DailyEntryResponse] = Field(default_factory=list)
    note: List[DailyEntryResponse] = Field(default_factory=list)
    events: List[EventResponse] = Field(default_factory=list)
    tasks: List[TaskResponse] = Field(default_factory=list)

class SyncMonthResponse(BaseModel):
    """
    Risposta aggregata per /sync/month.
    """
    start_date: date
    end_date: date
    events: List[EventResponse] = Field(default_factory=list)
    tasks: List[TaskResponse] = Field(default_factory=list)
    daily_entries: List[DailyEntryResponse] = Field(default_factory=list)


__all__ = [
    "SyncDayResponse",
    "SyncWeekResponse",
    "SyncMonthResponse",
    "DailyEntryResponse"
]