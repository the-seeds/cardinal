import os
import re
from typing import List

from cardinal.core.logging import get_logger
from cardinal.core.models import TokenHuggingFace, TokenOpenAI


logger = get_logger(__name__)


class RecursiveCharacterTextSplitter:
    r"""
    Modified from:
    https://github.com/langchain-ai/langchain/blob/v0.0.352/libs/langchain/langchain/text_splitter.py
    """

    def __init__(self) -> None:
        self._separators = ["\n\n", "\n", " ", ""]
        self._chunk_size = os.environ.get("CHUNK_SIZE")
        self._chunk_overlap = os.environ.get("CHUNK_OVERLAP")
        assert self._chunk_overlap < self._chunk_size, "chunk overlap must be larger than chunk size"
        if os.environ.get("TOKENIZER_PATH"):
            self._tokenizer = TokenHuggingFace()
        else:
            self._tokenizer = TokenOpenAI()

    @staticmethod
    def _split_text(text: str, separator: str) -> List[str]:
        splits = re.split(separator, text) if separator else list(text)
        return [split for split in splits if split]

    @staticmethod
    def _join_docs(docs: List[str], separator: str) -> str:
        return separator.join(docs).strip()

    def _merge(self, splits: List[str], separator: str) -> List[str]:
        separator_len = self._tokenizer.num_tokens(separator)
        merged_docs = []
        inprocess_docs = []
        total_length = 0
        for split in splits:
            split_length = self._tokenizer.num_tokens(split)
            if (
                total_length + split_length + (separator_len if len(inprocess_docs) > 0 else 0)
                > self._chunk_size
            ):
                if total_length > self._chunk_size:
                    logger.warning("Created a chunk of size {} > {}".format(total_length, self._chunk_size))

                if len(inprocess_docs) > 0:
                    text = self._join_docs(inprocess_docs, separator)
                    if text:
                        merged_docs.append(text)

                    while total_length > self._chunk_overlap or (
                        total_length + split + (separator_len if len(inprocess_docs) > 0 else 0)
                        > self._chunk_size
                        and total_length > 0
                    ):
                        discard_doc = inprocess_docs.pop(0)
                        total_length -= self._tokenizer.num_tokens(discard_doc) + (
                            separator_len if len(inprocess_docs) > 1 else 0
                        )

            inprocess_docs.append(split)
            total_length += split_length + (separator_len if len(inprocess_docs) > 1 else 0)

        text = self._join_docs(inprocess_docs, separator)
        if text is not None:
            merged_docs.append(text)

        return merged_docs

    def split(self, text: str) -> List[str]:
        return self._split(text, self._separators) # deepcopy

    def _split(self, text: str, separators: List[str]) -> List[str]:
        separators = [sep for sep in separators]
        separator = separators.pop(0)

        splits = self._split_text(text, separator)
        final_chunks = []
        good_splits = []
        for split in splits:
            if self._tokenizer.num_tokens(split) < self._chunk_size:
                good_splits.append(split)
            else:
                if good_splits:
                    merged_text = self._merge(good_splits, separator)
                    final_chunks.extend(merged_text)
                    good_splits = []
                if not separators:
                    final_chunks.append(split)
                else:
                    extra_chunks = self._split(split, separators)
                    final_chunks.extend(extra_chunks)
        if good_splits:
            merged_text = self._merge(good_splits, separator)
            final_chunks.extend(merged_text)
        return final_chunks


class ChineseTextSplitter(RecursiveCharacterTextSplitter):

    def split(self, text: str) -> List[str]:
        text = re.sub(r"\n{3,}", r"\n", text)
        text = re.sub(r" {3,}", r" ", text)
        text = re.sub(r"([。！？；])([^’”])", r"\1\n\2", text)  # split with chinese stops
        text = re.sub(r"(\…{2})([^’”])", r"\1\n\2", text)  # split with chinese ellipsis
        text = re.sub(r"([。！？；][’”]{0,2})([^，。！？；])", r"\1\n\2", text)
        text = text.rstrip()
        return super().split(text)


if __name__ == "__main__":
    splitter = ChineseTextSplitter()
    text = (
        "The document presents FastEdit, a repository aimed at efficiently injecting "
        "fresh and customized knowledge into large language models using a single command. "
        "It lists the supported models, implemented algorithms, "
        "hardware and software requirements, and provides a guide on getting started "
        "with model editing. It also includes a case study on editing language models "
        "and outlines future implementation goals."
    )
    print(splitter.split(text))
