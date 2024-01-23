import base64
import pickle
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple, TypeVar

from pydantic import BaseModel
from typing_extensions import Self

from ..config import settings
from ..schema import Condition, Operator, VectorStore
from ..utils.import_utils import is_chroma_available


if is_chroma_available():
    from chromadb import Client
    from chromadb.config import Settings

    if TYPE_CHECKING:
        from chromadb import ClientAPI


K = Sequence[float]
V = TypeVar("V", bound=BaseModel)


class ChromaCondition(Condition):
    def __init__(self, key: str, value: Any, op: Operator) -> None:
        self._key = key
        _ops = ["$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin", "$and", "$or"]
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
        if self._op == "$and" or self._op == "$or":
            return {self._op: [self._key, self._value]}
        else:
            return {self._key: {self._op: self._value}}


def _get_chroma_client() -> "ClientAPI":
    client = Client(Settings(is_persistent=True, persist_directory=settings.chroma_path))
    try:
        client.heartbeat()
    except Exception:
        raise Exception("Unable to connect with the Chroma client.")

    return client


class Chroma(VectorStore[V]):
    def __init__(self, name: str) -> None:
        client = _get_chroma_client()
        self.store = client.get_or_create_collection(name, embedding_function=None)
        self._batch_size = 1000
        self._data_field = "_data"

    @classmethod
    def create(cls, name: str, embeddings: Sequence[K], data: Sequence[V], drop_old: Optional[bool] = False) -> Self:
        if drop_old:
            client = _get_chroma_client()
            try:
                client.delete_collection(name)
            except Exception:
                pass

        chroma = cls(name=name)
        chroma.insert(embeddings, data)
        return chroma

    def insert(self, embeddings: Sequence[K], data: Sequence[V]) -> None:
        ids = []
        metadatas = []
        for example in data:
            ids.append(uuid.uuid4().hex)
            example_dict = {}
            for k, v in example.model_dump().items():
                if isinstance(v, (str, int, float, bool)):
                    example_dict[k] = v
                else:
                    raise ValueError("Expected str, int, float or bool, got {}".format(type(v)))

            example_dict[self._data_field] = base64.b64encode(pickle.dumps(example)).decode("ascii")
            metadatas.append(example_dict)

        for i in range(0, len(metadatas), self._batch_size):
            self.store.add(
                ids=ids[i : i + self._batch_size],
                embeddings=embeddings[i : i + self._batch_size],
                metadatas=metadatas[i : i + self._batch_size],
            )

    def delete(self, condition: ChromaCondition) -> None:
        self.store.delete(where=condition.to_filter())

    def search(
        self, embedding: K, top_k: Optional[int] = 4, condition: Optional[ChromaCondition] = None
    ) -> List[Tuple[V, float]]:
        result = self.store.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=condition.to_filter() if condition is not None else None,
            include=["metadatas", "distances"],
        )

        ret = []
        for metadata, score in zip(result["metadatas"][0], result["distances"][0]):
            example = pickle.loads(base64.b64decode(metadata[self._data_field]))
            ret.append((example, score))
        return ret


if __name__ == "__main__":

    class Person(BaseModel):
        name: str
        age: int

    embeddings = [[0.1, 0.5, 0.2], [0.7, 0.1, 0.6], [0.9, 0.2, 0.7]]
    data = [Person(name="alice", age=10), Person(name="bob", age=20), Person(name="jack", age=50)]
    chroma = Chroma[Person].create(name="test", embeddings=embeddings, data=data, drop_old=True)
    chroma.delete(ChromaCondition(key="name", value="jack", op=Operator.Eq))
    print(chroma.search([0.9, 0.2, 0.7], top_k=2))
