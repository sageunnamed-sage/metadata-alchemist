from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date as Date

import re

class MetadataRecord(BaseModel):
    """
    Core domain model representing a cultural heritage metadata record.

    This is a canonical internal representation used across:
        - Parsers (MARCXML, TEI)
        - Transformers (JSON-D, GeoJSON)
        - Quality validation
        - Indexing (Elasticsearch)
    """
    @field_validator("subjects")
    @classmethod
    def normalise_subjects(cls, v: list[str]) -> list[str]:
        cleaned = {s.strip().lower() for s in v if s and s.strip()}
        return sorted(cleaned)

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not re.match(r"^rec-\d+$", v):
            raise ValueError("Invalid ID format: id must follow rec-0001")
        return v


    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
        frozen=True,
    )

    id: str = Field(...,
                    min_length=1,
                    description="Unique identifier for this metadata record.",
                    examples=["rec-001"])
    title: str = Field(default="Untitled",
                       min_length=1,
                       description="Title of the resource.",
                       examples=["Medieval Manuscript"])
    creator: str | None = Field(default=None,
                                min_length=1,
                                description="Primary creator, author or contributor.")
    publication_date: Date | None = Field(default=None)
    place: str | None = Field(default=None,
                              min_length=1,
                              description="Geographic location associated with resource.")
    subjects: List[str] = Field(default_factory=list, description="Controlled vocabulary terms, keywords, or subjects.")
