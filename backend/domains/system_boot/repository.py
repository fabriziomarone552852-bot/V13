from __future__ import annotations

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
                SELECT COALESCE(
                    to_regclass(:qualified_table_name) IS NOT NULL,
                    FALSE
                )
                """
            ),
            {"qualified_table_name": f"{schema}.{table_name}"},
        )
        return bool(result.scalar())

    def column_exists(
        self,
        table_name: str,
        column_name: str,
        schema: str = "public",
    ) -> bool:
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
            {
                "schema": schema,
                "table_name": table_name,
                "column_name": column_name,
            },
        )
        return bool(result.scalar())

    def count_superusers(self) -> int:
        result = self.db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM users
                WHERE issuperuser = TRUE
                  AND deletedat IS NULL
                """
            )
        )
        return int(result.scalar() or 0)

    def count_users(self) -> int:
        result = self.db.execute(text("SELECT COUNT(*) FROM users"))
        return int(result.scalar() or 0)

    def get_system_metadata(self) -> dict | None:
        if not self.table_exists("system_metadata"):
            return None

        result = self.db.execute(text("SELECT * FROM system_metadata WHERE id = 1"))
        row = result.mappings().first()
        return dict(row) if row else None