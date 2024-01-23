import time
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

from ..schema import BaseMessage, Collector


if TYPE_CHECKING:
    from ..schema import StringKeyedStorage


Dialog = List[BaseMessage]


class History(BaseModel):
    id: int
    created: int = Field(default_factory=lambda: int(time.time()))
    messages: Dialog


class MsgCollector(Collector[Dialog]):
    def __init__(self, storage: "StringKeyedStorage[History]", drop_old: Optional[bool] = False) -> None:
        self._storage = storage
        self._prefix = "msgcollector_{}"
        if drop_old:
            storage.unique_reset()

    def collect(self, data: Dialog) -> None:
        num_collected = self._storage.unique_get()
        history = History(id=num_collected, messages=data)
        self._storage.insert([self._prefix.format(num_collected)], [history])
        self._storage.unique_incr()

    def dump(self) -> List[History]:
        results = []
        for i in range(self._storage.unique_get()):
            results.append(self._storage.query(self._prefix.format(i)))

        return results


if __name__ == "__main__":
    from ..schema import AssistantMessage, HumanMessage
    from ..storage import RedisStorage

    collector = MsgCollector(storage=RedisStorage[Dialog]("test"), drop_old=True)
    messages = [HumanMessage(content="hi"), AssistantMessage(content="hi there")]
    collector.collect(messages)
    messages = [HumanMessage(content="foo"), AssistantMessage(content="foo too")]
    collector.collect(messages)
    print(collector.dump())
