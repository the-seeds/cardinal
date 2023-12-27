import importlib.metadata
import importlib.util


def _is_package_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _get_package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except:
        return "0.0.0"


def is_tiktoken_available():
    return _is_package_available("tiktoken")


def is_pymilvus_availble():
    return _is_package_available("pymilvus")


def is_transformers_available():
    return _is_package_available("transformers")
