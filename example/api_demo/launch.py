from enum import Enum, unique
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv


load_dotenv()  # must before utils


from utils import build_database, dump_history, launch_app  # noqa: E402


try:
    import platform

    if platform.system() != "Windows":
        import readline  # noqa: F401
except ImportError:
    print("Install `readline` for a better experience.")


@unique
class Action(str, Enum):
    BUILD = "build"
    LAUNCH = "launch"
    DUMP = "dump"
    EXIT = "exit"


@click.command()
@click.option("--config", required=True, prompt="Config file")
@click.option("--action", required=True, type=click.Choice([act.value for act in Action]), prompt="Choose an action")
def interactive_cli(config, action):
    with open(config, "r", encoding="utf-8") as config_file:
        config_dict = yaml.safe_load(config_file)

    if action == Action.BUILD:
        database = config_dict["build"]["database"]
        folder = Path(config_dict["build"]["folder"])
        build_database(folder, database)
    elif action == Action.LAUNCH:
        database = config_dict["launch"]["database"]
        launch_app(database)
    elif action == Action.DUMP:
        database = config_dict["dump"]["database"]
        folder = Path(config_dict["dump"]["folder"])
        dump_history(Path(folder), database)


if __name__ == "__main__":
    interactive_cli()
