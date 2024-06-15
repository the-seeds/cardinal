from cardinal.vectorstore import AutoVectorStore, AutoCondition
from pydantic import BaseModel
from enum import IntEnum
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


@pytest.mark.skip(reason="no permission")
def test_vector_store():
    data = [Animal(name=text) for text in texts]
    vecstore = AutoVectorStore[Animal].create(name="test", texts=texts, data=data, drop_old=True)
    vecstore.delete(AutoCondition(key="name", value="dog", op=Operator.Eq))
    print(vecstore.search(query="dog", top_k=2))
    