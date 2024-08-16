from cardinal.model import EmbedOpenAI


def test_embed_openai():
    embed_openai = EmbedOpenAI()
    assert(embed_openai.batch_embed(["This is a test"]) is not None)
    