import base64
import pickle
from typing import List, Optional, Sequence, Tuple

from ..utils.import_utils import is_elasticsearch_available
from .config import settings
from .schema import Storage, T


if is_elasticsearch_available():
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk


class ElasticsearchStorage(Storage[T]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.database = Elasticsearch(hosts=[settings.elasticsearch_uri])
        self.searchable = True
        self._unique_key = "unique_{}".format(name)
        self._batch_size = 1000
        self._search_target = settings.search_target
        self._try_create_index()

        try:
            self.database.ping()
        except Exception:
            raise Exception("Unable to connect with the Elasticsearch server.")

    def _try_create_index(self) -> None:
        if self.database.indices.exists(index=self.name):
            return

        mappings = {"properties": {"data": {"type": "text"}}}
        index_settings = None
        if self._search_target is not None:
            index_settings = {
                "analysis": {
                    "analyzer": {
                        "standard_cjk_bigram": {
                            "tokenizer": "standard",
                            "filter": ["cjk_bigram"],
                        }
                    }
                }
            }
            mappings["properties"][self._search_target] = {
                "analyzer": "standard_cjk_bigram",
                "search_analyzer": "standard_cjk_bigram",
                "type": "text",
            }

        self.database.indices.create(index=self.name, mappings=mappings, settings=index_settings)

    def insert(self, keys: Sequence[str], values: Sequence[T]) -> None:
        for i in range(0, len(values), self._batch_size):
            actions = []
            for key, value in zip(keys[i : i + self._batch_size], values[i : i + self._batch_size]):
                source = {"data": base64.b64encode(pickle.dumps(value)).decode("ascii")}
                value_dict = value.model_dump()
                if self._search_target is not None and self._search_target in value_dict:
                    source[self._search_target] = value_dict.get(self._search_target)

                actions.append({"_index": self.name, "_id": key, "_source": source})

            bulk(self.database, actions=actions)

    def query(self, key: str) -> Optional[T]:
        if self.database.exists(index=self.name, id=key):
            result = self.database.get(index=self.name, id=key)
            return pickle.loads(base64.b64decode(result["_source"]["data"]))

    def search(self, query: str, top_k: Optional[int] = 10) -> List[Tuple[T, float]]:
        if self._search_target is None:
            raise ValueError("`SEARCH_TARGET` is not defined.")

        result = self.database.search(
            index=self.name,
            query={"match": {self._search_target: query}},
            size=top_k,
        )

        ret = []
        for hit in result["hits"]["hits"]:
            ret.append((pickle.loads(base64.b64decode(hit["_source"]["data"])), hit["_score"]))

        return ret

    def clear(self) -> None:
        if self.database.indices.exists(index=self.name):
            self.database.indices.delete(index=self.name)
        self._try_create_index()

    def unique_get(self) -> int:
        if self.database.exists(index=self.name, id=self._unique_key):
            return int(self.database.get(index=self.name, id=self._unique_key)["_source"]["data"])
        return 0

    def unique_incr(self) -> None:
        value = self.unique_get()
        self.database.index(index=self.name, id=self._unique_key, document={"data": str(value + 1)})

    def unique_reset(self) -> None:
        if self.database.exists(index=self.name, id=self._unique_key):
            self.database.delete(index=self.name, id=self._unique_key)


if __name__ == "__main__":
    from pydantic import BaseModel

    class Document(BaseModel):
        content: str
        title: str = "test"

    storage = ElasticsearchStorage[Document](name="test")
    storage.insert(keys=["doc1", "doc2"], values=[Document(content="I am alice."), Document(content="I am bob.")])
    storage.database.indices.refresh()
    print(storage.query("doc1"))
    print(storage.search("alice"))
    storage.clear()
    print(storage.query("doc1"))
    storage.unique_reset()
    storage.unique_incr()
    storage.unique_incr()
    print(storage.unique_get())
