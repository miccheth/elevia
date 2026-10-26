"""Implementazione SQLite del repository delle AttributeDefinition."""

from __future__ import annotations

import sqlite3

from app.domains.file_organization.models.attribute_definition import (
    AttributeDefinition,
    ValueType,
)
from app.domains.file_organization.repositories.attribute_definition_repository import (
    AttributeDefinitionRepository,
)
from app.infrastructure.database import Database

_SELECT = (
    "SELECT id, namespace_id, key, value_type, allowed_values, description, created_at "
    "FROM attribute_definition"
)


def _to_definition(row: sqlite3.Row) -> AttributeDefinition:
    return AttributeDefinition(
        id=row["id"],
        namespace_id=row["namespace_id"],
        key=row["key"],
        value_type=ValueType(row["value_type"]),
        allowed_values=AttributeDefinition.allowed_values_from_json(row["allowed_values"]),
        description=row["description"],
        created_at=row["created_at"],
    )


class SqliteAttributeDefinitionRepository(AttributeDefinitionRepository):
    """Definizioni di attributi su SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def add(
        self, definition: AttributeDefinition, conn: sqlite3.Connection | None = None
    ) -> AttributeDefinition:
        with self._db.session(conn) as cursor:
            result = cursor.execute(
                "INSERT INTO attribute_definition "
                "(namespace_id, key, value_type, allowed_values, description) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    definition.namespace_id,
                    definition.key,
                    str(definition.value_type),
                    definition.allowed_values_json(),
                    definition.description,
                ),
            )
            definition_id = int(result.lastrowid or 0)
        stored = self.get(definition_id, conn)
        if stored is None:  # pragma: no cover
            raise RuntimeError("Definizione appena inserita non trovata")
        return stored

    def get(
        self, definition_id: int, conn: sqlite3.Connection | None = None
    ) -> AttributeDefinition | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                _SELECT + " WHERE id = ?", (definition_id,)
            ).fetchone()
        return _to_definition(row) if row is not None else None

    def get_by_key(
        self, namespace_id: int, key: str, conn: sqlite3.Connection | None = None
    ) -> AttributeDefinition | None:
        wanted = key.casefold()
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " WHERE namespace_id = ?", (namespace_id,)
            ).fetchall()
        for row in rows:
            if row["key"].casefold() == wanted:
                return _to_definition(row)
        return None

    def list_by_namespace(
        self, namespace_id: int, conn: sqlite3.Connection | None = None
    ) -> list[AttributeDefinition]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " WHERE namespace_id = ? ORDER BY key COLLATE NOCASE, id",
                (namespace_id,),
            ).fetchall()
        return [_to_definition(row) for row in rows]

    def delete(self, definition_id: int, conn: sqlite3.Connection | None = None) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute(
                "DELETE FROM attribute_definition WHERE id = ?", (definition_id,)
            )
