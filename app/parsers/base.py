from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.models.metadata_record import MetadataRecord


class BaseParser(ABC):

    @abstractmethod
    def parse(self, file_path: str | Path,) -> MetadataRecord:
        pass