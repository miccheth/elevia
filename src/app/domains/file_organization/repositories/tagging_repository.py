"""Porta del repository dei Tagging."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models.tagging import Tagging


class TaggingRepository(ABC):
    """Persistenza delle assegnazioni Object / Placement."""

    @abstractmethod
    def add(self, tagging: Tagging, conn: Any | None = None) -> Tagging: ...

    @abstractmethod
    def get(
        self, object_id: int, placement_id: int, conn: Any | None = None
    ) -> Tagging | None: ...

    @abstractmethod
    def list_by_object(self, object_id: int, conn: Any | None = None) -> list[Tagging]: ...

    @abstractmethod
    def list_by_placement(
        self, placement_id: int, conn: Any | None = None
    ) -> list[Tagging]: ...

    @abstractmethod
    def list_all(self, conn: Any | None = None) -> list[Tagging]: ...

    @abstractmethod
    def delete(self, tagging_id: int, conn: Any | None = None) -> None: ...

    @abstractmethod
    def count_by_object(self, object_id: int, conn: Any | None = None) -> int: ...

    @abstractmethod
    def count_by_placement(self, placement_id: int, conn: Any | None = None) -> int: ...
