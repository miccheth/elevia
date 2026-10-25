"""Placement: collocazione contestuale di un Tag."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class Placement:
    """Nodo della gerarchia dei Tag.

    Un Placement ha un solo Tag e al massimo un padre (R13). ``parent_id``
    nullo indica una radice (R14).
    """

    tag_id: int
    id: int | None = None
    parent_id: int | None = None
    created_at: str | None = None
