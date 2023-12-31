import base64
import os
import pickle
from collections import defaultdict
from typing import List, Optional, Tuple, TypeVar

from pydantic import BaseModel
from typing_extensions import Self

from ..schema import VectorStore
from ..utils.import_utils import is_pymilvus_availble


if is_pymilvus_availble():
    from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility
    from pymilvus.orm.types import infer_dtype_bydata


K = List[float]
V = TypeVar("V", bound=BaseModel)


class Milvus(VectorStore[V]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.store: Optional[Collection] = None
        self._fields: List[str] = []
        self._alias = "default"
        self._batch_size = 1000
        self._primary_field = "pk"
        self._embedding_field = "embedding"
        self._data_field = "data"
        self._index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
        self._search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

    def _check_connection(self) -> None:
        if not connections.has_connection(self._alias):
            connections.connect(
                alias=self._alias, uri=os.environ.get("MILVUS_URI"), token=os.environ.get("MILVUS_TOKEN")
            )

    def _create_collection(self, embedding: K, example: V) -> None:
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
            for field in self.store.schema.fields:
                if isinstance(field, FieldSchema) and field.name != self._primary_field:
                    self._fields.append(field.name)

    def _init(self, embedding: Optional[K] = None, example: Optional[V] = None) -> None:
        # build connection
        self._check_connection()

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

    @classmethod
    def create(cls, name: str, embeddings: List[K], data: List[V], drop_old: Optional[bool] = False) -> Self:
        milvus = cls(name=name)
        milvus._init()

        if drop_old and milvus.store is not None:
            milvus.store.drop()
            milvus.store = None

        milvus.insert(embeddings, data)
        return milvus

    def insert(self, embeddings: List[K], data: List[V]) -> None:
        if self.store is None:
            self._init(embedding=embeddings[0], example=data[0])

        insert_dict = defaultdict(list)
        for embedding, example in zip(embeddings, data):
            insert_dict[self._embedding_field].append(embedding)
            insert_dict[self._data_field].append(base64.b64encode(pickle.dumps(example)).decode("ascii"))
            for key, value in example.model_dump().items():
                insert_dict[key].append(value)

        total_count = len(insert_dict[self._embedding_field])
        for i in range(0, total_count, self._batch_size):
            insert_list = [insert_dict[field][i : i + self._batch_size] for field in self._fields]
            self.store.insert(insert_list)

    def search(self, embedding: K, top_k: Optional[int] = 4, condition: Optional[str] = None) -> List[Tuple[V, float]]:
        if self.store is None:
            self._init()

        if self.store is None:
            raise ValueError("Index {} does not exist.".format(self.name))

        result = self.store.search(
            data=[embedding],
            anns_field=self._embedding_field,
            param=self._search_params,
            limit=top_k,
            expr=condition,
            output_fields=[self._data_field],
        )

        ret = []
        for hit in result[0]:
            example = pickle.loads(base64.b64decode(hit.entity.get(self._data_field)))
            ret.append((example, hit.score))
        return ret


if __name__ == "__main__":

    class Person(BaseModel):
        name: str
        age: int

    embeddings = [[0.1, 0.5, 0.2], [0.7, 0.1, 0.6]]
    data = [Person(name="alice", age=10), Person(name="bob", age=20)]
    milvus = Milvus[Person].create(name="test", embeddings=embeddings, data=data, drop_old=True)
    milvus.store.load()  # load into cache
    print(milvus.search([0.9, 0.2, 0.7]))
