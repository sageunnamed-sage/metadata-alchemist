from pydantic import BaseModel, Field, ConfigDict

from app.domain.enums.issue_type import IssueType


class QualityIssue(BaseModel):
    """
    Represents a single validation or quality issue detected in a metadata record.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
    record_id: str = Field(...,
                           min_length=1,
                           description="Identifier of the affected metadata record.")
    issue_type: IssueType = Field(..., description="Type of quality issue detected.")
    description: str = Field(...,
                             min_length=1,
                             description="Human-readable explanation of the issue.")