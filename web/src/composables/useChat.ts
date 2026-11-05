import { ref } from 'vue'
import type { ChatItem } from '../lib/types'
import { readSse } from '../lib/sse'
import { parseToolLine } from '../lib/toolLine'

// 空字符串走 Vite 开发代理；部署时可设为后端同源路径
const API_BASE = import.meta.env.VITE_API_BASE ?? ''

export function useChat() {
  const items = ref<ChatItem[]>([])
  const streaming = ref(false)

  let seq = 0
  let abort: AbortController | null = null

  async function send(text: string) {
    if (streaming.value) return
    const content = text.trim()
    if (!content) return

    items.value.push({ id: ++seq, role: 'user', content })
    streaming.value = true

    const ctrl = new AbortController()
    abort = ctrl

    try {
      const url = `${API_BASE}/web?content=${encodeURIComponent(content)}`
      for await (const data of readSse(url, ctrl.signal)) {
        const tool = parseToolLine(data)
        if (tool) {
          items.value.push({ id: ++seq, role: 'tool', content: '', tool })
          continue
        }
        const text = data.trim()
        if (text) items.value.push({ id: ++seq, role: 'agent', content: text })
      }
    } catch {
      // 主动中断（清空对话）不算错误
      if (!ctrl.signal.aborted) {
        items.value.push({
          id: ++seq,
          role: 'error',
          content: '旅行助手好像走神了（连接中断），再试一次吧。',
        })
      }
    } finally {
      if (abort === ctrl) {
        abort = null
        streaming.value = false
      }
    }
  }

  function clear() {
    abort?.abort()
    abort = null
    items.value = []
    streaming.value = false
    // 同步清空后端 Agent 上下文（尽力而为，失败不打扰用户）
    void fetch(`${API_BASE}/clear`).catch(() => {})
  }

  return { items, streaming, send, clear }
}
