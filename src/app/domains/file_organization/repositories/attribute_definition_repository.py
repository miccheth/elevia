"""Porta del repository delle AttributeDefinition."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models.attribute_definition import AttributeDefinition


class AttributeDefinitionRepository(ABC):
    """Persistenza delle definizioni di attributi."""

    @abstractmethod
    def add(self, definition: AttributeDefinition, conn: Any | None = None) -> AttributeDefinition: ...

    @abstractmethod
    def get(self, definition_id: int, conn: Any | None = None) -> AttributeDefinition | None: ...

    @abstractmethod
    def get_by_key(
        self, namespace_id: int, key: str, conn: Any | None = None
    ) -> AttributeDefinition | None: ...

    @abstractmethod
    def list_by_namespace(
        self, namespace_id: int, conn: Any | None = None
    ) -> list[AttributeDefinition]: ...

    @abstractmethod
    def delete(self, definition_id: int, conn: Any | None = None) -> None: ...
