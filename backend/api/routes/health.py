from fastapi import APIRouter

import agent
from config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "agent_configured": agent.is_configured(),
        "model": settings.ollama_model,
    }
