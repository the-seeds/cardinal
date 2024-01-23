from .config import settings
from .storage import ElasticsearchStorage, RedisStorage
from .vectorstore import Chroma, Milvus


STORAGES = {
    "es": ElasticsearchStorage,
    "redis": RedisStorage,
}


VECTORSTORES = {
    "chroma": Chroma,
    "milvus": Milvus,
}


Storage = STORAGES[settings.storage]
Vectorstore = VECTORSTORES[settings.vectorstore]
