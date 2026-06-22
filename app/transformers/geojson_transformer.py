from __future__ import annotations

import logging
from typing import Any, TypedDict
from app.domain.models.metadata_record import MetadataRecord

logger = logging.getLogger(__name__)

class GeoJSONValidationError(Exception):
    """Raised when a record cannot be converted into valid GeoJSON."""

class GeoJSONGeometry(TypedDict):
    type: str
    coordinates: list[float]

class GeoJSONFeature(TypedDict):
    type: str
    geometry: GeoJSONGeometry | None
    coordinates: list[float]
    properties: dict[str, Any]

class GeoJSONTransformer:
    """
    Tranforms MetadataRecord to GeoJSON Feature object.

    Designed for cultural heritage place-based metadata.
    """

    def transform(self, record: MetadataRecord) -> GeoJSONFeature:
        """
        Convert MetadataRecord into a GeoJSON Feature.
        Args:
            record: Domain metadata record.
        Returns:
            GeoJSON Feature dictionary.
        Raises:
            GeoJSONValidationError: If reqyired geographic data is invalid.
        """

        logger.debug(f"Starting GeoJSON Transformer.",
                     extra={"record_id": record.id},
                     )
        geometry = self._build_geometry(record)
        properties = self._build_properties(record)

        feature: GeoJSONFeature =  {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties,
        }
        self._validate(feature)

        logger.debug(f"Completed GeoJSON transformation.",
                     extra={"record_id": record.id},)
        return feature

    # Geometry
    def _build_geometry(self, record: MetadataRecord) -> GeoJSONGeometry:
        """
        Build a GeoJSON geomtetry if coordinates exist.
        """

        if not hasattr(record, "coordinates") or record.coordinates is None:
            return None
        lat, lon = record.coordinates

        if not self._validate_coordinates(lat, lon):
            raise GeoJSONValidationError(
                f"Invalid coordinates for record {record.id}: {(lat, lon)}"
            )
        return {
            "type": "Point",
            "coordinates": [lon, lat], # GeoJSON uses [lon, lat]
        }

    # Properties

    def _build_properties(self, record: MetadataRecord) -> dict[str, Any]:
        """
        Map MetadataRecord fields into GeoJSON properties.
        """

        return {
            "id": record.id,
            "title": record.title,
            "author": record.creator,
            "date": record.publication_date,
            "place": record.place,
            "subjects": list(record.subjects),
        }

    # Validation

    def _validate(self, feature: GeoJSONFeature) -> None:
        """
        Validate GeoJSON feature.
        """

        if feature["geometry"] is None:
            logger.warning(
                "GeoJSON feature has no geomtetry",
                extra={"feature_id": feature["properties"]["id"]},
            )
        if not isinstance(feature["properties"], dict):
            raise GeoJSONValidationError("Invalid GeoJSON properties")

        if "id" not in feature["properties"]:
            raise GeoJSONValidationError("Missing required property: id")

    # Helpers
    def _is_validate_coordinate(self, lat: float, lon: float) -> bool:
        """
        Validate latitude and longitude coordinates.
        """

        return -90 <= lat <= 90 and -180 <= lon <= 180