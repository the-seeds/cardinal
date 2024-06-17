from cardinal.collector import MsgCollector
from cardinal.common import HumanMessage, AssistantMessage

def test_msg_collector():
    collector = MsgCollector(storage_name="test", drop_old=True)
    messages = [HumanMessage(content="hi"), AssistantMessage(content="hi there")]
    collector.collect(messages)
    messages = [HumanMessage(content="foo"), AssistantMessage(content="foo too")]
    collector.collect(messages)
    results = collector.dump()
    assert(results[0][0].content=='hi')
    assert(results[0][1].content=='hi there')
    assert(results[1][0].content=='foo')
    assert(results[1][1].content=='foo too')
