"""Connessione SQLite e gestione delle transazioni di base."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class Database:
    """Wrapper su SQLite.

    Ogni connessione abilita le foreign key, come richiesto dallo schema.
    ``session`` commit-a le scritture se la connessione è stata aperta da lei,
    mentre una connessione passata dall'esterno resta sotto il controllo del
    chiamante (di norma il TransactionManager).
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        """Apre una connessione configurata."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def session(self, conn: sqlite3.Connection | None = None) -> Iterator[sqlite3.Connection]:
        """Restituisce la connessione condivisa oppure ne apre una nuova."""
        if conn is not None:
            yield conn
            return

        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
