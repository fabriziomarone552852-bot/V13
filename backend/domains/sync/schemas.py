from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import Field

from backend.core.schemas import ORMBaseModel
from backend.domains.categories.schemas import CategoryResponse
from backend.domains.countdowns.schemas import CountdownResponse
from backend.domains.events.schemas import EventResponse
from backend.domains.habits.schemas import HabitResponse
from backend.domains.planning.schemas import DailyEntryResponse
from backend.domains.shopping.schemas import ShoppingListResponse
from backend.domains.tasks.schemas import TaskResponse
from backend.domains.monthly_entries.schemas import MonthlyEntryResponse

class SyncDayResponse(ORMBaseModel):
    data_riferimento: date
    obiettivi: list[DailyEntryResponse] = Field(default_factory=list)
    priorita: list[DailyEntryResponse] = Field(default_factory=list)
    note: list[DailyEntryResponse] = Field(default_factory=list)
    tasks: list[TaskResponse] = Field(default_factory=list)
    events: list[EventResponse] = Field(default_factory=list)
    habits: list[HabitResponse] = Field(default_factory=list)
    categories: list[CategoryResponse] = Field(default_factory=list)
    shopping_lists: list[ShoppingListResponse] = Field(default_factory=list)
    countdowns: list[CountdownResponse] = Field(default_factory=list)


class SyncWeekResponse(ORMBaseModel):
    start_date: date
    end_date: date
    obiettivo_settimanale: Optional[DailyEntryResponse] = None
    priorita_settimanali: list[DailyEntryResponse] = Field(default_factory=list)
    eventi_positivi: list[DailyEntryResponse] = Field(default_factory=list)
    eventi_negativi: list[DailyEntryResponse] = Field(default_factory=list)
    note: list[DailyEntryResponse] = Field(default_factory=list)
    events: list[EventResponse] = Field(default_factory=list)
    tasks: list[TaskResponse] = Field(default_factory=list)


class SyncMonthResponse(ORMBaseModel):
    start_date: date
    end_date: date
    events: List[EventResponse] = Field(default_factory=list)
    tasks: List[TaskResponse] = Field(default_factory=list)
    daily_entries: List[DailyEntryResponse] = Field(default_factory=list)
    monthly_entries: List[MonthlyEntryResponse] = Field(default_factory=list)
