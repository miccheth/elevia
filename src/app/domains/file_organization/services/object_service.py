"""Servizio degli Object: registrazione, rinomina e rimozione."""

from __future__ import annotations

from abc import ABC
from typing import Any

from app.core.exceptions import NotFoundError, ValidationError
from app.core.transaction_manager import TransactionManager

from ..models.object import Object, ObjectType
from ..models.placement import Placement
from ..models.tagging import Tagging
from ..repositories.local_file_object_repository import LocalFileObjectRepository
from ..repositories.object_repository import ObjectRepository
from ..repositories.placement_repository import PlacementRepository
from ..repositories.tag_repository import TagRepository
from ..repositories.tagging_repository import TaggingRepository
from ._system import untagged_placement
from .preview_service import PreviewService


class ObjectService(ABC):
    """Regole comuni a tutti gli Object (R1-R7)."""

    def __init__(
        self,
        objects: ObjectRepository,
        local_files: LocalFileObjectRepository,
        taggings: TaggingRepository,
        tags: TagRepository,
        placements: PlacementRepository,
        transaction_manager: TransactionManager,
        previews: PreviewService,
    ) -> None:
        self._objects = objects
        self._local_files = local_files
        self._taggings = taggings
        self._tags = tags
        self._placements = placements
        self._tm = transaction_manager
        self._previews = previews

    def register(self, name: str, placement_ids: list[int] | None = None) -> Object:
        """Registra un Object generico con almeno una Tagging (R1)."""
        clean_name = _clean_name(name)
        target_ids = list(placement_ids or [])
        created_id: dict[str, int] = {}

        def work(conn: Any) -> Object:
            placements = self._resolve_placements(conn, target_ids)
            created = self._objects.add(
                Object(name=clean_name, object_type=ObjectType.GENERIC_OBJECT),
                conn,
            )
            for placement in placements:
                self._taggings.add(_tagging(created, placement), conn)
            if created.id is None:  # pragma: no cover
                raise ValidationError("Object registrato senza id")
            created_id["value"] = created.id
            return created

        def after(conn: Any) -> None:
            self._tm.assert_object_has_tagging(conn, created_id["value"])

        return self._tm.run(work, after=after)

    def rename(self, object_id: int, new_name: str) -> Object:
        """Rinomina l'Object senza toccare identità e associazioni (R2)."""
        clean_name = _clean_name(new_name)

        def work(conn: Any) -> Object:
            self._require_object(object_id, conn)
            self._objects.set_name(object_id, clean_name, conn)
            updated = self._objects.get(object_id, conn)
            if updated is None:  # pragma: no cover
                raise NotFoundError("Object", object_id)
            return updated

        return self._tm.run(work)

    def remove(self, object_id: int) -> None:
        """Rimuove l'Object da Elevia, mai la risorsa originale (R5-R7)."""

        def work(conn: Any) -> None:
            self._require_object(object_id, conn)
            self._objects.delete(object_id, conn)

        self._tm.run(work)

    def get(self, object_id: int) -> Object:
        """Legge un Object per id."""
        found = self._objects.get(object_id)
        if found is None:
            raise NotFoundError("Object", object_id)
        return found

    def list_objects(self) -> list[Object]:
        """Elenca gli Object registrati."""
        return self._objects.list_all()

    # --- Supporto -----------------------------------------------------------

    def _resolve_placements(
        self, conn: Any, placement_ids: list[int]
    ) -> list[Placement]:
        if not placement_ids:
            return [untagged_placement(self._tags, self._placements, conn)]

        resolved: list[Placement] = []
        seen: set[int] = set()
        for placement_id in placement_ids:
            placement = self._placements.get(placement_id, conn)
            if placement is None:
                raise NotFoundError("Placement", placement_id)
            if placement_id not in seen:
                resolved.append(placement)
                seen.add(placement_id)
        return resolved

    def _require_object(self, object_id: int, conn: Any) -> Object:
        found = self._objects.get(object_id, conn)
        if found is None:
            raise NotFoundError("Object", object_id)
        return found


def _clean_name(name: str) -> str:
    clean = name.strip()
    if not clean:
        raise ValidationError("Il nome dell'Object non può essere vuoto")
    return clean


def _tagging(obj: Object, placement: Placement) -> Tagging:
    if obj.id is None or placement.id is None:  # pragma: no cover
        raise ValidationError("Object o Placement senza id")
    return Tagging(object_id=obj.id, placement_id=placement.id)
