from typing import Dict, List, Optional, Sequence, Tuple, Type

from pydantic import BaseModel

from .config import settings
from .reranker import APIReranker
from .schema import Reranker


class AutoReranker(Reranker):
    def __init__(self, api_base: str = None, api_key: str = None) -> None:
        self._reranker = _get_reranker()(api_base, api_key)

    def score(self, query: str, doc: str) -> float:
        return self._reranker.score(query, doc)

    def batch_score(self, query: str, docs: Sequence[str]) -> List[float]:
        return self._reranker.batch_score(query, docs)

    def rerank(self, query: str, docs: Sequence[Tuple[BaseModel, float]], top_k: int = None) -> List[Tuple[BaseModel, float]]:
        return self._reranker.rerank(query, docs, top_k)


_rerankers: Dict[str, Type["Reranker"]] = {}


def _add_reranker(name: str, reranker: Type["Reranker"]) -> None:
    _rerankers[name] = reranker


def _list_rerankers() -> List[str]:
    return list(map(str, _rerankers.keys()))


def _get_reranker() -> Type["Reranker"]:
    return APIReranker  # 使用API方式的reranker


_add_reranker("api", APIReranker)
