"""Ricerca esplicita, sola lettura (R41-R45).

Le condizioni ``tag:percorso`` diventano una singola query SQL con ``EXISTS``.
I percorsi sono ricostruiti al momento della lettura e non vengono salvati:
restano un dato derivato.
"""

from __future__ import annotations

import sqlite3

from app.core.transaction_manager import TransactionManager

from ..models.object import Object, ObjectType
from ..models.placement import Placement
from ..models.tag import Tag
from ..query import (
    And,
    Condition,
    Group,
    Node,
    Not,
    Or,
    QueryParser,
    UnknownTagError,
)
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
