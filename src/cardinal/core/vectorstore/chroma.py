import base64
import os
import pickle
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, TypeVar

from pydantic import BaseModel
from typing_extensions import Self

from ..schema import Condition, Operator, VectorStore
from ..utils.import_utils import is_chroma_available


if is_chroma_available():
    from chromadb import Client
    from chromadb.config import Settings

    if TYPE_CHECKING:
        from chromadb import ClientAPI


K = List[float]
V = TypeVar("V", bound=BaseModel)


class ChromaCondition(Condition):
    def __init__(self, key: str, value: Any, op: Operator) -> None:
        self._key = key
        if isinstance(value, (str, int, float)):
            self._value = value
        else:
            raise ValueError("Only supports string, int or float.")

        _ops = ["$eq", "$ne", "$gt", "$gte", "$lt", "$lte"]
        if op < len(_ops):
            self._op = _ops[op]
        else:
            raise NotImplementedError

    def to_filter(self) -> Dict[str, Dict[str, str]]:
        return {self._key: {self._op: self._value}}


def _get_chroma_client() -> "ClientAPI":
    settings = Settings(is_persistent=True, persist_directory=os.environ.get("CHROMA_PATH"))
    client = Client(settings)
    try:
        client.heartbeat()
    except Exception:
        raise Exception("Unable to connect with the Chroma client.")

    return client


class Chroma(VectorStore[V]):
    def __init__(self, name: str) -> None:
        client = _get_chroma_client()
        self.store = client.get_or_create_collection(name, embedding_function=None)

    @classmethod
    def create(cls, name: str, embeddings: List[K], data: List[V], drop_old: Optional[bool] = False) -> Self:
        if drop_old:
            client = _get_chroma_client()
            try:
                client.delete_collection(name)
            except Exception:
                pass

        chroma = cls(name=name)
        chroma.insert(embeddings, data)
        return chroma

    def insert(self, embeddings: List[K], data: List[V]) -> None:
        ids = []
        metadatas = []
        for example in data:
            ids.append(uuid.uuid4().hex)
            example_dict = {}
            for k, v in example.model_dump().items():
                if isinstance(v, (str, int, float, bool)):
                    example_dict[k] = v
            example_dict["data"] = base64.b64encode(pickle.dumps(example)).decode("ascii")
            metadatas.append(example_dict)

        self.store.add(ids=ids, embeddings=embeddings, metadatas=metadatas)

    def delete(self, condition: ChromaCondition) -> None:
        return self.store.delete(where=condition.to_filter())

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
            example = pickle.loads(base64.b64decode(metadata["data"]))
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
