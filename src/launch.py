import enum
import click
from pathlib import Path

from cardinal import build_database, launch_app

try:
    import platform
    if platform.system() != "Windows":
        import readline # noqa: F401
except ImportError:
    print("Install `readline` for a better experience.")


@enum.unique
class Action(str, enum.Enum):
    BUILD = "build"
    LAUNCH = "launch"


@click.command()
@click.option("--action", required=True, type=click.Choice([act.value for act in Action]), prompt="Choose an action")
def interactive_cli(action):
    if action == Action.BUILD:
        folder = click.prompt("Folder path", type=str)
        build_database(Path(folder))
    elif action == Action.LAUNCH:
        launch_app()


if __name__ == "__main__":
    interactive_cli()
