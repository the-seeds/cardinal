from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Generic, List, Optional, Tuple, TypeVar
from typing_extensions import Self


K = List[float]
V = TypeVar("V", bound=BaseModel)


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
    def create(
        cls,
        store_name: str,
        embeddings: List[K],
        data: List[V],
        drop_old: Optional[bool] = False
    ) -> Self:
        r"""
        Creates a vector store with data and embeddings.

        Args:
            store_name: the name of the vector store.
            embeddings: the embedding vectors of the texts.
            data: the data dict of the texts.
            drop_old: whether to drop existing vector store.
        """
        ...

    @abstractmethod
    def insert(
        self,
        embeddings: List[K],
        data: List[V]
    ) -> None:
        r"""
        Inserts data with embeddings into the vector store.

        Args:
            embeddings: the embedding vectors of the texts.
            data: the data dict of the texts.
        """
        ...

    @abstractmethod
    def search(
        self,
        embedding: K,
        top_k: Optional[int] = 4,
        condition: Optional[str] = None
    ) -> List[Tuple[V, float]]:
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
