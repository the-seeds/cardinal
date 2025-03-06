from typing import Optional, Sequence, TypeVar
from pydantic import BaseModel
from collections import defaultdict

from .schema import GraphStorage
from .config import settings
from ..utils.import_utils import is_neo4j_available


if is_neo4j_available():
    from neo4j import GraphDatabase

T = TypeVar("T", bound=BaseModel)

class Neo4j(GraphStorage[T]):
    def __init__(self, name: str, neo4j_uri: str=None, cluster_level: int=None) -> None:
        self.name = name
        self.neo4j_uri = neo4j_uri if neo4j_uri else settings.neo4j_uri
        self.cluster_level = cluster_level if cluster_level else settings.cluster_level
        self.driver = GraphDatabase.driver(self.neo4j_uri)

    def insert_node(self, key: Sequence[str], node: Sequence[T]) -> None:
        with self.driver.session() as session:
            for k, n in zip(key, node):
                session.run(
                    """
                    MERGE (n:Node {key: $key})
                    SET n += $properties
                    """,
                    key=k,
                    properties=n.model_dump(),
                )

    def insert_edge(self, head_key: Sequence[str], tail_key: Sequence[str], edge: Sequence[T]) -> None:
        with self.driver.session() as session:
            for h, t, e in zip(head_key, tail_key, edge):
                session.run(
                    """
                    MATCH (h:Node {key: $head_key})
                    MATCH (t:Node {key: $tail_key})
                    MERGE (h)-[r:EDGE]->(t)
                    SET r += $properties
                    """,
                    head_key=h,
                    tail_key=t,
                    properties=e.model_dump(),
                )

    def query_node(self, key: str) -> Optional[T]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n:Node {key: $key})
                RETURN n
                """,
                key=key,
            )
            record = result.single()
            if record:
                return record["n"]
            return None

    def query_edge(self, head_key: str, tail_key: str) -> Optional[T]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (h:Node {key: $head_key})-[r:EDGE]-(t:Node {key: $tail_key})
                RETURN r
                """,
                head_key=head_key,
                tail_key=tail_key,
            )
            record = result.single()
            if record:
                return record["r"]
            return None

    def query_node_edges(self, key: str) -> Optional[T]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n:Node {key: $key})-[r:EDGE]->()
                RETURN r
                """,
                key=key,
            )
            edges = [record["r"] for record in result]
            return edges if edges else None
    
    """
    clustering part reference:
    - [nano-graphrag](https://github.com/gusye1234/nano-graphrag)
    """
    def clustering(self) -> None:
        max_level = self.cluster_level
        with self.driver.session() as session:
            # Project the graph with undirected relationships
            session.run(
                f"""
                CALL gds.graph.project(
                    'graph_{self.name}',
                    ['Node'],
                    {{
                        EDGE: {{
                            orientation: 'UNDIRECTED',
                            properties: ['strength']
                        }}
                    }}
                )
                """
            )

            # Run Leiden algorithm
            session.run(
                f"""
                CALL gds.leiden.write(
                    'graph_{self.name}',
                    {{
                        writeProperty: 'community_id',
                        includeIntermediateCommunities: True,
                        relationshipWeightProperty: "strength",
                        maxLevels: {max_level},
                        tolerance: 0.0001,
                        gamma: 1.0,
                        theta: 0.01
                    }}
                )
                """
            )
            
    def community_schema(self) -> dict[str, T]:
        results = defaultdict(
            lambda: {
                'level': None,
                'title': None,
                'edges': set(),
                'nodes': set(),
                'sub_communities':[]
            }
        )

        with self.driver.session() as session:
            # Fetch community data
            result = session.run(
                f"""
                MATCH (n:Node)
                WITH n, n.community_id AS community_id, [(n)-[]-(m:Node) | m.name] AS connected_nodes
                RETURN n.name AS node_name,
                       community_id AS cluster_key,
                       connected_nodes
                """
            )

            for record in result:
                for index, c_id in enumerate(record["cluster_key"]):
                    node_name = str(record["node_name"])
                    level = index
                    cluster_key = str(c_id)
                    connected_nodes = record["connected_nodes"]

                    results[cluster_key]["level"] = level
                    results[cluster_key]["title"] = f"Cluster {cluster_key}"
                    results[cluster_key]["nodes"].add(node_name)
                    results[cluster_key]["edges"].update(
                        [
                            tuple(sorted([node_name, str(connected)]))
                            for connected in connected_nodes
                            if connected != node_name
                        ]
                    )

            # Process results
            for k, v in results.items():
                v["edges"] = [list(e) for e in v["edges"]]
                v["nodes"] = list(v["nodes"])

            # Compute sub-communities (this is a simplified approach)
            for cluster in results.values():
                cluster["sub_communities"] = [
                    sub_key
                    for sub_key, sub_cluster in results.items()
                    if sub_cluster["level"] > cluster["level"]
                    and set(sub_cluster["nodes"]).issubset(set(cluster["nodes"]))
                ]

        return dict(results)
            
    def drop_community(self):
        with self.driver.session() as session:
            session.run(f"CALL gds.graph.drop('graph_{self.name}') YIELD graphName")

    def exists(self) -> bool:
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1")
                return result.single() is not None
        except Exception:
            return False

    def destroy(self) -> None:
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        self.driver.close()
