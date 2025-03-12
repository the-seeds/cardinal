import base64
import pickle
from typing import Any, Dict, List, Optional, Sequence, Tuple

from typing_extensions import Self

from ..model import EmbedOpenAI
from ..utils.import_utils import is_elasticsearch_available
from .config import settings
from .schema import Condition, Operator, T, VectorStore


if is_elasticsearch_available():
    from elasticsearch import Elasticsearch, NotFoundError


class ElasticsearchCondition(Condition):
    def __init__(self, key: str, value: Any, op: "Operator") -> None:
        self._key = key
        _ops = ["term", "not", "gt", "gte", "lt", "lte", "terms", "not_terms", "must", "should"]
        if op < len(_ops):
            self._op = _ops[op]
        else:
            raise NotImplementedError

        if isinstance(value, list) and op in [Operator.In, Operator.Notin]:
            self._value = value
        elif isinstance(value, dict) and op in [Operator.And, Operator.Or]:
            self._value = value
        elif isinstance(value, (str, int, float)):
            self._value = value
        else:
            raise ValueError("Unsupported operation {} for value {}".format(self._op, value))

    def to_filter(self) -> Dict[str, Any]:
        if self._op == "must" or self._op == "should":
            return {"bool": {self._op: [self._key, self._value]}}
        elif self._op == "not":
            return {"bool": {"must_not": {self._key: {"term": self._value}}}}
        elif self._op == "terms":
            return {self._key: {self._op: self._value}}
        elif self._op == "not_terms":
            return {"bool": {"must_not": {self._key: {"terms": self._value}}}}
        else:
            return {self._key: {self._op: self._value}}


class Elasticsearch(VectorStore[T]):
    def __init__(self, name: str, elasticsearch_uri: str=None) -> None:
        self.name = name
        self.elasticsearch_uri = elasticsearch_uri if elasticsearch_uri else settings.elasticsearch_uri
        self.store: Optional[Elasticsearch] = None
        self._batch_size = 1000
        self._vectorizer = EmbedOpenAI(batch_size=self._batch_size)
        self._data_field = "_data"
        self._embedding_field = "_embedding"
        self._index_settings = {
            "mappings": {
                "properties": {
                    self._embedding_field: {
                        "type": "dense_vector",
                        "dims": 1536,  # OpenAI embedding dimension
                        "index": True,
                        "similarity": "l2_norm"
                    }
                }
            }
        }

    def _init(self) -> None:
        if self.store is None:
            self.store = Elasticsearch(self.elasticsearch_uri)
        
        # Create index if not exists
        if not self.store.indices.exists(index=self.name):
            self.store.indices.create(index=self.name, body=self._index_settings)

    def _try_init_and_check_exists(self) -> None:
        if self.store is None:
            self._init()
            if not self.store.indices.exists(index=self.name):
                raise ValueError("Index {} does not exist.".format(self.name))

    @classmethod
    def create(cls, name: str, texts: Sequence[str], data: Sequence[T], drop_old: Optional[bool] = False) -> Self:
        es = cls(name=name)
        es._init()

        if drop_old and es.store.indices.exists(index=name):
            es.destroy()

        es.insert(texts, data)
        return es

    def insert(self, texts: Sequence[str], data: Sequence[T]) -> None:
        embeddings = self._vectorizer.batch_embed(texts)
        if self.store is None:
            self._init()

        for i in range(0, len(texts), self._batch_size):
            batch_data = []
            for j, (embedding, example) in enumerate(zip(
                embeddings[i:i + self._batch_size], 
                data[i:i + self._batch_size]
            )):
                doc = {}
                for k, v in example.model_dump().items():
                    if isinstance(v, (str, int, float, bool)):
                        doc[k] = v
                    else:
                        raise ValueError("Expected str, int, float or bool, got {}".format(type(v)))
                
                doc[self._data_field] = base64.b64encode(pickle.dumps(example)).decode("ascii")
                doc[self._embedding_field] = embedding
                batch_data.append({"index": {"_index": self.name}})
                batch_data.append(doc)
            
            if batch_data:
                self.store.bulk(operations=batch_data)

    def delete(self, condition: "ElasticsearchCondition") -> None:
        self._try_init_and_check_exists()
        self.store.delete_by_query(index=self.name, query=condition.to_filter())

    def search(
        self, query: str, top_k: Optional[int] = 4, condition: Optional["ElasticsearchCondition"] = None
    ) -> List[Tuple[T, float]]:
        self._try_init_and_check_exists()

        query_vector = self._vectorizer.batch_embed([query])[0]
        search_query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}} if condition is None else condition.to_filter(),
                    "script": {
                        "source": f"1 / (1 + l2norm(params.query_vector, '{self._embedding_field}'))",
                        "params": {"query_vector": query_vector}
                    }
                }
            },
            "size": top_k
        }

        response = self.store.search(index=self.name, body=search_query)
        
        ret = []
        for hit in response["hits"]["hits"]:
            example = pickle.loads(base64.b64decode(hit["_source"][self._data_field]))
            score = 1 / hit["_score"] - 1  # Convert similarity score back to L2 distance
            ret.append((example, score))
        return ret

    def exists(self) -> bool:
        try:
            self._try_init_and_check_exists()
            return True
        except (ValueError, NotFoundError):
            return False

    def destroy(self) -> None:
        self._try_init_and_check_exists()
        self.store.indices.delete(index=self.name)
        self.store = None

    def flush(self) -> None:
        if self.store is not None:
            self.store.indices.refresh(index=self.name)
