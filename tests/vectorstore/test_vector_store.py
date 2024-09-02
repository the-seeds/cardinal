from pydantic import BaseModel
from cardinal.vectorstore import AutoVectorStore, AutoCondition
from cardinal.vectorstore.schema import Operator

    
class Animal(BaseModel):
    name: str

texts = ["dog", "llama", "puppy"]
data = [Animal(name=text) for text in texts]


def test_vector_store():
    vectorstore = AutoVectorStore[Animal](name="test")
    assert(not vectorstore.exists())  # False
    vectorstore.insert(texts=texts, data=data)
    vectorstore.delete(AutoCondition(key="name", value="dog", op=Operator.Eq))
    vectorstore.flush()
    assert(vectorstore.search(query="dog", top_k=2)[0][0] == data[2])
    assert(vectorstore.search(query="dog", top_k=2)[1][0] == data[1])
    # [(Animal(name='puppy'), 0.8510237336158752), (Animal(name='llama'), 1.1970627307891846)]
    assert(vectorstore.exists())  # True
    vectorstore.destroy()
