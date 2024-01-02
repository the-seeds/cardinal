from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional


if TYPE_CHECKING:
    from .vectorstore import Condition


class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None) -> List[str]:
        r"""
        Performs a search on a query and returns results.

        Args:
            query: the query string being searched.
            top_k: the number of results to return.
            condition: the conditional expression.

        Returns:
            results: the retrieved results.
        """
        ...
