"""Comando di visualizzazione dell'albero delle collocazioni."""

from __future__ import annotations

from app.cli.output import print_tree
from app.core.bootstrap import get_container


def tree() -> None:
    """Mostra l'albero dei Placement."""
    container = get_container()
    print_tree(container.tree_service.get_tree())
