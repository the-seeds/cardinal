from typing import List, Optional

from ..storage import AutoStorage
from .schema import Collector, T


class BaseCollector(Collector[T]):
    def __init__(self, storage_name: str, drop_old: Optional[bool] = False) -> None:
        self._storage = AutoStorage[T](name=storage_name)
        self._prefix = "collector_{}"
        if drop_old:
            self._storage.unique_reset()

    def collect(self, data: T) -> None:
        num_collected = self._storage.unique_get()
        self._storage.insert([self._prefix.format(num_collected)], [data])
        self._storage.unique_incr()

    def dump(self) -> List[T]:
        results = []
        for i in range(self._storage.unique_get()):
            results.append(self._storage.query(self._prefix.format(i)))

        return results


if __name__ == "__main__":
    from pydantic import BaseModel

    from ..common import AssistantMessage, BaseMessage, HumanMessage

    class History(BaseModel):
        messages: List[BaseMessage]

    collector = BaseCollector[History](storage_name="test", drop_old=True)
    messages = [HumanMessage(content="hi"), AssistantMessage(content="hi there")]
    collector.collect(History(messages=messages))
    messages = [HumanMessage(content="foo"), AssistantMessage(content="foo too")]
    collector.collect(History(messages=messages))
    print(collector.dump())
    # [History(messages=[
    # HumanMessage(role=<Role.USER: 'user'>, content='hi'),
    # AssistantMessage(role=<Role.ASSISTANT: 'assistant'>, content='hi there', tool_calls=None)]),
    # History(messages=[HumanMessage(role=<Role.USER: 'user'>, content='foo'),
    # AssistantMessage(role=<Role.ASSISTANT: 'assistant'>, content='foo too', tool_calls=None)])]
