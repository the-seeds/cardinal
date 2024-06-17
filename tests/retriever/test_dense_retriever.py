from pydantic import BaseModel
from cardinal.vectorstore import AutoVectorStore
from cardinal.retriever import DenseRetriever
import pytest

class Animal(BaseModel):
    name: str

texts = ["llama", "puppy"]
data = [Animal(name=text) for text in texts]


@pytest.mark.skip(reason="no permission")
def test_dense_retriever():
    vectorstore = AutoVectorStore[Animal].create(name="test", texts=texts, data=data, drop_old=True)
    retriever = DenseRetriever[Animal](vectorstore_name="test", verbose=True)
    assert(retriever.retrieve(query="dog", top_k=1)[0] == data[1])
    