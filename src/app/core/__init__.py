"""Core di Elevia: eccezioni, transazioni e composizione."""

from .exceptions import (
    ConflictError,
    CycleError,
    DuplicateError,
    EleviaError,
    NotFoundError,
    PreviewRequiredError,
    PreviewStaleError,
    RepositoryError,
    ValidationError,
)
from .transaction_manager import PlanPreview, TransactionManager

__all__ = [
    "ConflictError",
    "CycleError",
    "DuplicateError",
    "EleviaError",
    "NotFoundError",
    "PlanPreview",
    "PreviewRequiredError",
    "PreviewStaleError",
    "RepositoryError",
    "TransactionManager",
    "ValidationError",
]
