"""Servizio dei namespace di attributi (R49-R52)."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.transaction_manager import TransactionManager

from ..models.attribute_namespace import AttributeNamespace
from ..repositories.attribute_namespace_repository import AttributeNamespaceRepository


class AttributeNamespaceService:
    """Gestisce i namespace (template) degli attributi."""

    def __init__(
        self,
        namespaces: AttributeNamespaceRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._namespaces = namespaces
        self._tm = transaction_manager

    def create(self, name: str, description: str | None = None) -> AttributeNamespace:
        """Crea un nuovo namespace (R49: nome univoco case insensitive)."""
        clean_name = _clean_name(name)

        def work(conn: Any) -> AttributeNamespace:
            existing = self._namespaces.get_by_name(clean_name, conn)
            if existing is not None:
                raise ConflictError(f"Namespace già esistente: {clean_name}")
            return self._namespaces.add(
                AttributeNamespace(name=clean_name, description=description), conn
            )

        return self._tm.run(work)

    def list_all(self) -> list[AttributeNamespace]:
        """Elenca tutti i namespace."""
        return self._namespaces.list_all()

    def get(self, namespace_id: int) -> AttributeNamespace:
        """Legge un namespace per id."""
        found = self._namespaces.get(namespace_id)
        if found is None:
            raise NotFoundError("Namespace", namespace_id)
        return found

    def get_by_name(self, name: str) -> AttributeNamespace:
        """Legge un namespace per nome."""
        found = self._namespaces.get_by_name(name)
        if found is None:
            raise NotFoundError("Namespace", name)
        return found

    def delete(self, namespace_id: int) -> None:
        """Elimina un namespace (R51: CASCADE su definizioni e valori)."""

        def work(conn: Any) -> None:
            if self._namespaces.get(namespace_id, conn) is None:
                raise NotFoundError("Namespace", namespace_id)
            self._namespaces.delete(namespace_id, conn)

        self._tm.run(work)


def _clean_name(name: str) -> str:
    clean = name.strip()
    if not clean:
        raise ValidationError("Il nome del namespace non può essere vuoto")
    return clean
