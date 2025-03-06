import pickle
from typing import List, Optional, Sequence, Tuple

from ..utils.import_utils import is_redis_available
from .config import settings
from .schema import Storage, T


if is_redis_available():
    import redis
    from redis import Redis


class RedisStorage(Storage[T]):
    def __init__(self, name: str, redis_uri: str=None) -> None:
        redis_uri = redis_uri if redis_uri else settings.redis_uri
        self.name = name
        self.database = Redis.from_url(url=redis_uri)
        self.searchable = False
        self._unique_key = "_unique_key"

        try:
            self.database.ping()
        except redis.ConnectionError:
            raise Exception("Unable to connect with the Redis server.")

    def insert(self, keys: Sequence[str], values: Sequence[T]) -> None:
        for key, value in zip(keys, values):
            encoded_value = pickle.dumps(value)
            self.database.hset(self.name, key, encoded_value)

    def delete(self, key: str) -> None:
        return self.database.hdel(self.name, key)

    def query(self, key: str) -> Optional[T]:
        encoded_value = self.database.hget(self.name, key)
        if encoded_value is not None:
            return pickle.loads(encoded_value)

    def search(self, query: str, top_k: Optional[int] = 10) -> List[Tuple[T, float]]:
        raise NotImplementedError

    def exists(self) -> bool:
        return self.database.hlen(self.name) > 0

    def destroy(self) -> None:
        self.database.hdel(self.name, *self.database.hkeys(self.name))

    def unique_get(self) -> int:
        value = self.database.hget(self.name, self._unique_key)
        if isinstance(value, bytes):
            return int(value.decode("utf-8"))

        return 0

    def unique_incr(self) -> None:
        self.database.hincrby(self.name, self._unique_key)

    def unique_reset(self) -> None:
        self.database.hdel(self.name, self._unique_key)
