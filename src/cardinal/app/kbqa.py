import os
from typing import TYPE_CHECKING, Generator, List

from ..core.model import ChatOpenAI, EmbedOpenAI
from ..core.retriever import BaseRetriever
from ..core.schema import Leaf, LeafIndex, Template
from ..core.storage import RedisStorage
from ..core.vectorstore import Chroma

from ..core.schema import FunctionAvailable, FunctionCall
from ..core.function_calls.functions import parse_function_availables, execute_function_call

if TYPE_CHECKING:
    from ..core.schema import BaseMessage


class KBQA:
    def __init__(self) -> None:
        self._chat_model = ChatOpenAI()
        self._retriever = BaseRetriever(
            vectorizer=EmbedOpenAI(),
            storage=RedisStorage[Leaf](name="default"),
            vectorstore=Chroma[LeafIndex](name="default"),
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
            question = self._kbqa_template.apply(
                context="\n".join(documents), question=question)
        else:
            question = self._plain_template.apply(question=question)

        # parse function availables
        question, tools = parse_function_availables(question)

        # execute function calls
        if tools:
            function_call = self._chat_model.function_call(
                messages=messages, tools=tools)
            # calling the function_calls, and get the response
            response = execute_function_call(function_call)
            yield response

        messages[-1].content = question
        yield from self._chat_model.stream_chat(messages=messages)
