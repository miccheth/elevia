"""Comando di reset completo dei dati Elevia."""

from __future__ import annotations

import typer

from app.cli.output import console
from app.core.bootstrap import reset_container


def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Non chiedere conferma"),
) -> None:
    """Elimina tutti i dati e ricrea il database iniziale."""
    if not yes and not typer.confirm(
        "Cancellare tutti i dati Elevia? I file originali non verranno toccati"
    ):
        raise typer.Abort()
    container = reset_container()
    console.print(
        f"[green]Reset completato[/green] Database ricreato: "
        f"{container.settings.db_path}"
    )
