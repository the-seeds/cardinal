from typing import List, Sequence, Tuple

from openai import OpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .config import settings
from .schema import Reranker


class APIReranker(Reranker):
    def __init__(self, api_base: str = None, api_key: str = None) -> None:
        """
        初始化API形式的reranker。

        Args:
            api_base: API基础URL
            api_key: API密钥
        """
        self.model = settings.reranker
        if self.model is not None and self.model.lower() != "none":
            self._client = OpenAI(
                api_key=api_key if api_key else settings.reranker_api_key,
                base_url=api_base if api_base else settings.reranker_api_base,
                max_retries=5,
                timeout=30.0
            )

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def score(self, query: str, doc: str) -> float:
        """
        对单个查询和文档对进行打分。

        Args:
            query: 查询文本
            doc: 文档文本

        Returns:
            score: 相关性分数
        """
        response = self._client.post(
            "/v1/score",
            json={
                "model": self.model,
                "query": query,
                "document": doc
            }
        )
        return float(response.json()["score"])

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def _batch_score_with_retry(self, query: str, docs: Sequence[str]) -> List[float]:
        response = self._client.post(
            "/v1/batch_score",
            json={
                "model": self.model,
                "query": query,
                "documents": docs
            }
        )
        return response.json()["scores"]

    def batch_score(self, query: str, docs: Sequence[str]) -> List[float]:
        """
        对单个查询和多个文档进行批量打分。

        Args:
            query: 查询文本
            docs: 文档文本列表

        Returns:
            scores: 相关性分数列表
        """
        batch_size = settings.reranker_batch_size
        scores = []

        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i + batch_size]
            scores.extend(self._batch_score_with_retry(query, batch_docs))

        return scores

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def rerank(self, query: str, docs: Sequence[Tuple[BaseModel, float]], top_k: int = None) -> List[Tuple[BaseModel, float]]:
        """
        对检索结果进行重排序。

        Args:
            query: 查询文本
            docs: 初始检索结果列表，每个元素为(文档,分数)对
            top_k: 返回前k个结果

        Returns:
            reranked_docs: 重排序后的文档列表
        """
        if not docs:
            return []

        doc_texts = [str(doc[0]) for doc in docs]
        response = self._client.post(
            "/v1/rerank",
            json={
                "model": self.model,
                "query": query,
                "documents": doc_texts,
                "top_k": top_k
            }
        )
        scores = response.json()["scores"]

        # 将原始文档与新的分数组合
        reranked = [(doc[0], score) for doc, score in zip(docs, scores)]
        reranked.sort(key=lambda x: x[1], reverse=True)

        if top_k is not None:
            reranked = reranked[:top_k]

        return reranked
