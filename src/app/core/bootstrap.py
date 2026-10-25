"""Avvio del Core: migrazione, seed e composizione dei servizi."""

from __future__ import annotations

import logging
from pathlib import Path

from app.infrastructure.migrator import Migrator
from app.infrastructure.seed import Seeder
from config.settings import Settings

from .container import Container

logger = logging.getLogger(__name__)

_container: Container | None = None


def build_container(settings: Settings | None = None) -> Container:
    """Prepara il database e restituisce il container pronto all'uso."""
    active_settings = settings or Settings.load()
    active_settings.ensure_directories()

    container = Container(active_settings)
    Migrator(container.database).migrate()
    Seeder(container.database).run()
    _reconcile_files(container)
    return container


def get_container() -> Container:
    """Container condiviso dalla CLI, creato alla prima chiamata."""
    global _container
    if _container is None:
        _container = build_container()
    return _container


def reset_container(settings: Settings | None = None) -> Container:
    """Elimina il database e ricrea i dati di sistema."""
    global _container
    active_settings = settings or Settings.load()
    active_settings.ensure_directories()
    _container = None
    _remove_database_files(active_settings.db_path)
    _container = build_container(active_settings)
    return _container


def _remove_database_files(db_path: Path) -> None:
    """Rimuove il database e i file di supporto SQLite."""
    for path in (
        db_path,
        db_path.with_name(f"{db_path.name}-wal"),
        db_path.with_name(f"{db_path.name}-shm"),
        db_path.with_name(f"{db_path.name}-journal"),
    ):
        try:
            path.unlink()
        except FileNotFoundError:
            continue


def _reconcile_files(container: Container) -> None:
    """Aggiorna subito la disponibilità dei file registrati."""
    try:
        container.available_check().scan_once()
    except Exception:
        logger.exception("Riconciliazione iniziale dei file fallita")
