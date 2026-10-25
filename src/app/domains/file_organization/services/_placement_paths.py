"""Calcolo dei percorsi delle collocazioni.

Il percorso è un dato derivato: viene ricostruito risalendo i ``parent_id`` e
non viene memorizzato nel database.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models.placement import Placement
from ..models.tag import Tag


@dataclass(frozen=True)
class PathIndex:
    """Indice dei percorsi dei Placement."""

    placements: dict[int, Placement]
    tags: dict[int, Tag]
    children: dict[int | None, list[int]]

    @classmethod
    def build(cls, placements: list[Placement], tags: list[Tag]) -> "PathIndex":
        placement_map = {p.id: p for p in placements if p.id is not None}
        tag_map = {t.id: t for t in tags if t.id is not None}
        children: dict[int | None, list[int]] = {}
        for placement in placements:
            if placement.id is None:
                continue
            children.setdefault(placement.parent_id, []).append(placement.id)
        return cls(placement_map, tag_map, children)

    def names_for(self, placement_id: int) -> tuple[str, ...]:
        """Nomi dei Tag dalla radice al nodo indicato."""
        names: list[str] = []
        seen: set[int] = set()
        current: int | None = placement_id
        while current is not None:
            if current in seen:
                raise ValueError(f"Ciclo nei Placement a partire da {placement_id}")
            seen.add(current)
            placement = self.placements.get(current)
            if placement is None:
                break
            tag = self.tags.get(placement.tag_id)
            names.append(tag.name if tag is not None else f"#{placement.tag_id}")
            current = placement.parent_id
        names.reverse()
        return tuple(names)

    def text_for(self, placement_id: int) -> str:
        """Percorso leggibile, separato da ``.``."""
        return ".".join(self.names_for(placement_id))

    def descendant_ids(self, placement_id: int) -> set[int]:
        """Tutti i discendenti del Placement, escluso il nodo stesso."""
        found: set[int] = set()
        stack = list(self.children.get(placement_id, []))
        while stack:
            current = stack.pop()
            if current in found:
                continue
            found.add(current)
            stack.extend(self.children.get(current, []))
        return found

    def subtree_ids(self, placement_id: int) -> set[int]:
        """Il Placement e tutti i suoi discendenti."""
        return {placement_id} | self.descendant_ids(placement_id)

    def path_exists(self, names: tuple[str, ...]) -> bool:
        """True se esiste un Placement con quel percorso esatto."""
        wanted = tuple(name.casefold() for name in names)
        for placement_id in self.placements:
            path = tuple(name.casefold() for name in self.names_for(placement_id))
            if path == wanted:
                return True
        return False
