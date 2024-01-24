import os
import random
import re
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from dotenv import load_dotenv

from ..core.choices import Storage
from ..core.logging import get_logger
from ..core.model import ChatOpenAI
from ..core.retriever import SparseRetriever
from ..core.schema import BaseMessage, HumanMessage, Leaf, Template
from ..core.utils.import_utils import is_jieba_available


if is_jieba_available():
    import jieba.posseg as pseg


logger = get_logger(__name__)


@dataclass
class WordGraphConfig:
    keyword_template: str
    keyword_temperature: float


def _is_zh_char(char: str) -> bool:
    if "\u4e00" <= char <= "\u9fd5":
        return True
    return False


def _is_accepted_word(word: str, pos: str) -> bool:
    if pos not in ["n", "nr", "nrt", "ns", "nz", "vn", "l"]:
        return False

    if not all(_is_zh_char(char) for char in word):
        return False

    if len(word) < 2 or len(word) > 5:
        return False

    return True


def _find_connected_words(keyword: str, texts: Sequence[str]) -> Tuple[List[str], List[str]]:
    prefix_words = set()
    suffix_words = set()
    for text in texts:
        pieces = text.split(keyword)
        if len(pieces) < 2:
            continue

        if pieces[0]:
            prefix_word, prefix_pos = pseg.lcut(pieces[0])[-1]
            if _is_accepted_word(prefix_word, prefix_pos):
                prefix_words.add(prefix_word)

        for piece in pieces[1:-1]:
            if piece:
                piece_words = pseg.lcut(piece)
                prefix_word, prefix_pos = piece_words[-1]
                suffix_word, suffix_pos = piece_words[0]
                if _is_accepted_word(prefix_word, prefix_pos):
                    prefix_words.add(prefix_word)
                if _is_accepted_word(suffix_word, suffix_pos):
                    suffix_words.add(suffix_word)

        if pieces[-1]:
            suffix_word, suffix_pos = pseg.lcut(pieces[-1])[0]
            if _is_accepted_word(suffix_word, suffix_pos):
                suffix_words.add(suffix_word)

    prefix_words = random.sample(list(prefix_words), min(len(prefix_words), 5))
    suffix_words = random.sample(list(suffix_words), min(len(suffix_words), 5))
    return prefix_words, suffix_words


class WordGraphEngine:
    def __init__(self, database: str) -> None:
        load_dotenv()
        self._settings = WordGraphConfig(
            keyword_template=os.environ.get("KEYWORD_TEMPLATE"),
            keyword_temperature=os.environ.get("KEYWORD_TEMPERATURE"),
        )
        self._chat_model = ChatOpenAI()
        self._retriever = SparseRetriever(storage=Storage[Leaf](name=database))
        self._keyword_template = Template(self._settings.keyword_template)

    def __call__(self, messages: List["BaseMessage"]) -> List[Tuple[str, List[str], List[str]]]:
        r"""
        Args:
            messages

        Returns:
            (keyword, prefix_words, suffix_words) * n
        """
        answer = messages[-1].content
        answer = self._keyword_template.apply(answer=answer)
        response = self._chat_model.chat(
            messages=[HumanMessage(content=answer)],
            temperature=self._settings.keyword_temperature,
        )
        matches = re.findall(r"([\u4e00-\u9fd5]+)", response)
        keywords = set()
        for match in matches:
            for word, pos in pseg.lcut(match):
                if _is_accepted_word(word, pos):
                    keywords.add(word)

        keywords = random.sample(list(keywords), min(len(keywords), 3))
        logger.info("Found keywords: {}".format(", ".join(keywords)))
        ret = []
        for keyword in keywords:
            documents = self._retriever.retrieve(keyword, top_k=5)
            prefix_words, suffix_words = _find_connected_words(keyword, documents)
            if len(prefix_words) or len(suffix_words):
                ret.append((keyword, prefix_words, suffix_words))

        return ret
