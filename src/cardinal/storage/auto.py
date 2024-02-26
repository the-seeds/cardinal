from typing import Dict, List, Optional, Sequence, Tuple, Type

from .config import settings
from .elasticsearch import ElasticsearchStorage
from .redis import RedisStorage
from .schema import Storage, T


_storages: Dict[str, Type["Storage"]] = {}


def _add_storage(name: str, storage: Type["Storage"]) -> None:
    _storages[name] = storage


def _list_storages() -> List[str]:
    return list(map(str, _storages.keys()))


_add_storage("es", ElasticsearchStorage)
_add_storage("redis", RedisStorage)
if settings.storage not in _storages:
    raise ValueError("Storage not found, should be one of {}.".format(_list_storages()))

_storage = _storages[settings.storage]


class AutoStorage(Storage[T]):
    def __init__(self, name: str) -> None:
        return _storage.__init__(self, name)

    def insert(self, keys: Sequence[str], values: Sequence[T]) -> None:
        return _storage.insert(self, keys, values)

    def query(self, key: str) -> Optional[T]:
        return _storage.query(self, key)

    def search(self, query: str, top_k: Optional[int] = 10) -> List[Tuple[T, float]]:
        return _storage.search(self, query, top_k)

    def clear(self) -> None:
        return _storage.clear(self)

    def unique_get(self) -> int:
        return _storage.unique_get(self)

    def unique_incr(self) -> None:
        return _storage.unique_incr(self)

    def unique_reset(self) -> None:
        return _storage.unique_reset(self)
