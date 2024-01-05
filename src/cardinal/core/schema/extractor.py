from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class Extractor(ABC):
    @abstractmethod
    def load(self, input_files: List[Path], user_id: str, verbose: Optional[bool] = False) -> None:
        r"""
        Loads the files into database.

        Args:
            input_files: a list of paths to input files.
            user_id: the user id.
            verbose: whether or not to show the process bar.
        """
        ...
