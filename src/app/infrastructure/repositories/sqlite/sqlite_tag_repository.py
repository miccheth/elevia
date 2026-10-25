"""Implementazione SQLite del repository dei Tag."""

from __future__ import annotations

import sqlite3

from app.domains.file_organization.models.tag import Tag
from app.domains.file_organization.repositories.tag_repository import TagRepository
from app.infrastructure.database import Database

_SELECT = "SELECT id, name, description, is_system, created_at, updated_at FROM tag"


def _to_tag(row: sqlite3.Row) -> Tag:
    return Tag(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        is_system=bool(row["is_system"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class SqliteTagRepository(TagRepository):
    """Tag su SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def add(self, tag: Tag, conn: sqlite3.Connection | None = None) -> Tag:
        with self._db.session(conn) as cursor:
            result = cursor.execute(
                "INSERT INTO tag (name, description, is_system) VALUES (?, ?, ?)",
                (tag.name, tag.description, int(tag.is_system)),
            )
            tag_id = int(result.lastrowid or 0)
        stored = self.get(tag_id, conn)
        if stored is None:  # pragma: no cover
            raise RuntimeError("Tag appena inserito non trovato")
        return stored

    def get(self, tag_id: int, conn: sqlite3.Connection | None = None) -> Tag | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(_SELECT + " WHERE id = ?", (tag_id,)).fetchone()
        return _to_tag(row) if row is not None else None

    def get_by_name(self, name: str, conn: sqlite3.Connection | None = None) -> Tag | None:
        # Confronto in Python con casefold: SQLite NOCASE non copre le lettere accentate.
        wanted = name.casefold()
        with self._db.session(conn) as cursor:
            rows = cursor.execute(_SELECT).fetchall()
        for row in rows:
            if row["name"].casefold() == wanted:
                return _to_tag(row)
        return None

    def get_system(self, conn: sqlite3.Connection | None = None) -> Tag | None:
        with self._db.session(conn) as cursor:
            row = cursor.execute(
                _SELECT + " WHERE is_system = 1 ORDER BY id LIMIT 1"
            ).fetchone()
        return _to_tag(row) if row is not None else None

    def list_all(self, conn: sqlite3.Connection | None = None) -> list[Tag]:
        with self._db.session(conn) as cursor:
            rows = cursor.execute(
                _SELECT + " ORDER BY name COLLATE NOCASE, id"
            ).fetchall()
        return [_to_tag(row) for row in rows]

    def save(self, tag: Tag, conn: sqlite3.Connection | None = None) -> Tag:
        if tag.id is None:
            raise ValueError("Tag senza id")
        with self._db.session(conn) as cursor:
            cursor.execute(
                "UPDATE tag SET name = ?, description = ? WHERE id = ?",
                (tag.name, tag.description, tag.id),
            )
        stored = self.get(tag.id, conn)
        if stored is None:  # pragma: no cover
            raise RuntimeError("Tag aggiornato non trovato")
        return stored

    def delete(self, tag_id: int, conn: sqlite3.Connection | None = None) -> None:
        with self._db.session(conn) as cursor:
            cursor.execute("DELETE FROM tag WHERE id = ?", (tag_id,))

    def count(self, conn: sqlite3.Connection | None = None) -> int:
        with self._db.session(conn) as cursor:
            row = cursor.execute("SELECT COUNT(*) AS total FROM tag").fetchone()
        return int(row["total"])
