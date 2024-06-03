#from dotenv import load_dotenv
#load_dotenv()

from cardinal.collector import MsgCollector
from cardinal.common import HumanMessage, AssistantMessage

def test_msg_collector():
    collector = MsgCollector(storage_name="test", drop_old=True)
    messages = [HumanMessage(content="hi"), AssistantMessage(content="hi there")]
    collector.collect(messages)
    messages = [HumanMessage(content="foo"), AssistantMessage(content="foo too")]
    collector.collect(messages)
    res = "[[HumanMessage(content='hi', role=<Role.USER: 'user'>), AssistantMessage(content='hi there', role=<Role.ASSISTANT: 'assistant'>)], [HumanMessage(content='foo', role=<Role.USER: 'user'>), AssistantMessage(content='foo too', role=<Role.ASSISTANT: 'assistant'>)]]"
    assert(str(collector.dump()) == res)
