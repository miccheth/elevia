"""Servizio delle assegnazioni Object / Placement (R22-R29)."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import ConflictError, NotFoundError
from app.core.transaction_manager import TransactionManager

from ..models.tagging import Tagging
from ..repositories.object_repository import ObjectRepository
from ..repositories.placement_repository import PlacementRepository
from ..repositories.tag_repository import TagRepository
from ..repositories.tagging_repository import TaggingRepository
from ._system import untagged_placement


class TaggingService:
    """Aggiunge, trasferisce e rimuove assegnazioni."""

    def __init__(
        self,
        objects: ObjectRepository,
        tags: TagRepository,
        placements: PlacementRepository,
        taggings: TaggingRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._objects = objects
        self._tags = tags
        self._placements = placements
        self._taggings = taggings
        self._tm = transaction_manager

    def assign(self, object_id: int, placement_id: int) -> Tagging:
        """Aggiunge l'assegnazione se assente; se presente non cambia nulla (R22, R28)."""

        def work(conn: Any) -> Tagging:
            self._require_object(object_id, conn)
            self._require_placement(placement_id, conn)
            existing = self._taggings.get(object_id, placement_id, conn)
            if existing is not None:
                return existing
            created = self._taggings.add(
                Tagging(object_id=object_id, placement_id=placement_id), conn
            )
            self._tm.assert_object_has_tagging(conn, object_id)
            return created

        return self._tm.run(work)

    def transfer(
        self, object_id: int, from_placement_id: int, to_placement_id: int
    ) -> Tagging | None:
        """Sposta l'Object da un contesto a un altro (R26, R27)."""
        def work(conn: Any) -> Tagging | None:
            self._require_object(object_id, conn)
            source = self._taggings.get(object_id, from_placement_id, conn)
            if source is None:
                raise ConflictError(
                    "L'Object non è assegnato al Placement di partenza (R26)"
                )
            self._require_placement(to_placement_id, conn)
            if from_placement_id == to_placement_id:
                return source
            destination = self._taggings.get(object_id, to_placement_id, conn)
            if destination is None:
                destination = self._taggings.add(
                    Tagging(object_id=object_id, placement_id=to_placement_id), conn
                )
            self._taggings.delete(source.id, conn)  # type: ignore[arg-type]
            self._tm.assert_object_has_tagging(conn, object_id)
            return destination

        return self._tm.run(work)

    def remove(self, object_id: int, placement_id: int) -> None:
        """Rimuove l'assegnazione scelta; se è l'ultima, passa a Untagged (R25, R48)."""

        def work(conn: Any) -> None:
            self._require_object(object_id, conn)
            target = self._taggings.get(object_id, placement_id, conn)
            if target is None:
                return

            assignments = self._taggings.list_by_object(object_id, conn)
            if len(assignments) > 1:
                self._taggings.delete(target.id, conn)  # type: ignore[arg-type]
                return

            placement = self._require_placement(placement_id, conn)
            tag = self._tags.get(placement.tag_id, conn)
            if tag is not None and tag.is_system:
                raise ConflictError(
                    "L'ultima assegnazione di un Object già in Untagged non può essere rimossa (R1, R48)"
                )

            fallback = untagged_placement(self._tags, self._placements, conn)
            self._taggings.delete(target.id, conn)  # type: ignore[arg-type]
            self._taggings.add(
                Tagging(
                    object_id=object_id,
                    placement_id=fallback.id,
                ),
                conn,
            )
            self._tm.assert_object_has_tagging(conn, object_id)

        self._tm.run(work)

    def list_for_object(self, object_id: int) -> list[Tagging]:
        """Assegnazioni correnti di un Object."""
        self._require_object(object_id, None)
        return self._taggings.list_by_object(object_id)

    def _require_object(self, object_id: int, conn: Any) -> None:
        if self._objects.get(object_id, conn) is None:
            raise NotFoundError("Object", object_id)

    def _require_placement(self, placement_id: int, conn: Any) -> Any:
        placement = self._placements.get(placement_id, conn)
        if placement is None:
            raise NotFoundError("Placement", placement_id)
        return placement
