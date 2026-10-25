"""TransactionManager: atomicità, validazione finale e anteprime.

Ogni scrittura passa da ``run``: la transazione è una sola (R34), qualunque
errore annulla tutto (R35) e l'eventuale anteprima viene ricontrollata contro
lo stato corrente (R38, R39). I controlli sui cicli (R30-R33) girano sullo
stato finale, dopo le modifiche e prima del commit.
"""

from __future__ import annotations

import hashlib
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, TypeVar

from .exceptions import (
    ConflictError,
    CycleError,
    PreviewStaleError,
)

T = TypeVar("T")


@dataclass(frozen=True)
class PlanPreview:
    """Anteprima di un'operazione strutturale.

    Il token è monouso. Il fingerprint fotografia lo stato usato per
    calcolare l'impatto: se al momento della conferma lo stato è diverso, la
    conferma viene rifiutata.
    """

    token: str
    operation: str
    fingerprint: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    impacts: tuple[dict[str, Any], ...] = ()
    conflicts: tuple[str, ...] = ()


class TransactionManager:
    """Esegue operazioni atomiche e applica i controlli globali."""

    def __init__(self, database: Any) -> None:
        self._database = database
        self._used_previews: set[str] = set()

    @contextmanager
    def read(self) -> Iterator[sqlite3.Connection]:
        """Connessione per le letture, senza transazione esplicita."""
        with self._database.session() as conn:
            yield conn

    def run(
        self,
        work: Callable[[sqlite3.Connection], T],
        *,
        before: Callable[[sqlite3.Connection], None] | None = None,
        after: Callable[[sqlite3.Connection], None] | None = None,
        preview: PlanPreview | None = None,
    ) -> T:
        """Esegue ``work`` in una transazione tutto-o-niente.

        ``before`` ricontrolla le precondizioni, ``after`` valida lo stato
        finale. Un errore in uno dei due passaggi annulla ogni modifica.
        """
        with self._database.session() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                if preview is not None:
                    self._check_preview(conn, preview)
                if before is not None:
                    before(conn)
                result = work(conn)
                if after is not None:
                    after(conn)
                if preview is not None:
                    self._used_previews.add(preview.token)
                conn.commit()
                return result
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                raise ConflictError(f"Vincolo del database violato: {exc}") from exc
            except Exception:
                conn.rollback()
                raise

    def fingerprint(self) -> str:
        """Fingerprint dello stato strutturale corrente."""
        with self._database.session() as conn:
            return state_fingerprint(conn)

    def _check_preview(self, conn: sqlite3.Connection, preview: PlanPreview) -> None:
        if preview.token in self._used_previews:
            raise PreviewStaleError("Anteprima già utilizzata: generane una nuova")
        if state_fingerprint(conn) != preview.fingerprint:
            raise PreviewStaleError(
                "I dati sono cambiati dopo l'anteprima: conferma rifiutata"
            )

    # --- Controlli globali sullo stato finale -------------------------------

    def assert_object_has_tagging(
        self, conn: sqlite3.Connection, object_id: int
    ) -> None:
        """R1: un Object registrato ha almeno una Tagging."""
        row = conn.execute(
            "SELECT COUNT(*) AS total FROM tagging WHERE object_id = ?",
            (object_id,),
        ).fetchone()
        if row["total"] == 0:
            raise ConflictError(
                "Un Object registrato deve avere almeno un'assegnazione (R1)"
            )

    def assert_placement_acyclic(self, conn: sqlite3.Connection) -> None:
        """R30: nessun ciclo nella gerarchia dei Placement."""
        rows = conn.execute("SELECT id, parent_id FROM placement").fetchall()
        parents = {row["id"]: row["parent_id"] for row in rows}
        for start in parents:
            seen: list[int] = []
            current: int | None = start
            while current is not None:
                if current in seen:
                    cycle = seen[seen.index(current) :] + [current]
                    raise CycleError(
                        "Ciclo tra Placement: "
                        + " -> ".join(str(item) for item in cycle)
                    )
                seen.append(current)
                current = parents.get(current)

    def assert_tag_graph_acyclic(self, conn: sqlite3.Connection) -> None:
        """R31/R32: il grafo delle identità dei Tag resta aciclico."""
        rows = conn.execute(
            """
            SELECT parent.tag_id AS parent_tag, child.tag_id AS child_tag
            FROM placement AS child
            JOIN placement AS parent ON child.parent_id = parent.id
            """
        ).fetchall()
        edges: dict[int, set[int]] = {}
        for row in rows:
            edges.setdefault(row["parent_tag"], set()).add(row["child_tag"])

        visiting: set[int] = set()
        visited: set[int] = set()
        stack: list[int] = []

        def visit(tag_id: int) -> None:
            if tag_id in visited:
                return
            if tag_id in visiting:
                cycle = stack[stack.index(tag_id) :] + [tag_id]
                raise CycleError(
                    "Ciclo tra identità dei Tag: "
                    + " -> ".join(str(item) for item in cycle)
                )
            visiting.add(tag_id)
            stack.append(tag_id)
            for child in edges.get(tag_id, set()):
                visit(child)
            stack.pop()
            visiting.remove(tag_id)
            visited.add(tag_id)

        for tag_id in list(edges):
            visit(tag_id)

    def assert_placement_deletable(
        self, conn: sqlite3.Connection, placement_id: int
    ) -> None:
        """R20: niente figli e niente assegnazioni."""
        children = conn.execute(
            "SELECT COUNT(*) AS total FROM placement WHERE parent_id = ?",
            (placement_id,),
        ).fetchone()["total"]
        if children:
            raise ConflictError(
                "Il Placement ha figli: risolvili prima di eliminarlo (R20)"
            )
        taggings = conn.execute(
            "SELECT COUNT(*) AS total FROM tagging WHERE placement_id = ?",
            (placement_id,),
        ).fetchone()["total"]
        if taggings:
            raise ConflictError(
                "Il Placement ha assegnazioni: risolvile prima di eliminarlo (R20)"
            )


def state_fingerprint(conn: sqlite3.Connection) -> str:
    """Hash deterministico delle tabelle che influenzano la struttura."""
    digest = hashlib.sha256()
    queries = (
        "SELECT id, name, is_system FROM tag ORDER BY id",
        "SELECT id, tag_id, parent_id FROM placement ORDER BY id",
        "SELECT id, object_id, placement_id FROM tagging ORDER BY id",
    )
    for query in queries:
        for row in conn.execute(query):
            digest.update(repr(tuple(row)).encode("utf-8"))
            digest.update(b"\n")
    return digest.hexdigest()
