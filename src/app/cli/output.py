"""Rendering dei risultati per la CLI."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table

from app.core.transaction_manager import PlanPreview
from app.domains.file_organization.models.local_file_object import LocalFileObject
from app.domains.file_organization.models.object import Object
from app.domains.file_organization.models.tag import Tag
from app.domains.file_organization.services.tag_placement_tree_service import TreeNode

console = Console()


def print_objects(objects: list[Object]) -> None:
    """Tabella degli Object."""
    if not objects:
        console.print("[yellow]Nessun oggetto trovato[/yellow]")
        return
    table = Table(title="Object")
    table.add_column("ID", justify="right")
    table.add_column("Nome")
    table.add_column("Tipo")
    for item in objects:
        table.add_row(str(item.id), item.name, str(item.object_type))
    console.print(table)


def print_search_results(rows: list[dict[str, Any]]) -> None:
    """Tabella dei risultati con Tag e Placement associati."""
    if not rows:
        console.print("[yellow]Nessun oggetto trovato[/yellow]")
        return
    table = Table(title="Risultati")
    table.add_column("ID", justify="right")
    table.add_column("Nome")
    table.add_column("Tipo")
    table.add_column("Tag")
    table.add_column("Placement")
    for row in rows:
        table.add_row(
            str(row["id"]),
            row["nome"],
            row["tipo"],
            row["tag"],
            row["placement"],
        )
    console.print(table)


def print_local_files(files: list[LocalFileObject]) -> None:
    """Tabella dei file locali registrati."""
    if not files:
        console.print("[yellow]Nessun file registrato[/yellow]")
        return
    table = Table(title="File locali")
    table.add_column("ID", justify="right")
    table.add_column("Nome")
    table.add_column("Percorso")
    table.add_column("Disponibile")
    table.add_column("Dimensione", justify="right")
    for item in files:
        table.add_row(
            str(item.id),
            item.name,
            item.file_path,
            "yes" if item.is_available else "no",
            str(item.file_size),
        )
    console.print(table)


def print_tags(tags: list[Tag]) -> None:
    """Tabella dei Tag."""
    if not tags:
        console.print("[yellow]Nessun Tag[/yellow]")
        return
    table = Table(title="Tag")
    table.add_column("ID", justify="right")
    table.add_column("Nome")
    table.add_column("Sistema")
    table.add_column("Descrizione")
    for tag in tags:
        table.add_row(
            str(tag.id),
            tag.name,
            "sì" if tag.is_system else "no",
            tag.description or "",
        )
    console.print(table)


def print_placements(rows: list[dict[str, Any]]) -> None:
    """Tabella dei Placement con percorso e assegnazioni."""
    if not rows:
        console.print("[yellow]Nessun Placement[/yellow]")
        return
    table = Table(title="Placement")
    table.add_column("ID", justify="right")
    table.add_column("Percorso")
    table.add_column("Tag ID", justify="right")
    table.add_column("Padre", justify="right")
    table.add_column("Assegnazioni", justify="right")
    for row in rows:
        table.add_row(
            str(row["id"]),
            row["percorso"],
            str(row["tag_id"]),
            "-" if row["parent_id"] is None else str(row["parent_id"]),
            str(row["assegnazioni"]),
        )
    console.print(table)


def print_tree(nodes: list[TreeNode]) -> None:
    """Albero delle collocazioni."""
    if not nodes:
        console.print("[yellow]Albero vuoto[/yellow]")
        return
    for index, node in enumerate(nodes):
        _print_node(node, "", index == len(nodes) - 1)


def _print_node(node: TreeNode, prefix: str, is_last: bool) -> None:
    connector = "└── " if is_last else "├── "
    console.print(
        f"{prefix}{connector}{node.tag_name} "
        f"[dim](placement {node.placement_id}, oggetti {node.object_count})[/dim]"
    )
    child_prefix = prefix + ("    " if is_last else "│   ")
    for index, child in enumerate(node.children):
        _print_node(child, child_prefix, index == len(node.children) - 1)


def print_preview(preview: PlanPreview) -> None:
    """Mostra riepilogo, impatto e conflitti di un'anteprima."""
    console.print(f"[bold]Anteprima:[/bold] {preview.summary}")
    if preview.impacts:
        table = Table(title="Impatto")
        columns = list(preview.impacts[0])
        for column in columns:
            table.add_column(column)
        for impact in preview.impacts:
            table.add_row(*(str(impact.get(column, "")) for column in columns))
        console.print(table)
    if preview.conflicts:
        console.print("[bold red]Conflitti:[/bold red]")
        for conflict in preview.conflicts:
            console.print(f"  - {conflict}")


def print_error(message: str) -> None:
    """Messaggio di errore applicativo."""
    console.print(f"[bold red]Errore:[/bold red] {message}", highlight=False)
