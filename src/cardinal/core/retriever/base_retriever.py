from typing import TYPE_CHECKING, List, Optional

from ..schema import Leaf, Retriever


if TYPE_CHECKING:
    from ..model import EmbedOpenAI
    from ..schema import LeafIndex, StringKeyedStorage, VectorStore


class BaseRetriever(Retriever[Leaf]):
    def __init__(
        self, vectorizer: "EmbedOpenAI", storage: "StringKeyedStorage[Leaf]", vectorstore: "VectorStore[LeafIndex]"
    ) -> None:
        self._vectorizer = vectorizer
        self._storage = storage
        self._vectorstore = vectorstore

    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional[str] = None) -> List[Leaf]:
        embedding = self._vectorizer.batch_embed([query])[0]
        leaf_ids: List["LeafIndex"] = []
        for example, _ in self._vectorstore.search(embedding=embedding, top_k=top_k, condition=condition):
            leaf_ids.append(example.leaf_id)

        results: List["Leaf"] = []
        for i in range(top_k):
            results.append(self._storage.query(leaf_ids[i]))
        return results


if __name__ == "__main__":
    from ..model import EmbedOpenAI
    from ..schema import LeafIndex
    from ..storage import RedisStorage
    from ..vectorstore import Milvus

    retriever = BaseRetriever(
        vectorizer=EmbedOpenAI(), storage=RedisStorage[Leaf]("test"), vectorstore=Milvus[LeafIndex]("test")
    )
    print(retriever.retrieve("How to edit LLMs", top_k=1))
