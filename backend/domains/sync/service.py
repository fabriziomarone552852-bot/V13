# backend/domains/sync/service.py
from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session

from backend.domains.sync import repository, mappers
from backend.domains.sync.schemas import SyncDayResponse, SyncWeekResponse, SyncMonthResponse
from backend.domains.users.models import User


def get_day_sync(db: Session, current_user: User, data_riferimento: date) -> SyncDayResponse:
    bundle = repository.build_day_bundle(db, current_user.id, data_riferimento)
    return mappers.to_day_response(bundle, data_riferimento)


def get_week_sync(db: Session, current_user: User, start_date: date, end_date: date) -> SyncWeekResponse:
    bundle = repository.build_week_bundle(db, current_user.id, start_date, end_date)
    return mappers.to_week_response(bundle, start_date, end_date)


def get_month_sync(db: Session, current_user: User, start_date: date, end_date: date) -> SyncMonthResponse:
    bundle = repository.build_month_bundle(db, current_user.id, start_date, end_date)
    return mappers.to_month_response(bundle, start_date, end_date)