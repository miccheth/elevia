"""Utility temporali condivise da modelli e servizi."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> str:
    """Timestamp ISO 8601 in UTC, formato usato dallo schema."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def from_timestamp(value: float) -> str:
    """Converte un timestamp POSIX in ISO 8601 UTC."""
    return datetime.fromtimestamp(value, tz=UTC).isoformat(timespec="seconds")
