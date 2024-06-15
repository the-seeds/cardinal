from cardinal.common import HumanMessage
from cardinal.model import ChatOpenAI


def test_chat_openai():
    chat_openai = ChatOpenAI()
    messages = [HumanMessage(content="Say 'This is a test.'")]
    assert(chat_openai.chat(messages) == 'This is a test.')
    