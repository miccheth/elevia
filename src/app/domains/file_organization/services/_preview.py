"""Verifica dei dati di un'anteprima."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import ConflictError, PreviewRequiredError
from app.core.transaction_manager import PlanPreview


def require_preview(
    preview: PlanPreview | None, operation: str, **expected: Any
) -> PlanPreview:
    """Controlla che l'anteprima esista, sia del tipo giusto e senza conflitti."""
    if preview is None:
        raise PreviewRequiredError(
            f"L'operazione '{operation}' richiede un'anteprima (R36)"
        )
    if preview.operation != operation:
        raise PreviewRequiredError(
            f"Anteprima non valida: attesa '{operation}', ricevuta '{preview.operation}'"
        )
    for key, value in expected.items():
        if preview.details.get(key) != value:
            raise PreviewRequiredError(
                f"Anteprima non coerente: {key} diverso da quello confermato (R39)"
            )
    if preview.conflicts:
        raise ConflictError(
            "L'anteprima contiene conflitti: " + "; ".join(preview.conflicts)
        )
    return preview
