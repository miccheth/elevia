"""Seed del Tag nativo Untagged e del suo Placement radice (R46)."""

from __future__ import annotations

from app.core.exceptions import ConflictError

from .database import Database

UNTAGGED_TAG_NAME = "Untagged"
UNTAGGED_DESCRIPTION = "Collocazione assegnata quando manca un Tag esplicito"


class Seeder:
    """Crea i dati di sistema mancanti, senza duplicarli."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def run(self) -> None:
        with self._db.session() as conn:
            rows = conn.execute("SELECT id, name, is_system FROM tag").fetchall()
            existing = next(
                (
                    row
                    for row in rows
                    if row["name"].casefold() == UNTAGGED_TAG_NAME.casefold()
                ),
                None,
            )
            if existing is None:
                cursor = conn.execute(
                    "INSERT INTO tag (name, description, is_system) VALUES (?, ?, 1)",
                    (UNTAGGED_TAG_NAME, UNTAGGED_DESCRIPTION),
                )
                tag_id = int(cursor.lastrowid or 0)
            else:
                if not existing["is_system"]:
                    raise ConflictError(
                        "Il nome 'Untagged' è riservato al Tag di sistema (R46)"
                    )
                tag_id = int(existing["id"])

            root = conn.execute(
                "SELECT id FROM placement WHERE tag_id = ? AND parent_id IS NULL",
                (tag_id,),
            ).fetchone()
            if root is None:
                conn.execute(
                    "INSERT INTO placement (tag_id, parent_id) VALUES (?, NULL)",
                    (tag_id,),
                )
