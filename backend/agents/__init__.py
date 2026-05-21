"""agents 包对外入口。

对外 API：
    - is_configured()
    - chat_stream(user_message, history)

内部流程：
    1. router 用一次轻量 LLM 调用，把问题分类到 general / emergency
    2. 取出对应的 Agent，流式输出
"""

from collections.abc import AsyncIterator

from agents import base, emergency, general, router
from schemas.chat import ChatMessage

# Agent 注册表：name -> 模块（每个模块必须有 NAME / get_agent()）
_AGENTS = {
    general.NAME: general,
    emergency.NAME: emergency,
}

_DEFAULT_AGENT = general.NAME


def is_configured() -> bool:
    """检查是否已配置 API Key。"""
    return base.is_configured()



async def chat_stream(
    user_message: str,
    history: list[ChatMessage] | None = None,
) -> AsyncIterator[str]:
    """流式对话：先路由，再分派到对应 Agent 流式输出。"""
    agent_module = await _select_agent(user_message)
    async for chunk in base.stream(agent_module.get_agent(), user_message, history):
        yield chunk


async def _select_agent(user_message: str):
    """用路由器选 Agent；选不到合法的则兜底走默认 Agent。"""
    name = await router.route(user_message)
    return _AGENTS.get(name, _AGENTS[_DEFAULT_AGENT])


__all__ = ["is_configured", "chat_stream"]
