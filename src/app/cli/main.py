"""Entry point della CLI di Elevia."""

from __future__ import annotations

import sys

import typer

from app.cli.output import print_error
from app.core.exceptions import EleviaError

from .commands import (
    attribute_cmd,
    import_cmd,
    object_cmd,
    placement_cmd,
    query_cmd,
    reset_cmd,
    tag_cmd,
    tree_cmd,
)

app = typer.Typer(
    name="elevia",
    help="Organizzazione logica di risorse tramite Tag, Placement e Tagging.",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_enable=False,
)

app.add_typer(object_cmd.app, name="object")
app.add_typer(tag_cmd.app, name="tag")
app.add_typer(placement_cmd.app, name="placement")
app.add_typer(attribute_cmd.app, name="attr")
app.command("tree")(tree_cmd.tree)
app.command("query")(query_cmd.query)
app.command("reset")(reset_cmd.reset)
app.add_typer(import_cmd.app, name="import", hidden=True)


def main() -> None:
    """Avvia la CLI traducendo gli errori di dominio in messaggi."""
    try:
        app()
    except EleviaError as exc:
        print_error(str(exc))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
