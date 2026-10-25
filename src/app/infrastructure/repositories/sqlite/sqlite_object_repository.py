"""Implementazione SQLite del repository degli Object."""

from __future__ import annotations

import sqlite3

from app.domains.file_organization.models.object import Object, ObjectType
from app.domains.file_organization.repositories.object_repository import (
    ObjectRepository,
)
from app.infrastructure.database import Database


def _to_object(row: sqlite3.Row) -> Object:
    return Object(
        id=row["id"],
        name=row["name"],
        object_type=ObjectType(row["object_type"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class SqliteObjectRepository(ObjectRepository):
    """Object su SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def add(self, obj: Object, conn: sqlite3.Connection | None = None) -> Object:
        with self._db.session(conn) as cursor:
            result = cursor.execute(
                "INSERT INTO object (name, object_type) VALUES (?, ?)",
                (obj.name, str(obj.object_type)),
            )
            object_id = int(result.lastrowid or 0)
        stored = self.get(object_id, conn)
        if stored is None:  # pragma: no cover - difesa da stato incoerente
            raise RuntimeError("Object appena inserito non trovato")
        return stored

    def get(self, object_id: int, conn: sqlite3.Connection | None = None) -> Object | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                "SELECT id, name, object_type, created_at, updated_at "
                "FROM object WHERE id = ?",
                (object_id,),
            ).fetchone()
        return _to_object(row) if row is not None else None

    def list_all(self, conn: sqlite3.Connection | None = None) -> list[Object]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                "SELECT id, name, object_type, created_at, updated_at "
                "FROM object ORDER BY name COLLATE NOCASE, id"
            ).fetchall()
        return [_to_object(row) for row in rows]

    def set_name(
        self, object_id: int, name: str, conn: sqlite3.Connection | None = None
    ) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute("UPDATE object SET name = ? WHERE id = ?", (name, object_id))

    def delete(self, object_id: int, conn: sqlite3.Connection | None = None) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute("DELETE FROM object WHERE id = ?", (object_id,))

    def count(self, conn: sqlite3.Connection | None = None) -> int:
        with self._db.session(conn) as cursor:
            row = cursor.execute("SELECT COUNT(*) AS total FROM object").fetchone()
        return int(row["total"])
