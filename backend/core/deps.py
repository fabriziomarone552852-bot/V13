from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Generator

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.core.settings import get_settings
from backend.domains.config import Config
from backend.domains.tasks.models import Task
from backend.domains.users.models import User


settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
password_hasher = PasswordHasher()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(data: dict[str, Any], expire_minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expire_minutes or settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def verify_refresh_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
        if payload.get("type") != "refresh":
            return None
        subject = payload.get("sub")
        return str(subject) if subject is not None else None
    except JWTError:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
        username = payload.get("sub")
        if not isinstance(username, str) or not username.strip():
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    stmt = (
        select(User)
        .where(func.lower(User.username) == username.lower())
        .where(User.deleted_at.is_(None))
    )
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.issuperuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permessi insufficienti",
        )
    return current_user


def get_admin_max_depth(db: Session) -> int:
    stmt = select(Config).where(Config.key == "maxsubtaskdepth")
    config_db = db.execute(stmt).scalar_one_or_none()
    return int(config_db.value) if config_db else settings.default_max_subtask_depth


def get_effective_max_depth(user: User, db: Session) -> int:
    admin_limit = get_admin_max_depth(db)
    user_limit = (
        user.max_subtask_depth_user
        if user.max_subtask_depth_user is not None
        else settings.default_max_subtask_depth
    )
    return min(user_limit, admin_limit)


def get_task_owned(task_id: int, current_user: User, db: Session) -> Task:
    stmt = select(Task).where(Task.id == task_id, Task.userid == current_user.id)
    task = db.execute(stmt).scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task non trovato o non accessibile",
        )

    return task


def would_create_cycle(
    task_id: int,
    new_parent_id: int | None,
    current_user: User,
    db: Session,
) -> bool:
    if new_parent_id is None:
        return False

    if task_id == new_parent_id:
        return True

    ancestor_cte = (
        select(Task.id, Task.parentid)
        .where(Task.id == new_parent_id, Task.userid == current_user.id)
        .cte(name="cycle_ancestors", recursive=True)
    )

    recursive_part = (
        select(Task.id, Task.parentid)
        .join(ancestor_cte, Task.id == ancestor_cte.c.parentid)
        .where(Task.userid == current_user.id)
    )

    ancestor_cte = ancestor_cte.union_all(recursive_part)
    cycle_query = select(ancestor_cte.c.id).where(ancestor_cte.c.id == task_id)

    return db.execute(cycle_query).first() is not None


__all__ = [
    "oauth2_scheme",
    "get_db",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_refresh_token",
    "get_current_user",
    "require_superuser",
    "get_admin_max_depth",
    "get_effective_max_depth",
    "get_task_owned",
    "would_create_cycle",
]