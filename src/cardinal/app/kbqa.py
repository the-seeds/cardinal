import os
from typing import Generator, List

from ..core.collector import MsgCollector
from ..core.model import ChatOpenAI, EmbedOpenAI
from ..core.retriever import BaseRetriever
from ..core.schema import AssistantMessage, BaseMessage, HumanMessage, Leaf, LeafIndex, Template
from ..core.storage import RedisStorage
from ..core.vectorstore import Chroma


class KBQA:
    def __init__(self, database: str) -> None:
        self._chat_model = ChatOpenAI()
        self._collector = MsgCollector(storage=RedisStorage[List[BaseMessage]](name="msg_collector"))
        self._retriever = BaseRetriever(
            vectorizer=EmbedOpenAI(),
            storage=RedisStorage[Leaf](name=database),
            vectorstore=Chroma[LeafIndex](name=database),
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

        augmented_messages = messages[:-1] + [HumanMessage(content=question)]
        response = ""
        for new_token in self._chat_model.stream_chat(messages=augmented_messages):
            yield new_token
            response += new_token

        self._collector.collect(messages + [AssistantMessage(content=response)])
