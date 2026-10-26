"""AttributeNamespace: template di attributi (es. photo, work)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class AttributeNamespace:
    """Namespace che raggruppa definizioni di attributi.

    Il namespace è un template: definisce quali attributi esistono
    e di che tipo sono. Gli attributi possono anche esistere senza
    namespace (attributi liberi).
    """

    name: str
    description: str | None = None
    id: int | None = None
    created_at: str | None = None
