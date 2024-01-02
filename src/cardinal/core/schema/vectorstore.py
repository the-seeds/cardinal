from abc import ABC, abstractmethod
from enum import IntEnum, unique
from typing import Any, Generic, List, Optional, Tuple, TypeVar

from pydantic import BaseModel
from typing_extensions import Self


K = List[float]
V = TypeVar("V", bound=BaseModel)


@unique
class Operator(IntEnum):
    Eq = 0
    Ne = 1
    Gt = 2
    Ge = 3
    Lt = 4
    Le = 5
    NOT = 6
    AND = 7
    OR = 8


class Condition(ABC):
    @abstractmethod
    def __init__(self, key: str, value: Any, op: Operator) -> None:
        ...

    @abstractmethod
    def to_filter(self) -> Any:
        ...


class VectorStore(Generic[V], ABC):
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
    def create(cls, name: str, embeddings: List[K], data: List[V], drop_old: Optional[bool] = False) -> Self:
        r"""
        Creates a vector store with data and embeddings.

        Args:
            name: the name of the vector store.
            embeddings: the embedding vectors of the texts.
            data: the data dict of the texts.
            drop_old: whether to drop existing vector store.
        """
        ...

    @abstractmethod
    def insert(self, embeddings: List[K], data: List[V]) -> None:
        r"""
        Inserts data with embeddings into the vector store.

        Args:
            embeddings: the embedding vectors of the texts.
            data: the data dict of the texts.
        """
        ...

    @abstractmethod
    def delete(self, condition: Condition) -> None:
        r"""
        Deletes data according to the conditional expression.

        Args:
            condition: the conditional expression.
        """
        ...

    @abstractmethod
    def search(self, embedding: K, top_k: Optional[int] = 4, condition: Optional[Condition] = None) -> List[Tuple[V, float]]:
        r"""
        Performs a search on an embedding and returns results with score (in L2 distance).

        Args:
            embedding: the embedding vector being searched.
            top_k: the number of results to return.
            condition: the conditional expression.

        Returns:
            hits_with_scores: the hit results with scores (smaller is better).
        """
        ...
