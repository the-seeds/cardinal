import json
import os
from typing import Dict, Generator, List

import click
import requests
from dotenv import load_dotenv


try:
    import platform

    if platform.system() != "Windows":
        import readline  # noqa: F401
except ImportError:
    print("Install `readline` for a better experience.")


def get_stream_response(messages: List[Dict[str, str]]) -> Generator[str, None, None]:
    url = os.path.join(os.environ.get("SERVER_URL"), "chat")
    headers = {"Content-Type": "application/json"}
    payload = {"uuid": "test", "messages": messages}
    response = requests.post(url, headers=headers, json=payload, stream=True)
    for line in response.iter_lines(decode_unicode=True):
        if line:
            if line == "data: [DONE]":
                break
            data = json.loads(line[6:])
            yield data["content"]


if __name__ == "__main__":
    load_dotenv()
    messages = []

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
        for new_text in get_stream_response(messages=messages):
            answer += new_text
            print(new_text, end="", flush=True)
        print()
        messages.append({"role": "assistant", "content": answer})
