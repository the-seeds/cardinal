import os

from ..core.schema import Template


PLAIN_TEMPLATE = Template(os.environ.get("PLAIN_TEMPLATE"))
KBQA_TEMPLATE = Template(os.environ.get("KBQA_TEMPLATE"))
