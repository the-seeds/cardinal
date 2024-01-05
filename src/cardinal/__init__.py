from dotenv import load_dotenv

from .service import launch_app
from .utils import build_database, view_messages


__all__ = ["launch_app", "build_database", "view_messages"]
__version__ = "0.1.0"


load_dotenv()
