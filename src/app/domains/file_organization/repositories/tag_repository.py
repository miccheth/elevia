"""Porta del repository dei Tag."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models.tag import Tag


class TagRepository(ABC):
    """Persistenza del vocabolario controllato."""

    @abstractmethod
    def add(self, tag: Tag, conn: Any | None = None) -> Tag: ...

    @abstractmethod
    def get(self, tag_id: int, conn: Any | None = None) -> Tag | None: ...

    @abstractmethod
    def get_by_name(self, name: str, conn: Any | None = None) -> Tag | None: ...

    @abstractmethod
    def get_system(self, conn: Any | None = None) -> Tag | None: ...

    @abstractmethod
    def list_all(self, conn: Any | None = None) -> list[Tag]: ...

    @abstractmethod
    def save(self, tag: Tag, conn: Any | None = None) -> Tag: ...

    @abstractmethod
    def delete(self, tag_id: int, conn: Any | None = None) -> None: ...

    @abstractmethod
    def count(self, conn: Any | None = None) -> int: ...
