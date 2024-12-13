import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    graph_storage: str
    neo4j_uri: Optional[str]
    cluster_level: str


settings = Config(
    graph_storage=os.environ.get("GRAPH_STORAGE"),
    neo4j_uri=os.environ.get("NEO4J_URI"),
    cluster_level=os.environ.get("CLUSTER_LEVEL")
)
