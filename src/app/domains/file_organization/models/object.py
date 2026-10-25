"""Object: risorsa logica con identità indipendente."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ObjectType(StrEnum):
    """Tipo di risorsa rappresentata da un Object."""

    LOCAL_FILE = "LOCAL_FILE"
    GENERIC_OBJECT = "GENERIC_OBJECT"


@dataclass(kw_only=True)
class Object:
    """Risorsa logica con identità indipendente dalla posizione fisica."""

    name: str
    object_type: ObjectType = ObjectType.GENERIC_OBJECT
    id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
