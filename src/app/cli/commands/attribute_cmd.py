"""Comandi CLI per la gestione degli attributi."""

from __future__ import annotations

import typer

from app.cli.output import console
from app.core.bootstrap import get_container
from app.domains.file_organization.models.attribute_definition import ValueType

app = typer.Typer(help="Attributi: namespace, definizioni e valori sugli oggetti.")
namespace_app = typer.Typer(help="Gestione dei namespace (template di attributi).")
definition_app = typer.Typer(help="Gestione delle definizioni di attributi.")
value_app = typer.Typer(help="Assegnazione di valori agli oggetti.")

app.add_typer(namespace_app, name="namespace")
app.add_typer(definition_app, name="def")
app.add_typer(value_app, name="set")


# --- Namespace ---------------------------------------------------------------

@namespace_app.command("list")
def namespace_list() -> None:
    """Elenca tutti i namespace."""
    container = get_container()
    namespaces = container.attribute_namespace_service.list_all()
    if not namespaces:
        console.print("[yellow]Nessun namespace definito[/yellow]")
        return
    for ns in namespaces:
        desc = f" — {ns.description}" if ns.description else ""
        console.print(f"  [bold]{ns.name}[/bold]{desc} (id {ns.id})")


@namespace_app.command("add")
def namespace_add(
    name: str = typer.Argument(..., help="Nome del namespace"),
    description: str | None = typer.Option(None, "--description", "-d"),
) -> None:
    """Crea un nuovo namespace."""
    container = get_container()
    created = container.attribute_namespace_service.create(name, description)
    console.print(f"[green]Creato[/green] namespace '{created.name}' (id {created.id})")


@namespace_app.command("delete")
def namespace_delete(
    name: str = typer.Argument(..., help="Nome del namespace"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Non chiedere conferma"),
) -> None:
    """Elimina un namespace e tutti i suoi attributi (CASCADE)."""
    container = get_container()
    ns = container.attribute_namespace_service.get_by_name(name)
    if not yes and not typer.confirm(
        f"Eliminare il namespace '{ns.name}'? Verranno eliminati anche tutti "
        f"i suoi attributi e i valori sugli oggetti."
    ):
        raise typer.Abort()
    container.attribute_namespace_service.delete(ns.id)
    console.print(f"[green]Eliminato[/green] namespace '{ns.name}'")


# --- Definizioni -------------------------------------------------------------

@definition_app.command("list")
def definition_list(
    namespace: str = typer.Argument(..., help="Nome del namespace"),
) -> None:
    """Elenca le definizioni di attributi in un namespace."""
    container = get_container()
    ns = container.attribute_namespace_service.get_by_name(namespace)
    definitions = container.attribute_definition_service.list_by_namespace(ns.id)
    if not definitions:
        console.print(f"[yellow]Nessuna definizione nel namespace '{namespace}'[/yellow]")
        return
    for d in definitions:
        type_str = str(d.value_type)
        if d.value_type == ValueType.ENUM and d.allowed_values:
            values_str = ", ".join(str(v) for v in d.allowed_values)
            type_str = f"ENUM [{values_str}]"
        elif d.value_type == ValueType.ENUM:
            type_str = "ENUM [nessun valore definito]"
        desc = f" — {d.description}" if d.description else ""
        console.print(f"  [bold]{d.key}[/bold]: {type_str}{desc}")


@definition_app.command("add")
def definition_add(
    namespace: str = typer.Argument(..., help="Nome del namespace"),
    key: str = typer.Argument(..., help="Chiave dell'attributo"),
    type_: str = typer.Option(
        "TEXT",
        "--type",
        "-t",
        help="Tipo: TEXT, NUMBER, DATE, BOOLEAN, ENUM",
    ),
    values: str | None = typer.Option(
        None,
        "--values",
        "-v",
        help="Valori possibili per ENUM (separati da virgola)",
    ),
    description: str | None = typer.Option(None, "--description", "-d"),
) -> None:
    """Definisce un attributo in un namespace."""
    container = get_container()
    ns = container.attribute_namespace_service.get_by_name(namespace)

    try:
        value_type = ValueType(type_.upper())
    except ValueError:
        valid = ", ".join(v.value for v in ValueType)
        console.print(f"[red]Tipo non valido: {type_}. Valori ammessi: {valid}[/red]")
        raise typer.Exit(1)

    allowed_values = None
    if values is not None:
        allowed_values = [v.strip() for v in values.split(",") if v.strip()]

    created = container.attribute_definition_service.create(
        namespace_id=ns.id,
        key=key,
        value_type=value_type,
        allowed_values=allowed_values,
        description=description,
    )
    console.print(
        f"[green]Definito[/green] attributo '{namespace}.{created.key}' "
        f"(tipo {created.value_type})"
    )


@definition_app.command("delete")
def definition_delete(
    namespace: str = typer.Argument(..., help="Nome del namespace"),
    key: str = typer.Argument(..., help="Chiave dell'attributo"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Non chiedere conferma"),
) -> None:
    """Elimina una definizione di attributo (CASCADE sui valori)."""
    container = get_container()
    ns = container.attribute_namespace_service.get_by_name(namespace)
    definition = container.attribute_definition_service.get_by_key(ns.id, key)
    if not yes and not typer.confirm(
        f"Eliminare l'attributo '{namespace}.{key}'? Verranno eliminati "
        f"anche i valori sugli oggetti."
    ):
        raise typer.Abort()
    container.attribute_definition_service.delete(definition.id)
    console.print(f"[green]Eliminato[/green] attributo '{namespace}.{key}'")


# --- Valori sugli oggetti -----------------------------------------------------

@value_app.command("set")
def value_set(
    object_id: int = typer.Argument(..., help="ID dell'oggetto"),
    key: str = typer.Argument(..., help="Chiave: 'namespace.chiave' o 'chiave' (libero)"),
    value: str = typer.Argument(..., help="Valore da assegnare"),
) -> None:
    """Assegna un attributo a un oggetto.

    Con namespace: la definizione deve esistere.
    Senza namespace: attributo libero, il tipo viene dedotto automaticamente.
    """
    container = get_container()
    attr = container.object_attribute_service.set(object_id, key, value)
    console.print(
        f"[green]Assegnato[/green] {attr.full_key} = {attr.value} "
        f"(tipo {attr.value_type})"
    )


@value_app.command("unset")
def value_unset(
    object_id: int = typer.Argument(..., help="ID dell'oggetto"),
    key: str = typer.Argument(..., help="Chiave: 'namespace.chiave' o 'chiave' (libero)"),
) -> None:
    """Rimuove un attributo da un oggetto."""
    container = get_container()
    container.object_attribute_service.unset(object_id, key)
    console.print(f"[green]Rimosso[/green] {key} dall'oggetto {object_id}")


@value_app.command("show")
def value_show(
    object_id: int = typer.Argument(..., help="ID dell'oggetto"),
) -> None:
    """Mostra tutti gli attributi di un oggetto."""
    container = get_container()
    obj = container.object_service.get(object_id)
    attributes = container.object_attribute_service.list_for_object(object_id)
    console.print(f"[bold]Object {obj.id}[/bold]: {obj.name}")
    if not attributes:
        console.print("  [yellow]Nessun attributo[/yellow]")
        return
    for attr in attributes:
        if attr.namespace:
            console.print(
                f"  [bold]{attr.namespace}.{attr.key}[/bold] = {attr.value} "
                f"[dim]({attr.value_type})[/dim]"
            )
        else:
            console.print(
                f"  [bold]{attr.key}[/bold] = {attr.value} "
                f"[dim]({attr.value_type}, libero)[/dim]"
            )
