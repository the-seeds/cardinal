from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class GraphStorage(Generic[T], ABC):
    name = None

    @abstractmethod
    def __init__(self, name: str) -> None:
        r"""
        Initializes a graph storage.

        Args:
            name: the name of the database.
        """
        ...

    @abstractmethod
    def insert_node(self, key: Sequence[str], node: Sequence[T]) -> None:
        r"""
        Inserts the node along with the key.
        """
        ...

    @abstractmethod
    def insert_edge(self, head_key: Sequence[str], tail_key: Sequence[str], edge: Sequence[T]) -> None:
        r"""
        Inserts the edge along with the key.
        """
        ...

    @abstractmethod
    def query_node(self, key: str) -> Optional[T]:
        r"""
        Gets the node associated with the given key.

        Args:
            key: the key to queried node.
        """
        ...
        
    @abstractmethod
    def query_edge(self, head_key: str, tail_key: str) -> Optional[T]:
        r"""
        Gets the edge associated with the given key.

        Args:
            head_key: the key to the head of queried edge.
            tail_key: the key to the tail of queried edge.
        """
        ...
        
    @abstractmethod
    def query_node_edges(self, key: str) -> Optional[T]:
        r"""
        Gets all edges of the node associated with the given key.

        Args:
            key: the key to the head of queried node.
        """
        ...
        
    @abstractmethod
    def clustering(self) -> None:
        r"""
        call clustering algorithm of graph storage.
        """
        ...

    @abstractmethod
    def community_schema(self) -> None:
        r"""
        get community info.
        """
        ...

    @abstractmethod
    def drop_community(self) -> None:
        r"""
        drop community from memory.
        """
        ...

    @abstractmethod
    def exists(self) -> bool:
        r"""
        Checks if the graph storage exists.
        """
        ...

    @abstractmethod
    def destroy(self) -> None:
        r"""
        Destroys the graph storage.
        """
        ...
