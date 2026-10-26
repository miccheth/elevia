"""Implementazione SQLite del repository degli AttributeNamespace."""

from __future__ import annotations

import sqlite3

from app.domains.file_organization.models.attribute_namespace import AttributeNamespace
from app.domains.file_organization.repositories.attribute_namespace_repository import (
    AttributeNamespaceRepository,
)
from app.infrastructure.database import Database

_SELECT = "SELECT id, name, description, created_at FROM attribute_namespace"


def _to_namespace(row: sqlite3.Row) -> AttributeNamespace:
    return AttributeNamespace(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        created_at=row["created_at"],
    )


class SqliteAttributeNamespaceRepository(AttributeNamespaceRepository):
    """Namespace di attributi su SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def add(
        self, namespace: AttributeNamespace, conn: sqlite3.Connection | None = None
    ) -> AttributeNamespace:
        with self._db.session(conn) as cursor:
            result = cursor.execute(
                "INSERT INTO attribute_namespace (name, description) VALUES (?, ?)",
                (namespace.name, namespace.description),
            )
            namespace_id = int(result.lastrowid or 0)
        stored = self.get(namespace_id, conn)
        if stored is None:  # pragma: no cover
            raise RuntimeError("Namespace appena inserito non trovato")
        return stored

    def get(
        self, namespace_id: int, conn: sqlite3.Connection | None = None
    ) -> AttributeNamespace | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(_SELECT + " WHERE id = ?", (namespace_id,)).fetchone()
        return _to_namespace(row) if row is not None else None

    def get_by_name(
        self, name: str, conn: sqlite3.Connection | None = None
    ) -> AttributeNamespace | None:
        wanted = name.casefold()
        with self._db.session(conn) as cursor:
            rows = cursor.execute(_SELECT).fetchall()
        for row in rows:
            if row["name"].casefold() == wanted:
                return _to_namespace(row)
        return None

    def list_all(
        self, conn: sqlite3.Connection | None = None
    ) -> list[AttributeNamespace]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " ORDER BY name COLLATE NOCASE, id"
            ).fetchall()
        return [_to_namespace(row) for row in rows]

    def delete(self, namespace_id: int, conn: sqlite3.Connection | None = None) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute(
                "DELETE FROM attribute_namespace WHERE id = ?", (namespace_id,)
            )
