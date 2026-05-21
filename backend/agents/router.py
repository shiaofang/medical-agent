"""LLM 路由器：用一次轻量的大模型调用，判断用户问题应交给哪个 Agent。

设计要点：
  - 只让模型输出一个标签词（`general` / `emergency`），尽量快、尽量便宜。
  - 解析时容错：模型若返回多余文字，按关键词匹配；都匹配不到则兜底走 general。
  - 路由失败时（异常、网络问题等）也兜底走 general，避免阻塞主流程。
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from agents import emergency, general
from agents.base import get_model

logger = logging.getLogger(__name__)

# 路由系统提示词：尽量短，约束模型只输出一个词
_ROUTER_SYSTEM_PROMPT = """你是一个医疗问答路由器。请判断用户的问题应该交给哪个助手回答：

- emergency：突发急症、危及生命或时间敏感的情况（如剧烈胸痛、呼吸困难、严重外伤、
  大出血、意识不清、抽搐、急性中毒、过敏休克、烧烫伤、骨折、心脏骤停、CPR/急救技能
  请求等）。
- general：日常医疗健康常识（如慢病管理、用药保健、健康饮食、就医建议、症状科普、
  非急性的轻微不适等）。

请**只输出一个英文单词**：`emergency` 或 `general`，不要任何其他文字、标点或解释。"""


async def route(user_message: str) -> str:
    """让大模型判断该用哪个 Agent，返回 Agent 的 NAME。

    出现任何异常都兜底返回 general，保证主链路可用。
    """
    try:
        response = await get_model().ainvoke(
            [
                SystemMessage(content=_ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]
        )
        label = _parse_label(response.content)
        logger.info("router 选择 agent=%s for message=%r", label, user_message[:60])
        return label
    except Exception as exc:  # noqa: BLE001  路由失败必须兜底
        logger.warning("router 调用失败，兜底走 general: %s", exc)
        return general.NAME


def _parse_label(content: str | list) -> str:
    """把模型输出解析成 Agent NAME，匹配不上则兜底 general。"""
    text = _flatten(content).strip().lower()
    if "emergency" in text:
        return emergency.NAME
    if "general" in text:
        return general.NAME
    return general.NAME


def _flatten(content: str | list) -> str:
    """模型返回内容可能是 str 或块列表，统一压平成字符串。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)
    return ""
