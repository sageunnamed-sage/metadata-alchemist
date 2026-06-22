import pytest

from app.domain.models.metadata_record import MetadataRecord
from app.transformers.jsonld_transformers import JSONLDTransformer

def test_transform_basic_record():
    record = MetadataRecord(
        id="rec-001",
        title="Canterbury Tales",
    )

    transformer = JSONLDTransformer()

    result = transformer.transform(record)

    assert result["@context"] == "https://schema.org"
    assert result["@type"] == "CreativeWork"
    assert result["@id"] == "rec-001"
    assert result["name"] == "Canterbury Tales"

    assert "author" not in result
    assert "datePublished" not in result
    assert "spatialCoverage" not in result


def test_transform_full_record():
    record = MetadataRecord(
        id="rec-002",
        title="Medieval Manuscript",
        creator="Geoffrey Chaucer",
        date="1400-01-01",
        place="Canterbury",
        subjects=["history", "literature"],
    )

    transformer = JSONLDTransformer()

    result = transformer.transform(record)

    assert result["author"] == {
        "@type": "Person",
        "name": "Geoffrey Chaucer",
    }

    assert result["datePublished"] == "1400"

    assert result["spatialCoverage"] == {
        "@type": "Place",
        "name": "Canterbury",
    }

    assert result["keywords"] == ["history", "literature"]


def test_transform_subjects_optional():
    record = MetadataRecord(
        id="rec-003",
        title="Test",
        subjects=[],
    )

    transformer = JSONLDTransformer()

    result = transformer.transform(record)

    assert "keywords" not in result


def test_creator_is_wrapped_as_person():
    record = MetadataRecord(
        id="rec-004",
        title="Test",
        creator="Jane Doe",
    )

    transformer = JSONLDTransformer()

    result = transformer.transform(record)

    assert result["author"] == {
        "@type": "Person",
        "name": "Jane Doe",
    }
