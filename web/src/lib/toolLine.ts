import { parsePyLiteral } from './pyLiteral'
import type { ToolPayload } from './types'

const PREFIX = '[ToolUse]'

/**
 * 解析后端工具调用事件行，格式：
 *   [ToolUse]\ttool_name=shell\targs={'cmd': ['date']}\treturns={...}
 * 非工具行返回 null。args/returns 用 Python 字面量解析，
 * 失败时保留原始字符串。
 */
export function parseToolLine(line: string): ToolPayload | null {
  if (!line.startsWith(PREFIX)) return null

  const body = line.slice(PREFIX.length).trimStart()
  const nameEnd = body.indexOf('\t')
  if (nameEnd === -1) return null

  const namePart = body.slice(0, nameEnd)
  if (!namePart.startsWith('tool_name=')) return null
  const toolName = namePart.slice('tool_name='.length)

  const rest = body.slice(nameEnd + 1) // "args={...}\treturns={...}"
  if (!rest.startsWith('args=')) return null
  // 用最后一个 \treturns= 切分，避免结果内容里出现同名字段
  const returnsIdx = rest.lastIndexOf('\treturns=')
  if (returnsIdx === -1) return null

  const argsRaw = rest.slice('args='.length, returnsIdx)
  const resultRaw = rest.slice(returnsIdx + '\treturns='.length)

  return {
    toolName,
    args: tryParse(argsRaw),
    result: tryParse(resultRaw),
    argsRaw,
    resultRaw,
  }
}

function tryParse(src: string): unknown {
  try {
    return parsePyLiteral(src)
  } catch {
    return src
  }
}
