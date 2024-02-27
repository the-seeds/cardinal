from multiprocessing import Pool
from pathlib import Path
from typing import List, Optional

from tqdm import tqdm

from cardinal import AutoStorage, AutoVectorStore, CJKTextSplitter, get_logger

from .protocol import DocIndex, Document


logger = get_logger(__name__)
BATCH_SIZE = 1000


def build_database(folder: Path, database: str, verbose: Optional[bool] = True) -> None:
    vectorstore = AutoVectorStore[DocIndex](name=database)
    storage = AutoStorage[Document](name=database)
    splitter = CJKTextSplitter()

    input_files: List[Path] = []
    for path in folder.rglob("*.*"):
        if path.is_file() and path.suffix == ".txt":
            input_files.append(path)

    file_contents: List[str] = []
    for file_path in tqdm(input_files, desc="Extract content", disable=(not verbose)):
        if file_path.suffix == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                file_contents.append(f.read())
        else:
            raise NotImplementedError

    text_chunks = []
    with Pool(processes=32) as pool:
        for chunks in tqdm(
            pool.imap_unordered(splitter.split, file_contents),
            total=len(file_contents),
            desc="Split content",
            disable=(not verbose),
        ):
            text_chunks.extend(chunks)

    for i in tqdm(range(0, len(text_chunks), BATCH_SIZE), desc="Build index", disable=(not verbose)):
        batch_text = text_chunks[i : i + BATCH_SIZE]
        batch_index, batch_ids, batch_document = [], [], []
        for text in batch_text:
            index = DocIndex()
            document = Document(doc_id=index.doc_id, content=text)
            batch_ids.append(index.doc_id)
            batch_index.append(index)
            batch_document.append(document)
        vectorstore.insert(batch_text, batch_index)
        storage.insert(batch_ids, batch_document)

    logger.info("Build completed.")
