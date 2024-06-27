from typing import TYPE_CHECKING, List, Optional

from ..logging import get_logger
from ..storage import AutoStorage
from .schema import Retriever, T


if TYPE_CHECKING:
    from ..vectorstore.schema import Condition


logger = get_logger(__name__)


class SparseRetriever(Retriever[T]):
    def __init__(self, storage_name: str, verbose: Optional[bool] = False) -> None:
        self._storage = AutoStorage[T](name=storage_name)
        self._verbose = verbose

    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None) -> List[T]:
        if condition is not None:
            raise ValueError("Condition is not applicable in sparse retriever.")

        results = []
        for hit, score in self._storage.search(query, top_k):
            if self._verbose:
                logger.info("Hit with score {:.4f}".format(score))

            results.append(hit)

        return results
