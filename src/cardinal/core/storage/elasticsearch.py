import base64
import pickle
from typing import List, Optional, Sequence, TypeVar

from pydantic import BaseModel

from ..config import settings
from ..schema import StringKeyedStorage
from ..utils.import_utils import is_elasticsearch_available


if is_elasticsearch_available():
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk


V = TypeVar("V", bound=BaseModel)


class ElasticsearchStorage(StringKeyedStorage[V]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.database = Elasticsearch(hosts=[settings.elasticsearch_uri])
        self.can_search = True
        self._unique_key = "unique_{}".format(name)
        self._batch_size = 1000
        self._search_target = "content"
        self._try_create_index()

        try:
            self.database.ping()
        except Exception:
            raise Exception("Unable to connect with the Elasticsearch server.")

    def _try_create_index(self) -> None:
        if self.database.indices.exists(index=self.name):
            return

        mappings = {
            "properties": {
                "data": {"type": "text"},
                self._search_target: {
                    "analyzer": "standard_cjk_bigram",
                    "search_analyzer": "standard_cjk_bigram",
                    "type": "text",
                },
            }
        }
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
        self.database.indices.create(index=self.name, mappings=mappings, settings=index_settings)

    def insert(self, keys: Sequence[str], values: Sequence[V]) -> None:
        for i in range(0, len(values), self._batch_size):
            actions = []
            for key, value in zip(keys[i : i + self._batch_size], values[i : i + self._batch_size]):
                actions.append(
                    {
                        "_index": self.name,
                        "_id": key,
                        "_source": {
                            "data": base64.b64encode(pickle.dumps(value)).decode("ascii"),
                            self._search_target: value.model_dump().get(self._search_target),
                        },
                    }
                )
            bulk(self.database, actions=actions)

    def query(self, key: str) -> Optional[V]:
        if self.database.exists(index=self.name, id=key):
            result = self.database.get(index=self.name, id=key)
            return pickle.loads(base64.b64decode(result["_source"]["data"]))

    def search(self, keyword: str, top_k: Optional[int] = 10) -> List[V]:
        result = self.database.search(
            index=self.name,
            query={"match": {self._search_target: keyword}},
            size=top_k,
        )

        ret = []
        for hit in result["hits"]["hits"]:
            ret.append(pickle.loads(base64.b64decode(hit["_source"]["data"])))

        return ret

    def clear(self) -> None:
        if self.database.indices.exists(index=self.name):
            self.database.indices.delete(index=self.name)

        self._try_create_index()

    def unique_incr(self) -> None:
        if self.database.exists(index=self.name, id=self._unique_key):
            value = int(self.database.get(index=self.name, id=self._unique_key)["_source"]["data"])
            self.database.index(index=self.name, id=self._unique_key, document={"data": str(value + 1)})
        else:
            self.database.index(index=self.name, id=self._unique_key, document={"data": "1"})

    def unique_get(self) -> int:
        if self.database.exists(index=self.name, id=self._unique_key):
            return int(self.database.get(index=self.name, id=self._unique_key)["_source"]["data"])
        return 0

    def unique_reset(self) -> None:
        if self.database.exists(index=self.name, id=self._unique_key):
            self.database.delete(index=self.name, id=self._unique_key)


if __name__ == "__main__":

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
