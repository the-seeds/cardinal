import base64
import pickle
from collections import defaultdict
from typing import Any, List, Optional, Sequence, Tuple

from typing_extensions import Self

from ..model import EmbedOpenAI
from ..utils.import_utils import is_pymilvus_availble
from .config import settings
from .schema import Condition, Operator, T, VectorStore


if is_pymilvus_availble():
    from pymilvus import Collection, CollectionSchema, Connections, DataType, FieldSchema, Hit, connections, utility
    from pymilvus.orm.types import infer_dtype_bydata

    SearchResult = Sequence[Sequence[Hit]]


class MilvusCondition(Condition):
    def __init__(self, key: str, value: Any, op: "Operator") -> None:
        self._key = key
        _ops = ["==", "!=", ">", ">=", "<", "<=", "in", "not in", "&&", "||"]
        if op < len(_ops):
            self._op = _ops[op]
        else:
            raise NotImplementedError

        if isinstance(value, list) and op in [Operator.In, Operator.Notin]:
            self._value = str(value)
        elif isinstance(value, str) and op in [Operator.And, Operator.Or]:
            self._value = value
        elif isinstance(value, str):
            self._value = "'{}'".format(value)
        elif isinstance(value, (int, float)):
            self._value = str(value)
        else:
            raise ValueError("Unsupported operation {} for value {}".format(self._op, value))

    def to_filter(self) -> str:
        return " ".join((self._key, self._op, self._value))


class Milvus(VectorStore[T]):
    def __init__(self, name: str, milvus_uri: str=None, milvus_token: str=None) -> None:
        self.name = name
        self.milvus_uri = milvus_uri if milvus_uri else settings.milvus_uri
        self.milvus_token = milvus_token if milvus_token else settings.milvus_token
        self.store: Optional["Collection"] = None
        self._fields: List[str] = []
        self._alias = "default"
        self._batch_size = 1000
        self._vectorizer = EmbedOpenAI(batch_size=self._batch_size)
        self._primary_field = "_pk"
        self._embedding_field = "_embedding"
        self._data_field = "_data"
        self._index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
        self._search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    def _check_connection(self, conn: "Connections") -> None:
        if not conn.has_connection(self._alias):
            conn.connect(alias=self._alias, uri=self.milvus_uri, token=self.milvus_token)

    def _create_collection(self, embedding: Sequence[float], example: T) -> None:
        fields = [
            FieldSchema(name=self._primary_field, dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name=self._embedding_field, dtype=DataType.FLOAT_VECTOR, dim=len(embedding)),
            FieldSchema(name=self._data_field, dtype=DataType.VARCHAR, max_length=2048),
        ]

        for key, value in example.model_dump().items():
            dtype = infer_dtype_bydata(value)
            if dtype == DataType.UNKNOWN or dtype == DataType.NONE:
                raise ValueError("Unrecognized datatype for {}".format(key))
            elif dtype == DataType.VARCHAR:
                fields.append(FieldSchema(name=key, dtype=DataType.VARCHAR, max_length=512))
            else:
                fields.append(FieldSchema(name=key, dtype=dtype))

        self.store = Collection(name=self.name, schema=CollectionSchema(fields=fields))

    def _create_index(self) -> None:
        if len(self.store.indexes) == 0:
            self.store.create_index(field_name=self._embedding_field, index_params=self._index_params)

    def _extract_fields(self) -> None:
        if len(self._fields) == 0:
            field: FieldSchema
            for field in self.store.schema.fields:
                if field.name != self._primary_field:
                    self._fields.append(field.name)

    def _init(self, embedding: Optional[Sequence[float]] = None, example: Optional[T] = None) -> None:
        # build connection
        self._check_connection(connections)

        # check existing store
        if utility.has_collection(self.name):
            self.store = Collection(name=self.name)

        # create store if example is given
        if embedding is not None and example is not None and self.store is None:
            self._create_collection(embedding, example)

        # load store if exists
        if self.store is not None:
            self._extract_fields()
            self._create_index()
            self.store.load()

    def _try_init_and_check_exists(self) -> None:
        if self.store is None:
            self._init()

        if self.store is None:
            raise ValueError("Index {} does not exist.".format(self.name))

    @classmethod
    def create(cls, name: str, texts: Sequence[str], data: Sequence[T], drop_old: Optional[bool] = False) -> Self:
        milvus = cls(name=name)
        milvus._init()

        if drop_old and milvus.store is not None:
            milvus.destroy()

        milvus.insert(texts, data)
        return milvus

    def insert(self, texts: Sequence[str], data: Sequence[T]) -> None:
        embeddings = self._vectorizer.batch_embed(texts)
        if self.store is None:
            self._init(embedding=embeddings[0], example=data[0])

        insert_dict = defaultdict(list)
        for embedding, example in zip(embeddings, data):
            insert_dict[self._embedding_field].append(embedding)
            insert_dict[self._data_field].append(base64.b64encode(pickle.dumps(example)).decode("ascii"))
            for key, value in example.model_dump().items():
                insert_dict[key].append(value)

        for i in range(0, len(insert_dict[self._embedding_field]), self._batch_size):
            insert_list = [insert_dict[field][i : i + self._batch_size] for field in self._fields]
            self.store.insert(insert_list)

    def delete(self, condition: "MilvusCondition") -> None:
        self._try_init_and_check_exists()
        self.store.delete(condition.to_filter())

    def search(
        self, query: str, top_k: Optional[int] = 4, condition: Optional["MilvusCondition"] = None
    ) -> List[Tuple[T, float]]:
        self._try_init_and_check_exists()

        result: "SearchResult" = self.store.search(
            data=self._vectorizer.batch_embed([query]),
            anns_field=self._embedding_field,
            param=self._search_params,
            limit=top_k,
            expr=condition.to_filter() if condition is not None else None,
            output_fields=[self._data_field],
        )

        ret = []
        for hit in result[0]:
            example = pickle.loads(base64.b64decode(hit.entity.get(self._data_field)))
            ret.append((example, hit.score))

        return ret

    def exists(self) -> bool:
        try:
            self._try_init_and_check_exists()
            return True
        except ValueError:
            return False

    def destroy(self):
        self._try_init_and_check_exists()
        self.store.drop()
        self.store = None

    def flush(self) -> None:
        return self.store.flush()
    