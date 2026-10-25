"""Implementazione SQLite del repository dei Tagging."""

from __future__ import annotations

import sqlite3

from app.domains.file_organization.models.tagging import Tagging
from app.domains.file_organization.repositories.tagging_repository import (
    TaggingRepository,
)
from app.infrastructure.database import Database

_SELECT = (
    "SELECT id, object_id, placement_id, created_at FROM tagging"
)


def _to_tagging(row: sqlite3.Row) -> Tagging:
    return Tagging(
        id=row["id"],
        object_id=row["object_id"],
        placement_id=row["placement_id"],
        created_at=row["created_at"],
    )


class SqliteTaggingRepository(TaggingRepository):
    """Tagging su SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def add(self, tagging: Tagging, conn: sqlite3.Connection | None = None) -> Tagging:
        with self._db.session(conn) as cursor:
            result = cursor.execute(
                "INSERT INTO tagging (object_id, placement_id) VALUES (?, ?)",
                (tagging.object_id, tagging.placement_id),
            )
            tagging_id = int(result.lastrowid or 0)
        with self._db.session(conn) as cursor:
            row = cursor.execute(_SELECT + " WHERE id = ?", (tagging_id,)).fetchone()
        if row is None:  # pragma: no cover
            raise RuntimeError("Tagging appena inserito non trovato")
        return _to_tagging(row)

    def get(
        self, object_id: int, placement_id: int, conn: sqlite3.Connection | None = None
    ) -> Tagging | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                _SELECT + " WHERE object_id = ? AND placement_id = ?",
                (object_id, placement_id),
            ).fetchone()
        return _to_tagging(row) if row is not None else None

    def list_by_object(
        self, object_id: int, conn: sqlite3.Connection | None = None
    ) -> list[Tagging]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " WHERE object_id = ? ORDER BY id", (object_id,)
            ).fetchall()
        return [_to_tagging(row) for row in rows]

    def list_by_placement(
        self, placement_id: int, conn: sqlite3.Connection | None = None
    ) -> list[Tagging]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " WHERE placement_id = ? ORDER BY id", (placement_id,)
            ).fetchall()
        return [_to_tagging(row) for row in rows]

    def list_all(self, conn: sqlite3.Connection | None = None) -> list[Tagging]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(_SELECT + " ORDER BY id").fetchall()
        return [_to_tagging(row) for row in rows]

    def delete(self, tagging_id: int, conn: sqlite3.Connection | None = None) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute("DELETE FROM tagging WHERE id = ?", (tagging_id,))

    def count_by_object(
        self, object_id: int, conn: sqlite3.Connection | None = None
    ) -> int:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                "SELECT COUNT(*) AS total FROM tagging WHERE object_id = ?",
                (object_id,),
            ).fetchone()
        return int(row["total"])

    def count_by_placement(
        self, placement_id: int, conn: sqlite3.Connection | None = None
    ) -> int:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                "SELECT COUNT(*) AS total FROM tagging WHERE placement_id = ?",
                (placement_id,),
            ).fetchone()
        return int(row["total"])
