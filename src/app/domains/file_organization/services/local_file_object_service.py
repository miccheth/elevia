"""Servizio degli Object che rappresentano file locali."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.time import from_timestamp

from ..models.local_file_object import LocalFileObject
from ..models.object import ObjectType
from .object_service import ObjectService, _tagging


class LocalFileObjectService(ObjectService):
    """Importa file e ne aggiorna il riferimento senza toccarli (R3-R6)."""

    def register(
        self,
        file_path: str | Path,
        name: str | None = None,
        placement_ids: list[int] | None = None,
    ) -> LocalFileObject:  # type: ignore[override]
        """Registra un file locale e almeno una Tagging (R1, R6)."""
        resolved = _resolve_file(file_path)
        metadata = _metadata(resolved)
        object_name = (name or resolved.name).strip()
        if not object_name:
            raise ValidationError("Il nome dell'Object non può essere vuoto")
        target_ids = list(placement_ids or [])
        created_id: dict[str, int] = {}

        def work(conn: Any) -> LocalFileObject:
            duplicate = self._local_files.find_by_normalized_path(
                metadata["normalized_path"], conn
            )
            if duplicate is not None:
                raise ConflictError(
                    f"File già registrato come Object {duplicate.id}: {duplicate.file_path}"
                )
            placements = self._resolve_placements(conn, target_ids)
            created = self._objects.add(
                LocalFileObject(
                    name=object_name,
                    object_type=ObjectType.LOCAL_FILE,
                    **metadata,
                ),
                conn,
            )
            local = self._local_files.add(
                LocalFileObject(
                    id=created.id,
                    name=object_name,
                    **metadata,
                ),
                conn,
            )
            for placement in placements:
                self._taggings.add(_tagging(local, placement), conn)
            if local.id is None:  # pragma: no cover
                raise ValidationError("LocalFileObject registrato senza id")
            created_id["value"] = local.id
            return local

        def after(conn: Any) -> None:
            self._tm.assert_object_has_tagging(conn, created_id["value"])

        return self._tm.run(work, after=after)

    def get_local(self, object_id: int) -> LocalFileObject:
        """Legge i dettagli del file locale."""
        found = self._local_files.get(object_id)
        if found is None:
            raise NotFoundError("LocalFileObject", object_id)
        return found

    def list_local_files(self) -> list[LocalFileObject]:
        """Elenca i file locali registrati."""
        return self._local_files.list_all()

    def find_by_path(self, file_path: str | Path) -> LocalFileObject | None:
        """Cerca un Object dal percorso del file."""
        resolved = _resolve_file(file_path, must_exist=False)
        return self._local_files.find_by_normalized_path(
            os.path.normcase(str(resolved))
        )

    def update_path(
        self, object_id: int, new_file_path: str | Path
    ) -> LocalFileObject:
        """Aggiorna il riferimento a un file spostato, senza cambiare identità (R3)."""
        resolved = _resolve_file(new_file_path)
        metadata = _metadata(resolved)

        def work(conn: Any) -> LocalFileObject:
            current = self._local_files.get(object_id, conn)
            if current is None:
                raise NotFoundError("LocalFileObject", object_id)
            duplicate = self._local_files.find_by_normalized_path(
                metadata["normalized_path"], conn
            )
            if duplicate is not None and duplicate.id != object_id:
                raise ConflictError(
                    f"Percorso già registrato dall'Object {duplicate.id}"
                )
            current.file_path = metadata["file_path"]
            current.normalized_path = metadata["normalized_path"]
            current.file_size = metadata["file_size"]
            current.modified_at = metadata["modified_at"]
            current.file_extension = metadata["file_extension"]
            current.is_available = True
            return self._local_files.save(current, conn)

        return self._tm.run(work)

    def mark_unavailable(self, object_id: int) -> LocalFileObject:
        """Segnala la risorsa come indisponibile, lasciandola ricercabile (R4)."""

        def work(conn: Any) -> LocalFileObject:
            current = self._local_files.get(object_id, conn)
            if current is None:
                raise NotFoundError("LocalFileObject", object_id)
            if not current.is_available:
                return current
            current.is_available = False
            return self._local_files.save(current, conn)

        return self._tm.run(work)

    def mark_available(
        self, object_id: int, file_path: str | Path | None = None
    ) -> LocalFileObject:
        """Ripristina la disponibilità e rilegge i metadati dal file."""
        if file_path is not None:
            return self.update_path(object_id, file_path)

        def work(conn: Any) -> LocalFileObject:
            current = self._local_files.get(object_id, conn)
            if current is None:
                raise NotFoundError("LocalFileObject", object_id)
            resolved = _resolve_file(current.file_path)
            metadata = _metadata(resolved)
            current.file_size = metadata["file_size"]
            current.modified_at = metadata["modified_at"]
            current.file_extension = metadata["file_extension"]
            current.is_available = True
            return self._local_files.save(current, conn)

        return self._tm.run(work)


def _resolve_file(file_path: str | Path, *, must_exist: bool = True) -> Path:
    path = Path(file_path).expanduser()
    if must_exist:
        try:
            path = path.resolve(strict=True)
        except OSError as exc:
            raise ValidationError(f"File non trovato: {file_path}") from exc
        if not path.is_file():
            raise ValidationError(f"Il percorso non è un file: {file_path}")
    else:
        path = path.resolve()
    return path


def _metadata(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "file_path": str(path),
        "normalized_path": os.path.normcase(str(path)),
        "file_size": stat.st_size,
        "modified_at": from_timestamp(stat.st_mtime),
        "file_extension": path.suffix.lower().lstrip("."),
        "is_available": True,
    }
