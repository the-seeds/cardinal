from typing import TYPE_CHECKING, List

from ..schema import BaseMessage, Collector


if TYPE_CHECKING:
    from ..schema import StringKeyedStorage


class MsgCollector(Collector[List[BaseMessage]]):
    def __init__(self, storage: "StringKeyedStorage[List[BaseMessage]]") -> None:
        self._storage = storage
        self._prefix = "msgcollector_{}"

    def collect(self, data: List[BaseMessage]) -> None:
        num_collected = self._storage.unique_get()
        self._storage.insert(self._prefix.format(num_collected), data)
        self._storage.unique_incr()

    def dump(self) -> List[List[BaseMessage]]:
        results = []
        for i in range(self._storage.unique_get()):
            results.append(self._storage.query(self._prefix.format(i)))

        return results


if __name__ == "__main__":
    from ..schema import AssistantMessage, HumanMessage
    from ..storage import RedisStorage

    collector = MsgCollector(storage=RedisStorage[List[BaseMessage]]("test"))
    messages = [HumanMessage(content="hi"), AssistantMessage(content="hi there")]
    collector._storage.unique_reset()
    collector.collect(messages)
    collector.collect(messages)
    print(collector.dump())
