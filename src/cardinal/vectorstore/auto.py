from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple, Type

from typing_extensions import Self

from .chroma import Chroma, ChromaCondition
from .config import settings
from .milvus import Milvus, MilvusCondition
from .schema import Condition, T, VectorStore


if TYPE_CHECKING:
    from .schema import Operator


_vectorstores: Dict[str, Type["VectorStore"]] = {}
_conditions: Dict[str, Type["Condition"]] = {}


def _add_vectorstore(name: str, vectorstore: Type["VectorStore"], condition: Type["Condition"]) -> None:
    _vectorstores[name] = vectorstore
    _conditions[name] = condition


def _list_vectorstores() -> List[str]:
    return list(map(str, _vectorstores.keys()))


_add_vectorstore("chroma", Chroma, ChromaCondition)
_add_vectorstore("milvus", Milvus, MilvusCondition)
if settings.vectorstore not in _vectorstores:
    raise ValueError("Vectorstore not found, should be one of {}.".format(_list_vectorstores()))

_condition = _conditions[settings.vectorstore]
_vectorstore = _vectorstores[settings.vectorstore]


class AutoCondition(Condition):
    def __init__(self, key: str, value: Any, op: "Operator") -> None:
        return _condition.__init__(self, key, value, op)

    def to_filter(self) -> Any:
        return _condition.to_filter(self)


class AutoVectorStore(VectorStore[T]):
    def __init__(self, name: str) -> None:
        return _vectorstore.__init__(self, name)

    @classmethod
    def create(cls, name: str, texts: Sequence[str], data: Sequence[T], drop_old: Optional[bool] = False) -> Self:
        return _vectorstore.create(name, texts, data, drop_old)

    def insert(self, texts: Sequence[str], data: Sequence[T]) -> None:
        return _vectorstore.insert(self, texts, data)

    def delete(self, condition: "Condition") -> None:
        return _vectorstore.delete(self, condition)

    def search(
        self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None
    ) -> List[Tuple[T, float]]:
        return _vectorstore.search(self, query, top_k, condition)
