"""ObjectAttribute: valore di un attributo assegnato a un Object."""

from __future__ import annotations

from dataclasses import dataclass

from .attribute_definition import ValueType


@dataclass(kw_only=True)
class ObjectAttribute:
    """Valore di un attributo su un oggetto.

    Può essere:
    - **Con namespace**: ``definition_id`` punta a una definizione,
      ``namespace`` è il nome del namespace (denormalizzato).
    - **Libero**: ``definition_id = None``, ``namespace = None``,
      il tipo è dedotto dal valore.
    """

    object_id: int
    key: str
    value: str
    value_type: ValueType
    definition_id: int | None = None
    namespace: str | None = None
    id: int | None = None
    created_at: str | None = None

    @property
    def full_key(self) -> str:
        """Restituisce 'namespace.key' o solo 'key' se libero."""
        if self.namespace:
            return f"{self.namespace}.{self.key}"
        return self.key
