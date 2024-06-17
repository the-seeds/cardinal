from cardinal.model import TokenCounter


def test_token_counter():
    counter = TokenCounter()
    assert(counter("This is a test") == 4)
