import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    graph_storage: str
    neo4j_uri: Optional[str]
    cluster_size: int


settings = Config(
    graph_storage=os.environ.get("GRAPH_STORAGE"),
    neo4j_uri=os.environ.get("NEO4J_URI"),
    cluster_size=int(os.environ.get("CLUSTER_SIZE"))
)
