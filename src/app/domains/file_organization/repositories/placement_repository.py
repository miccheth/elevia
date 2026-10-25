"""Porta del repository dei Placement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models.placement import Placement


class PlacementRepository(ABC):
    """Persistenza della gerarchia delle collocazioni."""

    @abstractmethod
    def add(self, placement: Placement, conn: Any | None = None) -> Placement: ...

    @abstractmethod
    def get(self, placement_id: int, conn: Any | None = None) -> Placement | None: ...

    @abstractmethod
    def list_all(self, conn: Any | None = None) -> list[Placement]: ...

    @abstractmethod
    def list_by_tag(self, tag_id: int, conn: Any | None = None) -> list[Placement]: ...

    @abstractmethod
    def list_children(
        self, parent_id: int | None, conn: Any | None = None
    ) -> list[Placement]: ...

    @abstractmethod
    def get_root_by_tag(self, tag_id: int, conn: Any | None = None) -> Placement | None: ...

    @abstractmethod
    def set_parent(
        self, placement_id: int, parent_id: int | None, conn: Any | None = None
    ) -> None: ...

    @abstractmethod
    def set_tag(
        self, placement_id: int, tag_id: int, conn: Any | None = None
    ) -> None: ...

    @abstractmethod
    def delete(self, placement_id: int, conn: Any | None = None) -> None: ...

    @abstractmethod
    def count(self, conn: Any | None = None) -> int: ...
