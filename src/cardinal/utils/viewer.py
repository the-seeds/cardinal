import json
from pathlib import Path
from typing import List

from ..core.collector import MsgCollector
from ..core.logging import get_logger
from ..core.schema import BaseMessage
from ..core.storage import RedisStorage


logger = get_logger(__name__)


def view_messages(folder: Path) -> None:
    collector = MsgCollector(storage=RedisStorage[List[BaseMessage]](name="msg_collector"))
    all_messages = []
    for i, messages in enumerate(collector.dump()):
        all_messages.append({"id": i, "conversations": [message.model_dump() for message in messages]})

    folder.mkdir(exist_ok=True)
    output_path = folder / "messages.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_messages, f, ensure_ascii=False, indent=2)

    logger.info("Messages saved at: {}".format(output_path))
