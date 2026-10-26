"""AttributeDefinition: definisce tipo e valori di un attributo in un namespace."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ValueType(StrEnum):
    """Tipo di dato di un attributo."""

    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    BOOLEAN = "BOOLEAN"
    ENUM = "ENUM"


@dataclass(kw_only=True)
class AttributeDefinition:
    """Definizione di un attributo dentro un namespace.

    Per gli attributi ENUM, ``allowed_values`` contiene la lista
    dei valori possibili (può essere di tipo TEXT, NUMBER, DATE o BOOLEAN).
    """

    namespace_id: int
    key: str
    value_type: ValueType
    allowed_values: list[Any] | None = None
    description: str | None = None
    id: int | None = None
    created_at: str | None = None

    def allowed_values_json(self) -> str | None:
        """Serializza allowed_values in JSON per il database."""
        if self.allowed_values is None:
            return None
        return json.dumps(self.allowed_values)

    @classmethod
    def allowed_values_from_json(cls, raw: str | None) -> list[Any] | None:
        """Deserializza allowed_values da JSON."""
        if raw is None:
            return None
        return json.loads(raw)
