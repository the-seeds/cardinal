from typing import Generator, List

from cardinal.core.models import ChatOpenAI, EmbedOpenAI
from cardinal.core.retriever import BaseRetriever
from cardinal.core.schema import BaseMessage, LeafIndex, Leaf
from cardinal.core.storage import RedisStorage
from cardinal.core.vectorstore import Milvus


class BasicQA:

    def __init__(self) -> None:
        self._chat_model = ChatOpenAI()
        self._retriever = BaseRetriever(
            vectorizer=EmbedOpenAI(),
            storage=RedisStorage[Leaf](name="default"),
            vectorstore=Milvus[LeafIndex](name="default")
        )

    def __call__(self, messages: List[BaseMessage]) -> Generator[str, None, None]:
        pass
