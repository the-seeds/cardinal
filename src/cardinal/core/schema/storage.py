from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Sequence, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class Storage(Generic[K, V], ABC):
    name = None
    database = None
    can_search = False

    @abstractmethod
    def __init__(self, name: str) -> None:
        r"""
        Initializes a storage.

        Args:
            name: the name of the database.
        """
        ...

    @abstractmethod
    def insert(self, keys: Sequence[K], values: Sequence[V]) -> None:
        r"""
        Inserts the value along with the key.
        """
        ...

    @abstractmethod
    def query(self, key: K) -> Optional[V]:
        r"""
        Gets the value associated with the given key.
        """
        ...

    @abstractmethod
    def search(self, keyword: str, top_k: Optional[int] = 10) -> List[V]:
        r"""
        Performs a search on a keyword and returns results.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        r"""
        Clears all the data in the storage.
        """

    @abstractmethod
    def unique_incr(self) -> None:
        r"""
        Increments the value of the unique key by 1.
        """
        ...

    @abstractmethod
    def unique_get(self) -> int:
        r"""
        Gets the value of the unique key.
        """
        ...

    @abstractmethod
    def unique_reset(self) -> None:
        r"""
        Resets the value of the unique key.
        """
        ...


StringKeyedStorage = Storage[str, V]
