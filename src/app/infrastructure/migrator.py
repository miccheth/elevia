"""Applicazione dello schema SQL al database."""

from __future__ import annotations

from pathlib import Path

from .database import Database

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class Migrator:
    """Esegue lo schema idempotente (tabelle, indici, trigger)."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def migrate(self) -> None:
        ddl = SCHEMA_PATH.read_text(encoding="utf-8")
        with self._db.session() as conn:
            conn.executescript(ddl)
