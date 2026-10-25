"""Eccezioni del Core.

Ogni errore previsto dal dominio espone un messaggio leggibile: la CLI non
deve mostrare un traceback per una regola di business violata.
"""

from __future__ import annotations


class EleviaError(Exception):
    """Radice di tutti gli errori applicativi."""


class ValidationError(EleviaError):
    """Input non valido prima di toccare il database."""


class NotFoundError(EleviaError):
    """Entità richiesta inesistente."""

    def __init__(self, entity: str, identifier: object) -> None:
        super().__init__(f"{entity} non trovato: {identifier}")
        self.entity = entity
        self.identifier = identifier


class ConflictError(EleviaError):
    """Operazione rifiutata da un vincolo o da una regola di business."""


class DuplicateError(ConflictError):
    """Elemento già presente dove l'unicità è richiesta."""


class CycleError(ConflictError):
    """La modifica introdurrebbe un ciclo."""


class PreviewRequiredError(EleviaError):
    """L'operazione strutturale richiede un'anteprima confermata."""


class PreviewStaleError(EleviaError):
    """Lo stato è cambiato dopo l'anteprima: serve una nuova anteprima."""


class RepositoryError(EleviaError):
    """Errore di accesso al database."""
