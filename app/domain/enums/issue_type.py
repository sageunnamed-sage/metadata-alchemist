from enum import Enum

class IssueType(str, Enum):
    """
    Controlled vocabulary of metadata quality issues.

    Used across:
        - Quality validation
        - Reporting
        - Elasticsearch aggregation
    """
    MISSING_DATE = "missing_date"
    MISSING_CREATOR = "missing_creator"
    DUPLICATE_TITLE = "duplicate_title"
    INVALID_FIELD = "invalid_field"
    FORMAT_ERROR = "format_error"