"""Composizione delle dipendenze del Core."""

from __future__ import annotations

from app.domains.file_organization.services.attribute_definition_service import (
    AttributeDefinitionService,
)
from app.domains.file_organization.services.attribute_namespace_service import (
    AttributeNamespaceService,
)
from app.domains.file_organization.services.local_file_object_service import (
    LocalFileObjectService,
)
from app.domains.file_organization.services.object_attribute_service import (
    ObjectAttributeService,
)
from app.domains.file_organization.services.object_service import ObjectService
from app.domains.file_organization.services.placement_service import PlacementService
from app.domains.file_organization.services.preview_service import PreviewService
from app.domains.file_organization.services.query_service import QueryService
from app.domains.file_organization.services.tag_placement_tree_service import (
    TagPlacementTreeService,
)
from app.domains.file_organization.services.tag_service import TagService
from app.domains.file_organization.services.tagging_service import TaggingService
from app.infrastructure.database import Database
from app.infrastructure.repositories.sqlite import (
    SqliteAttributeDefinitionRepository,
    SqliteAttributeNamespaceRepository,
    SqliteLocalFileObjectRepository,
    SqliteObjectAttributeRepository,
    SqliteObjectRepository,
    SqlitePlacementRepository,
    SqliteTaggingRepository,
    SqliteTagRepository,
)
from app.infrastructure.watchers.local_file_available_check import (
    LocalFileAvailableCheck,
)
from config.settings import Settings

from .transaction_manager import TransactionManager


class Container:
    """Wiring unico dei repository e dei servizi."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.database = Database(settings.db_path)
        self.transaction_manager = TransactionManager(self.database)

        self.objects = SqliteObjectRepository(self.database)
        self.local_files = SqliteLocalFileObjectRepository(self.database)
        self.tags = SqliteTagRepository(self.database)
        self.placements = SqlitePlacementRepository(self.database)
        self.taggings = SqliteTaggingRepository(self.database)
        self.attribute_namespaces = SqliteAttributeNamespaceRepository(self.database)
        self.attribute_definitions = SqliteAttributeDefinitionRepository(self.database)
        self.object_attributes = SqliteObjectAttributeRepository(self.database)

        self.previews = PreviewService(
            self.transaction_manager, self.tags, self.placements, self.taggings
        )
        self.object_service = ObjectService(
            self.objects,
            self.local_files,
            self.taggings,
            self.tags,
            self.placements,
            self.transaction_manager,
            self.previews,
        )
        self.local_file_service = LocalFileObjectService(
            self.objects,
            self.local_files,
            self.taggings,
            self.tags,
            self.placements,
            self.transaction_manager,
            self.previews,
        )
        self.tag_service = TagService(
            self.tags,
            self.placements,
            self.transaction_manager,
            self.previews,
        )
        self.placement_service = PlacementService(
            self.tags,
            self.placements,
            self.transaction_manager,
            self.previews,
        )
        self.tagging_service = TaggingService(
            self.objects,
            self.tags,
            self.placements,
            self.taggings,
            self.transaction_manager,
        )
        self.tree_service = TagPlacementTreeService(
            self.tags, self.placements, self.taggings
        )
        self.attribute_namespace_service = AttributeNamespaceService(
            self.attribute_namespaces,
            self.transaction_manager,
        )
        self.attribute_definition_service = AttributeDefinitionService(
            self.attribute_definitions,
            self.attribute_namespaces,
            self.transaction_manager,
        )
        self.object_attribute_service = ObjectAttributeService(
            self.object_attributes,
            self.attribute_definitions,
            self.attribute_namespaces,
            self.objects,
            self.transaction_manager,
        )
        self.query_service = QueryService(self.transaction_manager)
        self._available_check: LocalFileAvailableCheck | None = None

    def available_check(self) -> LocalFileAvailableCheck:
        """Restituisce il controllo di disponibilità dei file registrati."""
        if self._available_check is None:
            self._available_check = LocalFileAvailableCheck(
                self.local_file_service, self.local_files
            )
        return self._available_check
