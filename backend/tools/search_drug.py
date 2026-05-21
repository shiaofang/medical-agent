from __future__ import annotations

import logging
import re
from pathlib import Path

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_DRUG_GUIDE = Path(__file__).parent.parent / "referenceFiles" / "drug_guide.md"


def _load_sections() -> dict[str, str]:
    """把 drug_guide.md 按 ### 标题切成字典：标题文本 → 内容块。"""
    text = _DRUG_GUIDE.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    current_title = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("### "):
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
def search_drug(drug_name: str) -> str:
    """在药品说明手册中查询指定药品的适应症、用法用量和注意事项。
       当用户询问任何具体药品（包括药品通用名、商品名、成分名）的信息时，必须调用此工具。

    Args:
        drug_name: 药品通用名或商品名，如"布洛芬"、"泰诺"、"奥美拉唑"

    Returns:
        匹配到的药品说明文本；若未找到则返回提示信息。
    """
    logger.info("🔧 search_drug 被调用，参数: drug_name=%r", drug_name)
    query = drug_name.strip().lower()
    matched: list[str] = []
    for title, content in _SECTIONS.items():
        if re.search(query, title.lower()) or re.search(query, content.lower()):
            matched.append(content)
    if not matched:
        logger.info("🔧 search_drug 未命中: drug_name=%r", drug_name)
        return f"未在药品手册中找到与'{drug_name}'相关的信息，建议咨询药师或医生。"
    logger.info("🔧 search_drug 命中 %d 条结果", len(matched))
    return "\n\n---\n\n".join(matched)

