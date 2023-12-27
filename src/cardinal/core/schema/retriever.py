from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar


V = TypeVar("V")


class Retriever(Generic[V], ABC):

    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = 4,
        condition: Optional[str] = None
    ) -> List[V]:
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
