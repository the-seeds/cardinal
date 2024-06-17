from abc import ABC, abstractmethod
from enum import IntEnum, unique
from typing import Any, Generic, List, Optional, Sequence, Tuple, TypeVar

from pydantic import BaseModel
from typing_extensions import Self


T = TypeVar("T", bound=BaseModel)


@unique
class Operator(IntEnum):
    Eq = 0
    Ne = 1
    Gt = 2
    Ge = 3
    Lt = 4
    Le = 5
    In = 6
    Notin = 7
    And = 8
    Or = 9


class Condition(ABC):
    @abstractmethod
    def __init__(self, key: str, value: Any, op: "Operator") -> None:
        r"""
        Initializes a condition.

        Args:
            key: the key of the condition.
            value: the value of the condition.
            op: the operator.
        """
        ...

    @abstractmethod
    def to_filter(self) -> Any:
        r"""
        Converts the condition to filter.
        """
        ...


class VectorStore(Generic[T], ABC):
    name = None
    store = None

    @abstractmethod
    def __init__(self, name: str) -> None:
        r"""
        Initializes a vector store.

        Args:
            name: the name of the vector store.
        """
        ...

    @classmethod
    @abstractmethod
    def create(cls, name: str, texts: Sequence[str], data: Sequence[T], drop_old: Optional[bool] = False) -> Self:
        r"""
        Creates a vector store with data and embeddings.

        Args:
            name: the name of the vector store.
            texts: the texts to embed.
            data: the data dict of the texts.
            drop_old: whether to drop existing vector store.
        """
        ...

    @abstractmethod
    def insert(self, texts: Sequence[str], data: Sequence[T]) -> None:
        r"""
        Inserts data with embeddings into the vector store.

        Args:
            texts: the texts to embed.
            data: the data dict of the texts.
        """
        ...

    @abstractmethod
    def delete(self, condition: "Condition") -> None:
        r"""
        Deletes data according to the conditional expression.

        Args:
            condition: the conditional expression.
        """
        ...

    @abstractmethod
    def search(
        self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None
    ) -> List[Tuple[T, float]]:
        r"""
        Performs a search on an embedding and returns results with score (in L2 distance).

        Args:
            query: the query text being searched.
            top_k: the number of results to return.
            condition: the conditional expression.

        Returns:
            hits_with_scores: the hit results with scores (smaller is better).
        """
        ...

    @abstractmethod
    def exists(self) -> bool:
        r"""
        Checks if the vectorstore exists.
        """
        ...

    @abstractmethod
    def destroy(self) -> None:
        r"""
        Destroys the vectorstore.
        """
        ...
