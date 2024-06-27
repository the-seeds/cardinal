from typing import List, Optional

from ..storage import AutoStorage
from .schema import Collector, T


class BaseCollector(Collector[T]):
    def __init__(self, storage_name: str, drop_old: Optional[bool] = False) -> None:
        self._storage = AutoStorage[T](name=storage_name)
        self._prefix = "collector_{}"
        if drop_old:
            self._storage.unique_reset()

    def collect(self, data: T) -> None:
        num_collected = self._storage.unique_get()
        self._storage.insert([self._prefix.format(num_collected)], [data])
        self._storage.unique_incr()

    def dump(self) -> List[T]:
        results = []
        for i in range(self._storage.unique_get()):
            results.append(self._storage.query(self._prefix.format(i)))

        return results
