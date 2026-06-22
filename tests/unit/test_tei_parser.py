from datetime import date
from pathlib import Path
import pytest
from lxml import etree

from app.parsers.tei_parser import TEIParser, TEIParserError
from app.domain.models.metadata_record import MetadataRecord

def test_parse_valid_tei_file(tmp_path: Path) -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Cantebury Tales</title>
                    <author>Geoffery Chaucer</author>
                </titleStmt>
                <publicationStmt>
                    <date>1400-01-01</date>
                </publicationStmt>
            </fileDesc>
        </teiHeader>
        <text>
            <body>
                <placeName>Cantebury</placeName>
            </body>
        </text>
    </TEI>
    """

    xml_file = tmp_path / "rec-001.xml"
    xml_file.write_text(xml_content)

    parser = TEIParser()
    result = parser.parse(xml_file)

    assert isinstance(result, MetadataRecord)
    assert result.id == "rec-001"
    assert result.title == "Cantebury Tales"
    assert result.creator == "Geoffery Chaucer"
    assert result.publication_date == date(1400, 1, 1)
    assert result.place == "Cantebury"
    assert result.subjects == []

def test_parse_missing_optional_fields(tmp_path: Path) -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Untitled Work</title>
                </titleStmt>
            </fileDesc>
        </teiHeader>
    </TEI>
    """

    xml_file = tmp_path / "rec-002.xml"
    xml_file.write_text(xml_content)

    parser = TEIParser()

    result = parser.parse(xml_file)

    assert result.id == "rec-002"
    assert result.title == "Untitled Work"
    assert result.creator is None
    assert result.publication_date is None
    assert result.place is None


def test_parse_uses_default_title_when_title_missing(tmp_path: Path) -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <author>Anonymous</author>
                </titleStmt>
            </fileDesc>
        </teiHeader>
    </TEI>
    """

    xml_file = tmp_path / "rec-003.xml"
    xml_file.write_text(xml_content)

    parser = TEIParser()

    result = parser.parse(xml_file)

    assert result.title == "Untitled"
    assert result.creator == "Anonymous"


def test_extract_text_returns_value() -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Sample Title</title>
                </titleStmt>
            </fileDesc>
        </teiHeader>
    </TEI>
    """

    root = etree.fromstring(xml_content.encode())

    parser = TEIParser()

    value = parser._extract_text(
        root,
        "//tei:titleStmt/tei:title",
    )

    assert value == "Sample Title"


def test_extract_text_returns_none_when_missing() -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader/>
    </TEI>
    """

    root = etree.fromstring(xml_content.encode())

    parser = TEIParser()

    value = parser._extract_text(
        root,
        "//tei:titleStmt/tei:title",
    )

    assert value is None


def test_invalid_xml_raises_exception(tmp_path: Path) -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
    """

    xml_file = tmp_path / "broken.xml"
    xml_file.write_text(xml_content)

    parser = TEIParser()

    with pytest.raises(TEIParserError):
        parser.parse(xml_file)


def test_namespace_handling(tmp_path: Path) -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Namespaced Title</title>
                    <author>Namespaced Author</author>
                </titleStmt>
                <publicationStmt>
                    <date>1850-01-01</date>
                </publicationStmt>
            </fileDesc>
        </teiHeader>
    </TEI>
    """

    xml_file = tmp_path / "rec-004.xml"
    xml_file.write_text(xml_content)

    parser = TEIParser()

    result = parser.parse(xml_file)

    assert result.title == "Namespaced Title"
    assert result.creator == "Namespaced Author"
    assert result.publication_date == date(1850, 1, 1)

# Tests for _load_xml()
from lxml import etree
from app.parsers.tei_parser import TEIParser, TEIParserError

def test_load_xml_returns_root_element(tmp_path: Path) -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader />
    </TEI>
    """

    xml_file = tmp_path / "rec-001.xml"
    xml_file.write_text(xml_content)

    parser = TEIParser()

    root = parser._load_xml(xml_file)

    assert isinstance(root, etree._Element)
    assert root.tag.endswith("TEI")


def test_load_xml_raises_parser_error_for_invalid_xml(
    tmp_path: Path,
) -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
    """

    xml_file = tmp_path / "rec-001.xml"
    xml_file.write_text(xml_content)

    parser = TEIParser()

    with pytest.raises(TEIParserError):
        parser._load_xml(xml_file)


def test_load_xml_raises_parser_error_for_missing_file() -> None:
    parser = TEIParser()

    with pytest.raises(TEIParserError):
        parser._load_xml(Path("does_not_exist.xml"))

# Tests for _extract_text()
def test_extract_text_returns_text_value() -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Canterbury Tales</title>
                </titleStmt>
            </fileDesc>
        </teiHeader>
    </TEI>
    """

    root = etree.fromstring(xml_content.encode())

    parser = TEIParser()

    value = parser._extract_text(
        root,
        parser.TITLE_XPATH,
    )

    assert value == "Canterbury Tales"


def test_extract_text_returns_none_for_missing_node() -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader />
    </TEI>
    """

    root = etree.fromstring(xml_content.encode())

    parser = TEIParser()

    value = parser._extract_text(
        root,
        parser.TITLE_XPATH,
    )

    assert value is None


def test_extract_text_strips_whitespace() -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>
                        Canterbury Tales
                    </title>
                </titleStmt>
            </fileDesc>
        </teiHeader>
    </TEI>
    """

    root = etree.fromstring(xml_content.encode())

    parser = TEIParser()

    value = parser._extract_text(
        root,
        parser.TITLE_XPATH,
    )

    assert value == "Canterbury Tales"

# Test for _extract_metadata
def test_extract_metadata_returns_expected_fields() -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <title>Canterbury Tales</title>
                    <author>Geoffrey Chaucer</author>
                </titleStmt>
                <publicationStmt>
                    <date>1400</date>
                </publicationStmt>
            </fileDesc>
        </teiHeader>

        <text>
            <body>
                <placeName>Canterbury</placeName>
            </body>
        </text>
    </TEI>
    """

    root = etree.fromstring(xml_content.encode())

    parser = TEIParser()

    metadata = parser._extract_metadata(root)

    assert metadata["title"] == "Canterbury Tales"
    assert metadata["creator"] == "Geoffrey Chaucer"
    assert metadata["publication_date"] == "1400"
    assert metadata["place"] == "Canterbury"


def test_extract_metadata_returns_none_for_missing_fields() -> None:
    xml_content = """
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader />
    </TEI>
    """

    root = etree.fromstring(xml_content.encode())

    parser = TEIParser()

    metadata = parser._extract_metadata(root)

    assert metadata["title"] is None
    assert metadata["creator"] is None
    assert metadata["publication_date"] is None
    assert metadata["place"] is None

