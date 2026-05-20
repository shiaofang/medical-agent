"""医疗问答 AI 助手。

本文件包含三部分，从上到下依次是：
  1. 配置：大模型连接参数、系统提示词
  2. 初始化：创建模型和 Agent（只创建一次，后续复用）
  3. 对话入口：is_configured() 和 chat() 供 HTTP 接口调用
"""

from functools import lru_cache

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph.state import CompiledStateGraph

from config.settings import settings
from schemas.chat import ChatMessage
from tools.registry import ALL_TOOLS

# ── 1. 系统提示词 ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "你是一位专业、严谨的医疗问答助手，能够回答用户关于疾病症状、常见药物、"
    "预防保健、健康饮食等医疗健康问题。请用简洁、易懂的中文回答。\n\n"
    "重要原则：\n"
    "1. 你的回答仅供参考，不能替代专业医生的诊断和治疗意见。\n"
    "2. 遇到紧急医疗情况（如胸痛、呼吸困难、意识不清等），请立即提醒用户拨打急救电话 120。\n"
    "3. 不要主动推荐处方药，建议用户遵医嘱用药。\n"
    "4. 若问题超出你的知识范围或需要检查才能确诊，请如实说明并建议就医。"
)

# Agent 最多执行多少步（防止无限循环）
_MAX_STEPS = 15

# ── 2. 初始化（带缓存，整个程序只创建一次）──────────────────────────────────


@lru_cache
def _get_model() -> ChatOllama:
    """创建并返回大模型客户端。"""
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


@lru_cache
def _get_agent() -> CompiledStateGraph:
    """创建并返回医疗问答 Agent。"""
    return create_agent(
        model=_get_model(),
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="medical_assistant",
    )


# ── 3. 对外接口（供 HTTP 路由调用）──────────────────────────────────────────


def is_configured() -> bool:
    """检查是否已配置 API Key，未配置则不应启动对话。"""
    return bool(settings.ollama_api_key.strip())


def chat(user_message: str, history: list[ChatMessage] | None = None) -> str:
    """接收用户消息和历史记录，返回 AI 的回复文本。"""
    agent = _get_agent()
    messages = _build_messages(history, user_message)
    result = agent.invoke(
        {"messages": messages},
        config={"recursion_limit": _MAX_STEPS},
    )
    return _extract_last_reply(result["messages"])


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


def _extract_last_reply(messages: list[BaseMessage]) -> str:
    """从 Agent 返回的消息列表里，取最后一条有内容的 AI 回复。"""
    for msg in reversed(messages):
        if not isinstance(msg, AIMessage):
            continue
        text = _message_text(msg.content)
        if text:
            return text
    return "抱歉，我暂时无法回答您的问题，请稍后再试或咨询专业医生。"


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
