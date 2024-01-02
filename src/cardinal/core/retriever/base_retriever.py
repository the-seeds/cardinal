from typing import TYPE_CHECKING, List, Optional

from ..logging import get_logger
from ..schema import Leaf, Retriever


if TYPE_CHECKING:
    from ..model import EmbedOpenAI
    from ..schema import LeafIndex, StringKeyedStorage, VectorStore


logger = get_logger(__name__)


class BaseRetriever(Retriever[Leaf]):
    def __init__(
        self,
        vectorizer: "EmbedOpenAI",
        storage: "StringKeyedStorage[Leaf]",
        vectorstore: "VectorStore[LeafIndex]",
        threshold: Optional[float] = 1e5,
    ) -> None:
        self._vectorizer = vectorizer
        self._storage = storage
        self._vectorstore = vectorstore
        self._threshold = threshold

    def retrieve(self, query: str, top_k: Optional[int] = 4, condition: Optional[str] = None) -> List[str]:
        embedding = self._vectorizer.batch_embed([query])[0]
        results: List[str] = []
        for example, score in self._vectorstore.search(embedding=embedding, top_k=top_k, condition=condition):
            logger.info("Retrieved document with score {:.4f}".format(score))
            if score <= self._threshold:
                results.append(self._storage.query(example.leaf_id).content)

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
