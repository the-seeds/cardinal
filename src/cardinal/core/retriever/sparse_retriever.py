from typing import TYPE_CHECKING, List, Optional

from ..logging import get_logger
from ..schema import Retriever


if TYPE_CHECKING:
    from ..schema import Leaf, StringKeyedStorage


logger = get_logger(__name__)


class SparseRetriever(Retriever):
    def __init__(
        self,
        storage: "StringKeyedStorage[Leaf]",
    ) -> None:
        self._storage = storage

    def retrieve(self, keyword: str, top_k: Optional[int] = 4) -> List[str]:
        results: List[str] = []
        for example, _ in self._storage.search(keyword=keyword, top_k=top_k):
            results.append(example.content)

        return results


if __name__ == "__main__":
    from ..schema import Leaf
    from ..storage import RedisStorage

    retriever = SparseRetriever(storage=RedisStorage[Leaf]("test"))
    print(retriever.retrieve("edit", top_k=1))
