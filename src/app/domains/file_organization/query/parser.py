"""Parser della sintassi di ricerca.

Grammatica:

    query     = or_expr ;
    or_expr   = and_expr , { "OR" , and_expr } ;
    and_expr  = term , { "AND" , term } ;
    term      = [ "NOT" ] , atom ;
    atom      = "(" , query , ")" | condition ;
    condition = "tag:" , value ;
    value     = "*" | name , { "." , name } ;
    name      = parola | '"' , testo , '"' ;

Lo stile richiesto impone le parentesi quando si combinano più condizioni:
``tag:A AND tag:B`` è un errore, ``(tag:A) AND (tag:B)`` è valido.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ast import And, Condition, Group, Node, Not, Or
from .errors import QuerySyntaxError


@dataclass(frozen=True)
class _Token:
    kind: str
    value: str
    position: int


class QueryParser:
    """Trasforma un'espressione in un albero sintattico."""

    def __init__(self, text: str) -> None:
        self._text = text
        self._tokens = list(_tokenize(text))
        self._index = 0

    def parse(self) -> Node:
        """Restituisce la radice dell'albero."""
        if not self._tokens:
            raise QuerySyntaxError("espressione vuota", 0)
        node = self._parse_or()
        if self._peek() is not None:
            token = self._peek()
            assert token is not None
            raise QuerySyntaxError(
                f"token inatteso '{token.value or token.kind}'", token.position
            )
        return node

    # --- Grammatica ---------------------------------------------------------

    def _parse_or(self) -> Node:
        left = self._parse_and()
        while self._match("OR"):
            right = self._parse_and()
            self._require_grouped(left)
            self._require_grouped(right)
            left = Or(left, right)
        return left

    def _parse_and(self) -> Node:
        left = self._parse_term()
        while self._match("AND"):
            right = self._parse_term()
            self._require_grouped(left)
            self._require_grouped(right)
            left = And(left, right)
        return left

    def _parse_term(self) -> Node:
        if self._match("NOT"):
            return Not(self._parse_atom())
        return self._parse_atom()

    def _parse_atom(self) -> Node:
        if self._match("LPAREN"):
            if self._peek_kind("RPAREN"):
                raise QuerySyntaxError("parentesi vuote", self._position())
            node = self._parse_or()
            self._expect("RPAREN", "parentesi di chiusura mancante")
            return Group(node)
        return self._parse_condition()

    def _parse_condition(self) -> Node:
        self._expect("TAG", "attesa la parola chiave 'tag:'")
        if self._match("STAR"):
            token = self._peek()
            if token is not None and token.kind in {"DOT", "WORD", "QUOTED"}:
                raise QuerySyntaxError(
                    "la wildcard non può essere combinata con un percorso",
                    token.position,
                )
            return Condition(wildcard=True)

        first = self._parse_name()
        segments = [first]
        while self._match("DOT"):
            segments.append(self._parse_name())
        return Condition(segments=tuple(segments))

    def _parse_name(self) -> str:
        if self._match("QUOTED"):
            value = self._previous().value
            if not value.strip():
                raise QuerySyntaxError("nome vuoto", self._previous().position)
            return value
        if self._match("WORD"):
            return self._previous().value
        token = self._peek()
        position = token.position if token is not None else len(self._text)
        raise QuerySyntaxError("atteso un nome di Tag", position)

    # --- Supporto -----------------------------------------------------------

    def _require_grouped(self, node: Node) -> None:
        if isinstance(node, Group):
            return
        if isinstance(node, Not) and isinstance(node.node, Group):
            return
        token = self._peek()
        position = token.position if token is not None else len(self._text)
        raise QuerySyntaxError(
            "le condizioni combinate richiedono le parentesi", position
        )

    def _peek(self) -> _Token | None:
        if self._index >= len(self._tokens):
            return None
        return self._tokens[self._index]

    def _peek_kind(self, kind: str) -> bool:
        token = self._peek()
        return token is not None and token.kind == kind

    def _previous(self) -> _Token:
        return self._tokens[self._index - 1]

    def _match(self, kind: str) -> bool:
        if self._peek_kind(kind):
            self._index += 1
            return True
        return False

    def _expect(self, kind: str, message: str) -> _Token:
        if not self._match(kind):
            raise QuerySyntaxError(message, self._position())
        return self._previous()

    def _position(self) -> int:
        token = self._peek()
        if token is not None:
            return token.position
        return len(self._text)


def _tokenize(text: str) -> list[_Token]:
    tokens: list[_Token] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char == "(":
            tokens.append(_Token("LPAREN", char, index))
            index += 1
            continue
        if char == ")":
            tokens.append(_Token("RPAREN", char, index))
            index += 1
            continue
        if char == "*":
            tokens.append(_Token("STAR", char, index))
            index += 1
            continue
        if char == ".":
            tokens.append(_Token("DOT", char, index))
            index += 1
            continue
        if char == '"':
            start = index
            index += 1
            value_start = index
            while index < length and text[index] != '"':
                index += 1
            if index >= length:
                raise QuerySyntaxError("virgolette non chiuse", start)
            value = text[value_start:index]
            index += 1
            tokens.append(_Token("QUOTED", value, start))
            continue
        if char == ":":
            raise QuerySyntaxError("':' inatteso", index)

        start = index
        while index < length:
            current = text[index]
            if current.isspace() or current in '()"*.:':
                break
            index += 1
        word = text[start:index]
        if not word:
            raise QuerySyntaxError(f"carattere inatteso '{char}'", start)

        lowered = word.lower()
        if lowered in {"and", "or", "not"}:
            tokens.append(_Token(lowered.upper(), word, start))
        elif (
            lowered == "tag"
            and index < length
            and text[index] == ":"
        ):
            index += 1
            tokens.append(_Token("TAG", "tag:", start))
        else:
            tokens.append(_Token("WORD", word, start))
    return tokens
