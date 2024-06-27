from typing import TYPE_CHECKING, List, Optional

from ..logging import get_logger
from ..vectorstore import AutoVectorStore
from .schema import Retriever, T


if TYPE_CHECKING:
    from ..vectorstore.schema import Condition


logger = get_logger(__name__)


class DenseRetriever(Retriever[T]):
    def __init__(
        self,
        vectorstore_name: str,
        threshold: Optional[float] = 1e5,
        verbose: Optional[bool] = False,
    ) -> None:
        self._vectorstore = AutoVectorStore[T](name=vectorstore_name)
        self._threshold = threshold
        self._verbose = verbose

    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None) -> List[T]:
        results = []
        for hit, score in self._vectorstore.search(query, top_k, condition):
            if self._verbose:
                logger.info("Hit with score {:.4f}".format(score))

            if score <= self._threshold:
                results.append(hit)

        return results
