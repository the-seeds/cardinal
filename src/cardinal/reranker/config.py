import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    reranker: Optional[str]
    reranker_api_base: Optional[str]
    reranker_api_key: Optional[str]
    reranker_batch_size: int = 32


settings = Config(
    reranker=os.environ.get("RERANKER"),
    reranker_api_base=os.environ.get("OPENAI_BASE_URL"),
    reranker_api_key=os.environ.get("OPENAI_API_KEY"),
    reranker_batch_size=int(os.environ.get("RERANKER_BATCH_SIZE", "32")),
)
