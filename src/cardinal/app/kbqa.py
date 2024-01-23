import os
from dataclasses import dataclass
from typing import Generator, List

from dotenv import load_dotenv

from ..core.choices import Storage, Vectorstore
from ..core.collector import MsgCollector
from ..core.model import ChatOpenAI, EmbedOpenAI
from ..core.retriever import DenseRetriever
from ..core.schema import AssistantMessage, BaseMessage, HumanMessage, Leaf, LeafIndex, Template


@dataclass
class KbqaConfig:
    plain_template: str
    kbqa_template: str
    kbqa_threshold: float
    kbqa_temperature: float
    embed_instruction: str


class KbqaEngine:
    def __init__(self, database: str) -> None:
        load_dotenv()
        self._window_size = 6
        self._settings = KbqaConfig(
            plain_template=os.environ.get("PLAIN_TEMPLATE"),
            kbqa_template=os.environ.get("KBQA_TEMPLATE"),
            kbqa_threshold=float(os.environ.get("KBQA_THRESHOLD", 1.0)),
            kbqa_temperature=float(os.environ.get("KBQA_TEMPERATURE", 1.0)),
            embed_instruction=os.environ.get("EMBED_INSTRUCTION"),
        )
        self._chat_model = ChatOpenAI()
        self._collector = MsgCollector(storage=Storage[List[BaseMessage]](name="msg_collector"))
        self._retriever = DenseRetriever(
            vectorizer=EmbedOpenAI(),
            storage=Storage[Leaf](name=database),
            vectorstore=Vectorstore[LeafIndex](name=database),
            threshold=self._settings.kbqa_threshold,
        )
        self._plain_template = Template(self._settings.plain_template)
        self._kbqa_template = Template(self._settings.kbqa_template)

    def __call__(self, messages: List["BaseMessage"]) -> Generator[str, None, None]:
        messages = messages[-(self._window_size * 2 + 1) :]
        question = messages[-1].content
        if self._settings.embed_instruction:
            query = self._settings.embed_instruction + question
        else:
            query = question

        documents = self._retriever.retrieve(query, top_k=2)
        if len(documents):
            question = self._kbqa_template.apply(context="\n".join(documents), question=question)
        else:
            question = self._plain_template.apply(question=question)

        augmented_messages = messages[:-1] + [HumanMessage(content=question)]
        response = ""
        for new_token in self._chat_model.stream_chat(
            messages=augmented_messages, temperature=self._settings.kbqa_temperature
        ):
            yield new_token
            response += new_token

        self._collector.collect(messages + [AssistantMessage(content=response)])
