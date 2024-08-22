from pydantic import BaseModel
from cardinal.vectorstore import AutoVectorStore, AutoCondition
from cardinal.vectorstore.schema import Operator

    
class Animal(BaseModel):
    name: str

texts = ["dog", "llama", "puppy"]
data = [Animal(name=text) for text in texts]


def test_vector_store():
    vectorStore = AutoVectorStore[Animal](name="test")
    assert(not vectorStore.exists())  # False
    vectorStore.insert(texts=texts, data=data)
    vectorStore.delete(AutoCondition(key="name", value="dog", op=Operator.Eq))
    assert(vectorStore.search(query="dog", top_k=2)[0][0] == data[2])
    assert(vectorStore.search(query="dog", top_k=2)[1][0] == data[1])
    # [(Animal(name='puppy'), 0.8510237336158752), (Animal(name='llama'), 1.1970627307891846)]
    assert(vectorStore.exists())  # True
    vectorStore.destroy()
