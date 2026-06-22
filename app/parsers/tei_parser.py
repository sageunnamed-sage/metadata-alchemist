"""
TEI XML parser

Extracts core metadata fields from TEI documents and converts them into
MetadataRecord domain objects.
"""
from __future__ import annotations

import logging
from pathlib import Path
from datetime import date as Date
from lxml import etree

from app.domain.models.metadata_record import MetadataRecord
from app.parsers.base import BaseParser

logger = logging.getLogger(__name__)

class TEIParserError(Exception):
    """Raised when a TEI document cannot be parsed."""


class TEIParser(BaseParser):
    """
    Parser for TEI XML documents.
    """

    TEI_NS = "http://www.tei-c.org/ns/1.0"

    NAMESPACES = {
        "tei": TEI_NS,
    }

    TITLE_XPATH = "//tei:titleStmt/tei:title"
    AUTHOR_XPATH = "//tei:titleStmt/tei:author"
    DATE_XPATH = "//tei:publicationStmt/tei:date"
    PLACE_XPATH = "//tei:placeName"

    def parse(self, file_path: str | Path) -> MetadataRecord:
        """
        Parse a TEI XML file.
        Args:
            file_path: Path to the TEI XML document.
        Returns:
            MetadataRecord..
        """
        path = Path(file_path)
        logger.info("Parsing TEI XML file %s", path)

        root = self._load_xml(path)

        metadata = self.extract_metadata(root)

        record = MetadataRecord(
            id=file_path.stem,
            title=metadata["title"] or "Untitled",
            creator=metadata["creator"],
            publication_date=metadata["publication_date"],
            place=metadata["place"],
            subjects=[],
        )

        logger.info("Successfully parsed TEI document", extra={"record_id": record.id,
                                                               },
                    )
        return record

    def _load_xml(self, file_path: Path) -> etree._Element:
        """
        Load and validate XML document
        """
        try:
            tree = etree.parse(str(file_path))
            return tree.getroot()
        except (OSError, etree.XMLSyntaxError) as exc:
            logger.exception("Failed to parse TEI XML", extra={"file_path": str(file_path),
                                                               },
                             )
            raise TEIParserError(f"Unable to parse TEI file: {file_path}")
    def extract_metadata(self, root: etree._Element) -> dict[str, str| None]:
        return {
            "title" : self._extract_text(root, self.TITLE_XPATH),
            "creator" : self._extract_text(root, self.AUTHOR_XPATH),
            "publication_date" : self._extract_text(root, self.DATE_XPATH),
            "place" : self._extract_text(root, self.PLACE_XPATH),
        }

    def _extract_text(self, root: etree._Element, xpath: str) -> str | None:
        """
        Extract text from the first XPath match.
        """
        result = root.xpath(xpath, namespaces=self.NAMESPACES,
                            )
        if not result:
            return None
        node = result[0]
        if isinstance(node, etree._Element):
            value = "".join(node.itertext()).strip()
            return value or None
        return str(node).strip() or None