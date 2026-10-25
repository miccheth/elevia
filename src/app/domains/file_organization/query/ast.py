"""Albero sintattico delle query."""

from __future__ import annotations

from dataclasses import dataclass


class Node:
    """Nodo dell'albero sintattico."""


@dataclass(frozen=True)
class Condition(Node):
    """Condizione ``tag:percorso``."""

    segments: tuple[str, ...] = ()
    wildcard: bool = False


@dataclass(frozen=True)
class Group(Node):
    """Espressione tra parentesi."""

    node: Node


@dataclass(frozen=True)
class Not(Node):
    """Negazione di un nodo."""

    node: Node


@dataclass(frozen=True)
class And(Node):
    """Intersezione tra due nodi."""

    left: Node
    right: Node


@dataclass(frozen=True)
class Or(Node):
    """Unione tra due nodi."""

    left: Node
    right: Node
