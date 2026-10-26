"""Porte dei repository."""

from .attribute_definition_repository import AttributeDefinitionRepository
from .attribute_namespace_repository import AttributeNamespaceRepository
from .local_file_object_repository import LocalFileObjectRepository
from .object_attribute_repository import ObjectAttributeRepository
from .object_repository import ObjectRepository
from .placement_repository import PlacementRepository
from .tag_repository import TagRepository
from .tagging_repository import TaggingRepository

__all__ = [
    "AttributeDefinitionRepository",
    "AttributeNamespaceRepository",
    "LocalFileObjectRepository",
    "ObjectAttributeRepository",
    "ObjectRepository",
    "PlacementRepository",
    "TagRepository",
    "TaggingRepository",
]
