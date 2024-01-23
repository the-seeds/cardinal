from ..config import settings
from ..utils.import_utils import is_transformers_available


if is_transformers_available():
    from transformers import AutoTokenizer


class TokenHuggingFace:
    def __init__(self) -> None:
        self._tokenizer = AutoTokenizer.from_pretrained(
            settings.tokenizer_path,
            trust_remote_code=True,
        )

    def num_tokens(self, text: str) -> int:
        return len(self._tokenizer.tokenize(text))


if __name__ == "__main__":
    token_hf = TokenHuggingFace()
    print(token_hf.num_tokens("This is a test"))
