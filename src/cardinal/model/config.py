import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    default_embed_model: str
    default_chat_model: str
    hf_tokenizer_path: Optional[str]


settings = Config(
    default_embed_model=os.environ.get("DEFAULT_EMBED_MODEL", "text-embedding-ada-002"),
    default_chat_model=os.environ.get("DEFAULT_CHAT_MODEL", "gpt-3.5-turbo"),
    hf_tokenizer_path=os.environ.get("HF_TOKENIZER_PATH", None),
)
