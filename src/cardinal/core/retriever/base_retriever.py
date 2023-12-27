from typing import TYPE_CHECKING, List, Optional

from cardinal.core.schema import Leaf, Retriever

if TYPE_CHECKING:
    from cardinal.core.models import EmbedOpenAI
    from cardinal.core.schema import LeafIndex, StringKeyedStorage, VectorStore


class BaseRetriever(Retriever[Leaf]):

    def __init__(
        self,
        vectorizer: "EmbedOpenAI",
        storage: "StringKeyedStorage[Leaf]",
        vectorstore: "VectorStore[LeafIndex]"
    ) -> None:
        self._vectorizer = vectorizer
        self._storage = storage
        self._vectorstore = vectorstore

    def retrieve(
        self,
        query: str, 
        top_k: Optional[int] = 4,
        condition: Optional[str] = None
    ) -> List[Leaf]:
        embedding = self._vectorizer.batch_embed([query])[0]
        ranked_leaves: List["Leaf"] = []
        for example, score in self._vectorstore.search(
            embedding=embedding,
            top_k=top_k,
            condition=condition
        ):
            ranked_leaves.append((example.leaf_id, score))
        
        results = []
        for i in range(top_k):
            results.append(self._storage.query(ranked_leaves[i].leaf_id))
        return results


if __name__ == "__main__":
    from cardinal.core.models import EmbedOpenAI
    from cardinal.core.schema import LeafIndex
    from cardinal.core.storage import RedisStorage
    from cardinal.core.vectorstore import Milvus

    retriever = BaseRetriever(
        vectorizer=EmbedOpenAI(),
        storage=RedisStorage[Leaf]("test"),
        vectorstore=Milvus[LeafIndex]("test")
    )
    print(retriever.retrieve("How to edit LLMs", top_k=1))
