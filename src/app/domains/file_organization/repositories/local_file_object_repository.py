"""Porta del repository dei LocalFileObject."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models.local_file_object import LocalFileObject


class LocalFileObjectRepository(ABC):
    """Persistenza dei dettagli dei file locali."""

    @abstractmethod
    def add(self, obj: LocalFileObject, conn: Any | None = None) -> LocalFileObject: ...

    @abstractmethod
    def get(self, object_id: int, conn: Any | None = None) -> LocalFileObject | None: ...

    @abstractmethod
    def list_all(self, conn: Any | None = None) -> list[LocalFileObject]: ...

    @abstractmethod
    def save(self, obj: LocalFileObject, conn: Any | None = None) -> LocalFileObject: ...

    @abstractmethod
    def find_by_normalized_path(
        self, normalized_path: str, conn: Any | None = None
    ) -> LocalFileObject | None: ...
