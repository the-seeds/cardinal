import base64
import pickle
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple

from typing_extensions import Self

from ..model import EmbedOpenAI
from ..utils.import_utils import is_chroma_available
from .config import settings
from .schema import Condition, Operator, T, VectorStore


if is_chroma_available():
    from chromadb import Client
    from chromadb.config import Settings

    if TYPE_CHECKING:
        from chromadb import ClientAPI


class ChromaCondition(Condition):
    def __init__(self, key: str, value: Any, op: "Operator") -> None:
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


class Chroma(VectorStore[T]):
    def __init__(self, name: str) -> None:
        client = _get_chroma_client()
        self.store = client.get_or_create_collection(name, embedding_function=None)
        self._batch_size = 1000
        self._vectorizer = EmbedOpenAI(self._batch_size)
        self._data_field = "_data"

    @classmethod
    def create(cls, name: str, texts: Sequence[str], data: Sequence[T], drop_old: Optional[bool] = False) -> Self:
        if drop_old:
            client = _get_chroma_client()
            try:
                client.delete_collection(name)
            except Exception:
                pass

        chroma = cls(name=name)
        chroma.insert(texts, data)
        return chroma

    def insert(self, texts: Sequence[str], data: Sequence[T]) -> None:
        embeddings = self._vectorizer.batch_embed(texts)
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

    def delete(self, condition: "ChromaCondition") -> None:
        self.store.delete(where=condition.to_filter())

    def search(
        self, query: str, top_k: Optional[int] = 4, condition: Optional["ChromaCondition"] = None
    ) -> List[Tuple[T, float]]:
        result = self.store.query(
            query_embeddings=self._vectorizer.batch_embed([query]),
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
    from pydantic import BaseModel

    class Animal(BaseModel):
        name: str

    texts = ["dog", "llama", "puppy"]
    data = [Animal(name=text) for text in texts]
    chroma = Chroma[Animal].create(name="test", texts=texts, data=data, drop_old=True)
    chroma.delete(ChromaCondition(key="name", value="dog", op=Operator.Eq))
    print(chroma.search(query="dog", top_k=2))
