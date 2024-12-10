import importlib.metadata
import importlib.util


def _is_package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def is_chroma_available():
    return _is_package_available("chromadb")


def is_elasticsearch_available():
    return _is_package_available("elasticsearch")


def is_pymilvus_availble():
    return _is_package_available("pymilvus")


def is_redis_available():
    return _is_package_available("redis")


def is_neo4j_available():
    return _is_package_available("neo4j")


def is_tiktoken_available():
    return _is_package_available("tiktoken")


def is_transformers_available():
    return _is_package_available("transformers")
