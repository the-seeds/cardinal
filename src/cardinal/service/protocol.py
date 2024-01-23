import time
from typing import List, Optional

from pydantic import BaseModel, Field

from ..core.schema import BaseMessage


class ChatCompletionRequest(BaseModel):
    uuid: str
    messages: List[BaseMessage]


class ChatCompletionResponse(BaseModel):
    created: int = Field(default_factory=lambda: int(time.time()))
    content: Optional[str] = None


class WordGraphRequest(BaseModel):
    uuid: str
    messages: List[BaseMessage]


class WordGraphNode(BaseModel):
    id: str
    name: str
    category: int
    x: int
    y: int


class WordGraphLink(BaseModel):
    source: str
    target: str


class WordGraphCategory(BaseModel):
    name: str


class WordGraphObject(BaseModel):
    nodes: List[WordGraphNode]
    links: List[WordGraphLink]
    categories: List[WordGraphCategory]


class WordGraphResponse(BaseModel):
    graph: List[WordGraphObject]
