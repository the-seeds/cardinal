import time
import uuid
from typing import List, Optional

from pydantic import BaseModel, Field

from cardinal import BaseMessage


class DocIndex(BaseModel):
    doc_id: str = Field(default_factory=lambda: uuid.uuid4().hex)


class Document(DocIndex):
    content: str


class ChatCompletionRequest(BaseModel):
    messages: List[BaseMessage]


class ChatCompletionResponse(BaseModel):
    created: int = Field(default_factory=lambda: int(time.time()))
    content: Optional[str] = None
