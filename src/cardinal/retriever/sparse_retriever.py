from typing import TYPE_CHECKING, List, Optional

from ..logging import get_logger
from ..storage import AutoStorage
from .schema import Retriever, T


if TYPE_CHECKING:
    from ..vectorstore.schema import Condition

logger = get_logger(__name__)


class SparseRetriever(Retriever[T]):
    def __init__(self, storage_name: str) -> None:
        self._storage = AutoStorage[T](name=storage_name)

    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None) -> List[T]:
        if condition is not None:
            raise ValueError("Condition is not applicable in sparse retriever.")

        results = []
        for hit, _ in self._storage.search(query, top_k):
            results.append(hit)

        return results


if __name__ == "__main__":
    from pydantic import BaseModel

    class Document(BaseModel):
        content: str
        title: str = "test"

    storage = AutoStorage[Document](name="test")
    storage.insert(keys=["doc1", "doc2"], values=[Document(content="I am alice."), Document(content="I am bob.")])
    retriever = SparseRetriever(storage_name="test")
    print(retriever.retrieve(query="alice", top_k=1))
