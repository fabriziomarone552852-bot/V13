from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.core.deps import get_db
from .checks import SystemBootChecks
from .repository import SystemBootRepository
from .schemas import BootStatus

BOOT_PUBLIC_PATHS = {
    "/api/system-boot/status",
    "/api/system-boot/run",
    "/api/system-boot/metadata/init",
    "/api/system-boot/superuser",
    "/docs",
    "/openapi.json",
    "/redoc",
}


def _compute_boot_status(db: Session) -> BootStatus:
    repo = SystemBootRepository(db)
    checks = SystemBootChecks(repo)

    db_reachable, _ = checks.database_reachable()
    if not db_reachable:
        return "ERROR"

    tables = checks.critical_tables_status()
    core_schema_present = all(
        [tables["config"], tables["config_codes"], tables["users"]]
    )
    system_metadata_present = tables["system_metadata"]
    superuser_present = checks.superuser_present()

    if not core_schema_present:
        return "EMPTY"

    if not system_metadata_present:
        return "LEGACY_SCHEMA_DETECTED"

    if not superuser_present:
        return "SUPERUSER_REQUIRED"

    return "READY"


def _is_public_boot_path(path: str) -> bool:
    return path in BOOT_PUBLIC_PATHS or path.startswith("/auth/")


async def system_boot_guard(request: Request, call_next):
    path = request.url.path

    if _is_public_boot_path(path):
        return await call_next(request)

    db = SessionLocal()
    try:
        current_state = _compute_boot_status(db)
    finally:
        db.close()

    if current_state != "READY":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "System boot is incomplete.",
                "boot_status": current_state,
            },
        )

    return await call_next(request)


def require_boot_state(*allowed_states: BootStatus):
    allowed: tuple[BootStatus, ...] = tuple(allowed_states)

    def dependency(db: Session = Depends(get_db)) -> None:
        current_state = _compute_boot_status(db)
        if current_state not in allowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Operation not allowed in current boot state: {current_state}. "
                    f"Allowed states: {', '.join(allowed)}."
                ),
            )

    return dependency