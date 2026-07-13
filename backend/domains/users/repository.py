"""Repository del dominio Users — solo accesso ai dati."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.domains.users.models import User


def email_in_use(db: Session, email: str) -> bool:
    return (
        db.query(User)
        .filter(func.lower(User.email) == email.lower())
        .first()
        is not None
    )


def save(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_by_username(db: Session, username: str) -> User | None:
    return (
        db.query(User)
        .filter(func.lower(User.username) == username.lower())
        .filter(User.deleted_at.is_(None))
        .first()
    )


def get_by_username_including_deleted(db: Session, username: str) -> User | None:
    return (
        db.query(User)
        .filter(func.lower(User.username) == username.lower())
        .first()
    )


def get_by_email(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .filter(func.lower(User.email) == email.lower())
        .filter(User.deleted_at.is_(None))
        .first()
    )


def get_by_email_including_deleted(db: Session, email: str) -> User | None:
    return (
        db.query(User)
        .filter(func.lower(User.email) == email.lower())
        .first()
    )


def get_by_id(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id)
        .filter(User.deleted_at.is_(None))
        .first()
    )


def get_by_id_including_deleted(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def username_or_email_exists(db: Session, username: str, email: str) -> bool:
    return (
        db.query(User)
        .filter(
            or_(
                func.lower(User.username) == username.lower(),
                func.lower(User.email) == email.lower(),
            )
        )
        .first()
        is not None
    )


def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(
    db: Session,
    user: User,
    deleted_by_user_id: int | None = None,
) -> User:
    user.deleted_at = datetime.now(timezone.utc)
    user.deleted_by_user_id = deleted_by_user_id
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def restore_user(db: Session, user: User) -> User:
    user.deleted_at = None
    user.deleted_by_user_id = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_deleted_by_username_or_email(db: Session, username: str, email: str) -> User | None:
    return (
        db.query(User)
        .filter(
            or_(
                func.lower(User.username) == username.lower(),
                func.lower(User.email) == email.lower(),
            )
        )
        .filter(User.deleted_at.is_not(None))
        .first()
    )