"""Servizio delle definizioni di attributi (R53-R57)."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.transaction_manager import TransactionManager

from ..models.attribute_definition import AttributeDefinition, ValueType
from ..repositories.attribute_definition_repository import AttributeDefinitionRepository
from ..repositories.attribute_namespace_repository import AttributeNamespaceRepository


class AttributeDefinitionService:
    """Gestisce le definizioni di attributi dentro un namespace."""

    def __init__(
        self,
        definitions: AttributeDefinitionRepository,
        namespaces: AttributeNamespaceRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._definitions = definitions
        self._namespaces = namespaces
        self._tm = transaction_manager

    def create(
        self,
        namespace_id: int,
        key: str,
        value_type: ValueType,
        allowed_values: list | None = None,
        description: str | None = None,
    ) -> AttributeDefinition:
        """Crea una definizione di attributo (R53-R55).

        - R53: (namespace_id, key) univoco
        - R54: ENUM richiede allowed_values non vuoto
        - R55: TEXT/NUMBER/DATE/BOOLEAN non usano allowed_values
        """
        clean_key = _clean_key(key)

        if value_type == ValueType.ENUM:
            if not allowed_values:
                raise ValidationError(
                    "Gli attributi ENUM richiedono una lista di valori possibili (--values)"
                )
        else:
            allowed_values = None

        def work(conn: Any) -> AttributeDefinition:
            if self._namespaces.get(namespace_id, conn) is None:
                raise NotFoundError("Namespace", namespace_id)
            existing = self._definitions.get_by_key(namespace_id, clean_key, conn)
            if existing is not None:
                raise ConflictError(
                    f"Attributo già definito nel namespace: {clean_key}"
                )
            return self._definitions.add(
                AttributeDefinition(
                    namespace_id=namespace_id,
                    key=clean_key,
                    value_type=value_type,
                    allowed_values=allowed_values,
                    description=description,
                ),
                conn,
            )

        return self._tm.run(work)

    def list_by_namespace(self, namespace_id: int) -> list[AttributeDefinition]:
        """Elenca le definizioni di un namespace."""
        if self._namespaces.get(namespace_id) is None:
            raise NotFoundError("Namespace", namespace_id)
        return self._definitions.list_by_namespace(namespace_id)

    def get(self, definition_id: int) -> AttributeDefinition:
        """Legge una definizione per id."""
        found = self._definitions.get(definition_id)
        if found is None:
            raise NotFoundError("Definizione attributo", definition_id)
        return found

    def get_by_key(self, namespace_id: int, key: str) -> AttributeDefinition:
        """Legge una definizione per namespace e chiave."""
        found = self._definitions.get_by_key(namespace_id, key)
        if found is None:
            raise NotFoundError("Definizione attributo", f"{namespace_id}.{key}")
        return found

    def delete(self, definition_id: int) -> None:
        """Elimina una definizione (R56: CASCADE sui valori)."""

        def work(conn: Any) -> None:
            if self._definitions.get(definition_id, conn) is None:
                raise NotFoundError("Definizione attributo", definition_id)
            self._definitions.delete(definition_id, conn)

        self._tm.run(work)


def _clean_key(key: str) -> str:
    clean = key.strip()
    if not clean:
        raise ValidationError("La chiave dell'attributo non può essere vuota")
    if "." in clean:
        raise ValidationError(
            "La chiave non può contenere il punto (usa il namespace per raggruppare)"
        )
    return clean
