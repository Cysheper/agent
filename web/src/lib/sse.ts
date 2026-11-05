/**
 * 读取 SSE 流，逐个产出 data 事件的内容。
 * 用 fetch + ReadableStream 实现，避免 EventSource 的自动重连行为，
 * 并支持 AbortController 主动中断。
 */

/**
 * 容错版 SSE 解析器。
 *
 * 后端以 `f"data: {text}\n\n"` 直接拼接事件，text 里可能包含真实换行
 * （Markdown 回复的每一行），甚至空行。此时只有第一行带 `data:` 前缀，
 * 其余行是裸文本；空行还会让事件提前断开，后续碎片没有任何前缀。
 * 本解析器把「没有 data: 前缀的碎片」续到上一条事件后面，保证内容不丢；
 * 纯注释事件（`: Connected Successfully`）仍按规范忽略。
 */
export class SseDecoder {
  private buf = ''
  private pending: string | null = null

  /** 喂入一段文本，返回本次完整解析出的 data 事件 */
  push(chunk: string): string[] {
    this.buf += chunk.replace(/\r\n/g, '\n')
    const out: string[] = []

    let sep: number
    while ((sep = this.buf.indexOf('\n\n')) !== -1) {
      const raw = this.buf.slice(0, sep)
      this.buf = this.buf.slice(sep + 2)
      const lines = raw.split('\n')
      const dataIdx = lines.findIndex((l) => l.startsWith('data:'))

      if (dataIdx === -1) {
        // 没有 data: 行：若是纯注释事件则忽略，否则续到上一条事件末尾
        if (this.pending !== null) {
          const cont = lines.filter((l) => !l.startsWith(':')).join('\n')
          if (cont) this.pending += '\n' + cont
        }
        continue
      }

      if (this.pending !== null) out.push(this.pending)
      const first = lines[dataIdx].slice(5).trimStart()
      const rest = lines.slice(dataIdx + 1).join('\n')
      this.pending = rest ? first + '\n' + rest : first
    }
    return out
  }

  /** 流结束时冲刷最后一条未完结的事件（含没有空行结尾的残余内容） */
  flush(): string[] {
    const out: string[] = []
    if (this.buf.length > 0) {
      out.push(...this.push('\n\n'))
    }
    if (this.pending !== null) {
      out.push(this.pending)
      this.pending = null
    }
    return out
  }
}

export async function* readSse(
  url: string,
  signal?: AbortSignal,
): AsyncGenerator<string, void, unknown> {
  const res = await fetch(url, { signal, headers: { Accept: 'text/event-stream' } })
  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  const sse = new SseDecoder()

  try {
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      for (const ev of sse.push(decoder.decode(value, { stream: true }))) yield ev
    }
    for (const ev of sse.flush()) yield ev
  } finally {
    reader.releaseLock()
  }
}
