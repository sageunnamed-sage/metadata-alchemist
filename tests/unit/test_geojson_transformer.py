import pytest

from app.domain.models.metadata_record import MetadataRecord
from app.transformers.geojson_transformer import GeoJSONTransformer, GeoJSONValidationError

@pytest.mark.parametrize(
    ("coordinates", "valid"),
    [
        ((90.0, 180.0), True),
        ((-90.0, -180.0), True),
        ((91.0, 0.0), False),
        ((0.0, -181.0), False),
    ],
)
def test_transform_with_coordinates(coordinates, valid):
    record = MetadataRecord(
        id="rec-001",
        title="Ancient Site",
        publication_date="2020-04-01",
        place="Rome",
    ).model_copy(update={"coordinates": coordinates})

    transformer = GeoJSONTransformer()

    if valid:
        result = transformer.transform(record)
        assert result["geometry"] is not None
    else:
        with pytest.raises(GeoJSONValidationError):
            transformer.transform(record)

    result = transformer.transform(record)
    assert result["type"] == "Feature"
    assert result["geometry"]["type"] == "Point"
    assert result["geometry"]["coordinates"] == [12.4964, 41.9028]
    assert "geometry" in result
    assert "properties" in result
    assert result["id"] == "rec-001"

def test_transform_without_coordinates():
    record: MetadataRecord = MetadataRecord(id="rec-002", title="No Location Record")
    transformer = GeoJSONTransformer()
    result = transformer.transform(record)

    assert result["geometry"] is None
    assert result["properties"]["id"] == "rec-002"

def test_invalid_coordinates_raise_error():
    record: MetadataRecord = MetadataRecord(id="rec-003",
                                            title="Bad Coordinates",
                                            coordinates=(999.0, 999.0),)
    transformer = GeoJSONTransformer()
    with pytest.raises(GeoJSONValidationError):
        transformer.transform(record)


def test_properties_mapping():
    record: MetadataRecord = MetadataRecord(id="rec-004",
                                            title="Test",
                                            creator="Author",
                                            publication_date="1900-04-01",
                                            place="London",
                                            subjects=["history", "maps"])
    transformer = GeoJSONTransformer()
    result = transformer.transform(record)

    assert result["id"] == "rec-004"
    assert result["properties"]["title"] == "Test"
    assert result["properties"]["author"] == "Author"
    assert result["properties"]["place"] == "London"
    assert result["properties"]["date"] == "1900-04-01"
    assert result["properties"]["subjects"] == ["history", "maps"]

def test_subjects_are_mapped():
    record: MetadataRecord = MetadataRecord(
        id="rec-005",
        title="Test",
        subjects=["history", "maps"],
    )

    transformer = GeoJSONTransformer()
    result = transformer.transform(record)
    assert result["properties"]["subjects"] == ["history", "maps"]
