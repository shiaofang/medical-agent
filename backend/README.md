# 天气助手后端

FastAPI + LangChain 的小型示例项目，目录按「从外到内」分层，方便初学者顺着请求链路阅读。

## 目录说明

```
backend/
├── main.py              # 程序入口，注册路由与 CORS
├── config/              # 环境变量与配置（.env）
├── api/routes/          # HTTP 接口（只做参数校验和调用 service）
├── schemas/             # 请求/响应的数据结构（Pydantic）
├── services/            # 业务编排（对话、查天气）
├── agents/              # LangChain Agent 定义（模型 + 工具 + 提示词）
├── tools/               # Agent 可调用的工具 + 共用的天气数据
├── clients/             # 连接外部服务（当前：Ollama 大模型）
└── .env                 # 本地密钥（不要提交到 Git）
```

## 一次对话请求怎么走

以 `POST /chat` 为例：

```
浏览器/前端
    → api/routes/chat.py      校验 API Key、解析 JSON
    → services/agent.py       把 history 转成 LangChain 消息
    → agents/weather_agent.py  LangChain Agent（图）
         ├→ clients/llm.py     调用 Ollama 模型
         └→ tools/weather_tool.py  模型决定查天气时执行
              └→ tools/weather_data.py  请求 Open-Meteo
    → 返回最后一条 AI 文本给前端
```

`GET /weather?city=上海` **不经过 AI**，路径更短：

```
api/routes/weather.py → services/weather.py → tools/weather_data.py
```

## 各层职责（记住这一句）

| 目录 | 职责 |
|------|------|
| `api/` | 对外 HTTP，越薄越好 |
| `schemas/` | 数据长什么样 |
| `services/` | 业务流程 |
| `agents/` | AI 助手怎么配置 |
| `tools/` | AI 能调哪些函数 |
| `clients/` | 连哪家大模型 |

## 如何扩展

### 新增一个 Agent 工具

1. 在 `tools/` 新建文件，用 `@tool` 定义函数（参考 `weather_tool.py`）
2. 在 `tools/registry.py` 的 `ALL_TOOLS` 里追加
3. 在 `agents/weather_agent.py` 的 `SYSTEM_PROMPT` 里说明何时使用该工具

### 新增一个 HTTP 接口

1. 在 `schemas/` 定义请求/响应模型
2. 在 `services/` 写业务逻辑
3. 在 `api/routes/` 写路由，并在 `main.py` 里 `include_router`

## 本地运行

```bash
cd backend
cp .env.example .env   # 填入 OLLAMA_API_KEY
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

文档：http://127.0.0.1:8000/docs
