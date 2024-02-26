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


load_dotenv()
settings = Config(
    embed_model=os.environ.get("EMBED_MODEL"),
    chat_model=os.environ.get("CHAT_MODEL"),
    tokenizer_path=os.environ.get("TOKENIZER_PATH"),
    default_system_prompt=os.environ.get("DEFAULT_SYSTEM_PROMPT"),
)
