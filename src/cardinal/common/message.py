from enum import Enum, unique
from typing import Any, Dict, Iterable, Optional

from pydantic import BaseModel
from typing_extensions import Literal


@unique
class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"


class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class BaseMessage(BaseModel):
    role: str
    content: str


class SystemMessage(BaseMessage):
    role: Literal[Role.SYSTEM] = Role.SYSTEM


class HumanMessage(BaseMessage):
    role: Literal[Role.USER] = Role.USER


class AssistantMessage(BaseMessage):
    role: Literal[Role.ASSISTANT] = Role.ASSISTANT
    content: Optional[str] = None
    tool_calls: Optional[Iterable[Dict[str, Any]]] = None


class ToolMessage(BaseMessage):
    role: Literal[Role.TOOL] = Role.TOOL


class FunctionAvailable(BaseModel):
    function: Dict[str, Any]
    type: Literal["function"] = "function"
