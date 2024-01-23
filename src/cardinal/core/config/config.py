import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    embed_model: str
    chat_model: str
    tokenizer_path: Optional[str]
    default_system_prompt: Optional[str]
    temperature: float

    chunk_size: int
    chunk_overlap: int
    num_cpu_core: int

    storage: str
    redis_uri: Optional[str]
    elasticsearch_uri: Optional[str]

    vectorstore: str
    chroma_path: Optional[str]
    milvus_uri: Optional[str]
    milvus_token: Optional[str]
    admin_user_id: str


load_dotenv()
settings = Config(
    embed_model=os.environ.get("EMBED_MODEL"),
    chat_model=os.environ.get("CHAT_MODEL"),
    tokenizer_path=os.environ.get("TOKENIZER_PATH"),
    default_system_prompt=os.environ.get("DEFAULT_SYSTEM_PROMPT"),
    temperature=float(os.environ.get("TEMPERATURE", 1.0)),
    chunk_size=int(os.environ.get("CHUNK_SIZE", 100)),
    chunk_overlap=int(os.environ.get("CHUNK_OVERLAP", 0)),
    num_cpu_core=int(os.environ.get("NUM_CPU_CORE", 8)),
    storage=os.environ.get("STORAGE"),
    redis_uri=os.environ.get("REDIS_URI"),
    elasticsearch_uri=os.environ.get("ELASTICSEARCH_URI"),
    vectorstore=os.environ.get("VECTORSTORE"),
    chroma_path=os.environ.get("CHROMA_PATH"),
    milvus_uri=os.environ.get("MILVUS_URI"),
    milvus_token=os.environ.get("MILVUS_TOKEN"),
    admin_user_id=os.environ.get("ADMIN_USER_ID"),
)
