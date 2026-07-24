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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
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
    to_encode.update({"exp": expire, "type": "access"})
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


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_refresh_token(token: str) -> str | None:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        return None
    subject = payload.get("sub")
    return str(subject) if subject is not None else None


def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token di accesso non valido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def _get_user_from_payload(payload: dict[str, Any], db: Session) -> User:
    username = str(payload["sub"]).strip().lower()

    stmt = (
        select(User)
        .where(func.lower(User.username) == username)
        .where(User.deleted_at.is_(None))
    )
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user(
    payload: dict[str, Any] = Depends(get_token_payload),
    db: Session = Depends(get_db),
) -> User:
    return _get_user_from_payload(payload, db)


def require_app_scope(payload: dict[str, Any] = Depends(get_token_payload)) -> dict[str, Any]:
    if payload.get("scope") != "app":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PASSWORD_CHANGE_REQUIRED",
        )
    return payload


def require_password_change_scope(
    payload: dict[str, Any] = Depends(get_token_payload),
) -> dict[str, Any]:
    if payload.get("scope") != "password_change":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid scope for required password change flow",
        )
    return payload


def get_current_app_user(
    payload: dict[str, Any] = Depends(require_app_scope),
    db: Session = Depends(get_db),
) -> User:
    return _get_user_from_payload(payload, db)


def get_current_password_change_user(
    payload: dict[str, Any] = Depends(require_password_change_scope),
    db: Session = Depends(get_db),
) -> User:
    return _get_user_from_payload(payload, db)


def require_superuser(current_user: User = Depends(get_current_app_user)) -> User:
    if not current_user.is_superuser:
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
    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
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
        select(Task.id, Task.parent_id)
        .where(Task.id == new_parent_id, Task.user_id == current_user.id)
        .cte(name="cycle_ancestors", recursive=True)
    )

    recursive_part = (
        select(Task.id, Task.parent_id)
        .join(ancestor_cte, Task.id == ancestor_cte.c.parent_id)
        .where(Task.user_id == current_user.id)
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
    "decode_token",
    "get_token_payload",
    "get_current_user",
    "get_current_app_user",
    "get_current_password_change_user",
    "require_app_scope",
    "require_password_change_scope",
    "require_superuser",
    "get_admin_max_depth",
    "get_effective_max_depth",
    "get_task_owned",
    "would_create_cycle",
]