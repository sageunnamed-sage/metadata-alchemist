"""
TEI XML parser

Extracts core metadata fields from TEI documents and converts them into
MetadataRecord domain objects.
"""
from __future__ import annotations
from app.domain.models.metadata_record import MetadataRecord

import logging
from pathlib import Path
from lxml import etree
logger = logging.getLogger(__name__)

class TEIParser:
    """
    Parser for TEI XML documents.

    Extracts"
    - title
    - author
    - date
    - placeName
    """

    TEI_NAMESPACE = "http://www.tei-c.org/ns/1.0"

    NAMESPACES = {
        "tei": TEI_NAMESPACE,
    }

    def parse(self, file_path: str | Path) -> MetadataRecord:
        """
        Parse a TEI XML file into a MetadataRecord.
        Args:
            file_path (str | Path): Path to a TEI XML file.
        Returns:
            MetadataRecord containing extracted metadata.
        Raises:
            OSError: If file cannot be read.
            etree.XMLSyntaxError: If XML is malformed.
            ValueError: If a required field is cannot be extracted.
        """
        file_path = Path(file_path)
        logger.info(f"Parsing TEI XML file {file_path}")

        tree = etree.parse(str(file_path))
        root = tree.getroot()

        title = self._extract_text(
            root,
            "//tei:titleStmt/tei:title",
        )
        author = self._extract_text(
            root,
            "//tei:titleStmt/tei:author",
        )
        date = self._extract_text(
            root,
            "//tei:publicationStmt/tei:date",
        )
        place = self._extract_text(
            root,
            "//tei:placeName",
        )
        record_id = file_path.stem

        logger.debug("Extract metadata",
                     extra={"record_id": record_id,
                            "title": title,
                            "author": author,
                            "date": date,
                            "place": place})
        record = MetadataRecord(id=record_id,
                                title=title,
                                creator=author,
                                publication_date=date,
                                place=place,
                                subjects=[],
                                )
        logger.info("Successfully parsed TEI record '%s'", record_id)

        return record

    def _extract_text(self, root: etree._Element, xpath: str, ) -> str | None:
        """
        Extract text from the first Xpath Match.
        Args:
            root (etree._Element): The root element of the TEI XML document.
            xpath (str): XPath Match.
        Returns:
            str | None: The extracted text.

        """
        result = root.xpath(xpath, namespaces=self.NAMESPACES)
        if not result:
            return None
        element = result[0]



        if isinstance(element, etree._Element):
            text = "".join(element.itertext()).strip()
            return text or None
        return str(element).strip() or None