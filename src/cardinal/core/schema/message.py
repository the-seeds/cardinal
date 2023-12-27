from pydantic import BaseModel
from typing import Any, Dict
from typing_extensions import Literal


class BaseMessage(BaseModel):
    content: str
    role: str


class SystemMessage(BaseMessage):
    role: Literal["system"] = "system"


class HumanMessage(BaseMessage):
    role: Literal["user"] = "user"


class AssistantMessage(BaseMessage):
    role: Literal["assistant"] = "assistant"


class FunctionAvailable(BaseModel):
    function: Dict[str, Any]
    type: Literal["function"] = "function"


class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
