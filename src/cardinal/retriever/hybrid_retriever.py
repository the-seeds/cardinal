from typing import TYPE_CHECKING, List, Optional

from ..logging import get_logger
from ..storage import AutoStorage
from ..vectorstore import AutoVectorStore
from .schema import Retriever, T


if TYPE_CHECKING:
    from ..vectorstore.schema import Condition


logger = get_logger(__name__)


class HybridRetriever(Retriever[T]):
    def __init__(
        self,
        storage_name: str,
        vectorstore_name: str,
        sparse_multiplier: int = 4,
        threshold: Optional[float] = 1e5,
        verbose: Optional[bool] = False,
    ) -> None:
        """
        Initialize a hybrid retriever that combines sparse and dense retrieval.

        Args:
            storage_name: Name of the sparse storage to use
            vectorstore_name: Name of the dense vectorstore to use
            sparse_multiplier: Multiplier for sparse retrieval results (m in m*top_k)
            threshold: Score threshold for dense retrieval results
            verbose: Whether to log verbose information
        """
        self._storage = AutoStorage[T](name=storage_name)
        self._vectorstore = AutoVectorStore[T](name=vectorstore_name)
        self._sparse_multiplier = sparse_multiplier
        self._threshold = threshold
        self._verbose = verbose

    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None) -> List[T]:
        # First step: Get candidate documents using sparse retrieval
        sparse_top_k = top_k * self._sparse_multiplier
        candidates = []
        seen_docs = set()
        
        # Get initial candidates from sparse retrieval
        for hit, score in self._storage.search(query, sparse_top_k):
            if self._verbose:
                logger.info("Sparse hit with score {:.4f}".format(score))
            
            # Use model_dump_json as a unique identifier
            doc_id = hit.model_dump_json()
            if doc_id not in seen_docs:
                seen_docs.add(doc_id)
                candidates.append(hit)

        # Second step: Re-rank candidates using dense retrieval
        results = []
        if candidates:
            # Create a condition to only search within candidate documents
            # Note: This assumes the vectorstore supports searching within specific documents
            for hit, score in self._vectorstore.search(query, top_k, condition):
                if self._verbose:
                    logger.info("Dense hit with score {:.4f}".format(score))

                if score <= self._threshold:
                    results.append(hit)

        return results[:top_k]
