/** 一次工具调用的信息（解析自后端 [ToolUse] 事件行） */
export interface ToolPayload {
  toolName: string
  /** 解析成功时为对象/数组等 JS 值，失败时为原始字符串 */
  args: unknown
  result: unknown
  argsRaw: string
  resultRaw: string
}

export type ItemRole = 'user' | 'agent' | 'tool' | 'error'

export interface ChatItem {
  id: number
  role: ItemRole
  content: string
  tool?: ToolPayload
}
