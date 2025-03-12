from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from ..logging import get_logger
from ..vectorstore import AutoVectorStore
from .schema import Retriever, T


if TYPE_CHECKING:
    from ..vectorstore.schema import Condition


logger = get_logger(__name__)


class MultiRetriever(Retriever[T]):
    def __init__(
        self,
        vectorstore_names: List[str],
        weights: Optional[List[float]] = None,
        threshold: Optional[float] = 1e5,
        verbose: Optional[bool] = False,
    ) -> None:
        weights = [1.0] * len(vectorstore_names) if weights is None else weights
        if len(vectorstore_names) != len(weights):
            raise ValueError("The length of vectorstores does not match weights.")

        self._vectorstores = [AutoVectorStore[T](name=name) for name in vectorstore_names]
        self._weights = weights
        self._threshold = threshold
        self._verbose = verbose

    def _rrf_fuse(self, all_hit_ids: List[List[int]]) -> List[int]:
        r"""
        Performs weighted Reciprocal Rank Fusion on multiple rank lists.
        Ref: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

        Args:
            all_hit_ids: A list of hit ids.

        Returns:
            fused_ids: the merged hits.
        """
        # Create a union of all unique hits in the input
        all_ids = set(hit_id for hit_ids in all_hit_ids for hit_id in hit_ids)  # noqa: C401
        # Initialize the RRF score dictionary for each hit
        rrf_scores = defaultdict(float)

        for hit_ids, weight in zip(all_hit_ids, self._weights):
            # Align the number of the hits
            hit_ids = hit_ids + list(all_ids.difference(hit_ids))
            # Calculate RRF scores for each hit
            for rank, hit_id in enumerate(hit_ids, start=1):
                rrf_scores[hit_id] += weight * (1 / (rank + 60))

        # Sort hits by their RRF scores in descending order
        results = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        return results

    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional["Condition"] = None) -> List[T]:
        hit_id = 0
        id_to_hit: Dict[int, T] = {}
        feat_to_id: Dict[str, int] = {}
        all_hit_ids: List[List[int]] = []
        for vectorstore in self._vectorstores:
            current_feats: Set[str] = set()
            hit_ids: List[int] = []
            for hit, score in vectorstore.search(query, top_k=max(8, top_k * 2), condition=condition):
                if self._verbose:
                    logger.info("Hit with score {:.4f}".format(score))

                if score <= self._threshold:
                    feat = hit.model_dump_json()
                    if feat not in current_feats:
                        current_feats.add(feat)
                        if feat in feat_to_id:
                            hit_ids.append(feat_to_id[feat])
                        else:
                            id_to_hit[hit_id] = hit
                            feat_to_id[feat] = hit_id
                            hit_ids.append(hit_id)
                            hit_id += 1

            all_hit_ids.append(hit_ids)

        fused_ids = self._rrf_fuse(all_hit_ids)[:top_k]
        results = [id_to_hit[hit_id] for hit_id in fused_ids]

        return results
