from ..utils.import_utils import is_tiktoken_available, is_transformers_available
from .config import settings


if is_tiktoken_available():
    import tiktoken

if is_transformers_available():
    from transformers import AutoTokenizer


class TokenCounter:
    def __init__(self) -> None:
        if settings.tokenizer_path is not None:
            self._encoding = AutoTokenizer.from_pretrained(
                settings.tokenizer_path,
                trust_remote_code=True,
            )
        else:
            self._encoding = tiktoken.encoding_for_model(settings.chat_model)

    def __call__(self, text: str) -> int:
        if settings.tokenizer_path is not None:
            return len(self._encoding.tokenize(text))
        else:
            return len(self._encoding.encode(text))


if __name__ == "__main__":
    counter = TokenCounter()
    print(counter("This is a test"))
