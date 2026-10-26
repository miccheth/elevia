"""Implementazione SQLite del repository degli ObjectAttribute."""

from __future__ import annotations

import sqlite3

from app.domains.file_organization.models.attribute_definition import ValueType
from app.domains.file_organization.models.object_attribute import ObjectAttribute
from app.domains.file_organization.repositories.object_attribute_repository import (
    ObjectAttributeRepository,
)
from app.infrastructure.database import Database

_SELECT = (
    "SELECT id, object_id, definition_id, namespace, key, value, value_type, created_at "
    "FROM object_attribute"
)


def _to_attribute(row: sqlite3.Row) -> ObjectAttribute:
    return ObjectAttribute(
        id=row["id"],
        object_id=row["object_id"],
        definition_id=row["definition_id"],
        namespace=row["namespace"],
        key=row["key"],
        value=row["value"],
        value_type=ValueType(row["value_type"]),
        created_at=row["created_at"],
    )


class SqliteObjectAttributeRepository(ObjectAttributeRepository):
    """Valori degli attributi sugli oggetti su SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def add(
        self, attribute: ObjectAttribute, conn: sqlite3.Connection | None = None
    ) -> ObjectAttribute:
        with self._db.session(conn) as cursor:
            result = cursor.execute(
                "INSERT INTO object_attribute "
                "(object_id, definition_id, namespace, key, value, value_type) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    attribute.object_id,
                    attribute.definition_id,
                    attribute.namespace,
                    attribute.key,
                    attribute.value,
                    str(attribute.value_type),
                ),
            )
            attribute_id = int(result.lastrowid or 0)
        stored = self._get_by_id(attribute_id, conn)
        if stored is None:  # pragma: no cover
            raise RuntimeError("Attributo appena inserito non trovato")
        return stored

    def get(
        self,
        object_id: int,
        namespace: str | None,
        key: str,
        conn: sqlite3.Connection | None = None,
    ) -> ObjectAttribute | None:
        wanted_key = key.casefold()
        with self._db.session(conn) as cursor:
            if namespace is None:
                rows = cursor.execute(
                    _SELECT + " WHERE object_id = ? AND namespace IS NULL",
                    (object_id,),
                ).fetchall()
            else:
                wanted_ns = namespace.casefold()
                rows = cursor.execute(
                    _SELECT + " WHERE object_id = ? AND namespace IS NOT NULL",
                    (object_id,),
                ).fetchall()
                rows = [r for r in rows if r["namespace"].casefold() == wanted_ns]
        for row in rows:
            if row["key"].casefold() == wanted_key:
                return _to_attribute(row)
        return None

    def get_by_definition(
        self, object_id: int, definition_id: int, conn: sqlite3.Connection | None = None
    ) -> ObjectAttribute | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                _SELECT + " WHERE object_id = ? AND definition_id = ?",
                (object_id, definition_id),
            ).fetchone()
        return _to_attribute(row) if row is not None else None

    def list_for_object(
        self, object_id: int, conn: sqlite3.Connection | None = None
    ) -> list[ObjectAttribute]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " WHERE object_id = ? ORDER BY namespace COLLATE NOCASE, key COLLATE NOCASE, id",
                (object_id,),
            ).fetchall()
        return [_to_attribute(row) for row in rows]

    def delete(
        self,
        object_id: int,
        namespace: str | None,
        key: str,
        conn: sqlite3.Connection | None = None,
    ) -> None:
        wanted_key = key.casefold()
        with self._db.session(conn) as cursor:
            if namespace is None:
                rows = cursor.execute(
                    "SELECT id FROM object_attribute WHERE object_id = ? AND namespace IS NULL",
                    (object_id,),
                ).fetchall()
            else:
                wanted_ns = namespace.casefold()
                all_rows = cursor.execute(
                    "SELECT id, namespace FROM object_attribute WHERE object_id = ? AND namespace IS NOT NULL",
                    (object_id,),
                ).fetchall()
                rows = [
                    {"id": r["id"]}
                    for r in all_rows
                    if r["namespace"].casefold() == wanted_ns
                ]
            for row in rows:
                attr = self._get_by_id(row["id"], conn)
                if attr is not None and attr.key.casefold() == wanted_key:
                    cursor.execute(
                        "DELETE FROM object_attribute WHERE id = ?", (row["id"],)
                    )
                    return

    def delete_by_definition(
        self, definition_id: int, conn: sqlite3.Connection | None = None
    ) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute(
                "DELETE FROM object_attribute WHERE definition_id = ?",
                (definition_id,),
            )

    def list_objects_with(
        self,
        namespace: str | None,
        key: str,
        value: str | None = None,
        conn: sqlite3.Connection | None = None,
    ) -> list[int]:
        wanted_key = key.casefold()
        with self._db.session(conn) as cursor:
            if namespace is None:
                rows = cursor.execute(
                    "SELECT object_id, key FROM object_attribute WHERE namespace IS NULL"
                ).fetchall()
            else:
                wanted_ns = namespace.casefold()
                all_rows = cursor.execute(
                    "SELECT object_id, namespace, key FROM object_attribute WHERE namespace IS NOT NULL"
                ).fetchall()
                rows = [
                    {"object_id": r["object_id"], "key": r["key"]}
                    for r in all_rows
                    if r["namespace"].casefold() == wanted_ns
                ]
        result: list[int] = []
        for row in rows:
            if row["key"].casefold() != wanted_key:
                continue
            if value is not None:
                attr = self.get(row["object_id"], namespace, key, conn)
                if attr is None or attr.value != value:
                    continue
            if row["object_id"] not in result:
                result.append(row["object_id"])
        return result

    def _get_by_id(
        self, attribute_id: int, conn: sqlite3.Connection | None = None
    ) -> ObjectAttribute | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                _SELECT + " WHERE id = ?", (attribute_id,)
            ).fetchone()
        return _to_attribute(row) if row is not None else None
