import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    storage: str
    search_target: Optional[str]
    redis_uri: Optional[str]
    elasticsearch_uri: Optional[str]


settings = Config(
    storage=os.environ.get("STORAGE"),
    search_target=os.environ.get("SEARCH_TARGET"),
    redis_uri=os.environ.get("REDIS_URI"),
    elasticsearch_uri=os.environ.get("ELASTICSEARCH_URI"),
)
