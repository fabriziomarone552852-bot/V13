from __future__ import annotations

from datetime import date

from backend.domains.categories.schemas import CategoryResponse
from backend.domains.countdowns.schemas import CountdownResponse
from backend.domains.events.schemas import EventResponse
from backend.domains.habits.schemas import HabitResponse
from backend.domains.planning.schemas import DailyEntryResponse
from backend.domains.shopping.schemas import ShoppingListResponse
from backend.domains.sync.repository import DaySyncBundle, MonthSyncBundle, WeekSyncBundle
from backend.domains.sync.schemas import SyncDayResponse, SyncMonthResponse, SyncWeekResponse
from backend.domains.tasks.schemas import TaskResponse

DAY_OBJECTIVE_TYPES = {"OD"}
DAY_PRIORITY_TYPES = {"PD"}
DAY_NOTE_TYPES = {"N1", "N2", "N3", "N4"}

WEEK_OBJECTIVE_TYPES = {"OW"}
WEEK_PRIORITY_TYPES = {"PW"}
WEEK_POSITIVE_TYPES = {"EP"}
WEEK_NEGATIVE_TYPES = {"EN"}
WEEK_NOTE_TYPES = {"N1", "N2", "N3", "N4"}


def _category_to_response(category) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.category_name,
        colore=category.colore,
        user_id=category.user_id,
        genre=category.genre,
    )


def _daily_entries_to_response(items) -> list[DailyEntryResponse]:
    return [DailyEntryResponse.model_validate(x) for x in items]


def to_day_response(bundle: DaySyncBundle, data_riferimento: date) -> SyncDayResponse:
    obiettivi = [e for e in bundle.daily_entries if e.tipo in DAY_OBJECTIVE_TYPES]
    priorita = [e for e in bundle.daily_entries if e.tipo in DAY_PRIORITY_TYPES]
    note = [e for e in bundle.daily_entries if e.tipo in DAY_NOTE_TYPES]

    return SyncDayResponse(
        data_riferimento=data_riferimento,
        obiettivi=_daily_entries_to_response(obiettivi),
        priorita=_daily_entries_to_response(priorita),
        note=_daily_entries_to_response(note),
        tasks=[TaskResponse.model_validate(x) for x in bundle.tasks],
        events=[EventResponse.model_validate(x) for x in bundle.events],
        habits=[HabitResponse.model_validate(x) for x in bundle.habits],
        categories=[_category_to_response(x) for x in bundle.categories],
        shopping_lists=[ShoppingListResponse.model_validate(x) for x in bundle.shopping_lists],
        countdowns=[CountdownResponse.model_validate(x) for x in bundle.countdowns],
    )


def to_week_response(bundle: WeekSyncBundle, start_date: date, end_date: date) -> SyncWeekResponse:
    obiettivo_settimanale = next((e for e in bundle.daily_entries if e.tipo in WEEK_OBJECTIVE_TYPES), None)
    priorita_settimanali = [e for e in bundle.daily_entries if e.tipo in WEEK_PRIORITY_TYPES]
    eventi_positivi = [e for e in bundle.daily_entries if e.tipo in WEEK_POSITIVE_TYPES]
    eventi_negativi = [e for e in bundle.daily_entries if e.tipo in WEEK_NEGATIVE_TYPES]
    note = [e for e in bundle.daily_entries if e.tipo in WEEK_NOTE_TYPES]

    return SyncWeekResponse(
        start_date=start_date,
        end_date=end_date,
        obiettivo_settimanale=DailyEntryResponse.model_validate(obiettivo_settimanale) if obiettivo_settimanale else None,
        priorita_settimanali=_daily_entries_to_response(priorita_settimanali),
        eventi_positivi=_daily_entries_to_response(eventi_positivi),
        eventi_negativi=_daily_entries_to_response(eventi_negativi),
        note=_daily_entries_to_response(note),
        events=[EventResponse.model_validate(x) for x in bundle.events],
        tasks=[TaskResponse.model_validate(x) for x in bundle.tasks],
    )


def to_month_response(bundle: MonthSyncBundle, start_date: date, end_date: date) -> SyncMonthResponse:
    return SyncMonthResponse(
        start_date=start_date,
        end_date=end_date,
        events=[EventResponse.model_validate(x) for x in bundle.events],
        tasks=[TaskResponse.model_validate(x) for x in bundle.tasks],
        daily_entries=_daily_entries_to_response(bundle.daily_entries),
    )
