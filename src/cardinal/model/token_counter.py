from typing import Optional

from ..utils.import_utils import is_tiktoken_available, is_transformers_available
from .config import settings


if is_tiktoken_available():
    import tiktoken

if is_transformers_available():
    from transformers import AutoTokenizer


class TokenCounter:
    def __init__(self, model: Optional[str] = None) -> None:
        if settings.hf_tokenizer_path is not None:
            tokenizer = AutoTokenizer.from_pretrained(
                settings.hf_tokenizer_path,
                trust_remote_code=True,
            )
            self._encode_func = lambda text: len(tokenizer.tokenize(text))
        else:
            encoding = tiktoken.encoding_for_model(model if model is not None else settings.default_chat_model)
            self._encode_func = lambda text: len(encoding.encode(text))

    def __call__(self, text: str) -> int:
        return self._encode_func(text)
