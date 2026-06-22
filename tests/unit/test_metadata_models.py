import pytest
from pydantic import ValidationError

from app.domain.models.metadata_record import MetadataRecord
from app.domain.models.quality_issue import QualityIssue
from app.domain.models.quality_report import QualityReport
from app.domain.enums.issue_type import IssueType

# MetadataRecord
def test_metadata_record_minimal_valid():
    record = MetadataRecord(id="rec-001", title="Test Title")

    assert record.id == "rec-001"
    assert record.title == "Test Title"
    assert record.creator is None
    assert record.publication_date is None
    assert record.place is None
    assert record.subjects == []


def test_metadata_record_subjects_are_normalised():
    record = MetadataRecord(id="rec-002",
                            title="Manuscript",
                            subjects=["History"," history", "ARCHIVES", "archives"])

    # normalised: lowercase + depulicated + sorted
    assert record.subjects == ["archives", "history"]

def test_metadata_record_missing_required_fields():
    with pytest.raises(ValidationError):
        MetadataRecord(id="rec-003")

def test_metadata_record_rejects_empty_string():
    with pytest.raises(ValidationError):
        MetadataRecord(id="rec-003")
    with pytest.raises(ValidationError):
        MetadataRecord(id="", title="Test")


# Quality Issue
def test_quality_issue_valid():
    issue= QualityIssue(record_id="rec-001",
                        issue_type=IssueType.MISSING_DATE,
                        description="Date field is missing")
    assert issue.record_id == "rec-001"
    assert issue.issue_type == IssueType.MISSING_DATE
    assert issue.issue_type.value == "missing_date"

def test_quality_issue_accepts_string_enum_value():
    # pydantic v2 allows coercion to Enum
    issue = QualityIssue(record_id="rec-001",
                         issue_type="missing_date",
                         description="Date field is missing")
    assert issue.issue_type == IssueType.MISSING_DATE

def test_quality_issue_invalid_enum_fails():
    with pytest.raises(ValidationError):
        QualityIssue(record_id="rec-001",
                     issue_type="not_a_real_issue",
                     description="Invalid issue")

# Quality Report

def test_quality_record_default():
    report = QualityReport(total_records=5)

    assert report.total_records == 5
    assert report.missing_dates == 0
    assert report.missing_creators == 0
    assert report.duplicate_titles == 0
    assert report.issues == 0

def test_quality_report_with_issues():
    issue = QualityIssue(record_id="rec-001",
                         issue_type=IssueType.MISSING_CREATOR,
                         description="Creator is missing")
    report = QualityReport(total_records=1,
                           missing_creators=1,
                           issues=[issue])
    assert len(report.issues) == 1
    assert report.issues[0].issue_type == IssueType.MISSING_CREATOR

def test_quality_report_negative_values_rejected():
    with pytest.raises(ValidationError):
        QualityReport(total_records=-1)

def test_quality_report_accepts_multiple_issues():
    issues = [QualityIssue(record_id="rec-001",
                           issue_type=IssueType.MISSING_DATE,
                           description="Date field is missing."),
              QualityIssue(record_id="rec-002",
                           issue_type=IssueType.DUPLICATE_TITLE,
                           description="Date field is duplicate."),
              ]
    report = QualityReport(total_records=1,issues=issues)
    assert len(report.issues) == 1