import os
from dataclasses import dataclass


@dataclass
class Config:
    chunk_size: int
    chunk_overlap: int


settings = Config(
    chunk_size=int(os.environ.get("CHUNK_SIZE", "100")),
    chunk_overlap=int(os.environ.get("CHUNK_OVERLAP", "0")),
)
