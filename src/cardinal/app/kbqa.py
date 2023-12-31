import os
from typing import TYPE_CHECKING, Generator, List

from ..core.model import ChatOpenAI, EmbedOpenAI
from ..core.retriever import BaseRetriever
from ..core.schema import Leaf, LeafIndex
from ..core.storage import RedisStorage
from ..core.vectorstore import Milvus
from ..template.kbqa import KBQA_TEMPLATE, PLAIN_TEMPLATE


if TYPE_CHECKING:
    from ..core.schema import BaseMessage


class KBQA:
    def __init__(self) -> None:
        self._chat_model = ChatOpenAI()
        self._retriever = BaseRetriever(
            vectorizer=EmbedOpenAI(),
            storage=RedisStorage[Leaf](name="default"),
            vectorstore=Milvus[LeafIndex](name="default"),
            threshold=float(os.environ.get("KBQA_THRESHOLD")),
        )
        self._plain_template = PLAIN_TEMPLATE
        self._kbqa_template = KBQA_TEMPLATE

    def __call__(self, messages: List["BaseMessage"]) -> Generator[str, None, None]:
        question = messages[-1].content
        documents = self._retriever.retrieve(query=question, top_k=2)
        if len(documents):
            context = "\n".join(documents)
            question = self._kbqa_template.apply(context=context, question=question)
        else:
            question = self._plain_template.apply(question=question)
        messages[-1].content = question
        yield from self._chat_model.stream_chat(messages=messages)
