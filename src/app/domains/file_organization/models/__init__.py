"""Entità di dominio di Elevia."""

from .local_file_object import LocalFileObject
from .object import Object, ObjectType
from .placement import Placement
from .tag import Tag
from .tagging import Tagging

__all__ = [
    "LocalFileObject",
    "Object",
    "ObjectType",
    "Placement",
    "Tag",
    "Tagging",
]
