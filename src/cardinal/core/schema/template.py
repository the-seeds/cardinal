import string
from typing import Any, Dict
from typing_extensions import Self


class Function:

    def __init__(self, name: str, desp: str, params: Dict[str, Any]) -> None:
        self.name = name
        self.desp = desp
        self.params = params

    def apply(self) -> Dict[str, Any]: # TODO: add kwargs
        return {
            "name": self.name,
            "description": self.desp,
            "parameters": self.params
        }


class Template:

    def __init__(self, content: str) -> None:
        self.content = content
        self.formatter = string.Formatter()
        self._check_empty_field()

    def apply(self, **kwargs) -> str:
        return self.content.format(**kwargs)

    def bind(self, **kwargs) -> Self:
        self.content = self.content.format(**kwargs)
        self._check_empty_field()
        return self

    def _check_empty_field(self) -> None:
        for (_, field, _, _) in self.formatter.parse(self.content):
            if isinstance(field, str) and len(field) == 0:
                raise ValueError("Non-keyword field is not allowed.")

    def _check_has_field(self) -> None: # not used: allow template without field
        has_field = False
        for (_, field, _, _) in self.formatter.parse(self.content):
            if field is not None:
                has_field = True

        if has_field is False:
            raise ValueError("At least one field is required.")
