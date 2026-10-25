"""Comando di ricerca esplicita."""

from __future__ import annotations

import typer

from app.cli.output import print_search_results
from app.core.bootstrap import get_container


def query(expression: str = typer.Argument(..., help="Espressione di ricerca")) -> None:
    """Cerca gli Object e mostra Tag e Placement associati."""
    container = get_container()
    results = container.query_service.search(expression)
    placements = {row["id"]: row for row in container.placement_service.describe()}
    tags = {tag.id: tag.name for tag in container.tag_service.list_tags()}
    rows = []
    for obj in results:
        for tagging in container.tagging_service.list_for_object(obj.id):
            placement = placements.get(tagging.placement_id)
            if placement is None:  # pragma: no cover
                continue
            rows.append(
                {
                    "id": obj.id,
                    "nome": obj.name,
                    "tipo": str(obj.object_type),
                    "tag": tags.get(placement["tag_id"], f"#{placement['tag_id']}"),
                    "placement": (
                        f"{placement['percorso']} (id {tagging.placement_id})"
                    ),
                }
            )
    print_search_results(rows)
