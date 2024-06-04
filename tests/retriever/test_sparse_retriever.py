from pydantic import BaseModel
from cardinal.storage import AutoStorage
from cardinal.retriever import SparseRetriever
import pytest


class Document(BaseModel):
        content: str
        title: str = "test"
        
doc1 = Document(content="I am alice.")
doc2 = Document(content="I am bob.")


@pytest.mark.skip(reason="not implemented func")
def test_sparse_retriever():
    storage = AutoStorage[Document](name="test")
    storage.insert(keys=["doc1", "doc2"], values=[doc1, doc2])
    retriever = SparseRetriever(storage_name="test", verbose=True)
    assert(retriever.retrieve(query="alice", top_k=1) == doc1)
