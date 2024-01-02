from dotenv import load_dotenv

from .service import launch_app
from .utils import build_database


__all__ = ["launch_app", "build_database"]
__version__ = "0.1.0"


load_dotenv()
