import base64
import json
import pickle
from typing import Any, Dict, List, Optional, Sequence, Tuple

from typing_extensions import Self

from ..model import EmbedOpenAI
from ..utils.import_utils import is_elasticsearch_available
from .config import settings
from .schema import Condition, Operator, T, VectorStore


if is_elasticsearch_available():
    from elasticsearch import Elasticsearch as ES
    from elasticsearch.helpers import bulk


class ESCondition(Condition):
    def __init__(self, key: str, value: Any, op: "Operator") -> None:
        self._key = key
        _ops = ["term", "must_not", "gt", "gte", "lt", "lte", "terms", "must_not", "must", "should"]
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
        if self._op in ["must", "should"]:
            return {
                "bool": {
                    self._op: [
                        {"term": {self._key: v}} if isinstance(v, (str, int, float)) else v
                        for v in (self._value if isinstance(self._value, list) else [self._value])
                    ]
                }
            }
        elif self._op == "must_not":
            return {"bool": {"must_not": {"term": {self._key: self._value}}}}
        elif self._op == "terms":
            return {"terms": {self._key: self._value}}
        else:
            return {"range": {self._key: {self._op: self._value}}}


class Elasticsearch(VectorStore[T]):
    def __init__(self, name: str, elasticsearch_uri: str=None) -> None:
        self.name = name
        self.elasticsearch_uri = elasticsearch_uri if elasticsearch_uri else settings.elasticsearch_uri
        self.store: Optional["ES"] = None
        self._batch_size = 1000
        self._vectorizer = EmbedOpenAI(batch_size=self._batch_size)
        self._data_field = "_data"
        self._embedding_field = "_embedding"
        self._index_params = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                }
            }
        }

    def _init(self, embedding: Optional[Sequence[float]] = None) -> None:
        if self.store is None:
            self.store = ES(hosts=[self.elasticsearch_uri])
            try:
                self.store.ping()
            except Exception:
                raise Exception("Unable to connect with the Elasticsearch server.")

        # Create index if it doesn't exist and we have embedding dimension
        if embedding is not None and not self.store.indices.exists(index=self.name):
            mappings = {
                "properties": {
                    self._data_field: {"type": "keyword"},
                    self._embedding_field: {
                        "type": "dense_vector",
                        "dims": len(embedding),
                        "index": True,
                        "similarity": "l2_norm"
                    }
                }
            }
            try:
                print("Creating index with mappings:", json.dumps(mappings, indent=2))
                self.store.indices.create(
                    index=self.name,
                    mappings=mappings,
                    settings=self._index_params["settings"]
                )
            except Exception as e:
                print("Error creating index:", str(e))
                raise

    def _try_init_and_check_exists(self) -> None:
        if self.store is None:
            self._init()

        if not self.store.indices.exists(index=self.name):
            raise ValueError("Index {} does not exist.".format(self.name))

    def _get_index_info(self) -> None:
        """打印索引信息用于调试"""
        try:
            print("\nIndex settings:", json.dumps(self.store.indices.get_settings(index=self.name), indent=2))
            print("\nIndex mappings:", json.dumps(self.store.indices.get_mapping(index=self.name), indent=2))
            print("\nIndex stats:", json.dumps(self.store.indices.stats(index=self.name), indent=2))
        except Exception as e:
            print("Error getting index info:", str(e))

    @classmethod
    def create(cls, name: str, texts: Sequence[str], data: Sequence[T], drop_old: Optional[bool] = False) -> Self:
        es = cls(name=name)
        es._init()

        if drop_old and es.exists():
            es.destroy()

        es.insert(texts, data)
        return es

    def insert(self, texts: Sequence[str], data: Sequence[T]) -> None:
        embeddings = self._vectorizer.batch_embed(texts)
        if self.store is None:
            self._init(embedding=embeddings[0])

        actions = []
        for embedding, example in zip(embeddings, data):
            doc = {
                self._embedding_field: embedding,
                self._data_field: base64.b64encode(pickle.dumps(example)).decode("ascii")
            }
            # Add metadata fields
            for k, v in example.model_dump().items():
                if isinstance(v, (str, int, float, bool)):
                    doc[k] = v
                else:
                    raise ValueError("Expected str, int, float or bool, got {}".format(type(v)))

            actions.append({
                "_index": self.name,
                "_source": doc
            })

            if len(actions) >= self._batch_size:
                try:
                    print("Bulk inserting {} documents".format(len(actions)))
                    bulk(self.store, actions)
                except Exception as e:
                    print("Error during bulk insert:", str(e))
                    raise
                actions = []

        if actions:
            try:
                print("Bulk inserting remaining {} documents".format(len(actions)))
                bulk(self.store, actions)
            except Exception as e:
                print("Error during bulk insert:", str(e))
                raise

        # 刷新索引以确保数据可见
        self.flush()

    def delete(self, condition: "ESCondition") -> None:
        self._try_init_and_check_exists()
        try:
            print("Deleting documents with query:", json.dumps(condition.to_filter(), indent=2))
            self.store.delete_by_query(
                index=self.name,
                query=condition.to_filter()
            )
        except Exception as e:
            print("Error during delete:", str(e))
            raise

    def search(
        self, query: str, top_k: Optional[int] = 4, condition: Optional["ESCondition"] = None
    ) -> List[Tuple[T, float]]:
        self._try_init_and_check_exists()

        # 打印索引信息
        self._get_index_info()

        # Get query embedding
        query_embedding = self._vectorizer.batch_embed([query])[0]

        # Build search query
        search_query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": """
                            float[] docVector = doc[params.field].vectorValue;
                            double l2norm = 0.0;
                            for (int i = 0; i < params.query_vector.length; i++) {
                                double diff = params.query_vector[i] - docVector[i];
                                l2norm += diff * diff;
                            }
                            return Math.sqrt(l2norm);
                        """,
                        "params": {
                            "query_vector": query_embedding,
                            "field": self._embedding_field
                        }
                    }
                }
            },
            "sort": [
                {"_score": {"order": "asc"}}  # 按分数升序排序（距离从小到大）
            ]
        }

        if condition is not None:
            search_query["query"] = {
                "bool": {
                    "must": [
                        condition.to_filter(),
                        search_query["query"]
                    ]
                }
            }

        # 先尝试解释查询
        explain = self.store.indices.validate_query(
            index=self.name,
            query=search_query["query"],
            explain=True
        )

        # 执行搜索
        result = self.store.search(
            index=self.name,
            body=search_query,
            size=top_k,
            _source=[self._data_field]
        )


        # Process results
        ret = []
        for hit in result["hits"]["hits"]:
            example = pickle.loads(base64.b64decode(hit["_source"][self._data_field]))
            score = hit["_score"]
            ret.append((example, score))

        return ret

    def exists(self) -> bool:
        try:
            self._try_init_and_check_exists()
            return True
        except ValueError:
            return False

    def destroy(self) -> None:
        self._try_init_and_check_exists()
        try:
            print("Deleting index:", self.name)
            self.store.indices.delete(index=self.name)
        except Exception as e:
            print("Error during index deletion:", str(e))
            raise
        self.store = None

    def flush(self) -> None:
        if self.exists():
            try:
                print("Refreshing index:", self.name)
                self.store.indices.refresh(index=self.name)
            except Exception as e:
                print("Error during index refresh:", str(e))
                raise
