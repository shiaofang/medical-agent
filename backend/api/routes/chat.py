import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

import agents
from config.settings import settings
from schemas.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])



@router.post("/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    if not agents.is_configured():
        raise HTTPException(
            status_code=503,
            detail="未配置 OLLAMA_API_KEY，请在 backend/.env 中设置后重启服务。",
        )

    async def event_generator():
        try:
            async for chunk in agents.chat_stream(request.message, request.history):
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
