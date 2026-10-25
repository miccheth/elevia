"""Comandi sui Tag."""

from __future__ import annotations

import typer

from app.cli.output import console, print_preview, print_tags
from app.core.bootstrap import get_container

app = typer.Typer(help="Tag: creazione, rinomina, eliminazione.")


@app.command("list")
def list_tags() -> None:
    """Elenca i Tag del vocabolario."""
    container = get_container()
    print_tags(container.tag_service.list_tags())


@app.command("create")
def create(
    name: str = typer.Argument(...),
    description: str | None = typer.Option(None, "--description", "-d"),
) -> None:
    """Crea un Tag senza Placement."""
    container = get_container()
    tag = container.tag_service.create(name, description)
    console.print(f"[green]Creato[/green] Tag {tag.id}: {tag.name}")


@app.command("rename")
def rename(
    tag: str = typer.Argument(..., help="ID o nome del Tag"),
    name: str = typer.Argument(...),
) -> None:
    """Rinomina un Tag; le assegnazioni restano valide."""
    container = get_container()
    resolved = container.tag_service.resolve(tag)
    renamed = container.tag_service.rename(resolved.id, name)
    console.print(f"[green]Rinominato[/green] Tag {renamed.id}: {renamed.name}")


@app.command("delete")
def delete(
    tag: str = typer.Argument(..., help="ID o nome del Tag"),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Elimina un Tag solo se non ha Placement."""
    container = get_container()
    resolved = container.tag_service.resolve(tag)
    preview = container.previews.preview_delete_tag(resolved.id)
    print_preview(preview)
    if preview.conflicts:
        raise typer.Exit(code=1)
    if not yes and not typer.confirm(f"Eliminare il Tag '{resolved.name}'?"):
        raise typer.Abort()
    container.tag_service.delete(resolved.id)
    console.print(f"[green]Eliminato[/green] Tag {resolved.id}")
