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
        for keyword, prefix_words, suffix_words in wordgraph(request.messages):
            pass
        return WordGraphResponse(graph=[])

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("SERVICE_PORT", 8000)), workers=1)
