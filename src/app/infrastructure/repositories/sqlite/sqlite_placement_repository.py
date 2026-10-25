"""Implementazione SQLite del repository dei Placement."""

from __future__ import annotations

import sqlite3

from app.domains.file_organization.models.placement import Placement
from app.domains.file_organization.repositories.placement_repository import (
    PlacementRepository,
)
from app.infrastructure.database import Database

_SELECT = "SELECT id, tag_id, parent_id, created_at FROM placement"


def _to_placement(row: sqlite3.Row) -> Placement:
    return Placement(
        id=row["id"],
        tag_id=row["tag_id"],
        parent_id=row["parent_id"],
        created_at=row["created_at"],
    )


class SqlitePlacementRepository(PlacementRepository):
    """Placement su SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def add(
        self, placement: Placement, conn: sqlite3.Connection | None = None
    ) -> Placement:
        with self._db.session(conn) as cursor:
            result = cursor.execute(
                "INSERT INTO placement (tag_id, parent_id) VALUES (?, ?)",
                (placement.tag_id, placement.parent_id),
            )
            placement_id = int(result.lastrowid or 0)
        stored = self.get(placement_id, conn)
        if stored is None:  # pragma: no cover
            raise RuntimeError("Placement appena inserito non trovato")
        return stored

    def get(
        self, placement_id: int, conn: sqlite3.Connection | None = None
    ) -> Placement | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(_SELECT + " WHERE id = ?", (placement_id,)).fetchone()
        return _to_placement(row) if row is not None else None

    def list_all(self, conn: sqlite3.Connection | None = None) -> list[Placement]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(_SELECT + " ORDER BY id").fetchall()
        return [_to_placement(row) for row in rows]

    def list_by_tag(
        self, tag_id: int, conn: sqlite3.Connection | None = None
    ) -> list[Placement]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " WHERE tag_id = ? ORDER BY id", (tag_id,)
            ).fetchall()
        return [_to_placement(row) for row in rows]

    def list_children(
        self, parent_id: int | None, conn: sqlite3.Connection | None = None
    ) -> list[Placement]:
        with self._db.session(conn) as cursor:
            if parent_id is None:
                rows = cursor.execute(
                    _SELECT + " WHERE parent_id IS NULL ORDER BY id"
                ).fetchall()
            else:
                rows = cursor.execute(
                    _SELECT + " WHERE parent_id = ? ORDER BY id", (parent_id,)
                ).fetchall()
        return [_to_placement(row) for row in rows]

    def get_root_by_tag(
        self, tag_id: int, conn: sqlite3.Connection | None = None
    ) -> Placement | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                _SELECT + " WHERE tag_id = ? AND parent_id IS NULL", (tag_id,)
            ).fetchone()
        return _to_placement(row) if row is not None else None

    def set_parent(
        self,
        placement_id: int,
        parent_id: int | None,
        conn: sqlite3.Connection | None = None,
    ) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute(
                "UPDATE placement SET parent_id = ? WHERE id = ?",
                (parent_id, placement_id),
            )

    def set_tag(
        self, placement_id: int, tag_id: int, conn: sqlite3.Connection | None = None
    ) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute(
                "UPDATE placement SET tag_id = ? WHERE id = ?",
                (tag_id, placement_id),
            )

    def delete(self, placement_id: int, conn: sqlite3.Connection | None = None) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute("DELETE FROM placement WHERE id = ?", (placement_id,))

    def count(self, conn: sqlite3.Connection | None = None) -> int:
        with self._db.session(conn) as cursor:
            row = cursor.execute("SELECT COUNT(*) AS total FROM placement").fetchone()
        return int(row["total"])
