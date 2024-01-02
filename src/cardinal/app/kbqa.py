import os
from typing import TYPE_CHECKING, Generator, List

from ..core.model import ChatOpenAI, EmbedOpenAI
from ..core.retriever import BaseRetriever
from ..core.schema import Leaf, LeafIndex, Template
from ..core.storage import RedisStorage
from ..core.vectorstore import Milvus


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
        self._plain_template = Template(os.environ.get("PLAIN_TEMPLATE"))
        self._kbqa_template = Template(os.environ.get("KBQA_TEMPLATE"))

    def __call__(self, messages: List["BaseMessage"]) -> Generator[str, None, None]:
        question = messages[-1].content
        if os.environ.get("EMBED_INSTRUCTION"):
            query = os.environ.get("EMBED_INSTRUCTION") + question
        else:
            query = question

        documents = self._retriever.retrieve(query, top_k=2)
        if len(documents):
            question = self._kbqa_template.apply(context="\n".join(documents), question=question)
        else:
            question = self._plain_template.apply(question=question)

        messages[-1].content = question
        yield from self._chat_model.stream_chat(messages=messages)
