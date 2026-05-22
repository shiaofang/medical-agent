# 搜索紧急情况处理方法
from __future__ import annotations

import logging
import re
from pathlib import Path

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_EMERGENCY_GUIDE = Path(__file__).parent.parent / "referenceFiles" / "emergency_guide.md"


def _load_sections() -> dict[str, str]:
    """把 emergency_guide.md 按 ## 标题切成字典：标题文本 → 内容块。"""
    text = _EMERGENCY_GUIDE.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    current_title = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_title:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = line.lstrip("# ").strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_title:
        sections[current_title] = "\n".join(current_lines).strip()
    return sections


_SECTIONS = _load_sections()


@tool
def search_emergency(query: str) -> str:
    """在急救处理指南中查询指定紧急情况的处理方法。
       当用户询问任何急救、紧急情况处理（如心肺复苏、噎食、出血、骨折、烧烫伤、中毒、中暑、过敏、癫痫等）时，必须调用此工具。

    Args:
        query: 紧急情况关键词，如"心肺复苏"、"CPR"、"噎食"、"出血"、"骨折"、"烧烫伤"、"中毒"、"中暑"、"过敏"、"癫痫"

    Returns:
        匹配到的急救处理说明文本；若未找到则返回提示信息。
    """
    logger.info("🔧 search_emergency 被调用，参数: query=%r", query)
    keyword = query.strip().lower()
    matched: list[str] = []
    for title, content in _SECTIONS.items():
        if re.search(keyword, title.lower()) or re.search(keyword, content.lower()):
            matched.append(content)
    if not matched:
        logger.info("🔧 search_emergency 未命中: query=%r", query)
        return f"未在急救指南中找到与'{query}'相关的处理方法，请立即拨打 120 或联系专业急救人员。"
    logger.info("🔧 search_emergency 命中 %d 条结果", len(matched))
    return "\n\n---\n\n".join(matched)
