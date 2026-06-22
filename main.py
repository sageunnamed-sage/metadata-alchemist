# This is a sample Python script.
from black import Report

from app.domain.models.metadata_record import MetadataRecord
from app.domain.models.quality_report import QualityReport


# Press ⌃F5 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    record = MetadataRecord(
        id="rec-001",
        title="Medieval Manuscript",
        creator="Unknown Scribe",
        publication_date="1450",
        place="Cantebury",
        subjects=["Manuscripts", "Middle Ages"]
    )

    report = QualityReport(total_records=1,
                           issues=[])

    print(record.model_dump())
    print(report.model_dump())

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
