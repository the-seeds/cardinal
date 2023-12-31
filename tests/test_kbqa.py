import os
import json
import click
import requests
from typing import Dict, Generator, List

try:
    import platform
    if platform.system() != "Windows":
        import readline # noqa: F401
except ImportError:
    print("Install `readline` for a better experience.")


def get_stream_response(url: str, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
    headers = {"Content-Type": "application/json"}
    payload = {"uuid": "test", "messages": messages}
    response = requests.post(url, headers=headers, json=payload, stream=True)
    for line in response.iter_lines(decode_unicode=True):
        if line:
            data = json.loads(line[6:])
            if data.get("content", None) is not None:
                yield data["content"]
            else:
                break


if __name__ == "__main__":
    messages = []
    base_url = click.prompt("Server Base URL", type=str)

    while True:
        query = click.prompt("User", type=str)
        if query == "exit":
            break

        if query == "clear":
            messages = []
            continue

        messages.append({"role": "user", "content": query})
        answer = ""
        print("Assistant: ", end="", flush=True)
        for new_text in get_stream_response(url=os.path.join(base_url, "chat"), messages=messages):
            answer += new_text
            print(new_text, end="", flush=True)
        print()
        messages.append({"role": "assistant", "content": answer})
