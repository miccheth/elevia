"""Porta del repository degli ObjectAttribute."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models.object_attribute import ObjectAttribute


class ObjectAttributeRepository(ABC):
    """Persistenza dei valori degli attributi sugli oggetti."""

    @abstractmethod
    def add(self, attribute: ObjectAttribute, conn: Any | None = None) -> ObjectAttribute: ...

    @abstractmethod
    def get(
        self,
        object_id: int,
        namespace: str | None,
        key: str,
        conn: Any | None = None,
    ) -> ObjectAttribute | None: ...

    @abstractmethod
    def get_by_definition(
        self, object_id: int, definition_id: int, conn: Any | None = None
    ) -> ObjectAttribute | None: ...

    @abstractmethod
    def list_for_object(
        self, object_id: int, conn: Any | None = None
    ) -> list[ObjectAttribute]: ...

    @abstractmethod
    def delete(
        self,
        object_id: int,
        namespace: str | None,
        key: str,
        conn: Any | None = None,
    ) -> None: ...

    @abstractmethod
    def delete_by_definition(self, definition_id: int, conn: Any | None = None) -> None: ...

    @abstractmethod
    def list_objects_with(
        self,
        namespace: str | None,
        key: str,
        value: str | None = None,
        conn: Any | None = None,
    ) -> list[int]: ...
