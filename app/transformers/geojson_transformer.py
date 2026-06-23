from __future__ import annotations

import logging
from typing import Any, TypedDict, Literal

from app.domain.models.metadata_record import MetadataRecord

logger = logging.getLogger(__name__)

class GeoJSONValidationError(Exception):
    """Raised when a record cannot be converted into valid GeoJSON."""

class GeoJSONGeometry(TypedDict):
    type: Literal["Point"]
    coordinates: list[float]

class GeoJSONFeature(TypedDict):
    type: Literal["Feature"]
    id: str
    geometry: GeoJSONGeometry | None
    properties: dict[str, Any]

class GeoJSONTransformer:
    """
    Transforms MetadataRecord to GeoJSON Feature object.

    Designed for cultural heritage place-based metadata.
    """
    FEATURE_TYPE = "Feature"
    POINT_TYPE = "Point"

    def transform(self, record: MetadataRecord) -> GeoJSONFeature:
        """
        Convert MetadataRecord into a GeoJSON Feature.
        Args:
            record: Domain metadata record.
        Returns:
            GeoJSON Feature dictionary.
        Raises:
            GeoJSONValidationError: If required geographic data is invalid.
        """

        logger.debug("Starting GeoJSON transformation",
            extra={"record_id": record.id},
                     )
        geometry = self._build_geometry(record)
        properties = self._build_properties(record)

        feature: GeoJSONFeature =  {
            "type": self.FEATURE_TYPE,
            "id": record.id,
            "geometry": geometry,
            "properties": properties,
        }
        self._validate(feature)

        logger.debug("Completed GeoJSON transformation.",
                     extra={"record_id": record.id},)
        return feature

    # Geometry
    def _build_geometry(self, record: MetadataRecord) -> GeoJSONGeometry | None:
        coords = record.coordinates

        if coords is None:
            return None

        try:
            lat, lon = coords
        except (TypeError, ValueError) as exc:
            raise GeoJSONValidationError(f"Invalid coordinates format for record: {record.id}"
                                         ) from exc


        if not self._is_valid_coordinate(lat, lon):
            raise GeoJSONValidationError(
                f"Invalid coordinates for record {record.id}: {(lat, lon)}"
            )

        return {"type": self.POINT_TYPE, "coordinates": [lon, lat], }

    # Properties

    def _build_properties(self, record: MetadataRecord) -> dict[str, Any]:
        """
        Map MetadataRecord fields into GeoJSON properties.
        """

        return {
            "id": record.id,
            "title": record.title,
            "author": record.creator,
            "date": (record.publication_date.isoformat()
                     if hasattr(record.publication_date, "isoformat")
                     else record.publication_date),
            "place": record.place,
            "subjects": list(record.subjects),
        }

    # Validation

    def _validate(self, feature: GeoJSONFeature) -> None:
        """
        Validate GeoJSON feature.
        """

        geometry = feature["geometry"]
        if geometry is None:
            logger.warning(
                "GeoJSON feature has no geometry",
                extra={"feature_id": feature["id"]},
            )
            return

        if geometry["type"] != self.POINT_TYPE:
            raise GeoJSONValidationError(
                f"Unsupported point type: {geometry['type']}",
            )

        coordinates = geometry["coordinates"]

        if len(coordinates) != 2:
            raise GeoJSONValidationError(
                "Point geometry must contain longitude and latitude",
            )

        if not all(
            isinstance(value, (int, float))
            for value in coordinates):
            raise GeoJSONValidationError(
                "Coordinates must be numeric",
            )

    # Helpers
    def _is_valid_coordinate(self, lat: float, lon: float) -> bool:
        """
        Validate latitude and longitude coordinates.
        """

        return -90 <= lat <= 90 and -180 <= lon <= 180