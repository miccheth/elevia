"""Servizio del vocabolario controllato dei Tag."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import (
    ConflictError,
    DuplicateError,
    NotFoundError,
    ValidationError,
)
from app.core.transaction_manager import PlanPreview, TransactionManager

from ..models.tag import Tag
from ..repositories.placement_repository import PlacementRepository
from ..repositories.tag_repository import TagRepository
from ._preview import require_preview
from .preview_service import PreviewService


class TagService:
    """Crea, rinomina, elimina e fonde i Tag (R8-R12, R47)."""

    def __init__(
        self,
        tags: TagRepository,
        placements: PlacementRepository,
        transaction_manager: TransactionManager,
        previews: PreviewService,
    ) -> None:
        self._tags = tags
        self._placements = placements
        self._tm = transaction_manager
        self._previews = previews

    def create(self, name: str, description: str | None = None) -> Tag:
        """Crea un Tag senza Placement (R9)."""
        clean_name = clean_tag_name(name)
        clean_description = description.strip() if description else None

        def work(conn: Any) -> Tag:
            if self._tags.get_by_name(clean_name, conn) is not None:
                raise DuplicateError(f"Esiste già un Tag chiamato '{clean_name}' (R8)")
            return self._tags.add(
                Tag(name=clean_name, description=clean_description, is_system=False),
                conn,
            )

        return self._tm.run(work)

    def rename(self, tag_id: int, new_name: str) -> Tag:
        """Rinomina un Tag senza interrompere le assegnazioni (R10)."""
        clean_name = clean_tag_name(new_name)

        def work(conn: Any) -> Tag:
            tag = self._require(tag_id, conn)
            if tag.is_system:
                raise ConflictError("Un Tag di sistema non può essere rinominato (R47)")
            existing = self._tags.get_by_name(clean_name, conn)
            if existing is not None and existing.id != tag_id:
                raise DuplicateError(f"Esiste già un Tag chiamato '{clean_name}' (R8)")
            tag.name = clean_name
            return self._tags.save(tag, conn)

        return self._tm.run(work)

    def delete(self, tag_id: int) -> None:
        """Elimina un Tag solo se non ha Placement (R11, R47)."""

        def work(conn: Any) -> None:
            tag = self._require(tag_id, conn)
            if tag.is_system:
                raise ConflictError("Un Tag di sistema non può essere eliminato (R47)")
            placements = self._placements.list_by_tag(tag_id, conn)
            if placements:
                raise ConflictError(
                    f"Il Tag ha {len(placements)} Placement non risolti (R11)"
                )
            self._tags.delete(tag_id, conn)

        self._tm.run(work)

    def merge(
        self, source_id: int, target_id: int, preview: PlanPreview | None
    ) -> Tag:
        """Fonde due Tag con scelta esplicita, senza fusioni automatiche (R33)."""
        if source_id == target_id:
            raise ValidationError("Un Tag non può essere fuso con sé stesso")
        checked = require_preview(
            preview, "merge_tags", source_id=source_id, target_id=target_id
        )

        def work(conn: Any) -> Tag:
            source = self._require(source_id, conn)
            target = self._require(target_id, conn)
            if source.is_system:
                raise ConflictError(
                    "Un Tag di sistema non può essere sorgente di fusione (R47)"
                )
            if target.is_system:
                raise ConflictError(
                    "Un Tag di sistema non può essere destinazione di fusione"
                )
            for placement in self._placements.list_by_tag(source_id, conn):
                if placement.id is None:  # pragma: no cover
                    continue
                conflict = _destination_conflict(
                    placement, target_id, self._placements, conn
                )
                if conflict is not None:
                    raise ConflictError(conflict)
                self._placements.set_tag(placement.id, target_id, conn)
            self._tags.delete(source_id, conn)
            refreshed = self._tags.get(target_id, conn)
            if refreshed is None:  # pragma: no cover
                raise NotFoundError("Tag", target_id)
            return refreshed

        return self._tm.run(
            work,
            preview=checked,
            after=self._tm.assert_tag_graph_acyclic,
        )

    def get(self, tag_id: int) -> Tag:
        """Legge un Tag."""
        return self._require(tag_id, None)

    def list_tags(self) -> list[Tag]:
        """Elenca i Tag in ordine di nome."""
        return self._tags.list_all()

    def get_by_name(self, name: str) -> Tag | None:
        """Cerca un Tag per nome, case insensitive."""
        return self._tags.get_by_name(name)

    def resolve(self, reference: str | int) -> Tag:
        """Risolve un Tag da ID numerico oppure nome, senza distinzione di caso."""
        token = str(reference).strip()
        if token.isdigit():
            tag = self._tags.get(int(token))
            if tag is not None:
                return tag
        tag = self._tags.get_by_name(token)
        if tag is None:
            raise NotFoundError("Tag", token)
        return tag

    def _require(self, tag_id: int, conn: Any) -> Tag:
        tag = self._tags.get(tag_id, conn)
        if tag is None:
            raise NotFoundError("Tag", tag_id)
        return tag


def clean_tag_name(name: str) -> str:
    clean = name.strip()
    if not clean:
        raise ValidationError("Il nome del Tag non può essere vuoto")
    if "." in clean:
        raise ValidationError(
            "Il nome del Tag non può contenere '.' perché separa i segmenti del percorso"
        )
    return clean


def _destination_conflict(
    placement: Any, target_id: int, placements: PlacementRepository, conn: Any
) -> str | None:
    if placement.parent_id is None:
        root = placements.get_root_by_tag(target_id, conn)
        if root is not None:
            return (
                "La destinazione ha già un Placement radice: conflitto da risolvere esplicitamente (R21, R33)"
            )
        return None
    siblings = [
        item
        for item in placements.list_children(placement.parent_id, conn)
        if item.tag_id == target_id
    ]
    if siblings:
        return (
            f"Il Tag di destinazione è già presente sotto il padre del Placement {placement.id} "
            f"(Placement id {siblings[0].id}): conflitto esplicito (R21, R33)"
        )
    return None
