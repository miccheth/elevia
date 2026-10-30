"""Anteprima dell'impatto delle modifiche strutturali (R36-R39)."""

from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundError
from app.core.transaction_manager import PlanPreview, TransactionManager

from ..models.placement import Placement
from ..models.tag import Tag
from ..repositories.placement_repository import PlacementRepository
from ..repositories.tag_repository import TagRepository
from ..repositories.tagging_repository import TaggingRepository
from ._placement_paths import PathIndex


class PreviewService:
    """Calcola impatto e conflitti senza modificare alcun dato (R37)."""

    def __init__(
        self,
        transaction_manager: TransactionManager,
        tags: TagRepository,
        placements: PlacementRepository,
        taggings: TaggingRepository,
    ) -> None:
        self._tm = transaction_manager
        self._tags = tags
        self._placements = placements
        self._taggings = taggings

    def preview_move_placement(
        self, placement_id: int, new_parent_id: int | None
    ) -> PlanPreview:
        """Anteprima dello spostamento di un Placement."""
        fingerprint = self._tm.fingerprint()
        placement = self._require_placement(placement_id)
        if new_parent_id is not None:
            self._require_placement(new_parent_id)

        index = self._load_index()
        conflicts: list[str] = []
        subtree = index.subtree_ids(placement_id)
        cycle = _tag_cycle_conflict(
            index,
            moved_placement_id=placement_id,
            new_parent_id=new_parent_id,
        )
        if cycle is not None:
            conflicts.append(cycle)
        if new_parent_id is not None and new_parent_id in subtree:
            conflicts.append(
                "Destinazione interna al ramo: vietato spostare un nodo dentro sé stesso o un discendente (R19, R30)"
            )

        tag_id = placement.tag_id
        if index.tags[tag_id].is_system:
            conflicts.append(
                "Il Placement del Tag di sistema non può essere spostato (R46)"
            )
        if new_parent_id is None:
            other_root = self._placements.get_root_by_tag(tag_id)
            if other_root is not None and other_root.id != placement_id:
                conflicts.append(
                    f"Esiste già un Placement radice per il Tag (id {other_root.id}) (R15)"
                )
        else:
            siblings = [
                item
                for item in self._placements.list_children(new_parent_id)
                if item.tag_id == tag_id and item.id != placement_id
            ]
            if siblings:
                conflicts.append(
                    "Il Tag è già presente sotto la destinazione "
                    f"(Placement id {siblings[0].id}) (R16, R21)"
                )

        old_names = index.names_for(placement_id)
        new_names = (
            index.names_for(new_parent_id) if new_parent_id is not None else ()
        ) + (index.tags[tag_id].name,)
        impacts = []
        for node_id in sorted(subtree):
            relative = index.names_for(node_id)[len(old_names) :]
            impacts.append(
                {
                    "placement_id": node_id,
                    "percorso_attuale": index.text_for(node_id),
                    "percorso_nuovo": ".".join(new_names + relative),
                    "assegnazioni": self._taggings.count_by_placement(node_id),
                }
            )

        return self._build(
            fingerprint=fingerprint,
            operation="move_placement",
            summary=(
                f"Spostamento del Placement {placement_id}: "
                f"{index.text_for(placement_id)} -> "
                f"{'.'.join(new_names)}"
            ),
            details={"placement_id": placement_id, "new_parent_id": new_parent_id},
            impacts=impacts,
            conflicts=conflicts,
        )

    def preview_delete_placement(self, placement_id: int) -> PlanPreview:
        """Anteprima dell'eliminazione di un Placement."""
        fingerprint = self._tm.fingerprint()
        self._require_placement(placement_id)
        index = self._load_index()
        conflicts: list[str] = []
        placement = index.placements.get(placement_id)
        tag = index.tags.get(placement.tag_id) if placement is not None else None
        if (
            tag is not None
            and tag.is_system
            and placement is not None
            and placement.parent_id is None
        ):
            conflicts.append(
                "Il Placement radice del Tag di sistema non può essere eliminato (R46)"
            )
        children = self._placements.list_children(placement_id)
        assignments = self._taggings.count_by_placement(placement_id)
        if children:
            conflicts.append(
                f"Il Placement ha {len(children)} figli: eliminazione bloccata (R20)"
            )
        if assignments:
            conflicts.append(
                f"Il Placement ha {assignments} assegnazioni: eliminazione bloccata (R20)"
            )

        impacts = [
            {
                "placement_id": placement_id,
                "percorso": index.text_for(placement_id),
                "assegnazioni": assignments,
                "figli": len(children),
            }
        ]
        return self._build(
            fingerprint=fingerprint,
            operation="delete_placement",
            summary=f"Eliminazione del Placement {placement_id} ({index.text_for(placement_id)})",
            details={"placement_id": placement_id},
            impacts=impacts,
            conflicts=conflicts,
        )

    def preview_delete_tag(self, tag_id: int) -> PlanPreview:
        """Anteprima dell'eliminazione di un Tag."""
        fingerprint = self._tm.fingerprint()
        tag = self._require_tag(tag_id)
        index = self._load_index()
        placements = self._placements.list_by_tag(tag_id)
        conflicts: list[str] = []
        if tag.is_system:
            conflicts.append("Il Tag di sistema non può essere eliminato (R47)")
        if placements:
            conflicts.append(
                f"Il Tag ha {len(placements)} Placement non risolti (R11)"
            )
        impacts = [
            {
                "placement_id": item.id,
                "percorso": index.text_for(item.id) if item.id is not None else "",
                "assegnazioni": (
                    self._taggings.count_by_placement(item.id)
                    if item.id is not None
                    else 0
                ),
            }
            for item in placements
        ]
        return self._build(
            fingerprint=fingerprint,
            operation="delete_tag",
            summary=f"Eliminazione del Tag '{tag.name}'",
            details={"tag_id": tag_id},
            impacts=impacts,
            conflicts=conflicts,
        )

    def preview_merge_tags(self, source_id: int, target_id: int) -> PlanPreview:
        """Anteprima della fusione esplicita tra due Tag (R33, R47)."""
        fingerprint = self._tm.fingerprint()
        source = self._require_tag(source_id)
        target = self._require_tag(target_id)
        if source_id == target_id:
            raise ValueError("Un Tag non può essere fuso con sé stesso")

        index = self._load_index()
        conflicts: list[str] = []
        if source.is_system:
            conflicts.append("Il Tag di sistema non può essere sorgente di fusione (R47)")
        if target.is_system:
            conflicts.append("Il Tag di sistema non può essere destinazione di fusione")

        impacts = []
        for placement in self._placements.list_by_tag(source_id):
            if placement.id is None:
                continue
            conflict = self._merge_conflict(placement, target_id)
            if conflict is not None:
                conflicts.append(conflict)
            parent_names = (
                index.names_for(placement.parent_id)
                if placement.parent_id is not None
                else ()
            )
            impacts.append(
                {
                    "placement_id": placement.id,
                    "percorso_attuale": index.text_for(placement.id),
                    "percorso_nuovo": ".".join(parent_names + (target.name,)),
                    "assegnazioni": self._taggings.count_by_placement(placement.id),
                }
            )

        cycle = _tag_cycle_conflict(
            index, tag_replacements={source_id: target_id}
        )
        if cycle is not None:
            conflicts.append(cycle)

        return self._build(
            fingerprint=fingerprint,
            operation="merge_tags",
            summary=f"Fusione del Tag '{source.name}' in '{target.name}'",
            details={"source_id": source_id, "target_id": target_id},
            impacts=impacts,
            conflicts=conflicts,
        )

    # --- Supporto -----------------------------------------------------------

    def _merge_conflict(self, placement: Placement, target_id: int) -> str | None:
        if placement.parent_id is None:
            root = self._placements.get_root_by_tag(target_id)
            if root is not None:
                return (
                    "La destinazione ha già un Placement radice: conflitto da risolvere esplicitamente (R21, R33)"
                )
            return None
        siblings = [
            item
            for item in self._placements.list_children(placement.parent_id)
            if item.tag_id == target_id
        ]
        if siblings:
            return (
                f"Il Tag di destinazione è già presente sotto il padre del Placement {placement.id} "
                f"(Placement id {siblings[0].id}): conflitto esplicito (R21, R33)"
            )
        return None

    def _build(
        self,
        *,
        fingerprint: str,
        operation: str,
        summary: str,
        details: dict[str, object],
        impacts: list[dict[str, object]],
        conflicts: list[str],
    ) -> PlanPreview:
        return PlanPreview(
            token=uuid.uuid4().hex,
            operation=operation,
            fingerprint=fingerprint,
            summary=summary,
            details=details,
            impacts=tuple(impacts),
            conflicts=tuple(conflicts),
        )

    def _require_placement(self, placement_id: int) -> Placement:
        placement = self._placements.get(placement_id)
        if placement is None:
            raise NotFoundError("Placement", placement_id)
        return placement

    def _require_tag(self, tag_id: int) -> Tag:
        tag = self._tags.get(tag_id)
        if tag is None:
            raise NotFoundError("Tag", tag_id)
        return tag

    def _load_index(self) -> PathIndex:
        return PathIndex.build(self._placements.list_all(), self._tags.list_all())


def _tag_cycle_conflict(
    index: PathIndex,
    *,
    moved_placement_id: int | None = None,
    new_parent_id: int | None = None,
    tag_replacements: dict[int, int] | None = None,
) -> str | None:
    """Controlla in memoria se la modifica crea un ciclo tra identità di Tag."""
    replacements = tag_replacements or {}
    edges: dict[int, set[int]] = {}
    for current_id, placement in index.placements.items():
        parent_id = (
            new_parent_id
            if moved_placement_id is not None and current_id == moved_placement_id
            else placement.parent_id
        )
        if parent_id is None:
            continue
        parent = index.placements.get(parent_id)
        if parent is None:
            continue
        child_tag = replacements.get(placement.tag_id, placement.tag_id)
        parent_tag = replacements.get(parent.tag_id, parent.tag_id)
        if parent_tag == child_tag and (
            current_id == moved_placement_id or replacements
        ):
            return "Ciclo tra identità dei Tag: A -> A (R32)"
        edges.setdefault(parent_tag, set()).add(child_tag)

    visiting: set[int] = set()
    visited: set[int] = set()
    stack: list[int] = []

    def visit(tag_id: int) -> str | None:
        if tag_id in visited:
            return None
        if tag_id in visiting:
            cycle = stack[stack.index(tag_id) :] + [tag_id]
            labels = [
                index.tags[item].name if item in index.tags else str(item)
                for item in cycle
            ]
            return "Ciclo tra identità dei Tag: " + " -> ".join(labels) + " (R31, R32)"
        visiting.add(tag_id)
        stack.append(tag_id)
        for child in edges.get(tag_id, set()):
            found = visit(child)
            if found is not None:
                return found
        stack.pop()
        visiting.remove(tag_id)
        visited.add(tag_id)
        return None

    for tag_id in list(edges):
        conflict = visit(tag_id)
        if conflict is not None:
            return conflict
    return None
