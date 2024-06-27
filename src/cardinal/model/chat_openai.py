import json
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Union

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from ..common import BaseMessage, FunctionAvailable, FunctionCall
from .config import settings


if TYPE_CHECKING:
    from openai import Stream
    from openai.types.chat import ChatCompletion, ChatCompletionChunk


class ChatOpenAI:
    def __init__(self, model: Optional[str] = None) -> None:
        self._client = OpenAI(max_retries=5, timeout=30.0)
        self._model = model if model is not None else settings.default_chat_model

    def _parse_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        return [message.model_dump() for message in messages]

    def _parse_tools(self, tools: List[FunctionAvailable]) -> List[Dict[str, Any]]:
        return [tool.model_dump() for tool in tools]

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def _completion_with_backoff(
        self,
        messages: List[BaseMessage],
        stream: bool = False,
        tools: Optional[List[FunctionAvailable]] = None,
        **kwargs,
    ) -> Union["ChatCompletion", "Stream[ChatCompletionChunk]"]:
        request_kwargs = {"messages": self._parse_messages(messages), "model": self._model, "stream": stream}
        if tools is not None:
            request_kwargs["tools"] = self._parse_tools(tools)

        return self._client.chat.completions.create(**request_kwargs, **kwargs)

    def chat(self, messages: List[BaseMessage], **kwargs) -> str:
        return self._completion_with_backoff(messages=messages, **kwargs).choices[0].message.content

    def stream_chat(self, messages: List[BaseMessage], **kwargs) -> Generator[str, None, None]:
        for chunk in self._completion_with_backoff(messages=messages, stream=True, **kwargs):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def function_call(self, messages: List[BaseMessage], tools: List[FunctionAvailable], **kwargs) -> FunctionCall:
        tool_call = (
            self._completion_with_backoff(messages=messages, tools=tools, **kwargs).choices[0].message.tool_calls[0]
        )  # current only support a single tool
        return FunctionCall(name=tool_call.function.name, arguments=json.loads(tool_call.function.arguments))
