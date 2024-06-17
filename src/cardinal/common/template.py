import string
from dataclasses import dataclass
from typing import Any, Dict

from typing_extensions import Self


@dataclass
class Function:
    name: str
    description: str
    parameters: Dict[str, Any]

    def apply(self) -> Dict[str, Any]:  # TODO: add kwargs
        return {"name": self.name, "description": self.description, "parameters": self.parameters}


@dataclass
class Template:
    content: str

    def __post_init__(self) -> None:
        formatter = string.Formatter()
        for _, field, _, _ in formatter.parse(self.content):
            if isinstance(field, str) and len(field) == 0:
                raise ValueError("Non-keyword field is not allowed.")

    def apply(self, **kwargs) -> str:
        return self.content.format(**kwargs)

    def bind(self, **kwargs) -> Self:
        return Template(self.content.format(**kwargs))
