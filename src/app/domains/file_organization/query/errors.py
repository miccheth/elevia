"""Errori della sintassi di ricerca."""

from __future__ import annotations

from app.core.exceptions import EleviaError


class QueryError(EleviaError):
    """Errore di una query."""


class QuerySyntaxError(QueryError):
    """Espressione non conforme alla grammatica."""

    def __init__(self, message: str, position: int | None = None) -> None:
        suffix = f" (posizione {position})" if position is not None else ""
        super().__init__(f"Sintassi non valida: {message}{suffix}")
        self.position = position


class UnknownTagError(QueryError):
    """La query cita un Tag che non esiste."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Tag inesistente: {name}")
        self.name = name
