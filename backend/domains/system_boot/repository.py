from sqlalchemy import text
from sqlalchemy.orm import Session


class SystemBootRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ping(self) -> bool:
        result = self.db.execute(text("SELECT 1"))
        _ = result.scalar()
        return True

    def table_exists(self, table_name: str, schema: str = "public") -> bool:
        result = self.db.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = :schema
                      AND table_name = :table_name
                )
                """
            ),
            {"schema": schema, "table_name": table_name},
        )
        return bool(result.scalar())

    def column_exists(self, table_name: str, column_name: str, schema: str = "public") -> bool:
        result = self.db.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = :schema
                      AND table_name = :table_name
                      AND column_name = :column_name
                )
                """
            ),
            {"schema": schema, "table_name": table_name, "column_name": column_name},
        )
        return bool(result.scalar())

    def count_superusers(self) -> int:
        result = self.db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM users
                WHERE is_superuser = TRUE
                  AND deleted_at IS NULL
                """
            )
        )
        return int(result.scalar() or 0)

    def get_system_metadata(self) -> dict | None:
        if not self.table_exists("system_metadata"):
            return None

        result = self.db.execute(text("SELECT * FROM system_metadata WHERE id = 1"))
        row = result.mappings().first()
        return dict(row) if row else None

    def create_system_metadata_table(self) -> None:
        self.db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS system_metadata (
                    id INTEGER PRIMARY KEY,
                    environment VARCHAR(20) NOT NULL,
                    schema_version VARCHAR(50) NOT NULL,
                    seed_version VARCHAR(50),
                    boot_status VARCHAR(50) NOT NULL,
                    initialized_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    initialized_by_user_id INTEGER NULL,
                    notes TEXT NULL
                )
                """
            )
        )

    def insert_initial_system_metadata(
        self,
        environment: str,
        schema_version: str,
        seed_version: str | None,
        notes: str | None,
    ) -> None:
        self.db.execute(
            text(
                """
                INSERT INTO system_metadata (
                    id,
                    environment,
                    schema_version,
                    seed_version,
                    boot_status,
                    notes
                )
                VALUES (
                    1,
                    :environment,
                    :schema_version,
                    :seed_version,
                    'READY',
                    :notes
                )
                ON CONFLICT (id) DO UPDATE SET
                    environment = EXCLUDED.environment,
                    schema_version = EXCLUDED.schema_version,
                    seed_version = EXCLUDED.seed_version,
                    boot_status = EXCLUDED.boot_status,
                    notes = EXCLUDED.notes,
                    updated_at = NOW()
                """
            ),
            {
                "environment": environment,
                "schema_version": schema_version,
                "seed_version": seed_version,
                "notes": notes,
            },
        )
