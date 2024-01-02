import os
from multiprocessing import Pool
from pathlib import Path
from typing import TYPE_CHECKING, List

from tqdm import tqdm

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

    def load(self, input_files: List[Path], user_id: str) -> None:
        file_contents: List[str] = []
        for file_path in tqdm(input_files, desc="Extract content"):
            if file_path.suffix == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    file_contents.append(f.read())
            else:
                raise NotImplementedError

        text_chunks = []
        with Pool(processes=int(os.environ.get("NUM_CPU_CORE"))) as pool:
            for chunks in tqdm(pool.imap_unordered(self._splitter.split, file_contents), total=len(file_contents)):
                text_chunks.extend(chunks)

        leaf_indexes = []
        for chunk in tqdm(text_chunks, desc="Build index"):
            leaf_index = LeafIndex(user_id=user_id)
            leaf = Leaf(content=chunk, leaf_id=leaf_index.leaf_id, user_id=user_id)
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
    extractor.load([Path("test1.txt"), Path("test2.txt")], user_id="admin")
