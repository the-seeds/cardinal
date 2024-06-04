from cardinal.common import HumanMessage
from cardinal.model import ChatOpenAI
import pytest


@pytest.mark.skip(reason="no openai api")
def test_chat_openai():
    chat_openai = ChatOpenAI()
    messages = [HumanMessage(content="Say this is a test")]
    print(chat_openai.chat(messages))
    