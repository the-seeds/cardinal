import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    vectorstore: str
    chroma_path: Optional[str]
    milvus_uri: Optional[str]
    milvus_token: Optional[str]
    elasticsearch_uri: Optional[str]


settings = Config(
    vectorstore=os.environ.get("VECTORSTORE"),
    chroma_path=os.environ.get("CHROMA_PATH"),
    milvus_uri=os.environ.get("MILVUS_URI"),
    milvus_token=os.environ.get("MILVUS_TOKEN"),
    elasticsearch_uri=os.environ.get("ELASTICSEARCH_URI"),
)
