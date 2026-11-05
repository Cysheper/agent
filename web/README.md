# 云游 · 前端对话页

Agent 项目的旅行主题 Web 前端（Vite + Vue 3 + TypeScript），通过后端
`GET /web?content=...` 的 SSE 接口与 Agent 对话。纯黑极简配色。

- 首页大标题随机轮播「你想去哪玩儿？」「出发吧！」等文案，下方随机展示
  5 条提问示例（点击填入输入框，可换一批）
- Agent 消息逐字浮现，结束后切换为 Markdown 渲染
- 工具调用折叠成卡片，默认收起，可展开查看参数与结果（长结果可展开全部）
- 等待回复时显示三点指示器；无登录鉴权、无会话功能，就一个对话页
- 所有动画均为纯 CSS（transform / opacity），无 UI 框架依赖

## 启动

1. 先启动后端（仓库根目录）：

   ```bash
   uv run python main.py
   ```

2. 安装依赖并启动前端：

   ```bash
   npm install
   npm run dev
   ```

3. 浏览器打开 <http://localhost:5173>

开发环境下 Vite 会把 `/web` 代理到 `http://127.0.0.1:3000`（后端端口可用
环境变量 `AGENT_PORT` 覆盖，例如 `AGENT_PORT=4000 npm run dev`）。

## 构建与部署

```bash
npm run build   # 产物在 dist/
```

`dist/` 可交给任意静态托管；前端与后端不同源时，需要反向代理 `/web` 路径，
或在构建时设置 `VITE_API_BASE` 环境变量指向后端同源地址。

## 与后端的协议

- 请求：`GET /web?content=<urlencoded 文本>`
- 响应：`text/event-stream`，每条 `data:` 是：
  - 注意：后端用 f-string 直接拼接事件，多行内容的续行**不带 `data:` 前缀**、
    内容里的空行会把事件截断，前端解析器已做容错处理（见
    [src/lib/sse.ts](src/lib/sse.ts) 的 SseDecoder）
  - Agent 文本消息，或
  - 工具调用 `[ToolUse]\ttool_name=xxx\targs={...}\treturns={...}`
    （`args` / `returns` 为 Python 字面量格式，见
    [src/lib/pyLiteral.ts](src/lib/pyLiteral.ts) 的解析器）

## 目录结构

```text
src/
  App.vue                 页面骨架：顶栏、首页/聊天切换、输入区
  style.css               全局样式与设计变量
  composables/useChat.ts  SSE 拉流与消息状态
  lib/
    sse.ts                fetch 版 SSE 读取器（可中断）
    toolLine.ts           [ToolUse] 事件行解析
    pyLiteral.ts          Python 字面量解析器
    markdown.ts           markdown-it 配置
    phrases.ts            首页文案、提问示例池
    types.ts              消息/工具数据类型
  components/
    LandingHero.vue       首页（轮播标题 + 随机示例）
    ChatMessage.vue       用户/Agent/错误消息（逐字浮现）
    ToolCard.vue          折叠工具调用卡片
    TypingIndicator.vue   等待回复的三点指示器
    ChatInput.vue         输入框（Enter 发送 / Shift+Enter 换行）
```
