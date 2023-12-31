from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class Extractor(ABC):
    @abstractmethod
    def load(self, documents: List[Path]) -> None:
        r"""
        Loads the documents into database.

        Args:
            documents: a list of paths to documents.
        """
        ...
