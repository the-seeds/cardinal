import os
import pickle
from typing import TypeVar

import redis
from redis import Redis

from ..schema import StringKeyedStorage


V = TypeVar("V")


class RedisStorage(StringKeyedStorage[V]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.database = Redis.from_url(url=os.environ.get("REDIS_URI"))

        try:
            self.database.ping()
        except redis.ConnectionError:
            raise Exception("Unable to connect with the Redis server.")

    def insert(self, key: str, value: V) -> None:
        encoded_value = pickle.dumps(value)
        self.database.hset(self.name, key, encoded_value)

    def query(self, key: str) -> V:
        encoded_value = self.database.hget(self.name, key)
        return pickle.loads(encoded_value)


if __name__ == "__main__":
    storage = RedisStorage[str](name="test")
    storage.insert("test_k", "test_v")
    print(storage.query("test_k"))
