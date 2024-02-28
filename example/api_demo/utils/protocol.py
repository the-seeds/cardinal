import time
import uuid
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field

from cardinal import BaseMessage, Role


class DocIndex(BaseModel):
    doc_id: str = Field(default_factory=lambda: uuid.uuid4().hex)


class Document(DocIndex):
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: List[BaseMessage]
    temperature: float = 0.9
    max_tokens: int = 2048
    stream: bool = False


class ChatCompletionMessage(BaseModel):
    role: Optional[Role] = None
    content: Optional[str] = None


class ChatCompletionResponseChoice(BaseModel):
    index: int = 0
    message: ChatCompletionMessage
    finish_reason: str = "stop"


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int = 0
    delta: ChatCompletionMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    id: Literal["chatcmpl-default"] = "chatcmpl-default"
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = "gpt-3.5-turbo"
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]


class ModelCard(BaseModel):
    id: str = "gpt-3.5-turbo"
    object: Literal["model"] = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: Literal["owner"] = "owner"


class ModelList(BaseModel):
    object: Literal["list"] = "list"
    data: List[ModelCard] = []
