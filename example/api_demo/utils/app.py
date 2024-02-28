import json
import os
from typing import Any, Dict, Generator

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse

from cardinal import Role

from .chat import ChatEngine
from .protocol import (
    ChatCompletionMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionResponseStreamChoice,
    ModelCard,
    ModelList,
)


def launch_app(database: str) -> None:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )
    engine = ChatEngine(database)

    def stream_response(input_kwargs: Dict[str, Any]) -> Generator[str, None, None]:
        choice_data = ChatCompletionResponseStreamChoice(delta=ChatCompletionMessage(role=Role.ASSISTANT, content=""))
        chunk = ChatCompletionResponse(choices=[choice_data])
        yield json.dumps(chunk.model_dump(exclude_unset=True), ensure_ascii=False)

        for new_token in engine.stream_chat(**input_kwargs):
            choice_data = ChatCompletionResponseStreamChoice(delta=ChatCompletionMessage(content=new_token))
            chunk = ChatCompletionResponse(choices=[choice_data])
            yield json.dumps(chunk.model_dump(exclude_unset=True), ensure_ascii=False)

        choice_data = ChatCompletionResponseStreamChoice(delta=ChatCompletionMessage(), finish_reason="stop")
        chunk = ChatCompletionResponse(choices=[choice_data])
        yield json.dumps(chunk.model_dump(exclude_unset=True), ensure_ascii=False)
        yield "[DONE]"

    @app.post("/v1/chat/completions", response_model=ChatCompletionResponse, status_code=status.HTTP_200_OK)
    async def create_chat_completion(request: ChatCompletionRequest):
        if request.messages[-1].role != Role.USER:
            raise ValueError("Invalid role.")

        input_kwargs = {
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        if request.stream:
            return EventSourceResponse(stream_response(input_kwargs), media_type="text/event-stream")

        response = ""
        for new_token in engine.stream_chat(**input_kwargs):
            response += new_token

        choice_data = ChatCompletionResponseChoice(
            message=ChatCompletionMessage(role=Role.ASSISTANT, content=response), finish_reason="stop"
        )
        return ChatCompletionResponse(choices=[choice_data])

    @app.get("/v1/models", response_model=ModelList)
    async def list_models():
        return ModelList(data=[ModelCard()])

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("SERVICE_PORT", "8000")))
