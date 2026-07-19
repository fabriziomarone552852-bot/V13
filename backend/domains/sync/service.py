"""
Service del dominio Sync - aggrega i dati di tutti i domini per la risposta
giornaliera sincronizzata (/sync/day).

Importa gli helper di tasks ed events direttamente dai rispettivi domini,
senza dipendere da backend/api/.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, selectinload, with_loader_criteria

from backend.core import models
from backend.core.settings import get_settings
from backend.domains.categories.schemas import CategoryResponse
from backend.domains.countdowns.schemas import CountdownResponse
from backend.domains.events.schemas import EventResponse
from backend.domains.events.service import (
    populate_category_name as _populate_event_category_name,
)
from backend.domains.habits.schemas import HabitResponse
from backend.domains.planning.schemas import DailyEntryResponse
from backend.domains.shopping.schemas import ShoppingListResponse
from backend.domains.sync.schemas import (
    SyncDayResponse,
    SyncWeekResponse,
    SyncMonthResponse
)
from backend.domains.tasks.schemas import TaskResponse
from backend.domains.tasks.service import (
    populate_category_name as _populate_task_category_name,
)
from backend.domains.users.models import User
from backend.utils import expand_events_for_range

_settings = get_settings()
DEFAULT_COMPLETED_TASK_LOOKBACK_DAYS = _settings.default_completed_task_lookback_days
UTC = timezone.utc


def _to_utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(UTC).replace(tzinfo=None)


def _category_to_response(category: models.UserCategory) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.category_name,
        colore=category.colore,
        user_id=category.user_id,
        genre=category.genre,
    )


def get_day_sync(
    db: Session,
    current_user: User,
    data_riferimento: date,
) -> SyncDayResponse:
    """
    Aggrega tutti i dati di un dato giorno per l'utente corrente:
    categories, tasks, daily entries (obiettivo/priorita/note), countdowns,
    habits, eventi (espansi per rrule), shopping lists.
    """
    categories_db = (
        db.query(models.UserCategory)
        .filter(models.UserCategory.user_id == current_user.id)
        .order_by(models.UserCategory.category_name.asc())
        .all()
    )

    lookback_threshold = datetime.now(UTC) - timedelta(
        days=DEFAULT_COMPLETED_TASK_LOOKBACK_DAYS
    )

    tasks_db = (
        db.query(models.Task)
        .filter(models.Task.user_id == current_user.id)
        .filter(
            or_(
                models.Task.fatto.is_(False),
                and_(
                    models.Task.fatto.is_(True),
                    models.Task.data_fatto >= lookback_threshold,
                ),
            )
        )
        .options(
            selectinload(models.Task.category),
            selectinload(models.Task.subtasks),
        )
        .all()
    )
    _populate_task_category_name(tasks_db)

    entries_db = (
        db.query(models.DailyEntry)
        .filter(
            models.DailyEntry.user_id == current_user.id,
            models.DailyEntry.data_riferimento == data_riferimento,
        )
        .order_by(models.DailyEntry.id.asc())
        .all()
    )

    obiettivi = []
    priorita = []
    note = []

    for entry in entries_db:
        if entry.tipo in ["OD", "Obiettivo"]:
            obiettivi.append(entry)
        elif entry.tipo in ["PD", "Priorità"]:
            priorita.append(entry)
        elif entry.tipo in ["N1", "N2", "N3", "N4", "Nota"]:
            note.append(entry)

    countdowns_db = (
        db.query(models.Countdown)
        .filter(models.Countdown.user_id == current_user.id)
        .order_by(
            models.Countdown.status.asc(),
            models.Countdown.target_date.asc(),
            models.Countdown.id.asc(),
        )
        .all()
    )

    habits_db = (
        db.query(models.Habit)
        .options(
            selectinload(models.Habit.periods),
            selectinload(models.Habit.logs),
            with_loader_criteria(
                models.HabitLog,
                models.HabitLog.data_riferimento == data_riferimento,
            ),
        )
        .filter(models.Habit.user_id == current_user.id)
        .join(models.HabitPeriod)
        .filter(
            models.HabitPeriod.data_inizio <= data_riferimento,
            or_(
                models.HabitPeriod.data_fine.is_(None),
                models.HabitPeriod.data_fine >= data_riferimento,
            ),
        )
        .distinct()
        .order_by(models.Habit.id.desc())
        .all()
    )

    eventi_db = (
        db.query(models.Event)
        .filter(models.Event.user_id == current_user.id)
        .options(selectinload(models.Event.category))
        .all()
    )
    _populate_event_category_name(eventi_db)

    eventi_espansi = expand_events_for_range(
        eventi_db,
        data_riferimento,
        data_riferimento,
    )
    eventi_espansi.sort(key=lambda event: _to_utc_naive(event.data_inizio))
    events_payload = [EventResponse.model_validate(event) for event in eventi_espansi]

    shopping_db = (
        db.query(models.ShoppingList)
        .filter(models.ShoppingList.owner_id == current_user.id)
        .options(
            selectinload(models.ShoppingList.items).selectinload(
                models.ShoppingListItem.product
            ),
            selectinload(models.ShoppingList.items).selectinload(
                models.ShoppingListItem.unit
            ),
            selectinload(models.ShoppingList.items).selectinload(
                models.ShoppingListItem.inventory_batches
            ),
            selectinload(models.ShoppingList.items).selectinload(
                models.ShoppingListItem.created_by_user
            ),
            selectinload(models.ShoppingList.items).selectinload(
                models.ShoppingListItem.updated_by_user
            ),
        )
        .order_by(models.ShoppingList.created_at.asc())
        .all()
    )

    return SyncDayResponse(
        data_riferimento=data_riferimento,
        obiettivi=[DailyEntryResponse.model_validate(o) for o in obiettivi],
        priorita=[DailyEntryResponse.model_validate(p) for p in priorita],
        note=[DailyEntryResponse.model_validate(n) for n in note],
        tasks=[TaskResponse.model_validate(t) for t in tasks_db],
        events=events_payload,
        habits=[HabitResponse.model_validate(h) for h in habits_db],
        categories=[_category_to_response(c) for c in categories_db],
        shopping_lists=[ShoppingListResponse.model_validate(s) for s in shopping_db],
        countdowns=[CountdownResponse.model_validate(c) for c in countdowns_db],
    )


def get_week_sync(
    db: Session,
    current_user: User,
    start_date: date,
    end_date: date,
) -> SyncWeekResponse:
    """Aggrega tutti i dati di una data settimana per l'utente corrente."""
    weekly_entries_db = (
        db.query(models.DailyEntry)
        .filter(
            models.DailyEntry.user_id == current_user.id,
            models.DailyEntry.data_riferimento == start_date,
            models.DailyEntry.tipo.in_(["OW", "PW", "EP", "EN"]),
        )
        .order_by(models.DailyEntry.id.asc())
        .all()
    )

    obiettivo_settimanale = None
    priorita_settimanali = []
    eventi_positivi = []
    eventi_negativi = []

    for entry in weekly_entries_db:
        if entry.tipo == "OW":
            obiettivo_settimanale = entry
        elif entry.tipo == "PW":
            priorita_settimanali.append(entry)
        elif entry.tipo == "EP":
            eventi_positivi.append(entry)
        elif entry.tipo == "EN":
            eventi_negativi.append(entry)

    note_settimanali_db = (
        db.query(models.DailyEntry)
        .filter(
            models.DailyEntry.user_id == current_user.id,
            models.DailyEntry.tipo.in_(["N1", "N2", "N3", "N4"]),
            models.DailyEntry.data_riferimento >= start_date,
            models.DailyEntry.data_riferimento <= end_date,
        )
        .order_by(
            models.DailyEntry.data_riferimento.asc(),
            models.DailyEntry.id.desc(),
        )
        .all()
    )

    eventi_db = (
        db.query(models.Event)
        .filter(models.Event.user_id == current_user.id)
        .options(selectinload(models.Event.category))
        .all()
    )
    _populate_event_category_name(eventi_db)

    eventi_espansi = expand_events_for_range(eventi_db, start_date, end_date)
    eventi_espansi.sort(key=lambda event: _to_utc_naive(event.data_inizio))
    events_payload = [EventResponse.model_validate(event) for event in eventi_espansi]

    lookback_threshold = datetime.now(UTC) - timedelta(
        days=DEFAULT_COMPLETED_TASK_LOOKBACK_DAYS
    )

    tasks_db = (
        db.query(models.Task)
        .filter(models.Task.user_id == current_user.id)
        .filter(
            or_(
                models.Task.fatto.is_(False),
                and_(
                    models.Task.fatto.is_(True),
                    models.Task.data_fatto >= lookback_threshold,
                ),
            )
        )
        .options(
            selectinload(models.Task.category),
            selectinload(models.Task.subtasks),
        )
        .all()
    )
    _populate_task_category_name(tasks_db)

    return SyncWeekResponse(
        start_date=start_date,
        end_date=end_date,
        obiettivo_settimanale=(
            DailyEntryResponse.model_validate(obiettivo_settimanale)
            if obiettivo_settimanale
            else None
        ),
        priorita_settimanali=[
            DailyEntryResponse.model_validate(p) for p in priorita_settimanali
        ],
        eventi_positivi=[DailyEntryResponse.model_validate(p) for p in eventi_positivi],
        eventi_negativi=[DailyEntryResponse.model_validate(n) for n in eventi_negativi],
        note=[DailyEntryResponse.model_validate(n) for n in note_settimanali_db],
        events=events_payload,
        tasks=[TaskResponse.model_validate(t) for t in tasks_db],
    )

def get_month_sync(
    db: Session,
    current_user: User,
    start_date: date,
    end_date: date,
) -> SyncMonthResponse:
    """Aggrega tutti i dati di un dato mese per l'utente corrente."""
    
    # 1. Recuperiamo le Daily Entries del mese (es. per i pallini Mood)
    entries_db = (
        db.query(models.DailyEntry)
        .filter(
            models.DailyEntry.user_id == current_user.id,
            models.DailyEntry.data_riferimento >= start_date,
            models.DailyEntry.data_riferimento <= end_date,
        )
        .all()
    )

    # 2. Recuperiamo ed espandiamo gli Eventi nel range mensile
    eventi_db = (
        db.query(models.Event)
        .filter(models.Event.user_id == current_user.id)
        .options(selectinload(models.Event.category))
        .all()
    )
    _populate_event_category_name(eventi_db)
    eventi_espansi = expand_events_for_range(eventi_db, start_date, end_date)
    eventi_espansi.sort(key=lambda event: _to_utc_naive(event.data_inizio))
    events_payload = [EventResponse.model_validate(event) for event in eventi_espansi]

    # 3. Recuperiamo i Task (stessa logica attiva/completati di recente)
    lookback_threshold = datetime.now(UTC) - timedelta(
        days=DEFAULT_COMPLETED_TASK_LOOKBACK_DAYS
    )
    tasks_db = (
        db.query(models.Task)
        .filter(models.Task.user_id == current_user.id)
        .filter(
            or_(
                models.Task.fatto.is_(False),
                and_(
                    models.Task.fatto.is_(True),
                    models.Task.data_fatto >= lookback_threshold,
                ),
            )
        )
        .options(
            selectinload(models.Task.category),
            selectinload(models.Task.subtasks),
        )
        .all()
    )
    _populate_task_category_name(tasks_db)

    return SyncMonthResponse(
        start_date=start_date,
        end_date=end_date,
        daily_entries=[DailyEntryResponse.model_validate(e) for e in entries_db],
        events=events_payload,
        tasks=[TaskResponse.model_validate(t) for t in tasks_db],
    )


