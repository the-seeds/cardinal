import json
import os

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse

from ..app import KbqaEngine, WordGraphEngine
from .protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    WordGraphCategory,
    WordGraphLink,
    WordGraphNode,
    WordGraphObject,
    WordGraphRequest,
    WordGraphResponse,
)


def launch_app(database: str) -> None:
    app = FastAPI()
    kbqa = KbqaEngine(database)
    wordgraph = WordGraphEngine(database)

    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )

    @app.post("/v1/chat/kbqa", response_model=ChatCompletionResponse, status_code=status.HTTP_200_OK)
    async def kbqa_chat(request: ChatCompletionRequest):
        def predict():
            for new_token in kbqa(messages=request.messages):
                chunk = ChatCompletionResponse(content=new_token)
                yield json.dumps(chunk.model_dump(exclude_unset=True), ensure_ascii=False)

            yield "[DONE]"

        return EventSourceResponse(predict(), media_type="text/event-stream")

    @app.post("/v1/chat/wordgraph", response_model=WordGraphResponse, status_code=status.HTTP_200_OK)
    async def draw_wordgraph(request: WordGraphRequest):
        graph = []
        for keyword, prefix_words, suffix_words in wordgraph(request.messages):
            nodes, links = [], []
            nodes.append(WordGraphNode(id="keyword", name=keyword, category=0, x=300, y=300))

            n = len(prefix_words)
            for i, prefix_word in enumerate(prefix_words):
                nodes.append(
                    WordGraphNode(
                        id="prefix_{}".format(i),
                        name=prefix_word,
                        category=1,
                        x=100,
                        y=round(400 * (i - n // 2) / (n - 1) + 300),
                    )
                )
                links.append(WordGraphLink(source="prefix_{}".format(i), target="keyword"))

            n = len(suffix_words)
            for i, suffix_word in enumerate(suffix_words):
                nodes.append(
                    WordGraphNode(
                        id="suffix_{}".format(i),
                        name=suffix_word,
                        category=2,
                        x=500,
                        y=round(400 * (i - n // 2) / (n - 1) + 300),
                    )
                )
                links.append(WordGraphLink(source="keyword", target="suffix_{}".format(i)))

            categories = [
                WordGraphCategory(name="keyword"),
                WordGraphCategory(name="prefix"),
                WordGraphCategory(name="suffix"),
            ]
            graph.append(WordGraphObject(nodes=nodes, links=links, categories=categories))
        return WordGraphResponse(graph=graph)

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("SERVICE_PORT", 8000)), workers=1)
