import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 后端 Agent 服务端口，可通过环境变量覆盖
const agentPort = Number(process.env.AGENT_PORT ?? 3000)

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      // 后端 GET /web?content=... 的 SSE 接口
      '/web': {
        target: `http://127.0.0.1:${agentPort}`,
        changeOrigin: true,
      },
      // 清空 Agent 上下文
      '/clear': {
        target: `http://127.0.0.1:${agentPort}`,
        changeOrigin: true,
      },
    },
  },
})
