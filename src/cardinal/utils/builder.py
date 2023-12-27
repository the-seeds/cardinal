from pathlib import Path

from cardinal.core.extractor import BaseExtractor
from cardinal.core.models import EmbedOpenAI
from cardinal.core.schema import LeafIndex, Leaf
from cardinal.core.storage import RedisStorage
from cardinal.core.vectorstore import Milvus


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
    extractor.load(input_files, user_id="admin")
