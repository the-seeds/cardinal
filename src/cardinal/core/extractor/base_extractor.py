import os
from multiprocessing import Pool
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

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
        self._batch_size = 1000
        self._vectorizer = vectorizer
        self._storage = storage
        self._vectorstore = vectorstore
        self._splitter = CJKTextSplitter()

    def load(self, input_files: List[Path], user_id: str, verbose: Optional[bool] = False) -> None:
        file_contents: List[str] = []
        for file_path in tqdm(input_files, desc="Extract content", disable=(not verbose)):
            if file_path.suffix == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    file_contents.append(f.read())
            else:
                raise NotImplementedError

        text_chunks = []
        with Pool(processes=int(os.environ.get("NUM_CPU_CORE"))) as pool:
            for chunks in tqdm(
                pool.imap_unordered(self._splitter.split, file_contents),
                total=len(file_contents),
                desc="Split content",
                disable=(not verbose),
            ):
                text_chunks.extend(chunks)

        for i in tqdm(range(0, len(text_chunks), self._batch_size), desc="Build index", disable=(not verbose)):
            batch_text = text_chunks[i : i + self._batch_size]
            batch_index, batch_ids, batch_content = [], [], []
            for text in batch_text:
                leaf_index = LeafIndex(user_id=user_id)
                leaf = Leaf(leaf_id=leaf_index.leaf_id, user_id=user_id, content=text)
                batch_ids.append(leaf_index.leaf_id)
                batch_index.append(leaf_index)
                batch_content.append(leaf)
            embeddings = self._vectorizer.batch_embed(batch_text)
            self._vectorstore.insert(embeddings, batch_index)
            self._storage.insert(batch_ids, batch_content)


if __name__ == "__main__":
    from ..model import EmbedOpenAI
    from ..storage import RedisStorage
    from ..vectorstore import Milvus

    extractor = BaseExtractor(
        vectorizer=EmbedOpenAI(), storage=RedisStorage[Leaf]("test"), vectorstore=Milvus[LeafIndex]("test")
    )
    extractor.load([Path("test1.txt"), Path("test2.txt")], user_id="admin")
