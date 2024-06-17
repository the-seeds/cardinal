from cardinal.model import EmbedOpenAI
import pytest


@pytest.mark.skip(reason="no permission")
def test_embed_openai():
    embed_openai = EmbedOpenAI()
    assert(embed_openai.batch_embed(["This is a test"]) is not None)
    