"""Comandi di importazione dei file locali."""

from __future__ import annotations

from pathlib import Path

import typer

from app.cli.output import console
from app.core.bootstrap import get_container

app = typer.Typer(help="Importa file nel catalogo logico, senza spostarli.")


@app.command("file")
def import_file(
    path: Path = typer.Argument(..., resolve_path=True, help="File da importare"),
    name: str | None = typer.Option(None, "--name", "-n", help="Nome logico"),
    placement: list[int] = typer.Option(
        [],
        "--placement",
        "-p",
        help="ID del Placement; se assente l'oggetto va in Untagged",
    ),
) -> None:
    """Registra un file locale con almeno una assegnazione."""
    container = get_container()
    created = container.local_file_service.register(path, name, placement)
    console.print(
        f"[green]Importato[/green] Object {created.id}: {created.name} "
        f"({created.file_path})"
    )
