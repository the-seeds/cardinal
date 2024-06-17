from cardinal.splitter import CJKTextSplitter


def test_text_splitter():
    splitter = CJKTextSplitter(chunk_size=30, chuck_overlap=10)
    text = (
        "The document presents FastEdit, a repository aimed at efficiently injecting "
        "fresh and customized knowledge into large language models using a single command. "
        "It lists the supported models, implemented algorithms, "
        "hardware and software requirements, and provides a guide on getting started "
        "with model editing. It also includes a case study on editing language models "
        "and outlines future implementation goals."
    )
    texts = splitter.split(text)
    assert(len(texts) == 3)