from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, selectinload, with_loader_criteria

from backend.core.settings import get_settings
from backend.domains.categories.models import UserCategory
from backend.domains.countdowns.models import Countdown
from backend.domains.events.models import Event
from backend.domains.events.recurrence import expand_events_for_range
from backend.domains.events.service import populate_category_name as populate_event_category_name
from backend.domains.habits.models import Habit, HabitLog, HabitPeriod
from backend.domains.planning.models import DailyEntry
from backend.domains.shopping.models import ShoppingList, ShoppingListItem
from backend.domains.tasks.models import Task
from backend.domains.tasks.service import populate_category_name as populate_task_category_name
from backend.domains.monthly_entries.models import MonthlyEntry
from backend.domains.monthly_entries.repository import list_entries as get_monthly_entries

UTC = timezone.utc
_settings = get_settings()
DEFAULT_COMPLETED_TASK_LOOKBACK_DAYS = _settings.default_completed_task_lookback_days


@dataclass
class DaySyncBundle:
    categories: list[UserCategory] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    daily_entries: list[DailyEntry] = field(default_factory=list)
    countdowns: list[Countdown] = field(default_factory=list)
    habits: list[Habit] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    shopping_lists: list[ShoppingList] = field(default_factory=list)


@dataclass
class WeekSyncBundle:
    daily_entries: list[DailyEntry] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)


@dataclass
class MonthSyncBundle:
    daily_entries: list[DailyEntry] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    monthly_entries: list[MonthlyEntry] = field(default_factory=list)


def _recent_task_threshold() -> datetime:
    return datetime.now(UTC) - timedelta(days=DEFAULT_COMPLETED_TASK_LOOKBACK_DAYS)


def get_recent_tasks(db: Session, user_id: int) -> list[Task]:
    tasks = (
        db.query(Task)
        .filter(Task.user_id == user_id)
        .filter(
            or_(
                Task.fatto.is_(False),
                and_(Task.fatto.is_(True), Task.data_fatto >= _recent_task_threshold()),
            )
        )
        .options(selectinload(Task.category), selectinload(Task.subtasks))
        .all()
    )
    populate_task_category_name(tasks)
    return tasks


def get_expanded_events(db: Session, user_id: int, start_date: date, end_date: date) -> list[Event]:
    events = (
        db.query(Event)
        .filter(Event.user_id == user_id)
        .options(selectinload(Event.category))
        .all()
    )
    populate_event_category_name(events)
    expanded = expand_events_for_range(events, start_date, end_date)
    expanded.sort(
        key=lambda event: event.data_inizio.astimezone(UTC).replace(tzinfo=None)
        if event.data_inizio.tzinfo
        else event.data_inizio
    )
    return expanded


def get_categories(db: Session, user_id: int) -> list[UserCategory]:
    return (
        db.query(UserCategory)
        .filter(UserCategory.user_id == user_id)
        .order_by(UserCategory.category_name.asc())
        .all()
    )


def get_daily_entries_for_day(db: Session, user_id: int, data_riferimento: date) -> list[DailyEntry]:
    return (
        db.query(DailyEntry)
        .filter(DailyEntry.user_id == user_id, DailyEntry.data_riferimento == data_riferimento)
        .order_by(DailyEntry.id.asc())
        .all()
    )


def get_daily_entries_for_range(db: Session, user_id: int, start_date: date, end_date: date) -> list[DailyEntry]:
    return (
        db.query(DailyEntry)
        .filter(
            DailyEntry.user_id == user_id,
            DailyEntry.data_riferimento >= start_date,
            DailyEntry.data_riferimento <= end_date,
        )
        .order_by(DailyEntry.data_riferimento.asc(), DailyEntry.id.asc())
        .all()
    )


def get_countdowns(db: Session, user_id: int) -> list[Countdown]:
    return (
        db.query(Countdown)
        .filter(Countdown.user_id == user_id)
        .order_by(Countdown.status.asc(), Countdown.target_date.asc(), Countdown.id.asc())
        .all()
    )


def get_habits_for_day(db: Session, user_id: int, data_riferimento: date) -> list[Habit]:
    return (
        db.query(Habit)
        .options(
            selectinload(Habit.periods),
            selectinload(Habit.logs),
            with_loader_criteria(HabitLog, HabitLog.data_riferimento == data_riferimento),
        )
        .filter(Habit.user_id == user_id)
        .join(HabitPeriod)
        .filter(HabitPeriod.data_inizio <= data_riferimento, or_(HabitPeriod.data_fine.is_(None), HabitPeriod.data_fine >= data_riferimento))
        .distinct()
        .order_by(Habit.id.desc())
        .all()
    )


def get_shopping_lists(db: Session, user_id: int) -> list[ShoppingList]:
    return (
        db.query(ShoppingList)
        .filter(ShoppingList.owner_id == user_id)
        .options(
            selectinload(ShoppingList.items).selectinload(ShoppingListItem.product),
            selectinload(ShoppingList.items).selectinload(ShoppingListItem.unit),
            selectinload(ShoppingList.items).selectinload(ShoppingListItem.inventory_batches),
            selectinload(ShoppingList.items).selectinload(ShoppingListItem.created_by_user),
            selectinload(ShoppingList.items).selectinload(ShoppingListItem.updated_by_user),
        )
        .order_by(ShoppingList.created_at.asc())
        .all()
    )


def build_day_bundle(db: Session, user_id: int, data_riferimento: date) -> DaySyncBundle:
    return DaySyncBundle(
        categories=get_categories(db, user_id),
        tasks=get_recent_tasks(db, user_id),
        daily_entries=get_daily_entries_for_day(db, user_id, data_riferimento),
        countdowns=get_countdowns(db, user_id),
        habits=get_habits_for_day(db, user_id, data_riferimento),
        events=get_expanded_events(db, user_id, data_riferimento, data_riferimento),
        shopping_lists=get_shopping_lists(db, user_id),
    )


def build_week_bundle(db: Session, user_id: int, start_date: date, end_date: date) -> WeekSyncBundle:
    return WeekSyncBundle(
        daily_entries=get_daily_entries_for_range(db, user_id, start_date, end_date),
        tasks=get_recent_tasks(db, user_id),
        events=get_expanded_events(db, user_id, start_date, end_date),
    )


def build_month_bundle(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
) -> MonthSyncBundle:
    target_date = start_date + timedelta(days=15)
    
    month_entries = get_monthly_entries(db, user_id, year=target_date.year, month=target_date.month)

    return MonthSyncBundle(
        daily_entries=get_daily_entries_for_range(db, user_id, start_date, end_date),
        tasks=get_recent_tasks(db, user_id),
        events=get_expanded_events(db, user_id, start_date, end_date),
        monthly_entries=month_entries
    )
