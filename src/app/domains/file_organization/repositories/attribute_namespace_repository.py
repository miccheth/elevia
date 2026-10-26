"""Porta del repository degli AttributeNamespace."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models.attribute_namespace import AttributeNamespace


class AttributeNamespaceRepository(ABC):
    """Persistenza dei namespace di attributi."""

    @abstractmethod
    def add(self, namespace: AttributeNamespace, conn: Any | None = None) -> AttributeNamespace: ...

    @abstractmethod
    def get(self, namespace_id: int, conn: Any | None = None) -> AttributeNamespace | None: ...

    @abstractmethod
    def get_by_name(self, name: str, conn: Any | None = None) -> AttributeNamespace | None: ...

    @abstractmethod
    def list_all(self, conn: Any | None = None) -> list[AttributeNamespace]: ...

    @abstractmethod
    def delete(self, namespace_id: int, conn: Any | None = None) -> None: ...
