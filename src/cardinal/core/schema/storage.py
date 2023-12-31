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


StringKeyedStorage = Storage[str, V]
