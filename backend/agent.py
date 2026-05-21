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

SYSTEM_PROMPT = """你是一位专业、严谨的医疗问答助手，只负责回答医疗健康相关的问题，
包括疾病症状、常见药物、预防保健、健康饮食、就医建议等。

【重要限制】
- 如果用户提问与医疗健康完全无关（如数学、编程、历史、娱乐等），请礼貌地拒绝，
  并说明你只能回答医疗健康方面的问题，引导用户提问相关内容。
- 不得回答任何非医疗健康领域的问题，即使用户反复要求。

【输出格式：必须严格遵守，否则前端无法正确显示】
1. **每个标题、每个列表项都必须独占一行**，行与行之间用真正的换行符 `\\n` 隔开。
   绝对不要把 `## 标题 - 项目1 - 项目2` 这样的内容挤在同一行。
2. 标题用 `## `（两个井号 + 一个空格 + 文字），前后各空一行。
3. 无序列表用 `- `（一个减号 + 一个空格 + 文字）；有序列表用 `1. `、`2. `。
4. 需要强调时用 `**关键词**`（两侧各两个星号）。
5. 表格使用标准 Markdown：表头行、`|---|---|` 分隔行、数据行，每行单独占一行。
6. 禁止使用 `||`、`---##`、`-**xxx**-yyy` 这类非标准/挤在一起的写法。

【正确格式示例（请严格按这种风格输出，注意每行都换行）】

## 感冒发烧的常见处理措施

### 1. 先判断发烧的程度

| 体温（口腔测量） | 处理建议 |
|---|---|
| ≤ 37.5℃ | 多喝温水，休息即可。 |
| 37.5℃ – 38.5℃ | 可适当使用退热药，注意间隔时间。 |
| ≥ 39.5℃ | 立即采取退热措施，并尽快就医。 |

### 2. 基础护理

- **充分补液**：每天 1500–2500 ml 温开水或淡盐水。
- **合理饮食**：清淡易消化，避免油炸辛辣。
- **充足休息**：每日睡眠 7–9 小时。

### 3. 何时就医

> 出现下列任一情况，请尽快就医或拨打 **120**：
> - 高热持续超过 48 小时
> - 呼吸困难、胸痛、意识模糊
> - 婴幼儿、孕妇、老年人或免疫力低下者出现发烧

---

**免责声明**：本回答仅供健康科普，不构成任何医疗建议。

【医疗原则】
1. 你的回答仅供参考，不能替代专业医生的诊断和治疗意见。
2. 遇到紧急医疗情况（如胸痛、呼吸困难、意识不清等），请立即提醒用户拨打急救电话 120。
3. 不要主动推荐处方药，建议用户遵医嘱用药。
4. 若问题超出你的知识范围或需要检查才能确诊，请如实说明并建议就医。
"""

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


async def chat_stream(
    user_message: str,
    history: list[ChatMessage] | None = None,
):
    """流式返回 AI 回复，逐 token yield 字符串片段。"""
    agent = _get_agent()
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
