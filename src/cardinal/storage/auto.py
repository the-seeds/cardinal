from typing import Dict, List, Optional, Sequence, Tuple, Type

from .config import settings
from .elasticsearch import ElasticsearchStorage
from .redis import RedisStorage
from .schema import Storage, T


class AutoStorage(Storage[T]):
    def __init__(self, name: str) -> None:
        self._storage = _get_storage()(name)

    def insert(self, keys: Sequence[str], values: Sequence[T]) -> None:
        return self._storage.insert(keys, values)

    def delete(self, key: str) -> None:
        return self._storage.delete(key)

    def query(self, key: str) -> Optional[T]:
        return self._storage.query(key)

    def search(self, query: str, top_k: Optional[int] = 10) -> List[Tuple[T, float]]:
        return self._storage.search(query, top_k)

    def exists(self) -> bool:
        return self._storage.exists()

    def destroy(self) -> None:
        return self._storage.destroy()

    def unique_get(self) -> int:
        return self._storage.unique_get()

    def unique_incr(self) -> None:
        return self._storage.unique_incr()

    def unique_reset(self) -> None:
        return self._storage.unique_reset()


_storages: Dict[str, Type["Storage"]] = {}


def _add_storage(name: str, storage: Type["Storage"]) -> None:
    _storages[name] = storage


def _list_storages() -> List[str]:
    return list(map(str, _storages.keys()))


def _get_storage() -> Type["Storage"]:
    if settings.storage not in _storages:
        raise ValueError("Storage not found, should be one of {}.".format(_list_storages()))

    return _storages[settings.storage]


_add_storage("es", ElasticsearchStorage)
_add_storage("redis", RedisStorage)
