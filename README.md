# Agent Project

一个基于 LLM 的 AI 智能体（Agent）服务。通过 FastAPI 提供 SSE 流式接口，智能体接收用户任务后自主运行事件循环：调用 LLM → 解析 JSON 指令 → 执行工具（shell、天气、记忆等）→ 将结果反馈给 LLM，直到任务结束。

## 功能特点

- **SSE 流式输出**：实时推送智能体消息与工具调用过程
- **JSON 协议驱动的事件循环**：`print`（输出）/ `tool_use`（调用工具）/ `end_task`（结束任务）
- **工具注册机制**：使用 `@tool` 装饰器一键注册，工具的 docstring 自动写入系统提示词
- **多会话（Chapter）管理**：每个会话的上下文持久化到 `context/{id}.json`，可通过 id 恢复历史会话
- **上下文管理**：超长自动压缩（LLM 摘要）、工具结果自动精简
- **SQLite 历史记录**：所有对话写入 `database/agent.db`
- **提示词文件化**：`prompt/agent.md` 与 `prompt/tools.md` 管理系统提示词

## 项目结构

```
.
├── main.py              # 入口文件，FastAPI 服务（端口 3000）
├── pyproject.toml       # 项目配置和依赖
├── src/                 # 核心源码
│   ├── agent.py         # Agent 主循环与工具分发
│   ├── LLM.py           # LLM 接口封装（AsyncOpenAI）
│   ├── context.py       # 上下文管理（压缩/精简）
│   ├── chapter.py       # 会话管理（chapter.toml + context/{id}.json）
│   ├── database.py      # SQLite 对话历史
│   ├── tool.py          # 工具注册器（@tool 装饰器）
│   ├── module.py        # Message/ToolUse 数据模型与枚举
│   ├── output.py        # 输出分发（控制台 / WebUI）
│   └── log.py           # 日志（app.log）
├── tools/               # 工具集
│   ├── shell.py         # shell 与 weather 工具
│   └── memory.py        # memory_get 记忆工具（开发中）
├── memory/              # 记忆系统（开发中）
├── prompt/              # 系统提示词
│   ├── agent.md         # 智能体行为规范
│   └── tools.md         # 输出 JSON 协议说明
├── chapter.toml         # 会话索引（id → 名称）
├── context/             # 会话上下文持久化
└── database/            # SQLite 数据库
```

## 快速开始

1. **环境要求**：Python >= 3.12（本项目使用 [uv](https://docs.astral.sh/uv/) 管理依赖）

2. **安装依赖**：

   ```bash
   uv sync
   ```

3. **配置环境变量**：在 `.env` 中配置 LLM 相关参数（兼容任意 OpenAI 格式 API）：

   ```bash
   model_name=your-model-name
   base_url=https://api.openai.com/v1
   api_key=sk-xxx
   ```

4. **启动服务**：

   ```bash
   python main.py
   # 或
   uv run main.py
   ```

   服务运行于 `http://0.0.0.0:3000`。

5. **测试**：

   ```bash
   curl -N -X POST http://localhost:3000/stream \
     -H "Content-Type: application/json" \
     -d '{"prompt": "现在几点了？"}'
   ```

## API 接口

### POST /stream

发起/恢复一次智能体对话，返回 SSE 流。

请求体：

```json
{
  "prompt": "现在几点了？",
  "id": 1788273415
}
```

- `prompt`（必填）：用户任务
- `id`（可选）：会话 id。传入已存在的 id 会恢复该会话的历史上下文；不传则新建会话

SSE 消息格式（`Message` 模型）：

```json
{
  "input": 1,
  "role": "Agent",
  "content": "让我查看一下当前系统时间。",
  "output": 1
}
```

工具调用时 `content` 为 `ToolUse` 的 JSON：

```json
{
  "input": 1,
  "role": "Tool",
  "content": "{\"tool_name\":\"shell\",\"args\":[\"date\"],\"result\":{\"stdout\":\"...\",\"stderr\":\"\",\"returncode\":0}}",
  "output": 1
}
```

### POST /stop

停止当前正在运行的智能体任务：

```bash
curl -X POST http://localhost:3000/stop
```

### GET /load_chapter/{id}

按 id 加载已保存的会话（名称与完整上下文）：

```bash
curl http://localhost:3000/load_chapter/1788273415
```

### GET /

健康检查，返回 `{"message": "Agent is running!"}`。

## 智能体工作流程

### 系统提示词构成

由三部分拼接而成（见 `src/agent.py` 的 `construct_system_prompt`）：

1. `prompt/agent.md` — 智能体行为规范（制定计划 → 使用工具 → 结束任务）
2. `prompt/tools.md` — 输出 JSON 协议说明
3. 所有已注册工具的 docstring（自动收集）

### 事件循环

1. 用户提交 prompt，写入上下文与数据库
2. LLM 依据系统提示词输出 JSON
3. 解析 JSON：
   - `print`：消息直接通过 SSE 推送给用户
   - `tool_use`：依次执行各工具，结果以 `system` 消息写回上下文
   - `end_task: true`：结束循环，上下文持久化到 `context/{id}.json`
4. 若未结束，携带工具结果进入下一轮循环

### 输出协议

LLM 必须输出可被解析的 JSON，支持以下字段：

| 字段 | 说明 |
| ---- | ---- |
| `print` | 字符串数组，直接返回给用户的消息 |
| `tool_use` | 工具名 → `{"args": [...]}` 的映射，可同时调用多个工具 |
| `end_task` | 布尔值，任务结束时为 `true`，且必须放在 JSON 末尾 |

示例：

```json
{
  "print": ["我需要使用shell工具，获取当前目录下的文件。"],
  "tool_use": {
    "shell": {
      "args": ["ls", "-l"]
    }
  },
  "end_task": true
}
```

## 内置工具

| 工具 | 说明 |
| ---- | ---- |
| `shell(cmd: list[str])` | 执行 shell 命令，返回 stdout / stderr / returncode，智能体的主要工具 |
| `weather(city: str)` | 查询城市天气（示例占位实现） |
| `memory_get(keywords: list)` | 根据关键词获取相关记忆（开发中） |

## 自定义工具

使用 `@tool` 装饰器即可注册，docstring 会自动写入系统提示词供 LLM 了解用法：

```python
# tools/my_tool.py
from src.tool import tool

@tool
def my_tool(args: list):
    """
    ## my_tool(args: list), 工具功能描述

    ### 参数：
    **类型**： list
    **示例**：
    "args": [...]

    ### 返回值
    **类型**： str
    """
    return "结果"
```

然后在 `tools/__init__.py` 中导入即可：

```python
from .my_tool import *
```

## 配置项

| 环境变量 | 必填 | 默认值 | 说明 |
| -------- | ---- | ------ | ---- |
| `model_name` | 是 | — | LLM 模型名称 |
| `base_url` | 是 | — | API 地址（兼容 OpenAI 格式） |
| `api_key` | 是 | — | API 密钥 |
| `context_length` | 否 | 20 | 上下文超过该长度时触发压缩 |
| `compress_length` | 否 | 10 | 压缩时取前 N 条消息做摘要 |
| `compress_prompt` | 否 | 将以下内容压缩为简短的摘要… | 压缩时使用的提示词 |

## 依赖

- fastapi
- uvicorn
- openai
- httpx[socks]
- pydantic
- python-dotenv
- requests
