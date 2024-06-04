from pydantic import BaseModel
from cardinal.vectorstore import AutoVectorStore
from cardinal.retriever import HybridRetriever


class Animal(BaseModel):
    name: str
    color: str

animals = [("llama", "green"), ("llama", "blue"), ("puppy", "pink"), ("puppy", "blue")]
data = [Animal(name=name, color=color) for name, color in animals]


def test_hybird_retriever():
    names = [animal.name for animal in data]
    colors = [animal.color for animal in data]
    AutoVectorStore[Animal].create(name="test1", texts=names, data=data, drop_old=True)
    AutoVectorStore[Animal].create(name="test2", texts=colors, data=data, drop_old=True)
    retriever = HybridRetriever[Animal](vectorstore_names=["test1", "test2"], verbose=True)
    print(retriever.retrieve(query="a pink dog", top_k=2))
