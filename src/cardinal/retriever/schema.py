from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, List, Optional, TypeVar

from pydantic import BaseModel


if TYPE_CHECKING:
    from ..vectorstore.schema import Condition


T = TypeVar("T", bound=BaseModel)


class Retriever(Generic[T], ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None) -> List[T]:
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
