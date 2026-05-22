# 医疗问答助手

基于大语言模型的全栈医疗健康问答系统，支持通用医疗咨询与急诊应急处置两大场景，回答通过 SSE 流式推送，Markdown 格式渲染。

> **免责声明**：本系统回答仅供健康科普参考，不构成任何医疗诊断建议，紧急情况请立即拨打 **120**。

---

## 目录

- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [环境变量说明](#环境变量说明)
- [API 接口](#api-接口)

---

## 功能特性

- **智能路由**：由 LLM 自动判断用户问题类型，分流至通用助手或急诊助手
- **通用医疗助手**：解答慢病管理、用药常识、健康饮食、症状科普、就医建议等非紧急问题
- **急诊应急助手**：处理胸痛、呼吸困难、骨折、大出血、中毒、心脏骤停、CPR 等危急情况，优先提示拨打 120
- **Tool Calling**：Agent 强制调用本地知识库工具（急救指南、药品手册）后再作答，减少幻觉
- **流式输出**：基于 SSE（Server-Sent Events）逐 token 推送，前端实时渲染
- **Markdown 渲染**：回答支持标题、列表、表格、引用块等格式，阅读体验友好
- **对话历史**：多轮对话上下文感知，支持一键清除

---

## 系统架构

```
用户输入
   │
   ▼
┌──────────────────────────────────────────┐
│              Frontend (Vue 3)            │
│  ChatView → ChatStore → sendMessageStream│
└──────────────────┬───────────────────────┘
                   │  POST /chat/stream (SSE)
                   ▼
┌──────────────────────────────────────────┐
│              Backend (FastAPI)           │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │         LLM Router              │     │
│  │  判断 → general / emergency     │     │
│  └────────┬──────────┬─────────────┘     │
│           │          │                   │
│           ▼          ▼                   │
│   ┌───────────┐ ┌───────────────┐        │
│   │  General  │ │   Emergency   │        │
│   │   Agent   │ │    Agent      │        │
│   └─────┬─────┘ └──────┬────────┘        │
│         │              │                 │
│         ▼              ▼                 │
│   ┌───────────┐ ┌───────────────┐        │
│   │search_drug│ │search_emergency│       │
│   │(药品手册) │ │ (急救指南)    │        │
│   └───────────┘ └───────────────┘        │
│                                          │
│          Ollama LLM (本地或远程)          │
└──────────────────────────────────────────┘
```

---

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.12+ | 运行环境 |
| FastAPI | ≥0.136 | Web 框架 & SSE 流式响应 |
| LangChain | ≥1.3 | Agent 编排 & Tool Calling |
| LangGraph | ≥1.2 | Agent 状态图执行 |
| langchain-ollama | ≥1.1 | Ollama LLM 接入 |
| Pydantic Settings | ≥2.8 | 环境变量管理 |
| Uvicorn | ≥0.47 | ASGI 服务器 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ≥3.5 | 前端框架 |
| TypeScript | ~6.0 | 类型安全 |
| Vite | ≥8.0 | 构建工具 |
| Element Plus | ≥2.14 | UI 组件库 |
| Pinia | ≥3.0 | 状态管理 |
| Axios | ≥1.16 | HTTP 客户端 & SSE |
| Marked | ≥18.0 | Markdown 渲染 |

---

## 项目结构

```
aitest/
├── backend/
│   ├── agents/
│   │   ├── base.py          # 共享 Agent 基类（模型初始化、流式输出）
│   │   ├── general.py       # 通用医疗助手 Agent
│   │   ├── emergency.py     # 急诊应急助手 Agent
│   │   └── router.py        # LLM 路由器（判断问题类型）
│   ├── api/routes/
│   │   ├── chat.py          # POST /chat/stream 接口
│   │   └── health.py        # GET /health 健康检查
│   ├── tools/
│   │   ├── search_drug.py   # 药品手册检索工具
│   │   ├── search_emergency.py  # 急救指南检索工具
│   │   └── registry.py      # 工具注册表
│   ├── referenceFiles/
│   │   ├── drug_guide.md        # 药品知识库
│   │   ├── emergency_guide.md   # 急救处置指南
│   │   ├── common_symptoms.md   # 常见症状说明
│   │   ├── department_guide.md  # 科室就医指引
│   │   └── disclaimer_and_guidelines.md
│   ├── config/settings.py   # 环境变量配置
│   ├── schemas/chat.py      # 请求/响应数据模型
│   ├── main.py              # FastAPI 应用入口
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── views/ChatView.vue    # 主聊天界面
│   │   ├── components/ChatBubble.vue  # 消息气泡组件
│   │   ├── stores/chat.ts        # Pinia 对话状态管理
│   │   ├── api/chat.ts           # SSE 流式请求封装
│   │   └── types/chat.ts         # 类型定义
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## 快速开始

### 前置要求

- Python 3.12+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv)（Python 包管理器）
- 可访问的 Ollama 服务（本地或远程）

### 1. 克隆项目

```bash
git clone <repo-url>
cd aitest
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env   # 若无示例文件，直接创建 .env
# 编辑 .env，填写 OLLAMA_API_KEY、OLLAMA_HOST、OLLAMA_MODEL

# 启动服务（默认监听 8000 端口）
uv run uvicorn main:app --reload
```

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 复制环境变量（可选，用于修改后端地址）
cp .env.example .env.local

# 启动开发服务器（默认 5173 端口）
npm run dev
```

打开浏览器访问 `http://localhost:5173` 即可使用。

### 4. 生产构建

```bash
# 前端打包
cd frontend && npm run build
# 产物在 frontend/dist/
```

---

## 环境变量说明

在 `backend/.env` 中配置以下变量：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `OLLAMA_API_KEY` | *(必填)* | Ollama 服务的 API Key |
| `OLLAMA_HOST` | `https://ollama.com` | Ollama 服务地址 |
| `OLLAMA_MODEL` | `gpt-oss:120b` | 使用的模型名称 |
| `CORS_ORIGINS` | `*` | 允许的跨域来源，生产环境建议指定具体域名 |

---

## API 接口

### 健康检查

```
GET /health
```

### 流式对话

```
POST /chat/stream
Content-Type: application/json

{
  "message": "感冒发烧怎么处理？",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

**响应**（SSE 格式）：

```
data: {"chunk": "感冒发烧"}
data: {"chunk": "的处理方法..."}
data: {"done": true, "model": "gpt-oss:120b"}
```

交互式文档：启动后端后访问 `http://localhost:8000/docs`
