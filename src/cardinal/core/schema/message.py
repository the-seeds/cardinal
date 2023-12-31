from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict
from typing_extensions import Literal


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class BaseMessage(BaseModel):
    content: str
    role: str


class SystemMessage(BaseMessage):
    role: Literal[Role.SYSTEM] = Role.SYSTEM


class HumanMessage(BaseMessage):
    role: Literal[Role.USER] = Role.USER


class AssistantMessage(BaseMessage):
    role: Literal[Role.ASSISTANT] = Role.ASSISTANT


class FunctionAvailable(BaseModel):
    function: Dict[str, Any]
    type: Literal[Role.FUNCTION] = Role.FUNCTION


class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
