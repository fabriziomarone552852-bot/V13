from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.deps import get_password_hash
from backend.domains.users.models import User

from .checks import SystemBootChecks
from .constants import (
    BOOT_STATUS_EMPTY,
    BOOT_STATUS_ERROR,
    BOOT_STATUS_LEGACY_SCHEMA_DETECTED,
    BOOT_STATUS_READY,
    BOOT_STATUS_SUPERUSER_PASSWORD_CHANGE_REQUIRED,
    BOOT_STATUS_SUPERUSER_REQUIRED,
)
from .repository import SystemBootRepository
from .schemas import (
    BootInitRequest,
    BootMetadataInitRequest,
    BootMetadataInitResponse,
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
                system_metadata_present=False,
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
        core_schema_present = all([
            tables["config"],
            tables["config_codes"],
            tables["users"],
        ])
        system_metadata_present = tables["system_metadata"]
        metadata = self.repo.get_system_metadata()
        superuser_present = self.checks.superuser_present()

        if not core_schema_present:
            return BootStatusResponse(
                environment=payload.environment,
                db_name=payload.db_name,
                db_reachable=True,
                schema_present=False,
                system_metadata_present=system_metadata_present,
                schema_version=None,
                seed_version=None,
                config_present=tables["config"],
                config_codes_present=tables["config_codes"],
                users_present=tables["users"],
                superuser_present=superuser_present,
                boot_status=BOOT_STATUS_EMPTY,
                next_action="RUN_BOOTSTRAP",
                diagnostic_message=None,
            )

        if core_schema_present and not system_metadata_present:
            return BootStatusResponse(
                environment=payload.environment,
                db_name=payload.db_name,
                db_reachable=True,
                schema_present=True,
                system_metadata_present=False,
                schema_version=None,
                seed_version=None,
                config_present=tables["config"],
                config_codes_present=tables["config_codes"],
                users_present=tables["users"],
                superuser_present=superuser_present,
                boot_status=BOOT_STATUS_LEGACY_SCHEMA_DETECTED,
                next_action="INITIALIZE_BOOT_METADATA",
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
                system_metadata_present=True,
                schema_version=schema_version,
                seed_version=seed_version,
                config_present=tables["config"],
                config_codes_present=tables["config_codes"],
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
            system_metadata_present=True,
            schema_version=schema_version,
            seed_version=seed_version,
            config_present=tables["config"],
            config_codes_present=tables["config_codes"],
            users_present=tables["users"],
            superuser_present=True,
            boot_status=BOOT_STATUS_READY,
            next_action="ENTER_APP",
            diagnostic_message=None,
        )

    def initialize_boot_metadata(
        self,
        payload: BootMetadataInitRequest,
    ) -> BootMetadataInitResponse:
        try:
            self.repo.create_system_metadata_table()
            self.repo.insert_initial_system_metadata(
                environment=payload.environment,
                schema_version=payload.schema_version,
                seed_version=payload.seed_version,
                notes=payload.notes,
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return BootMetadataInitResponse(
            status="ok",
            boot_status=BOOT_STATUS_SUPERUSER_REQUIRED,
            message="System metadata initialized successfully. Initial superuser creation is required.",
        )

    def run_bootstrap(self, payload: BootInitRequest) -> BootRunResponse:
        return BootRunResponse(
            boot_status="BOOT_METADATA_REQUIRED",
            schema_created=False,
            seed_applied=False,
            superuser_required=False,
            message="Full bootstrap not implemented yet.",
        )

    def create_initial_superuser(
        self,
        payload: SuperUserBootstrapRequest,
    ) -> SuperUserBootstrapResponse:
        tables = self.checks.critical_tables_status()
        core_schema_present = all([
            tables["config"],
            tables["config_codes"],
            tables["users"],
        ])
        system_metadata_present = tables["system_metadata"]

        if not core_schema_present:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Core schema is not initialized. Run bootstrap first.",
            )

        if not system_metadata_present:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="System metadata is missing. Initialize boot metadata first.",
            )

        if self.checks.superuser_present():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A superuser already exists.",
            )

        normalized_username = payload.username.strip()
        normalized_email = str(payload.email).strip().lower()

        existing_by_username = self.db.execute(
            select(User)
            .where(func.lower(User.username) == normalized_username.lower())
            .where(User.deleted_at.is_(None))
        ).scalar_one_or_none()

        if existing_by_username is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already in use.",
            )

        existing_by_email = self.db.execute(
            select(User)
            .where(func.lower(User.email) == normalized_email)
            .where(User.deleted_at.is_(None))
        ).scalar_one_or_none()

        if existing_by_email is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use.",
            )

        user = User(
            username=normalized_username,
            email=normalized_email,
            password_hash=get_password_hash(payload.password),
            is_superuser=True,
            must_change_password=True,
        )

        self.db.add(user)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Unable to create superuser because the username or email already exists.",
            )

        self.db.refresh(user)

        return SuperUserBootstrapResponse(
            status="ok",
            boot_status=BOOT_STATUS_SUPERUSER_PASSWORD_CHANGE_REQUIRED,
            message=(
                f"Initial superuser '{user.username}' created successfully. "
                "The first login must complete the required password change before entering the app."
            ),
        )
