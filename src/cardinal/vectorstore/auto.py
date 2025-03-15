from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple, Type

from typing_extensions import Self

from .chroma import Chroma, ChromaCondition
from .config import settings
from .elasticsearch import Elasticsearch, ESCondition
from .milvus import Milvus, MilvusCondition
from .schema import Condition, T, VectorStore


if TYPE_CHECKING:
    from .schema import Operator


class AutoCondition(Condition):
    def __init__(self, key: str, value: Any, op: "Operator") -> None:
        self._condition = _get_condition()(key, value, op)

    def to_filter(self) -> Any:
        return self._condition.to_filter()


class AutoVectorStore(VectorStore[T]):
    def __init__(self, name: str) -> None:
        self._vectorstore = _get_vectorstore()(name)

    @classmethod
    def create(cls, name: str, texts: Sequence[str], data: Sequence[T], drop_old: Optional[bool] = False) -> Self:
        return _get_vectorstore().create(name, texts, data, drop_old)

    def insert(self, texts: Sequence[str], data: Sequence[T]) -> None:
        return self._vectorstore.insert(texts, data)

    def delete(self, condition: "Condition") -> None:
        return self._vectorstore.delete(condition)

    def search(
        self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None
    ) -> List[Tuple[T, float]]:
        return self._vectorstore.search(query, top_k, condition)

    def exists(self) -> bool:
        return self._vectorstore.exists()

    def destroy(self) -> None:
        return self._vectorstore.destroy()
    
    def flush(self) -> None:
        return self._vectorstore.flush()


_vectorstores: Dict[str, Type["VectorStore"]] = {}
_conditions: Dict[str, Type["Condition"]] = {}


def _add_vectorstore(name: str, vectorstore: Type["VectorStore"], condition: Type["Condition"]) -> None:
    _vectorstores[name] = vectorstore
    _conditions[name] = condition


def _list_vectorstores() -> List[str]:
    return list(map(str, _vectorstores.keys()))


def _get_condition() -> Type["Condition"]:
    if settings.vectorstore not in _vectorstores:
        raise ValueError("Condition not found, should be one of {}.".format(_list_vectorstores()))

    return _conditions[settings.vectorstore]


def _get_vectorstore() -> Type["VectorStore"]:
    if settings.vectorstore not in _vectorstores:
        raise ValueError("Vectorstore not found, should be one of {}.".format(_list_vectorstores()))

    return _vectorstores[settings.vectorstore]


_add_vectorstore("chroma", Chroma, ChromaCondition)
_add_vectorstore("milvus", Milvus, MilvusCondition)
_add_vectorstore("elasticsearch", Elasticsearch, ESCondition)
