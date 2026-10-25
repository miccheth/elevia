"""Configurazione di Elevia.

Elevia conserva i propri dati in ``.elevia`` nella root del clone Git.
Se il comando viene eseguito fuori da un clone, usa ``~/.elevia``.
Non si usano variabili d'ambiente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

SYSTEM_DIR_NAME = ".elevia"
DATABASE_NAME = "elevia.db"


def find_git_root(start: Path | None = None) -> Path | None:
    """Risale le directory finché trova una root Git."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def default_system_dir() -> Path:
    """Cartella dati del clone corrente, oppure della home."""
    root = find_git_root()
    if root is None:
        return Path.home() / SYSTEM_DIR_NAME
    return root / SYSTEM_DIR_NAME


def default_db_path() -> Path:
    """Percorso predefinito del database."""
    return default_system_dir() / DATABASE_NAME


@dataclass(frozen=True)
class Settings:
    """Parametri di esecuzione del Core."""

    db_path: Path = field(default_factory=default_db_path)

    @classmethod
    def load(cls) -> "Settings":
        """Restituisce la configurazione predefinita."""
        return cls()

    def ensure_directories(self) -> None:
        """Crea la cartella di sistema che contiene il database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
