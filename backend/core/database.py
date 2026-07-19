"""
Core database infrastructure.

Contiene:
- Base dichiarativa SQLAlchemy condivisa
- Engine applicativo
- Session factory condivisa
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.core.settings import get_settings


class Base(DeclarativeBase):
    """Classe base per tutti i modelli SQLAlchemy (stile 2.x)."""
    pass


settings = get_settings()
database_url = settings.database_url.strip()

engine_kwargs: dict = {
    "pool_pre_ping": True,
}

if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        {
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_recycle": settings.db_pool_recycle,
            "pool_timeout": settings.db_pool_timeout,
        }
    )

engine = create_engine(database_url, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

__all__ = ["Base", "engine", "SessionLocal"]