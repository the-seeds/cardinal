from pydantic import BaseModel
from cardinal.vectorstore import AutoVectorStore
from cardinal.retriever import DenseRetriever


class Animal(BaseModel):
    name: str

texts = ["llama", "puppy"]
data = [Animal(name=text) for text in texts]


def test_dense_retriever():
    vectorStore = AutoVectorStore[Animal].create(name="test", texts=texts, data=data, drop_old=True)
    retriever = DenseRetriever[Animal](vectorstore_name="test", verbose=True)
    assert(retriever.retrieve(query="dog", top_k=1) == [data[1]])
    vectorStore.destroy()
    