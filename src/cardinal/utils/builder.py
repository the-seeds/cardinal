from pathlib import Path

from ..core.extractor import BaseExtractor
from ..core.model import EmbedOpenAI
from ..core.schema import LeafIndex, Leaf
from ..core.storage import RedisStorage
from ..core.vectorstore import Milvus


def build_database(folder: Path) -> None:
    input_files = []
    for path in folder.rglob("*.*"):
        if path.is_file() and path.suffix == ".txt":
            input_files.append(path)

    extractor = BaseExtractor(
        vectorizer=EmbedOpenAI(),
        storage=RedisStorage[Leaf](name="default"),
        vectorstore=Milvus[LeafIndex](name="default")
    )
    extractor.load(input_files)
