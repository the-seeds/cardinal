from pydantic import BaseModel
from cardinal.storage import AutoStorage
from cardinal.retriever import SparseRetriever
import os
import pytest


class Document(BaseModel):
        content: str
        title: str = "test"
        
doc1 = Document(content="I am alice.")
doc2 = Document(content="I am bob.")


ENV_STORAGE = os.getenv('STORAGE')

@pytest.mark.skipif(ENV_STORAGE=='redis',
                    reason="not implemented")
def test_sparse_retriever():
    storage = AutoStorage[Document](name="test")
    storage.insert(keys=["doc1", "doc2"], values=[doc1, doc2])
    if ENV_STORAGE == 'es':
        storage._storage.database.indices.refresh()
    retriever = SparseRetriever(storage_name="test", verbose=True)
    assert(retriever.retrieve(query="alice", top_k=1) == [doc1])
    storage.destroy()