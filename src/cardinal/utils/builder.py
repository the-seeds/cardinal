import os
from pathlib import Path

from ..core.extractor import BaseExtractor
from ..core.logging import get_logger
from ..core.model import EmbedOpenAI
from ..core.schema import Leaf, LeafIndex
from ..core.storage import RedisStorage
from ..core.vectorstore import Chroma


logger = get_logger(__name__)


def build_database(folder: Path, database: str) -> None:
    input_files = []
    for path in folder.rglob("*.*"):
        if path.is_file() and path.suffix == ".txt":
            input_files.append(path)

    extractor = BaseExtractor(
        vectorizer=EmbedOpenAI(),
        storage=RedisStorage[Leaf](name=database),
        vectorstore=Chroma[LeafIndex](name=database),
    )
    extractor.load(input_files, user_id=os.environ.get("ADMIN_USER_ID"), verbose=True)
    logger.info("Build completed.")
