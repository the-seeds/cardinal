import os

from ..utils.import_utils import is_tiktoken_available


if is_tiktoken_available():
    import tiktoken


class TokenOpenAI:
    def __init__(self) -> None:
        self._encoding = tiktoken.encoding_for_model(os.environ.get("CHAT_MODEL"))

    def num_tokens(self, text: str) -> int:
        return len(self._encoding.encode(text))


if __name__ == "__main__":
    token_openai = TokenOpenAI()
    print(token_openai.num_tokens("This is a test"))
