import json
import time
from pathlib import Path

from cardinal import MsgCollector, get_logger


logger = get_logger(__name__)


def view_history(folder: Path) -> None:
    collector = MsgCollector(storage_name="msg_collector")
    histories = [[message.model_dump() for message in messages] for messages in collector.dump()]

    folder.mkdir(exist_ok=True)
    output_path = folder / "history-{}.json".format(int(time.time()))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(histories, f, ensure_ascii=False, indent=2)

    logger.info("History saved at: {}".format(output_path))
