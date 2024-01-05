from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar


V = TypeVar("V")


class Collector(Generic[V], ABC):
    @abstractmethod
    def collect(self, data: V) -> None:
        r"""
        Collects the data.

        Args:
            data: a single data example.
        """
        ...

    @abstractmethod
    def dump(self) -> List[V]:
        r"""
        Dumps the collected data.
        """
        ...
