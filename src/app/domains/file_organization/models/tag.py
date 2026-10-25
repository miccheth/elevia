"""Tag: identità stabile di un concetto."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class Tag:
    """Tag del vocabolario controllato.

    Il nome è univoco e case insensitive (R8). Un Tag può esistere senza
    Placement (R9). Il Tag di sistema non si rinomina né si elimina (R47).
    """

    name: str
    id: int | None = None
    description: str | None = None
    is_system: bool = False
    created_at: str | None = None
    updated_at: str | None = None
