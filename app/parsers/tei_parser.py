"""
TEI XML parser

Extracts core metadata fields from TEI documents and converts them into
MetadataRecord domain objects.
"""
from __future__ import annotations

import logging
from pathlib import Path
from datetime import date
from lxml import etree

from app.domain.models.metadata_record import MetadataRecord

logger = logging.getLogger(__name__)


class TEIParser:
    """
    Parser for TEI XML documents.

    Extracts:
    - title
    - author
    - publication_date
    - placeName
    """

    TEI_NAMESPACE = "http://www.tei-c.org/ns/1.0"

    NAMESPACES = {
        "tei": TEI_NAMESPACE,
    }

    def parse(self, file_path: str | Path) -> MetadataRecord:
        file_path = Path(file_path)
        logger.info("Parsing TEI XML file %s", file_path)

        tree = etree.parse(str(file_path))
        root = tree.getroot()

        title = self._extract_text(
            root,
            "//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title",
        )
        author = self._extract_text(
            root,
            "//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author",
        )
        date_text = self._extract_text(
            root,
            "//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date",
        )
        place = self._extract_text(
            root,
            "//tei:text//tei:placeName",
        )

        record = MetadataRecord(
            id=file_path.stem,
            title=title or "Untitled",
            creator=author,
            publication_date=self._parse_date(date_text),
            place=place,
            subjects=[],
        )

        logger.info("Successfully parsed TEI record '%s'", file_path.stem)
        return record

    def _parse_date(self, value: str | None) -> date | None:
        """
        Convert TEI date strings into datetime.date.

        Supports:
        - "1400" → 1400-01-01
        - "1400-01-01" → 1400-01-01
        """
        if not value:
            return None

        value = value.strip()

        if value.isdigit() and len(value) == 4:
            return date(int(value), 1, 1)

        return date.fromisoformat(value)

    def _extract_text(self, root: etree._Element, xpath: str) -> str | None:
        """
        Extract text from the first XPath match.
        """
        result = root.xpath(xpath, namespaces=self.NAMESPACES)

        if not result:
            return None

        element = result[0]

        if isinstance(element, etree._Element):
            text = "".join(element.itertext()).strip()
            return text or None

        return str(element).strip() or None