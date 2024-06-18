from pydantic import BaseModel
from typing import List
from cardinal.collector import BaseCollector
from cardinal.common import BaseMessage, AssistantMessage, HumanMessage

class History(BaseModel):
    messages: List[BaseMessage]

def test_base_collector():
    collector = BaseCollector[History](storage_name="test", drop_old=True)
    messages = [HumanMessage(content="hi"), AssistantMessage(content="hi there")]
    history1 = History(messages=messages)
    collector.collect(history1)
    messages = [HumanMessage(content="foo"), AssistantMessage(content="foo too")]
    history2 = History(messages=messages)
    collector.collect(history2)
    results = collector.dump()
    assert(results[0] == history1)
    assert(results[1] == history2)
