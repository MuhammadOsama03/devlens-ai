import json
import sqlite3
from pathlib import Path
from typing import Any


class AnalysisStore:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS analyses (
                    repository TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )

    def save(self, repository: str, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO analyses(repository, payload) VALUES(?, ?)
                ON CONFLICT(repository) DO UPDATE SET
                payload=excluded.payload, updated_at=CURRENT_TIMESTAMP""",
                (repository, encoded),
            )

    def get(self, repository: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM analyses WHERE repository = ?", (repository,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def list_repositories(self, limit: int = 100) -> list[str]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT repository FROM analyses ORDER BY updated_at DESC, repository LIMIT ?",
                (limit,),
            ).fetchall()
        return [row[0] for row in rows]

    def delete(self, repository: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM analyses WHERE repository = ?", (repository,)
            )
        return cursor.rowcount > 0

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)
