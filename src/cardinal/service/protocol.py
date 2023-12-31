import time
from pydantic import BaseModel, Field
from typing import List, Optional

from ..core.schema import BaseMessage


class ChatCompletionRequest(BaseModel):
    uuid: str
    messages: List[BaseMessage]


class ChatCompletionResponse(BaseModel):
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    content: Optional[str] = None
