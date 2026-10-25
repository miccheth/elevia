"""Tagging: collegamento univoco Object / Placement."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class Tagging:
    """Assegnazione di un Object a un Placement.

    La coppia (object_id, placement_id) è univoca (R22). Non esistono
    assegnazioni globali prive di collocazione (R23).
    """

    object_id: int
    placement_id: int
    id: int | None = None
    created_at: str | None = None
