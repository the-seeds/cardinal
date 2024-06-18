from cardinal.vectorstore import AutoVectorStore, AutoCondition
from pydantic import BaseModel
from enum import IntEnum
import os
import pytest


class Operator(IntEnum):
    Eq = 0
    Ne = 1
    Gt = 2
    Ge = 3
    Lt = 4
    Le = 5
    In = 6
    Notin = 7
    And = 8
    Or = 9
    

class Animal(BaseModel):
    name: str

texts = ["dog", "llama", "puppy"]
data = [Animal(name=text) for text in texts]


def test_vector_store():
    vectorStore = AutoVectorStore[Animal](name="test")
    ENV_VECTORSTORE = os.getenv('VECTORSTORE')
    assert(not vectorStore.exists())  # False
    vectorStore.insert(texts=texts, data=data)
    if ENV_VECTORSTORE == 'milvus':
        vectorStore._vectorstore.store.flush()
    vectorStore.delete(AutoCondition(key="name", value="dog", op=Operator.Eq))
    if ENV_VECTORSTORE == 'milvus':
        vectorStore._vectorstore.store.flush()
    assert(vectorStore.search(query="dog", top_k=2)[0][0] == data[2])
    assert(vectorStore.search(query="dog", top_k=2)[1][0] == data[1])
    # [(Animal(name='puppy'), 0.8510237336158752), (Animal(name='llama'), 1.1970627307891846)]
    assert(vectorStore.exists())  # True
    vectorStore.destroy()
