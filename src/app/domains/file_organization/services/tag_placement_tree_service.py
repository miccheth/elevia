"""Vista ad albero delle collocazioni (sola lettura)."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..repositories.placement_repository import PlacementRepository
from ..repositories.tag_repository import TagRepository
from ..repositories.tagging_repository import TaggingRepository
from ._placement_paths import PathIndex


@dataclass
class TreeNode:
    """Nodo dell'albero delle collocazioni."""

    placement_id: int
    tag_id: int
    tag_name: str
    path: str
    object_count: int = 0
    children: list["TreeNode"] = field(default_factory=list)


class TagPlacementTreeService:
    """Costruisce l'albero delle collocazioni, senza modificare nulla."""

    def __init__(
        self,
        tags: TagRepository,
        placements: PlacementRepository,
        taggings: TaggingRepository,
    ) -> None:
        self._tags = tags
        self._placements = placements
        self._taggings = taggings

    def get_tree(self) -> list[TreeNode]:
        """Restituisce le radici dell'albero, con figli ricorsivi."""
        index = PathIndex.build(
            self._placements.list_all(), self._tags.list_all()
        )
        counts: dict[int, int] = {}
        for tagging in self._taggings.list_all():
            counts[tagging.placement_id] = counts.get(tagging.placement_id, 0) + 1

        def build(placement_id: int, path: tuple[int, ...]) -> TreeNode | None:
            if placement_id in path:
                raise ValueError(f"Ciclo nei Placement su {placement_id}")
            placement = index.placements.get(placement_id)
            if placement is None:
                return None
            tag = index.tags.get(placement.tag_id)
            node = TreeNode(
                placement_id=placement_id,
                tag_id=placement.tag_id,
                tag_name=tag.name if tag is not None else f"#{placement.tag_id}",
                path=index.text_for(placement_id),
                object_count=counts.get(placement_id, 0),
            )
            child_ids = sorted(
                index.children.get(placement_id, []),
                key=lambda child_id: _child_name(index, child_id).casefold(),
            )
            for child_id in child_ids:
                child = build(child_id, path + (placement_id,))
                if child is not None:
                    node.children.append(child)
            return node

        roots = []
        for placement_id in sorted(
            index.children.get(None, []),
            key=lambda item: _child_name(index, item).casefold(),
        ):
            node = build(placement_id, ())
            if node is not None:
                roots.append(node)
        return roots


def _child_name(index: PathIndex, placement_id: int) -> str:
    placement = index.placements.get(placement_id)
    if placement is None:
        return ""
    tag = index.tags.get(placement.tag_id)
    return tag.name if tag is not None else ""
