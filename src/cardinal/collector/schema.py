from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar


T = TypeVar("T")


class Collector(Generic[T], ABC):
    @abstractmethod
    def collect(self, data: T) -> None:
        r"""
        Collects the data.

        Args:
            data: a single data example.
        """
        ...

    @abstractmethod
    def dump(self) -> List[T]:
        r"""
        Dumps the collected data.
        """
        ...
