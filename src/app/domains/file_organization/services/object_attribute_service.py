"""Servizio dei valori degli attributi sugli oggetti (R58-R65)."""

from __future__ import annotations

from typing import Any

from app.core.exceptions import NotFoundError, ValidationError
from app.core.transaction_manager import TransactionManager

from ..models.attribute_definition import ValueType
from ..models.object_attribute import ObjectAttribute
from ..repositories.attribute_definition_repository import AttributeDefinitionRepository
from ..repositories.attribute_namespace_repository import AttributeNamespaceRepository
from ..repositories.object_attribute_repository import ObjectAttributeRepository
from ..repositories.object_repository import ObjectRepository
from ._attribute_type import (
    deduce_type,
    is_comparable,
    validate_enum_value,
    validate_value,
)


class ObjectAttributeService:
    """Assegna, rimuove e legge attributi sugli oggetti."""

    def __init__(
        self,
        attributes: ObjectAttributeRepository,
        definitions: AttributeDefinitionRepository,
        namespaces: AttributeNamespaceRepository,
        objects: ObjectRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._attributes = attributes
        self._definitions = definitions
        self._namespaces = namespaces
        self._objects = objects
        self._tm = transaction_manager

    def set(
        self,
        object_id: int,
        key: str,
        value: str,
    ) -> ObjectAttribute:
        """Assegna un attributo a un oggetto (R58-R63).

        - Se ``key`` contiene un punto (es. "photo.year"):
          - Cerca il namespace "photo" e la definizione "year"
          - Se non esistono, ERRORE (R59)
          - Valida il valore in base al tipo (R62)
          - Per ENUM: valida contro allowed_values (R63)

        - Se ``key`` non contiene un punto (es. "colore"):
          - Attributo libero (R58)
          - Deduzione automatica del tipo (R60)
        """
        namespace_name, attr_key = _parse_key(key)

        def work(conn: Any) -> ObjectAttribute:
            self._require_object(object_id, conn)

            if namespace_name is not None:
                # Attributo con namespace: deve esistere la definizione (R59)
                namespace = self._namespaces.get_by_name(namespace_name, conn)
                if namespace is None:
                    raise NotFoundError("Namespace", namespace_name)
                definition = self._definitions.get_by_key(
                    namespace.id, attr_key, conn
                )
                if definition is None:
                    raise NotFoundError(
                        "Definizione attributo", f"{namespace_name}.{attr_key}"
                    )

                # Validazione del valore (R62, R63)
                validated = validate_value(value, definition.value_type)
                if definition.value_type == ValueType.ENUM:
                    validated = validate_enum_value(
                        validated, definition.allowed_values or []
                    )

                attribute = ObjectAttribute(
                    object_id=object_id,
                    definition_id=definition.id,
                    namespace=namespace.name,
                    key=definition.key,
                    value=validated,
                    value_type=definition.value_type,
                )
            else:
                # Attributo libero: deduzione del tipo (R60)
                value_type = deduce_type(value)
                validated = validate_value(value, value_type)
                attribute = ObjectAttribute(
                    object_id=object_id,
                    definition_id=None,
                    namespace=None,
                    key=attr_key,
                    value=validated,
                    value_type=value_type,
                )

            # Rimuovi eventuale valore esistente (R61: un solo valore per chiave)
            existing = self._attributes.get(
                object_id, attribute.namespace, attribute.key, conn
            )
            if existing is not None:
                self._attributes.delete(
                    object_id, attribute.namespace, attribute.key, conn
                )

            return self._attributes.add(attribute, conn)

        return self._tm.run(work)

    def unset(self, object_id: int, key: str) -> None:
        """Rimuove un attributo da un oggetto."""
        namespace_name, attr_key = _parse_key(key)

        def work(conn: Any) -> None:
            self._require_object(object_id, conn)
            existing = self._attributes.get(object_id, namespace_name, attr_key, conn)
            if existing is None:
                return  # Nessun effetto, nessuna modifica
            self._attributes.delete(object_id, namespace_name, attr_key, conn)

        self._tm.run(work)

    def get(self, object_id: int, key: str) -> ObjectAttribute | None:
        """Legge un attributo di un oggetto."""
        namespace_name, attr_key = _parse_key(key)
        return self._attributes.get(object_id, namespace_name, attr_key)

    def list_for_object(self, object_id: int) -> list[ObjectAttribute]:
        """Elenca tutti gli attributi di un oggetto."""
        if self._objects.get(object_id) is None:
            raise NotFoundError("Object", object_id)
        return self._attributes.list_for_object(object_id)

    def list_objects_with(
        self, key: str, value: str | None = None
    ) -> list[int]:
        """Elenca gli id degli oggetti con un attributo (per query)."""
        namespace_name, attr_key = _parse_key(key)
        return self._attributes.list_objects_with(namespace_name, attr_key, value)

    def _require_object(self, object_id: int, conn: Any) -> None:
        if self._objects.get(object_id, conn) is None:
            raise NotFoundError("Object", object_id)


def _parse_key(key: str) -> tuple[str | None, str]:
    """Separa namespace e chiave da 'namespace.key' o 'key'.

    Restituisce (namespace, key) oppure (None, key) per attributi liberi.
    """
    clean = key.strip()
    if not clean:
        raise ValidationError("La chiave dell'attributo non può essere vuota")
    if "." in clean:
        parts = clean.split(".", 1)
        namespace = parts[0].strip()
        attr_key = parts[1].strip()
        if not namespace or not attr_key:
            raise ValidationError(
                f"Chiave attributo non valida: '{key}' (formato atteso: namespace.chiave o chiave)"
            )
        return namespace, attr_key
    return None, clean
