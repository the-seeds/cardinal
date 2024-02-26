from typing import List, Optional

from ..common import BaseMessage
from ..storage import AutoStorage
from .schema import Collector


class MsgCollector(Collector[List[BaseMessage]]):
    def __init__(self, storage_name: str, drop_old: Optional[bool] = False) -> None:
        self._storage = AutoStorage[List[BaseMessage]](name=storage_name)
        self._prefix = "msgcollector_{}"
        if drop_old:
            self._storage.unique_reset()

    def collect(self, data: List[BaseMessage]) -> None:
        num_collected = self._storage.unique_get()
        self._storage.insert([self._prefix.format(num_collected)], [data])
        self._storage.unique_incr()

    def dump(self) -> List[BaseMessage]:
        results = []
        for i in range(self._storage.unique_get()):
            results.append(self._storage.query(self._prefix.format(i)))

        return results


if __name__ == "__main__":
    from ..common import AssistantMessage, HumanMessage

    collector = MsgCollector(storage_name="test", drop_old=True)
    messages = [HumanMessage(content="hi"), AssistantMessage(content="hi there")]
    collector.collect(messages)
    messages = [HumanMessage(content="foo"), AssistantMessage(content="foo too")]
    collector.collect(messages)
    print(collector.dump())
