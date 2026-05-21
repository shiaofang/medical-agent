import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

import agent
from config.settings import settings
from schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not agent.is_configured():
        raise HTTPException(
            status_code=503,
            detail="未配置 OLLAMA_API_KEY，请在 backend/.env 中设置后重启服务。",
        )

    try:
        reply = agent.chat(request.message, request.history)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI 服务暂时不可用：{exc}",
        ) from exc

    return ChatResponse(reply=reply, model=settings.ollama_model)


@router.post("/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    if not agent.is_configured():
        raise HTTPException(
            status_code=503,
            detail="未配置 OLLAMA_API_KEY，请在 backend/.env 中设置后重启服务。",
        )

    async def event_generator():
        try:
            async for chunk in agent.chat_stream(request.message, request.history):
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"
        finally:
            yield f"data: {json.dumps({'done': True, 'model': settings.ollama_model}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
