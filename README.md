# Agent Project

这是一个基于OpenAI API的简单AI智能体项目，提供了交互式命令行环境，能够根据用户输入调用多种工具（如shell、天气查询等）来完成任务。

## 功能特点

- 使用OpenAI GPT模型进行对话
- 支持工具调用：内置shell工具和天气查询工具
- 模块化设计：agent、LLM、context、tool等模块清晰分离
- 提示词管理：使用Markdown文件配置系统提示词

## 项目结构

```
.
├── main.py           # 入口文件，启动交互式对话
├── pyproject.toml    # 项目配置和依赖
├── src/              # 核心源码
│   ├── agent.py      # Agent实现
│   ├── LLM.py        # LLM接口封装
│   ├── context.py    # 上下文管理
│   ├── moduls.py     # 模块定义
│   └── tool.py       # 工具基类
├── tools/            # 工具集
│   └── shell.py      # shell工具
├── prompt/           # 提示词文件
│   ├── agent.md
│   └── tools.md
└── README.md         # 项目说明
```

## 快速开始

1. 安装依赖：`uv sync` 或 `pip install -e .`
2. 配置环境变量：在 `.env` 中设置 OpenAI API Key
3. 运行：`python main.py`

## 依赖

- openai
- pydantic
- python-dotenv
- requests
- httpx
