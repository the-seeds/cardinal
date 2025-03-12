from abc import ABC, abstractmethod
from typing import List, Sequence, Tuple

from pydantic import BaseModel


class Reranker(ABC):
    model = None
    tokenizer = None

    @abstractmethod
    def __init__(self, model_path: str) -> None:
        """
        初始化一个reranker。

        Args:
            model_path: 模型路径，可以是huggingface模型名或本地路径。
        """
        ...

    @abstractmethod
    def score(self, query: str, doc: str) -> float:
        """
        对单个查询和文档对进行打分。

        Args:
            query: 查询文本
            doc: 文档文本

        Returns:
            score: 相关性分数
        """
        ...

    @abstractmethod
    def batch_score(self, query: str, docs: Sequence[str]) -> List[float]:
        """
        对单个查询和多个文档进行批量打分。

        Args:
            query: 查询文本
            docs: 文档文本列表

        Returns:
            scores: 相关性分数列表
        """
        ...

    @abstractmethod
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
        ...
