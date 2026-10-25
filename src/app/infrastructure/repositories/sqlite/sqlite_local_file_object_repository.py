"""Implementazione SQLite del repository dei LocalFileObject."""

from __future__ import annotations

import sqlite3

from app.domains.file_organization.models.local_file_object import LocalFileObject
from app.domains.file_organization.models.object import ObjectType
from app.domains.file_organization.repositories.local_file_object_repository import (
    LocalFileObjectRepository,
)
from app.infrastructure.database import Database

_SELECT = """
    SELECT o.id, o.name, o.object_type, o.created_at, o.updated_at,
           f.is_available, f.file_path, f.normalized_path, f.file_size,
           f.modified_at, f.file_extension
    FROM object AS o
    JOIN local_file_object AS f ON f.object_id = o.id
"""


def _to_local_file(row: sqlite3.Row) -> LocalFileObject:
    return LocalFileObject(
        id=row["id"],
        name=row["name"],
        object_type=ObjectType(row["object_type"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        is_available=bool(row["is_available"]),
        file_path=row["file_path"],
        normalized_path=row["normalized_path"],
        file_size=row["file_size"],
        modified_at=row["modified_at"],
        file_extension=row["file_extension"],
    )


class SqliteLocalFileObjectRepository(LocalFileObjectRepository):
    """Dettagli dei file locali su SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def add(
        self, obj: LocalFileObject, conn: sqlite3.Connection | None = None
    ) -> LocalFileObject:
        if obj.id is None:
            raise ValueError("LocalFileObject senza object_id")
        with self._db.session(conn) as cursor:
            cursor.execute(
                """
                INSERT INTO local_file_object (
                    object_id, is_available, file_path, normalized_path,
                    file_size, modified_at, file_extension
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    obj.id,
                    int(obj.is_available),
                    obj.file_path,
                    obj.normalized_path,
                    obj.file_size,
                    obj.modified_at,
                    obj.file_extension,
                ),
            )
        stored = self.get(obj.id, conn)
        if stored is None:  # pragma: no cover - difesa da stato incoerente
            raise RuntimeError("LocalFileObject appena inserito non trovato")
        return stored

    def get(
        self, object_id: int, conn: sqlite3.Connection | None = None
    ) -> LocalFileObject | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(_SELECT + " WHERE o.id = ?", (object_id,)).fetchone()
        return _to_local_file(row) if row is not None else None

    def list_all(self, conn: sqlite3.Connection | None = None) -> list[LocalFileObject]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " ORDER BY o.name COLLATE NOCASE, o.id"
            ).fetchall()
        return [_to_local_file(row) for row in rows]

    def save(
        self, obj: LocalFileObject, conn: sqlite3.Connection | None = None
    ) -> LocalFileObject:
        if obj.id is None:
            raise ValueError("LocalFileObject senza object_id")
        with self._db.session(conn) as cursor:
            cursor.execute(
                """
                UPDATE local_file_object
                SET is_available = ?, file_path = ?, normalized_path = ?,
                    file_size = ?, modified_at = ?, file_extension = ?
                WHERE object_id = ?
                """,
                (
                    int(obj.is_available),
                    obj.file_path,
                    obj.normalized_path,
                    obj.file_size,
                    obj.modified_at,
                    obj.file_extension,
                    obj.id,
                ),
            )
        stored = self.get(obj.id, conn)
        if stored is None:  # pragma: no cover
            raise RuntimeError("LocalFileObject aggiornato non trovato")
        return stored

    def find_by_normalized_path(
        self, normalized_path: str, conn: sqlite3.Connection | None = None
    ) -> LocalFileObject | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                _SELECT + " WHERE f.normalized_path = ?", (normalized_path,)
            ).fetchone()
        return _to_local_file(row) if row is not None else None
