from fastapi import APIRouter, HTTPException

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
