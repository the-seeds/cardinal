from pathlib import Path
from typing import TYPE_CHECKING, List

from ..schema import Extractor, Leaf, LeafIndex
from ..splitter import CJKTextSplitter


if TYPE_CHECKING:
    from ..model import EmbedOpenAI
    from ..schema import StringKeyedStorage, VectorStore


class BaseExtractor(Extractor):
    def __init__(
        self, vectorizer: "EmbedOpenAI", storage: "StringKeyedStorage[Leaf]", vectorstore: "VectorStore[LeafIndex]"
    ) -> None:
        self._vectorizer = vectorizer
        self._storage = storage
        self._vectorstore = vectorstore
        self._splitter = CJKTextSplitter()

    def load(self, doc_files: List[Path], user_id: str) -> None:
        raw_docs: List[str] = []
        for doc_file in doc_files:
            if doc_file.suffix == ".txt":
                with open(doc_file, "r", encoding="utf-8") as f:
                    raw_docs.append(f.read())
            else:
                raise NotImplementedError

        text_chunks = []
        for doc in raw_docs:
            text_chunks.extend(self._splitter.split(doc))

        leaf_indexes = []
        for content in text_chunks:
            leaf_index = LeafIndex(user_id=user_id)
            leaf = Leaf(content=content, leaf_id=leaf_index.leaf_id, user_id=user_id)
            self._storage.insert(leaf.leaf_id, leaf)
            leaf_indexes.append(leaf_index)

        embeddings = self._vectorizer.batch_embed(text_chunks)
        self._vectorstore.insert(embeddings, leaf_indexes)


if __name__ == "__main__":
    from ..model import EmbedOpenAI
    from ..storage import RedisStorage
    from ..vectorstore import Milvus

    extractor = BaseExtractor(
        vectorizer=EmbedOpenAI(), storage=RedisStorage[Leaf]("test"), vectorstore=Milvus[LeafIndex]("test")
    )
    extractor.load(doc_files=[Path("test1.txt"), Path("test2.txt")])
