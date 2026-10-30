"""Servizio della gerarchia dei Placement."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import (
    ConflictError,
    DuplicateError,
    NotFoundError,
    ValidationError,
)
from app.core.transaction_manager import PlanPreview, TransactionManager

from ..models.placement import Placement
from ..models.tag import Tag
from ..repositories.placement_repository import PlacementRepository
from ..repositories.tag_repository import TagRepository
from ._placement_paths import PathIndex
from ._preview import require_preview
from .preview_service import PreviewService
from .tag_service import clean_tag_name


class PlacementService:
    """Crea, sposta ed elimina le collocazioni (R13-R21, R30, R32)."""

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

    def create_placement(self, tag_id: int, parent_id: int | None = None) -> Placement:
        """Crea un Placement vuoto, senza copiare figli o assegnazioni (R21)."""

        def work(conn: Any) -> Placement:
            self._require_tag(tag_id, conn)
            self._ensure_slot(conn, tag_id, parent_id)
            return self._placements.add(
                Placement(tag_id=tag_id, parent_id=parent_id), conn
            )

        return self._tm.run(
            work,
            after=_validate_structure(self._tm),
        )

    def create_placement_for_tag(
        self,
        reference: str,
        parent_id: int | None = None,
        *,
        create_tag: bool = False,
    ) -> Placement:
        """Crea un Placement da ID o nome del Tag, con creazione opzionale del Tag."""
        token = str(reference).strip()
        if not token:
            raise ValidationError("Il nome del Tag non può essere vuoto")

        def work(conn: Any) -> Placement:
            tag = self._resolve_tag(token, conn)
            if tag is None:
                if not create_tag:
                    raise NotFoundError("Tag", token)
                tag = self._tags.add(
                    Tag(
                        name=clean_tag_name(token),
                        description=None,
                        is_system=False,
                    ),
                    conn,
                )
            if tag.id is None:  # pragma: no cover
                raise ValidationError("Tag registrato senza id")
            self._ensure_slot(conn, tag.id, parent_id)
            return self._placements.add(
                Placement(tag_id=tag.id, parent_id=parent_id), conn
            )

        return self._tm.run(
            work,
            after=_validate_structure(self._tm),
        )

    def move(
        self,
        placement_id: int,
        new_parent_id: int | None,
        preview: PlanPreview | None,
    ) -> Placement:
        """Sposta un Placement conservando identità, figli e assegnazioni (R19)."""
        checked = require_preview(
            preview,
            "move_placement",
            placement_id=placement_id,
            new_parent_id=new_parent_id,
        )

        def work(conn: Any) -> Placement:
            current = self._require(placement_id, conn)
            tag = self._tags.get(current.tag_id, conn)
            if tag is not None and tag.is_system:
                raise ConflictError(
                    "Il Placement del Tag di sistema non può essere spostato (R46)"
                )
            if new_parent_id is not None:
                self._require(new_parent_id, conn)
            self._placements.set_parent(placement_id, new_parent_id, conn)
            moved = self._placements.get(placement_id, conn)
            if moved is None:  # pragma: no cover
                raise NotFoundError("Placement", placement_id)
            return moved

        return self._tm.run(
            work,
            preview=checked,
            after=_validate_structure(self._tm),
        )

    def delete(self, placement_id: int) -> None:
        """Elimina un Placement vuoto; nessuna eliminazione ricorsiva (R20)."""

        def before(conn: Any) -> None:
            placement = self._require(placement_id, conn)
            tag = self._tags.get(placement.tag_id, conn)
            if (
                tag is not None
                and tag.is_system
                and placement.parent_id is None
            ):
                raise ConflictError(
                    "Il Placement radice del Tag di sistema non può essere eliminato (R46)"
                )
            self._tm.assert_placement_deletable(conn, placement_id)

        def work(conn: Any) -> None:
            self._placements.delete(placement_id, conn)

        self._tm.run(work, before=before)

    def get(self, placement_id: int) -> Placement:
        """Legge un Placement."""
        return self._require(placement_id, None)

    def resolve(self, reference: str | int) -> Placement:
        """Risolve un Placement da ID numerico oppure percorso, case insensitive."""
        token = str(reference).strip()
        if not token:
            raise ValidationError("Il Placement non può essere vuoto")
        if token.isdigit():
            placement = self._placements.get(int(token))
            if placement is not None:
                return placement
        index = PathIndex.build(self._placements.list_all(), self._tags.list_all())
        wanted = token.casefold()
        matches = [
            placement_id
            for placement_id in index.placements
            if index.text_for(placement_id).casefold() == wanted
        ]
        if len(matches) == 1:
            return index.placements[matches[0]]
        if len(matches) > 1:
            ids = ", ".join(str(item) for item in sorted(matches))
            raise ConflictError(f"Percorso ambiguo '{token}': usa uno degli ID {ids}")
        raise NotFoundError("Placement", token)

    def list_placements(self) -> list[Placement]:
        """Elenca tutti i Placement."""
        return self._placements.list_all()

    def list_children(self, parent_id: int | None) -> list[Placement]:
        """Elenca i figli diretti di un Placement."""
        return self._placements.list_children(parent_id)

    def describe(self) -> list[dict[str, Any]]:
        """Elenca i Placement con percorso e numero di assegnazioni."""
        index = PathIndex.build(self._placements.list_all(), self._tags.list_all())
        rows = []
        with self._tm.read() as conn:
            for placement in index.placements.values():
                if placement.id is None:
                    continue
                count = conn.execute(
                    "SELECT COUNT(*) AS total FROM tagging WHERE placement_id = ?",
                    (placement.id,),
                ).fetchone()["total"]
                rows.append(
                    {
                        "id": placement.id,
                        "tag_id": placement.tag_id,
                        "parent_id": placement.parent_id,
                        "percorso": index.text_for(placement.id),
                        "assegnazioni": count,
                    }
                )
        rows.sort(key=lambda item: item["percorso"].casefold())
        return rows

    def path_for(self, placement_id: int) -> str:
        """Percorso leggibile di un Placement."""
        index = PathIndex.build(self._placements.list_all(), self._tags.list_all())
        if placement_id not in index.placements:
            raise NotFoundError("Placement", placement_id)
        return index.text_for(placement_id)

    def _require(self, placement_id: int, conn: Any) -> Placement:
        placement = self._placements.get(placement_id, conn)
        if placement is None:
            raise NotFoundError("Placement", placement_id)
        return placement

    def _resolve_tag(self, reference: str, conn: Any) -> Tag | None:
        if reference.isdigit():
            tag = self._tags.get(int(reference), conn)
            if tag is not None:
                return tag
        return self._tags.get_by_name(reference, conn)

    def _ensure_slot(self, conn: Any, tag_id: int, parent_id: int | None) -> None:
        tag = self._tags.get(tag_id, conn)
        if tag is not None and tag.is_system:
            raise ConflictError(
                f"Il Tag di sistema '{tag.name}' ammette solo il Placement radice (R46)"
            )
        if parent_id is not None:
            parent = self._require(parent_id, conn)
            if parent.tag_id == tag_id:
                raise DuplicateError(
                    "Lo stesso Tag non può stare sotto un padre che lo contiene già (R16)"
                )
            existing = _child_with_tag(self._placements, parent_id, tag_id, conn)
            if existing is not None:
                raise DuplicateError(
                    f"Esiste già un Placement di questo Tag sotto il padre (id {existing.id}) (R16)"
                )
            return
        root = self._placements.get_root_by_tag(tag_id, conn)
        if root is not None:
            raise DuplicateError(
                f"Esiste già un Placement radice per il Tag (id {root.id}) (R15)"
            )

    def _require_tag(self, tag_id: int, conn: Any) -> None:
        if self._tags.get(tag_id, conn) is None:
            raise NotFoundError("Tag", tag_id)


def _child_with_tag(
    placements: PlacementRepository, parent_id: int, tag_id: int, conn: Any
) -> Placement | None:
    for child in placements.list_children(parent_id, conn):
        if child.tag_id == tag_id:
            return child
    return None


def _validate_structure(tm: TransactionManager) -> Any:
    def validate(conn: Any) -> None:
        tm.assert_placement_acyclic(conn)
        tm.assert_tag_graph_acyclic(conn)

    return validate
