from abc import ABC, abstractmethod
from src.database import Database
from src.config import ExportConfig

class BaseExporter(ABC):
    def __init__(self, db: Database, config: ExportConfig):
        self.db = db
        self.config = config

    @abstractmethod
    def export(self) -> str:
        """Export the database as a single unified string."""
        pass

    @abstractmethod
    def export_multi(self, output_dir: str) -> None:
        """Export the database split into multiple include files in output_dir."""
        pass
