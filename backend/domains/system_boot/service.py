from __future__ import annotations

from sqlalchemy.orm import Session

from .checks import SystemBootChecks
from .constants import (
    BOOT_STATUS_EMPTY,
    BOOT_STATUS_ERROR,
    BOOT_STATUS_READY,
    BOOT_STATUS_SUPERUSER_REQUIRED,
)
from .repository import SystemBootRepository
from .schemas import (
    BootInitRequest,
    BootRunResponse,
    BootStatusResponse,
    SuperUserBootstrapRequest,
    SuperUserBootstrapResponse,
)


class SystemBootService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SystemBootRepository(db)
        self.checks = SystemBootChecks(self.repo)

    def get_status(self, payload: BootInitRequest) -> BootStatusResponse:
        db_reachable, diagnostic_message = self.checks.database_reachable()

        if not db_reachable:
            return BootStatusResponse(
                environment=payload.environment,
                db_name=payload.db_name,
                db_reachable=False,
                schema_present=False,
                schema_version=None,
                seed_version=None,
                config_present=False,
                config_codes_present=False,
                users_present=False,
                superuser_present=False,
                boot_status=BOOT_STATUS_ERROR,
                next_action="CHECK_CONNECTION",
                diagnostic_message=diagnostic_message,
            )

        tables = self.checks.critical_tables_status()
        schema_present = all(tables.values())
        metadata = self.repo.get_system_metadata()
        superuser_present = self.checks.superuser_present()

        if not schema_present:
            return BootStatusResponse(
                environment=payload.environment,
                db_name=payload.db_name,
                db_reachable=True,
                schema_present=False,
                schema_version=None,
                seed_version=None,
                config_present=tables["config"],
                config_codes_present=tables["configcodes"],
                users_present=tables["users"],
                superuser_present=superuser_present,
                boot_status=BOOT_STATUS_EMPTY,
                next_action="RUN_BOOTSTRAP",
                diagnostic_message=None,
            )

        schema_version = metadata["schema_version"] if metadata else None
        seed_version = metadata["seed_version"] if metadata else None

        if not superuser_present:
            return BootStatusResponse(
                environment=payload.environment,
                db_name=payload.db_name,
                db_reachable=True,
                schema_present=True,
                schema_version=schema_version,
                seed_version=seed_version,
                config_present=tables["config"],
                config_codes_present=tables["configcodes"],
                users_present=tables["users"],
                superuser_present=False,
                boot_status=BOOT_STATUS_SUPERUSER_REQUIRED,
                next_action="CREATE_SUPERUSER",
                diagnostic_message=None,
            )

        return BootStatusResponse(
            environment=payload.environment,
            db_name=payload.db_name,
            db_reachable=True,
            schema_present=True,
            schema_version=schema_version,
            seed_version=seed_version,
            config_present=tables["config"],
            config_codes_present=tables["configcodes"],
            users_present=tables["users"],
            superuser_present=True,
            boot_status=BOOT_STATUS_READY,
            next_action="ENTER_APP",
            diagnostic_message=None,
        )

    def run_bootstrap(self, payload: BootInitRequest) -> BootRunResponse:
        return BootRunResponse(
            boot_status=BOOT_STATUS_SUPERUSER_REQUIRED,
            schema_created=False,
            seed_applied=False,
            superuser_required=True,
            message="Bootstrap logic not implemented yet.",
        )

    def create_initial_superuser(
        self,
        payload: SuperUserBootstrapRequest,
    ) -> SuperUserBootstrapResponse:
        return SuperUserBootstrapResponse(
            status="ok",
            boot_status=BOOT_STATUS_READY,
            message=f"Initial superuser '{payload.username}' creation not implemented yet.",
        )