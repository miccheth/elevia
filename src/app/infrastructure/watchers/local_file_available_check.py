"""Controllo di disponibilità dei file locali.

Confronta i percorsi registrati con il filesystem e aggiorna lo stato degli
Object. Non usa thread, observer o processi in background: viene eseguito
all'avvio della CLI. Non modifica mai il file originale (R6).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.core.exceptions import EleviaError
from app.domains.file_organization.repositories.local_file_object_repository import (
    LocalFileObjectRepository,
)
from app.domains.file_organization.services.local_file_object_service import (
    LocalFileObjectService,
)

logger = logging.getLogger(__name__)


@dataclass
class LocalFileAvailabilityReport:
    """Esito di un controllo di disponibilità."""

    available: list[int] = field(default_factory=list)
    unavailable: list[int] = field(default_factory=list)


class LocalFileAvailableCheck:
    """Controlla i file registrati e aggiorna lo stato degli Object."""

    def __init__(
        self,
        service: LocalFileObjectService,
        local_files: LocalFileObjectRepository,
    ) -> None:
        self._service = service
        self._local_files = local_files

    def scan_once(self) -> LocalFileAvailabilityReport:
        """Confronta i percorsi registrati con il filesystem."""
        report = LocalFileAvailabilityReport()
        for local in self._local_files.list_all():
            object_id = local.id or 0
            try:
                exists = Path(local.file_path).is_file()
            except OSError:
                exists = False
            if exists:
                if not local.is_available:
                    try:
                        self._service.mark_available(object_id)
                    except (EleviaError, OSError):
                        continue
                    report.available.append(object_id)
                continue
            if not local.is_available:
                continue
            try:
                self._service.mark_unavailable(object_id)
            except (EleviaError, OSError):
                continue
            report.unavailable.append(object_id)
        return report
