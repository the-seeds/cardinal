from pydantic import BaseModel
from cardinal.storage import AutoStorage
import os


class Document(BaseModel):
        content: str
        title: str = "test"

        
doc1 = Document(content="I am alice.")
doc2 = Document(content="I am bob.")

def test_redis():
    temp = os.environ.get("STORAGE")
    os.environ["STORAGE"] = "redis"
    storage = AutoStorage[Document](name="test")
    
    storage.insert(keys=["doc1", "doc2"], values=[doc1, doc2])
    assert(storage.query("doc1")==doc1)
    storage.clear()
    assert(storage.query("doc1")==None)
    storage.unique_reset()
    storage.unique_incr()
    storage.unique_incr()
    assert(storage.unique_get()==2)
    os.environ["STORAGE"] = temp
    