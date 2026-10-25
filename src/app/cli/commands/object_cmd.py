"""Comandi sugli Object e sulle loro assegnazioni."""

from __future__ import annotations

from pathlib import Path

import typer

from app.cli.output import console, print_local_files, print_objects
from app.core.bootstrap import get_container

app = typer.Typer(help="Object: elenco, dettagli, rinomina, rimozione.")
file_app = typer.Typer(help="File locali degli Object.")
app.add_typer(file_app, name="file")


def _placement_ids(container, references: list[str]) -> list[int]:
    resolved: list[int] = []
    for reference in references:
        placement = container.placement_service.resolve(reference)
        if placement.id is not None and placement.id not in resolved:
            resolved.append(placement.id)
    return resolved


@app.command("list")
def list_objects() -> None:
    """Elenca gli Object registrati."""
    container = get_container()
    print_objects(container.object_service.list_objects())


@app.command("show")
def show(object_id: int = typer.Argument(..., help="ID dell'Object")) -> None:
    """Mostra dettagli e assegnazioni di un Object."""
    container = get_container()
    obj = container.object_service.get(object_id)
    console.print(f"[bold]Object {obj.id}[/bold]: {obj.name} ({obj.object_type})")
    if obj.object_type == "LOCAL_FILE":
        local = container.local_file_service.get_local(object_id)
        console.print(f"  percorso: {local.file_path}")
        console.print(f"  disponibile: {'sì' if local.is_available else 'no'}")
    assignments = container.tagging_service.list_for_object(object_id)
    if not assignments:
        console.print("  [yellow]Nessuna assegnazione[/yellow]")
    for tagging in assignments:
        path = container.placement_service.path_for(tagging.placement_id)
        console.print(f"  placement {tagging.placement_id}: {path}")


@app.command("add")
def add(
    name: str = typer.Argument(..., help="Nome dell'Object"),
    placement: list[str] = typer.Option(
        [], "--in", "--placement", "-p", help="Placement: ID o percorso"
    ),
) -> None:
    """Registra un Object generico con almeno una assegnazione."""
    container = get_container()
    created = container.object_service.register(
        name, _placement_ids(container, placement)
    )
    console.print(f"[green]Creato[/green] Object {created.id}: {created.name}")


@app.command("import")
def import_file(
    path: Path = typer.Argument(..., resolve_path=True, help="File da importare"),
    name: str | None = typer.Option(None, "--name", "-n", help="Nome logico"),
    placement: list[str] = typer.Option(
        [], "--in", "--placement", "-p", help="Placement: ID o percorso"
    ),
) -> None:
    """Registra un file locale con almeno una assegnazione."""
    container = get_container()
    created = container.local_file_service.register(
        path, name, _placement_ids(container, placement)
    )
    console.print(
        f"[green]Importato[/green] Object {created.id}: {created.name} "
        f"({created.file_path})"
    )


@app.command("rename")
def rename(
    object_id: int = typer.Argument(...),
    name: str = typer.Argument(...),
) -> None:
    """Rinomina un Object senza cambiarne identità e associazioni."""
    container = get_container()
    updated = container.object_service.rename(object_id, name)
    console.print(f"[green]Rinominato[/green] Object {updated.id}: {updated.name}")


@app.command("delete")
def delete(
    object_id: int = typer.Argument(...),
    yes: bool = typer.Option(False, "--yes", "-y", help="Non chiedere conferma"),
) -> None:
    """Rimuove l'Object da Elevia. Il file originale resta intatto."""
    container = get_container()
    obj = container.object_service.get(object_id)
    if not yes and not typer.confirm(
        f"Rimuovere l'Object {obj.id} '{obj.name}' da Elevia? Il file non verrà toccato"
    ):
        raise typer.Abort()
    container.object_service.remove(object_id)
    console.print(f"[green]Rimosso[/green] Object {object_id}")


@app.command("assign")
def assign(
    object_id: int = typer.Argument(...),
    placement: str = typer.Argument(..., help="Placement: ID o percorso"),
) -> None:
    """Aggiunge un'assegnazione, se non esiste già."""
    container = get_container()
    target = container.placement_service.resolve(placement)
    created = container.tagging_service.assign(object_id, target.id or 0)
    console.print(
        f"[green]Assegnato[/green] Object {created.object_id} -> Placement {created.placement_id}"
    )


@app.command("transfer")
def transfer(
    object_id: int = typer.Argument(...),
    from_placement: str = typer.Argument(
        ..., help="Placement di partenza: ID o percorso"
    ),
    to_placement: str = typer.Argument(..., help="Placement di arrivo: ID o percorso"),
) -> None:
    """Trasferisce un Object da un contesto a un altro."""
    container = get_container()
    source = container.placement_service.resolve(from_placement)
    target = container.placement_service.resolve(to_placement)
    result = container.tagging_service.transfer(
        object_id, source.id or 0, target.id or 0
    )
    console.print(
        f"[green]Trasferito[/green] Object {object_id} -> Placement {target.id}"
        if result is not None
        else f"Nessuna modifica per l'Object {object_id}"
    )


@app.command("unassign")
def unassign(
    object_id: int = typer.Argument(...),
    placement: str = typer.Argument(..., help="Placement: ID o percorso"),
) -> None:
    """Rimuove un'assegnazione; l'ultima viene sostituita da Untagged."""
    container = get_container()
    target = container.placement_service.resolve(placement)
    container.tagging_service.remove(object_id, target.id or 0)
    console.print(
        f"[green]Rimosso[/green] Object {object_id} dal Placement {target.id}"
    )


@file_app.command("list")
def list_files() -> None:
    """Elenca i file locali con lo stato di disponibilità."""
    container = get_container()
    print_local_files(container.local_file_service.list_local_files())


@file_app.command("unavailable")
def file_unavailable(object_id: int = typer.Argument(...)) -> None:
    """Segnala il file come indisponibile, senza rimuoverlo dal catalogo."""
    container = get_container()
    local = container.local_file_service.mark_unavailable(object_id)
    console.print(f"[yellow]Indisponibile[/yellow] Object {local.id}")


@file_app.command("relink")
def file_relink(
    object_id: int = typer.Argument(...),
    path: Path = typer.Argument(..., resolve_path=True),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Aggiorna il percorso di un file spostato e lo rende disponibile."""
    container = get_container()
    if not yes and not typer.confirm(
        f"Aggiornare il percorso dell'Object {object_id} in '{path}'?"
    ):
        raise typer.Abort()
    local = container.local_file_service.update_path(object_id, path)
    console.print(
        f"[green]Percorso aggiornato[/green] Object {local.id}: {local.file_path}"
    )


@app.command("files", hidden=True)
def files_legacy() -> None:
    """Alias di object file list."""
    list_files()


@app.command("unavailable", hidden=True)
def unavailable_legacy(object_id: int = typer.Argument(...)) -> None:
    """Alias di object file unavailable."""
    file_unavailable(object_id)


@app.command("available", hidden=True)
def available_legacy(
    object_id: int = typer.Argument(...),
    path: Path | None = typer.Option(
        None, "--path", help="Nuovo percorso, se il file è stato spostato"
    ),
) -> None:
    """Alias di object file relink o ripristino dal percorso registrato."""
    container = get_container()
    local = container.local_file_service.mark_available(object_id, path)
    console.print(f"[green]Disponibile[/green] Object {local.id}: {local.file_path}")


@app.command("update-path", hidden=True)
def update_path_legacy(
    object_id: int = typer.Argument(...),
    path: Path = typer.Argument(..., resolve_path=True),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Alias di object file relink."""
    file_relink(object_id, path, yes)


@app.command("remove", hidden=True)
def remove_legacy(
    object_id: int = typer.Argument(...),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    """Alias di object delete."""
    delete(object_id, yes)
