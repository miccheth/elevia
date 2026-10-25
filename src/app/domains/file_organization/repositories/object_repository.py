"""Porte dei repository del dominio.

Le implementazioni concrete vivono in ``app.infrastructure.repositories``.
Il parametro ``conn`` permette al TransactionManager di condividere la stessa
transazione tra più repository; quando è ``None`` il repository apre una
propria connessione.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..models.object import Object


class ObjectRepository(ABC):
    """Persistenza degli Object."""

    @abstractmethod
    def add(self, obj: Object, conn: Any | None = None) -> Object: ...

    @abstractmethod
    def get(self, object_id: int, conn: Any | None = None) -> Object | None: ...

    @abstractmethod
    def list_all(self, conn: Any | None = None) -> list[Object]: ...

    @abstractmethod
    def set_name(self, object_id: int, name: str, conn: Any | None = None) -> None: ...

    @abstractmethod
    def delete(self, object_id: int, conn: Any | None = None) -> None: ...

    @abstractmethod
    def count(self, conn: Any | None = None) -> int: ...
