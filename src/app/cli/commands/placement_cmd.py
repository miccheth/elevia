"""Comandi sui Placement."""

from __future__ import annotations

import typer

from app.cli.output import console, print_placements, print_preview
from app.core.bootstrap import get_container
from app.core.exceptions import ValidationError

app = typer.Typer(help="Placement: creazione, spostamento, eliminazione.")


@app.command("list")
def list_placements() -> None:
    """Elenca i Placement con percorso e assegnazioni."""
    container = get_container()
    print_placements(container.placement_service.describe())


@app.command("add")
def add(
    path: str = typer.Argument(
        ..., help="Percorso, per esempio Lavoro.Ferrari, oppure nome/ID del Tag"
    ),
    parent: str | None = typer.Option(
        None, "--parent", "-p", help="Placement padre: ID o percorso"
    ),
    create_tags: bool = typer.Option(
        False, "--create-tags", help="Crea il Tag mancante"
    ),
) -> None:
    """Crea una collocazione usando un percorso."""
    container = get_container()
    raw = path.strip()
    if not raw:
        raise ValidationError("Il percorso del Placement non può essere vuoto")
    if parent is not None and "." in raw:
        raise ValidationError("Usa il percorso oppure --parent, non entrambi")

    if parent is not None:
        parent_id = container.placement_service.resolve(parent).id
        tag_token = raw
    elif "." in raw:
        parent_token, _, tag_token = raw.rpartition(".")
        if not parent_token or not tag_token:
            raise ValidationError(f"Percorso non valido: {raw}")
        parent_id = container.placement_service.resolve(parent_token).id
    else:
        parent_id = None
        tag_token = raw

    placement = container.placement_service.create_placement_for_tag(
        tag_token, parent_id, create_tag=create_tags
    )
    created_id = placement.id or 0
    console.print(
        f"[green]Creato[/green] Placement {created_id}: "
        f"{container.placement_service.path_for(created_id)}"
    )


@app.command("move")
def move(
    placement: str = typer.Argument(..., help="ID o percorso del Placement"),
    parent: str | None = typer.Option(
        None, "--parent", "-p", help="Nuovo padre: ID o percorso; assente = radice"
    ),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Sposta un ramo, conservando identità, figli e assegnazioni."""
    container = get_container()
    current = container.placement_service.resolve(placement)
    parent_placement = (
        container.placement_service.resolve(parent) if parent is not None else None
    )
    new_parent_id = parent_placement.id if parent_placement is not None else None
    preview = container.previews.preview_move_placement(current.id, new_parent_id)
    print_preview(preview)
    if preview.conflicts:
        raise typer.Exit(code=1)
    if not yes and not typer.confirm("Confermare lo spostamento?"):
        raise typer.Abort()
    moved = container.placement_service.move(current.id, new_parent_id, preview)
    console.print(f"[green]Spostato[/green] Placement {moved.id}")


@app.command("delete")
def delete(
    placement: str = typer.Argument(..., help="ID o percorso del Placement"),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Elimina un Placement senza figli e senza assegnazioni."""
    container = get_container()
    current = container.placement_service.resolve(placement)
    preview = container.previews.preview_delete_placement(current.id)
    print_preview(preview)
    if preview.conflicts:
        raise typer.Exit(code=1)
    if not yes and not typer.confirm(f"Eliminare il Placement {current.id}?"):
        raise typer.Abort()
    container.placement_service.delete(current.id)
    console.print(f"[green]Eliminato[/green] Placement {current.id}")


@app.command("create", hidden=True)
def create_legacy(
    path: str = typer.Argument(...),
    parent: str | None = typer.Option(None, "--parent", "-p"),
    create_tags: bool = typer.Option(False, "--create-tags"),
) -> None:
    """Alias di add."""
    add(path, parent, create_tags)
