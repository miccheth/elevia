"""Deduzione e validazione del tipo di un attributo."""

from __future__ import annotations

import re
from datetime import date

from app.core.exceptions import ValidationError

from ..models.attribute_definition import ValueType

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def deduce_type(value: str) -> ValueType:
    """Deduce il tipo di un valore per gli attributi liberi (senza namespace).

    Ordine di deduzione:
    1. NUMBER: intero o decimale
    2. DATE: formato ISO 8601 (YYYY-MM-DD)
    3. BOOLEAN: "true" o "false" (case insensitive)
    4. TEXT: qualsiasi altra stringa
    """
    stripped = value.strip()
    if not stripped:
        return ValueType.TEXT

    # NUMBER: intero o decimale
    try:
        int(stripped)
        return ValueType.NUMBER
    except ValueError:
        pass
    try:
        float(stripped)
        return ValueType.NUMBER
    except ValueError:
        pass

    # DATE: formato ISO 8601
    if _DATE_RE.match(stripped):
        try:
            date.fromisoformat(stripped)
            return ValueType.DATE
        except ValueError:
            pass

    # BOOLEAN
    lowered = stripped.lower()
    if lowered in ("true", "false"):
        return ValueType.BOOLEAN

    return ValueType.TEXT


def validate_value(value: str, value_type: ValueType) -> str:
    """Valida un valore in base al tipo. Restituisce il valore normalizzato."""
    stripped = value.strip()
    if not stripped:
        raise ValidationError("Il valore dell'attributo non può essere vuoto")

    if value_type == ValueType.NUMBER:
        try:
            # Prova a convertire per validare
            float(stripped)
        except ValueError:
            raise ValidationError(
                f"Il valore '{value}' non è un numero valido (tipo NUMBER)"
            )
        return stripped

    if value_type == ValueType.DATE:
        if not _DATE_RE.match(stripped):
            raise ValidationError(
                f"Il valore '{value}' non è una data valida (formato atteso: YYYY-MM-DD)"
            )
        try:
            date.fromisoformat(stripped)
        except ValueError:
            raise ValidationError(
                f"Il valore '{value}' non è una data valida (tipo DATE)"
            )
        return stripped

    if value_type == ValueType.BOOLEAN:
        lowered = stripped.lower()
        if lowered not in ("true", "false"):
            raise ValidationError(
                f"Il valore '{value}' non è un booleano valido (atteso: true o false)"
            )
        return lowered

    # TEXT e ENUM: nessun vincolo di formato (ENUM viene validato separatamente)
    return stripped


def validate_enum_value(value: str, allowed_values: list) -> str:
    """Valida che un valore sia nella lista dei valori possibili di un ENUM."""
    stripped = value.strip()
    for allowed in allowed_values:
        if str(allowed) == stripped:
            return stripped
    allowed_str = ", ".join(str(v) for v in allowed_values)
    raise ValidationError(
        f"Il valore '{value}' non è tra i valori possibili: {allowed_str}"
    )


def is_comparable(value_type: ValueType) -> bool:
    """Indica se il tipo ammette confronti >, <, >=, <=."""
    return value_type in (ValueType.NUMBER, ValueType.DATE)
