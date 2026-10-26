"""Ricerca esplicita, sola lettura (R41-R48).

Le condizioni ``tag:percorso`` e ``namespace.chiave = valore`` (o ``chiave = valore``
per attributi liberi) diventano una singola query SQL con ``EXISTS``.
I percorsi sono ricostruiti al momento della lettura e non vengono salvati:
restano un dato derivato.
"""

from __future__ import annotations

import sqlite3

from app.core.exceptions import ValidationError
from app.core.transaction_manager import TransactionManager

from ..models.attribute_definition import ValueType
from ..models.object import Object, ObjectType
from ..models.placement import Placement
from ..models.tag import Tag
from ..query import (
    And,
    AttributeCondition,
    Condition,
    Group,
    Node,
    Not,
    Or,
    QueryParser,
    UnknownTagError,
)
from ._attribute_type import is_comparable
from ._placement_paths import PathIndex


class QueryService:
    """Traduce un'espressione in una query SQL di sola lettura."""

    def __init__(self, transaction_manager: TransactionManager) -> None:
        self._tm = transaction_manager

    def search(self, expression: str) -> list[Object]:
        """Restituisce gli Object che soddisfano l'espressione."""
        tree = QueryParser(expression).parse()
        with self._tm.read() as conn:
            self._resolve_tags(conn, tree)
            self._resolve_attributes(conn, tree)
            where, params = self._compile(tree, conn)
            rows = conn.execute(
                """
                SELECT o.id, o.name, o.object_type, o.created_at, o.updated_at
                FROM object AS o
                WHERE """
                + where
                + " ORDER BY o.name COLLATE NOCASE, o.id",
                params,
            ).fetchall()
        return [
            Object(
                id=row["id"],
                name=row["name"],
                object_type=ObjectType(row["object_type"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    # --- Compilazione -------------------------------------------------------

    def _compile(
        self, node: Node, conn: sqlite3.Connection
    ) -> tuple[str, list[object]]:
        if isinstance(node, Group):
            return self._compile(node.node, conn)
        if isinstance(node, Condition):
            if node.wildcard:
                return "1", []
            placement_ids = self._matching_placements(conn, node.segments)
            if not placement_ids:
                return "0", []
            placeholders = ", ".join("?" for _ in placement_ids)
            sql = (
                "EXISTS (SELECT 1 FROM tagging AS g "
                "WHERE g.object_id = o.id AND g.placement_id IN ("
                + placeholders
                + "))"
            )
            return sql, list(placement_ids)
        if isinstance(node, AttributeCondition):
            return self._compile_attribute(node, conn)
        if isinstance(node, Not):
            inner, params = self._compile(node.node, conn)
            return f"NOT ({inner})", params
        if isinstance(node, And):
            left, left_params = self._compile(node.left, conn)
            right, right_params = self._compile(node.right, conn)
            return f"({left}) AND ({right})", left_params + right_params
        if isinstance(node, Or):
            left, left_params = self._compile(node.left, conn)
            right, right_params = self._compile(node.right, conn)
            return f"({left}) OR ({right})", left_params + right_params
        raise TypeError(f"Nodo di query sconosciuto: {type(node)!r}")

    def _compile_attribute(
        self, node: AttributeCondition, conn: sqlite3.Connection
    ) -> tuple[str, list[object]]:
        """Compila una condizione su attributo in SQL."""
        # Determina il tipo dell'attributo per validare l'operatore (R47)
        value_type = self._attribute_type(conn, node.namespace, node.key)

        # Valida l'operatore in base al tipo (R47)
        if node.operator in (">", "<", ">=", "<="):
            if value_type is None or not is_comparable(value_type):
                raise ValidationError(
                    f"L'operatore '{node.operator}' non è ammesso per l'attributo "
                    f"'{node.key}' (tipo: {value_type or 'sconosciuto'})"
                )

        # Costruisci la sottoquery EXISTS su object_attribute
        namespace_clause = (
            "a.namespace IS NULL" if node.namespace is None
            else "a.namespace = ? COLLATE NOCASE"
        )
        params: list[object] = []
        if node.namespace is not None:
            params.append(node.namespace)

        # Per confronti numerici o date, confronta il valore direttamente
        # Per uguaglianza, confronto esatto
        op_sql = node.operator
        if op_sql == "!=":
            # NOT EXISTS con uguaglianza, oppure EXISTS con valore diverso
            # Usiamo: NOT EXISTS (SELECT 1 ... WHERE value = ?)
            sql = (
                "NOT EXISTS (SELECT 1 FROM object_attribute AS a "
                "WHERE a.object_id = o.id AND a.key = ? COLLATE NOCASE "
                f"AND {namespace_clause} AND a.value = ?)"
            )
            params = [node.key] + params + [node.value]
            return sql, params

        sql = (
            "EXISTS (SELECT 1 FROM object_attribute AS a "
            "WHERE a.object_id = o.id AND a.key = ? COLLATE NOCASE "
            f"AND {namespace_clause} AND a.value {op_sql} ?)"
        )
        params = [node.key] + params + [node.value]
        return sql, params

    def _attribute_type(
        self, conn: sqlite3.Connection, namespace: str | None, key: str
    ) -> ValueType | None:
        """Restituisce il tipo di un attributo, o None se non definito."""
        if namespace is not None:
            # Cerca la definizione nel namespace
            row = conn.execute(
                """
                SELECT d.value_type
                FROM attribute_definition AS d
                JOIN attribute_namespace AS n ON d.namespace_id = n.id
                WHERE n.name = ? COLLATE NOCASE AND d.key = ? COLLATE NOCASE
                """,
                (namespace, key),
            ).fetchone()
            if row is not None:
                return ValueType(row["value_type"])
            return None
        else:
            # Attributo libero: cerca il tipo dal primo valore trovato
            row = conn.execute(
                "SELECT value_type FROM object_attribute "
                "WHERE namespace IS NULL AND key = ? COLLATE NOCASE "
                "LIMIT 1",
                (key,),
            ).fetchone()
            if row is not None:
                return ValueType(row["value_type"])
            return None

    def _matching_placements(
        self, conn: sqlite3.Connection, segments: tuple[str, ...]
    ) -> list[int]:
        index = PathIndex.build(_all_placements(conn), _all_tags(conn))
        target = tuple(segment.casefold() for segment in segments)
        matches = []
        for placement_id in index.placements:
            path = tuple(
                name.casefold() for name in index.names_for(placement_id)
            )
            if _contains_sequence(path, target):
                matches.append(placement_id)
        return matches

    def _resolve_tags(self, conn: sqlite3.Connection, node: Node) -> None:
        known = {
            row["name"].casefold()
            for row in conn.execute("SELECT name FROM tag").fetchall()
        }
        for segment in _condition_segments(node):
            if segment.casefold() not in known:
                raise UnknownTagError(segment)

    def _resolve_attributes(self, conn: sqlite3.Connection, node: Node) -> None:
        """Valida che i namespace e le chiavi degli attributi esistano (R48)."""
        for attr_node in _attribute_conditions(node):
            if attr_node.namespace is not None:
                # Verifica che il namespace esista
                ns_row = conn.execute(
                    "SELECT id FROM attribute_namespace WHERE name = ? COLLATE NOCASE",
                    (attr_node.namespace,),
                ).fetchone()
                if ns_row is None:
                    raise ValidationError(
                        f"Namespace inesistente: {attr_node.namespace}"
                    )
                # Verifica che la definizione esista nel namespace
                def_row = conn.execute(
                    """
                    SELECT d.id FROM attribute_definition AS d
                    JOIN attribute_namespace AS n ON d.namespace_id = n.id
                    WHERE n.name = ? COLLATE NOCASE AND d.key = ? COLLATE NOCASE
                    """,
                    (attr_node.namespace, attr_node.key),
                ).fetchone()
                if def_row is None:
                    raise ValidationError(
                        f"Attributo '{attr_node.key}' non definito nel namespace "
                        f"'{attr_node.namespace}'"
                    )


def _contains_sequence(path: tuple[str, ...], target: tuple[str, ...]) -> bool:
    size = len(target)
    if size == 0 or size > len(path):
        return False
    for start in range(len(path) - size + 1):
        if path[start : start + size] == target:
            return True
    return False


def _condition_segments(node: Node) -> list[str]:
    if isinstance(node, (Group, Not)):
        return _condition_segments(node.node)
    if isinstance(node, (And, Or)):
        return _condition_segments(node.left) + _condition_segments(node.right)
    if isinstance(node, Condition):
        return list(node.segments)
    return []


def _attribute_conditions(node: Node) -> list[AttributeCondition]:
    if isinstance(node, (Group, Not)):
        return _attribute_conditions(node.node)
    if isinstance(node, (And, Or)):
        return _attribute_conditions(node.left) + _attribute_conditions(node.right)
    if isinstance(node, AttributeCondition):
        return [node]
    return []


def _all_tags(conn: sqlite3.Connection) -> list[Tag]:
    rows = conn.execute(
        "SELECT id, name, description, is_system, created_at, updated_at FROM tag"
    ).fetchall()
    return [
        Tag(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            is_system=bool(row["is_system"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        for row in rows
    ]


def _all_placements(conn: sqlite3.Connection) -> list[Placement]:
    rows = conn.execute(
        "SELECT id, tag_id, parent_id, created_at FROM placement"
    ).fetchall()
    return [
        Placement(
            id=row["id"],
            tag_id=row["tag_id"],
            parent_id=row["parent_id"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
