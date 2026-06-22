from pathlib import Path
import pytest
from lxml import etree

from app.parsers.tei_parser import TEIParser
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
                <placeName>Canterbury</placeName>
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
    assert result.publication_date == "1400-01-01"
    assert result.place == "Cantebury Tales"
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
    assert result.date is None
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

    with pytest.raises(etree.XMLSyntaxError):
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
    assert result.date == "1850-01-01"
