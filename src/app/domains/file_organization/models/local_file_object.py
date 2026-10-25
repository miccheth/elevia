"""LocalFileObject: dettagli del file locale collegato a un Object."""

from __future__ import annotations

from dataclasses import dataclass

from .object import Object, ObjectType


@dataclass(kw_only=True)
class LocalFileObject(Object):
    """Object che estende i dettagli di un file locale.

    Elevia conserva soltanto il riferimento al file: non lo sposta, non lo
    modifica e non lo elimina mai (R6).
    """

    is_available: bool = True
    file_path: str = ""
    normalized_path: str = ""
    file_size: int = 0
    modified_at: str = ""
    file_extension: str = ""

    def __post_init__(self) -> None:
        self.object_type = ObjectType.LOCAL_FILE
