# Agent Project

一个基于 OpenAI 兼容接口的 LLM Agent 原型。服务收到消息后，会循环请求模型、解析 JSON 指令、执行注册工具，并通过 SSE 返回 Agent 消息和工具结果。

当前入口提供健康检查和两个 QQ 风格的 GET 接口。项目还没有 README 旧版本里提到的 `/stream`、`/stop`、会话恢复 API；上下文也没有按会话持久化。

## 功能概览

- FastAPI 服务和 SSE 响应
- 由 `print`、`tool_use`、`end_task` 字段驱动的 JSON 事件循环
- `@tool` 装饰器注册工具，工具 docstring 会加入系统提示词
- 通过 `context_length` 配置触发上下文摘要；较长的工具结果会被精简
- 将用户消息写入 SQLite 历史表
- 系统提示词从 `prompt/fish.md`、`prompt/agent.md`、`prompt/tools.md` 拼装

## 环境要求

- Python 3.12 或更高版本
- [uv](https://docs.astral.sh/uv/)（推荐）
- 一个可用的 OpenAI 兼容聊天补全 API

安装依赖：

```bash
uv sync
```

在项目根目录创建 `.env`：

```dotenv
DEEPSEEK_MODULE_NAME=your-model-name
DEEPSEEK_API_BASE=https://api.deepseek.com
DEEPSEEK_API_KEY=your-api-key
agent_port=3000

# 可选：上下文摘要设置
context_length=20
compress_length=10
compress_prompt=将以下内容压缩为简短的摘要，简要描述做了什么。
```

变量名以上述代码读取的名称为准。`LLM` 在应用启动时初始化，因此模型名和 API 地址需要在启动前配置。

## 初始化数据库

无需手动操作：服务启动时会自动创建 `./database` 目录、`agent.db` 文件和 `AgentData` 表
（`id` 自增主键 / `created_time` / `role` / `content`），用户消息会写入其中。

## Windows 一键启动（无需 uv / Node）

1. `git clone` 项目后，先把 `.env.example` 复制为 `.env` 并填入你的 API Key（脚本会检查 `DEEPSEEK_API_KEY`、`DEEPSEEK_API_BASE`、`DEEPSEEK_MODULE_NAME`，缺失会提示）。
2. 双击 `run.bat`（或命令行执行），脚本会自动：
   - 检查 Python 3.12+（没有会提示安装地址）
   - 检查 `.env` 环境变量（缺哪个会提示哪个）
   - 用 pip 安装 `pyproject.toml` 中的全部依赖（不需要 uv）
   - 启动后端 `python main.py`（端口取 `.env` 的 `agent_port`，默认 3000）
   - 启动前端 `python serve.py`：直接托管仓库里已编译好的 `web/dist` 静态页面（**不需要安装 Node / 下载 vue 依赖**），并把 `/web`、`/clear` 等接口反向代理到后端
   - 自动打开浏览器 http://localhost:8000
3. 改过前端源码（`web/`）后，重新编译一次并提交 `web/dist`：`cd web && npm install && npm run build`

## 启动

```bash
uv run python main.py
```

服务默认监听 `127.0.0.1:3000`。可通过 `.env` 中的 `agent_port` 修改端口；监听地址目前在 `main.py` 中固定为 `127.0.0.1`。

开发前端：`cd web && npm run dev`（Vite 会把 `/web`、`/clear` 代理到后端，见 web/README.md）。

## HTTP 接口

### `GET /`

健康检查，返回：

```json
{"status":"Ok"}
```

### `GET /qq?content=...`

以 QQ 通道标记输入内容，并以 `text/event-stream` 返回 SSE。示例：

```bash
curl -N --get 'http://127.0.0.1:3000/qq' \
  --data-urlencode 'content=现在几点了？'
```

### `GET /qq_offical?user_name=...&content=...`

与 `/qq` 类似，额外接受 `user_name` 查询参数；当前实现没有使用该参数，也没有在此路由中启动 QQ Bot SDK。

SSE 每个事件的 `data:` 内容是可读文本，可能是 Agent 输出，也可能是工具调用结果，例如：

```text
data: 我先查询一下。

data: [ToolUse] tool_name=shell args={'cmd': ['date']} returns={'stdout': '...', 'stderr': '', 'returncode': 0}

```

接口目前使用 GET 请求，内容应进行 URL 编码；没有 `/stream` POST 接口，也没有会话 id 参数。

## Agent 工作流程

每轮模型输出 JSON，支持以下字段：

| 字段 | 作用 |
| --- | --- |
| `print` | 字符串数组，作为 Agent 消息返回 |
| `tool_use` | 工具名到参数对象的映射；执行结果写回上下文 |
| `end_task` | 为 `true` 时结束当前循环 |

示例：

```json
{
  "print": ["我先查看当前时间。"],
  "tool_use": {
    "shell": {"cmd": ["date"]}
  },
  "end_task": true
}
```

系统提示词要求模型以 JSON 格式输出。模型返回无法解析的 JSON 时，Agent 会把错误提示写入上下文并继续请求。

## 内置工具

| 工具 | 说明 |
| --- | --- |
| `shell(cmd: list[str])` | 执行本机命令，返回标准输出、标准错误和退出码 |
| `weather(city: str)` | 示例占位实现，固定返回晴天 |
| `web_search(query: str, count: int = 3)` | 调用 DeepSeek 搜索接口，需要 `DEEPSEEK_API_KEY` |
| `web_fetch(url: str)` | 调用 DeepSeek 网页抓取接口，需要 `DEEPSEEK_API_KEY` |
| `memory_get(content: list[str])` | 实验性记忆接口，依赖外部 `./mem` 可执行文件 |
| `memory_add(content: list[str])` | 实验性记忆接口，依赖外部 `./mem` 可执行文件 |

### 添加工具

在 `tools/` 下定义函数并用 `@tool` 注册，然后在 `tools/__init__.py` 导入：

```python
from src.tool import tool

@tool
def my_tool(query: str) -> str:
    """查询某项信息并返回结果。"""
    return f"查询内容：{query}"
```

## 项目结构

```text
main.py             FastAPI 入口
run.bat             Windows 一键启动脚本（检查环境/装依赖/起服务/开浏览器）
serve.py            前端静态服务器（托管 web/dist + 反代后端，仅标准库）
.env.example       环境变量模板
src/agent.py        Agent 主循环、提示词拼装和工具分发
src/LLM.py          OpenAI 兼容异步客户端封装
src/context.py      上下文压缩和工具结果精简
src/database.py     SQLite 历史写入
src/tool.py         工具注册器
src/module.py       消息、角色和工具调用数据结构
tools/              内置工具
memory/             实验性记忆实现
prompt/             系统提示词
web/                前端源码（Vue3 + Vite），编译产物在 web/dist（随仓库分发）
showcase/           项目介绍静态页面
```

## 当前限制

- 每个 `Agent` 持有单份上下文；并发请求可能共享状态，不适合多用户并发服务。
- 当前没有会话隔离、上下文持久化、停止任务接口或 QQ Bot 生命周期集成。
- `shell` 能执行服务进程可访问的本机命令。只应在可信、受控的环境中使用，不能直接暴露给不可信用户。
- `memory` 工具依赖仓库外部的 `./mem` 程序，未配置时不可用。
- 工具说明和实际可运行状态以代码为准；部分功能仍是原型或占位实现。
