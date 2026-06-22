from email.policy import default
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.domain.models.quality_issue import QualityIssue

class QualityReport(BaseModel):
    """
    Aggregated quality assessment report for a batch of metadata records.
    """

    model_config = ConfigDict(extra="forbid")

    total_records: int = Field(..., ge=0, description="Total number of records analysed.")
    missing_dates: int = Field(default=0, ge=0, description="Number of missing a date value.")
    missing_creators: int = Field(default=0, ge=0, description="Number of missing a creator value.")
    duplicate_titles: int = Field(default=0, ge=0, description="Number of duplicate titles detected.")
    issues: List[QualityIssue] = Field(default_factory=list, description="Detailed list of metadata quality issues.")