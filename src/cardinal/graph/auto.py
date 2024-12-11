from typing import Dict, List, Optional, Sequence, Tuple, Type
from .neo4j import Neo4j
from .config import settings
from .schema import GraphStorage, T


class AutoGraphStorage(GraphStorage[T]):
    def __init__(self, name: str) -> None:
        self._graph_storage = _get_graph_storage()(name)

    def insert_node(self, keys: Sequence[str], nodes: Sequence[T]) -> None:
        return self._graph_storage.insert_node(keys, nodes)

    def insert_edge(self, head_keys: Sequence[str], tail_keys: Sequence[str], edges: Sequence[T]) -> None:
        return self._graph_storage.insert_edge(head_keys, tail_keys, edges)

    def query_node(self, key: str) -> Optional[T]:
        return self._graph_storage.query_node(key)

    def query_edge(self, head_key: str, tail_key: str) -> Optional[T]:
        return self._graph_storage.query_edge(head_key, tail_key)

    def query_node_edges(self, key: str) -> Optional[List[T]]:
        return self._graph_storage.query_node_edges(key)
    
    def clustering(self) -> None:
        return self._graph_storage.clustering()
    
    def community_schema(self) -> dict[str, T]:
        return self._graph_storage.community_schema()
    
    def drop_community(self) -> None:
        return self._graph_storage.drop_community()
    
    def exists(self) -> bool:
        return self._graph_storage.exists()

    def destroy(self) -> None:
        return self._graph_storage.destroy()


_graph_storages: Dict[str, Type["GraphStorage"]] = {}


def _add_graph_storage(name: str, storage: Type["GraphStorage"]) -> None:
    _graph_storages[name] = storage


def _list_storages() -> List[str]:
    return list(map(str, _graph_storages.keys()))


def _get_graph_storage() -> Type["GraphStorage"]:
    if settings.graph_storage not in _graph_storages:
        raise ValueError("Graph Storage not found, should be one of {}.".format(_list_storages()))
    return _graph_storages[settings.graph_storage]


_add_graph_storage("neo4j", Neo4j)
