from abc import ABC, abstractmethod
from typing import Generic, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class Storage(Generic[K, V], ABC):
    name = None
    database = None

    @abstractmethod
    def __init__(self, name: str) -> None:
        r"""
        Initializes a storage.

        Args:
            name: the name of the database.
        """
        ...

    @abstractmethod
    def insert(self, key: K, value: V) -> None:
        r"""
        Inserts the value along with the key.
        """
        ...

    @abstractmethod
    def query(self, key: K) -> V:
        r"""
        Gets the value associated with the given key.
        """
        ...

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
