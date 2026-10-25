"""Helper per il Tag di sistema e la collocazione Untagged."""

from __future__ import annotations

import sqlite3

from app.core.exceptions import ConflictError, NotFoundError

from ..models.placement import Placement
from ..repositories.placement_repository import PlacementRepository
from ..repositories.tag_repository import TagRepository


def untagged_placement(
    tags: TagRepository,
    placements: PlacementRepository,
    conn: sqlite3.Connection | None = None,
) -> Placement:
    """Restituisce la radice del Tag di sistema Untagged (R46, R48)."""
    tag = tags.get_system(conn)
    if tag is None or tag.id is None:
        raise NotFoundError("Tag di sistema Untagged", "seed mancante")
    placement = placements.get_root_by_tag(tag.id, conn)
    if placement is None:
        raise ConflictError(
            "Il Tag di sistema Untagged non ha un Placement radice (R46)"
        )
    return placement
