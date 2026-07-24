from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core import deps
from .guards import require_boot_state
from .schemas import (
    BootInitRequest,
    BootMetadataInitRequest,
    BootMetadataInitResponse,
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
    db: Session = Depends(deps.get_db),
) -> BootStatusResponse:
    service = SystemBootService(db)
    return service.get_status(payload)


@router.post(
    "/run",
    response_model=BootRunResponse,
    dependencies=[Depends(require_boot_state("EMPTY"))],
)
def run_bootstrap(
    payload: BootInitRequest,
    db: Session = Depends(deps.get_db),
) -> BootRunResponse:
    service = SystemBootService(db)
    return service.run_bootstrap(payload)


@router.post(
    "/metadata/init",
    response_model=BootMetadataInitResponse,
    dependencies=[Depends(require_boot_state("LEGACY_SCHEMA_DETECTED"))],
)
def initialize_boot_metadata(
    payload: BootMetadataInitRequest,
    db: Session = Depends(deps.get_db),
) -> BootMetadataInitResponse:
    service = SystemBootService(db)
    return service.initialize_boot_metadata(payload)


@router.post(
    "/superuser",
    response_model=SuperUserBootstrapResponse,
    dependencies=[Depends(require_boot_state("SUPERUSER_REQUIRED"))],
)
def create_initial_superuser(
    payload: SuperUserBootstrapRequest,
    db: Session = Depends(deps.get_db),
) -> SuperUserBootstrapResponse:
    service = SystemBootService(db)
    return service.create_initial_superuser(payload)