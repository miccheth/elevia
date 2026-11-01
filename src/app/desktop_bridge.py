"""Operazioni sul vocabolario richieste dall'app desktop tramite JSON."""

from __future__ import annotations

import json
import sys
from typing import Any

from app.core.bootstrap import get_container


def handle(request: dict[str, Any]) -> list[dict[str, Any]]:
    """Esegue un'operazione e restituisce l'albero aggiornato."""
    container = get_container()
    action = request["action"]
    if action == "create":
        container.placement_service.create_placement_for_tag(
            request["name"], request.get("parentId"), create_tag=True
        )
    elif action == "rename":
        container.tag_service.rename(request["tagId"], request["name"])
    elif action == "delete":
        container.placement_service.delete(request["placementId"])
    elif action != "list":
        raise ValueError("Operazione non riconosciuta")

    tags = {tag.id: tag for tag in container.tag_service.list_tags()}
    return [
        {
            "id": row["id"],
            "tagId": row["tag_id"],
            "parentId": row["parent_id"],
            "name": tags[row["tag_id"]].name,
        }
        for row in container.placement_service.describe()
        if not tags[row["tag_id"]].is_system
    ]


def main() -> None:
    """Legge una richiesta e scrive una risposta JSON."""
    try:
        response = {"items": handle(json.load(sys.stdin))}
    except Exception as exc:
        response = {"error": str(exc)}
    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()
