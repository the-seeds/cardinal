from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Sequence, Tuple, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class Storage(Generic[T], ABC):
    name = None
    database = None
    searchable = False

    @abstractmethod
    def __init__(self, name: str) -> None:
        r"""
        Initializes a storage.

        Args:
            name: the name of the database.
        """
        ...

    @abstractmethod
    def insert(self, keys: Sequence[str], values: Sequence[T]) -> None:
        r"""
        Inserts the value along with the key.
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        r"""
        Deletes the value associated with the given key.

        Args:
            key: the key to delete.
        """
        ...

    @abstractmethod
    def query(self, key: str) -> Optional[T]:
        r"""
        Gets the value associated with the given key.

        Args:
            key: the key to query.
        """
        ...

    @abstractmethod
    def search(self, query: str, top_k: Optional[int] = 10) -> List[Tuple[T, float]]:
        r"""
        Performs a search on the `search_target` field using the keyword and returns results.

        Args:
            query: the query text being searched.
            top_k: the number of results to return.

        Returns:
            hits_with_scores: the hit results with scores (larger is better).
        """
        ...

    @abstractmethod
    def exists(self) -> bool:
        r"""
        Checks if the storage exists.
        """
        ...

    @abstractmethod
    def destroy(self) -> None:
        r"""
        Destroys the storage.
        """
        ...

    @abstractmethod
    def unique_get(self) -> int:
        r"""
        Gets the value of the unique key.
        """
        ...

    @abstractmethod
    def unique_incr(self) -> None:
        r"""
        Increments the value of the unique key by 1.
        """
        ...

    @abstractmethod
    def unique_reset(self) -> None:
        r"""
        Resets the value of the unique key.
        """
        ...
