from enum import Enum, unique
from pathlib import Path

import click
from dotenv import load_dotenv


load_dotenv()  # must before utils


from utils import build_database, launch_app, view_history  # noqa: E402


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
    VIEW = "view"
    EXIT = "exit"


@click.command()
@click.option("--action", required=True, type=click.Choice([act.value for act in Action]), prompt="Choose an action")
@click.option("--database", required=True, type=str, prompt="Enter database name")
def interactive_cli(action, database):
    if action == Action.BUILD:
        folder = click.prompt("Input folder", type=str)
        build_database(Path(folder), database)
    elif action == Action.LAUNCH:
        launch_app(database)
    elif action == Action.VIEW:
        folder = click.prompt("Output folder", type=str)
        view_history(Path(folder), database)


if __name__ == "__main__":
    interactive_cli()
