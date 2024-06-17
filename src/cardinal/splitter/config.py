import os
from dataclasses import dataclass


@dataclass
class Config:
    default_chunk_size: int
    default_chunk_overlap: int


settings = Config(
    default_chunk_size=int(os.environ.get("DEFAULT_CHUNK_SIZE", "100")),
    default_chunk_overlap=int(os.environ.get("DEFAULT_CHUNK_OVERLAP", "0")),
)
