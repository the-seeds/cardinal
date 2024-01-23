import json
import time
from pathlib import Path
from typing import List

from ..core.choices import Storage
from ..core.collector import MsgCollector
from ..core.logging import get_logger
from ..core.schema import BaseMessage


logger = get_logger(__name__)


def view_history(folder: Path) -> None:
    collector = MsgCollector(storage=Storage[List[BaseMessage]](name="msg_collector"))
    histories = [history.model_dump() for history in collector.dump()]

    folder.mkdir(exist_ok=True)
    output_path = folder / "history-{}.json".format(int(time.time()))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(histories, f, ensure_ascii=False, indent=2)

    logger.info("History saved at: {}".format(output_path))
