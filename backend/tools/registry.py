"""工具注册表：把本目录下的 @tool 收集起来，供 Agent 使用。"""

from langchain_core.tools import BaseTool

from tools.search_drug import search_drug


# 新增工具：1) 在 tools/ 里用 @tool 定义  2) 追加到下面列表
# 示例：from tools.drug_lookup import lookup_drug
ALL_TOOLS: list[BaseTool] = [search_drug]
