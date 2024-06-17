import json
import time
from pathlib import Path

from cardinal import BaseCollector, get_logger

from .protocol import History


logger = get_logger(__name__)


def dump_history(folder: Path, database: str) -> None:
    collector = BaseCollector[History](storage_name=database)
    histories = [[message.model_dump() for message in history.messages] for history in collector.dump()]

    folder.mkdir(exist_ok=True)
    output_path = folder / "history-{}.json".format(int(time.time()))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(histories, f, ensure_ascii=False, indent=2)

    logger.info("History saved at: {}".format(output_path))
