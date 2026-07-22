from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.deps import get_db
from .schemas import (
    BootInitRequest,
    BootRunResponse,
    BootStatusResponse,
    SuperUserBootstrapRequest,
    SuperUserBootstrapResponse,
)
from .service import SystemBootService

router = APIRouter(prefix="/api/system-boot", tags=["system-boot"])

@router.post("/status", response_model=BootStatusResponse)
def get_boot_status(
    payload: BootInitRequest,
    db: Session = Depends(get_db),
) -> BootStatusResponse:
    service = SystemBootService(db)
    return service.get_status(payload)

@router.post("/run", response_model=BootRunResponse)
def run_bootstrap(
    payload: BootInitRequest,
    db: Session = Depends(get_db),
) -> BootRunResponse:
    service = SystemBootService(db)
    return service.run_bootstrap(payload)

@router.post("/superuser", response_model=SuperUserBootstrapResponse)
def create_initial_superuser(
    payload: SuperUserBootstrapRequest,
    db: Session = Depends(get_db),
) -> SuperUserBootstrapResponse:
    service = SystemBootService(db)
    return service.create_initial_superuser(payload)