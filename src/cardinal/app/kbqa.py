from typing import TYPE_CHECKING, Generator, List

from ..core.model import ChatOpenAI, EmbedOpenAI
from ..core.retriever import BaseRetriever
from ..core.schema import Leaf, LeafIndex
from ..core.storage import RedisStorage
from ..core.vectorstore import Milvus
from ..template.kbqa import KBQA_TEMPLATE


if TYPE_CHECKING:
    from ..core.schema import BaseMessage


class KBQA:
    def __init__(self) -> None:
        self._chat_model = ChatOpenAI()
        self._retriever = BaseRetriever(
            vectorizer=EmbedOpenAI(),
            storage=RedisStorage[Leaf](name="default"),
            vectorstore=Milvus[LeafIndex](name="default"),
        )
        self._kbqa_template = KBQA_TEMPLATE

    def __call__(self, messages: List["BaseMessage"]) -> Generator[str, None, None]:
        question = messages[-1].content
        leaves = self._retriever.retrieve(query=question, top_k=2)
        context = "\n".join([leaf.content for leaf in leaves])
        messages[-1].content = self._kbqa_template.apply(context=context, question=question)
        yield from self._chat_model.stream_chat(messages=messages)
