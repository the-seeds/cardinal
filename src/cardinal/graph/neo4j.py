import json
from typing import Generic, Optional, Sequence, TypeVar
from pydantic import BaseModel
from neo4j import GraphDatabase

T = TypeVar("T", bound=BaseModel)

class Neo4j(Generic[T]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.driver = GraphDatabase.driver("bolt://localhost:7687")

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
                    MERGE (h)-[r:EDGE {properties: $properties}]->(t)
                    """,
                    head_key=h,
                    tail_key=t,
                    properties=e,
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
                MATCH (h:Node {key: $head_key})-[r:EDGE]->(t:Node {key: $tail_key})
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
