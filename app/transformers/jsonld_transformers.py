from __future__ import annotations

import logging
from typing import Any

from app.domain.models.metadata_record import MetadataRecord

logger = logging.getLogger(__name__)


def _format_person(name: str) -> dict[str, str]:
    """
    Map creator to Schema.ord Person.
    """

    return {
        "@type": "Person",
        "name": name,
    }

class JSONLDTransformer:
    """
    Transforms MetadataRecord objects into Schema.org-compliant JSON-LD format.

    Output is deterministic, serialisation ready, and aligned with linked data best practises.
    """

    CONTEXT: str = "https://schema.org"
    TYPE: str = "CreativeWork"

    def transform(self, record: MetadataRecord) -> dict[str, Any]:
        """
        Convert a MetadataRecord into a JSON-LD format
        """
        logger.debug("Starting JSON-LD transformation", extra={"record_id": record.id},
                     )

        jsonld: dict[str, Any] = {
            "@context": self.CONTEXT,
            "@type": self.TYPE,
            "@id": record.id,
            "name": record.title,
        }

        self._add_author(jsonld, record)
        self._add_date(jsonld, record)
        self._add_place(jsonld, record)
        self._add_keywords(jsonld, record)

        logger.debug("Completed JSON-LD transformation", extra={"record_id": record.id},)
        return jsonld

    # Field mapping helpers

    def _add_author(self, result: dict[str, Any], record: MetadataRecord) -> None:
        if record.creator:
            result["author"] = self._format_person(record.creator)

    def _add_date(self, result: dict[str, Any], record: MetadataRecord) -> None:
        if record.publication_date:
            result["datePublished"] = record.publication_date

    def _add_place(self, result: dict[str, Any], record: MetadataRecord) -> None:
        if not record.place:
            return
        result["spatialCoverage"] = {
            "@type": "Place",
            "name": record.place}

    def _add_keywords(self, result: dict[str, Any], record: MetadataRecord) -> None:
        if record.subjects:
            result["keywords"] = list(record.subjects)

    # Normalisation helpers

    def _format_person(self, name: str) -> dict[str, str]:
        """
        Convert creator to Schema.org Person object.
        """
        return {
            "@type": "Person",
            "name": name.strip(),
        }