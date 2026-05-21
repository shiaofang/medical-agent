"""Agent 公用代码。

所有 Agent 共享：
  - 同一个大模型客户端（通过 lru_cache 复用）
  - 同一套消息构建、流式输出、回复抽取逻辑

每个具体 Agent 只需要提供自己的「系统提示词」和「内部名称」。
"""

from collections.abc import AsyncIterator
from functools import lru_cache

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph.state import CompiledStateGraph

from config.settings import settings
from schemas.chat import ChatMessage
from tools.registry import ALL_TOOLS

# Agent 最多执行多少步（防止无限循环）
_MAX_STEPS = 15


# ── 1. 模型 & Agent 构建 ─────────────────────────────────────────────────────


@lru_cache
def get_model() -> ChatOllama:
    """创建并返回大模型客户端，所有 Agent 共用同一个实例。"""
    client_kwargs: dict[str, dict[str, str]] = {}
    if settings.ollama_api_key.strip():
        client_kwargs["headers"] = {
            "Authorization": f"Bearer {settings.ollama_api_key.strip()}",
        }
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_host.rstrip("/"),
        client_kwargs=client_kwargs or None,
    )


def build_agent(system_prompt: str, name: str) -> CompiledStateGraph:
    """根据系统提示词构建一个新的 Agent。"""
    return create_agent(
        model=get_model(),
        tools=ALL_TOOLS,
        system_prompt=system_prompt,
        name=name,
    )


# ── 2. 通用对话流程 ──────────────────────────────────────────────────────────


def is_configured() -> bool:
    """检查是否已配置 API Key，未配置则不应启动对话。"""
    return bool(settings.ollama_api_key.strip())



async def stream(
    agent: CompiledStateGraph,
    user_message: str,
    history: list[ChatMessage] | None = None,
) -> AsyncIterator[str]:
    """流式调用 Agent，逐 token yield 字符串片段。"""
    messages = _build_messages(history, user_message)
    async for event in agent.astream_events(
        {"messages": messages},
        version="v2",
        config={"recursion_limit": _MAX_STEPS},
    ):
        if event["event"] != "on_chat_model_stream":
            continue
        chunk = event["data"]["chunk"]
        text = _message_text(chunk.content)
        if text:
            yield text


# ── 内部辅助函数 ─────────────────────────────────────────────────────────────


def _build_messages(
    history: list[ChatMessage] | None,
    user_message: str,
) -> list[HumanMessage | AIMessage]:
    """把 API 传来的历史记录转成 LangChain 消息格式。"""
    messages: list[HumanMessage | AIMessage] = []
    for item in history or []:
        if item.role == "user":
            messages.append(HumanMessage(content=item.content))
        else:
            messages.append(AIMessage(content=item.content))
    messages.append(HumanMessage(content=user_message))
    return messages



def _message_text(content: str | list) -> str:
    """把 AI 消息内容（可能是字符串或块列表）统一转成纯文本。"""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts).strip()
    return ""
