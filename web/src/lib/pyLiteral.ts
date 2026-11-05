/**
 * 解析 Python 字面量（dict / list / str / int / float / True / False / None）
 * 为对应的 JS 值。后端工具事件的 args / returns 是 Python repr 格式
 * （单引号字符串），不能用 JSON.parse 直接解析。
 * 解析失败时抛出异常，由调用方回退到原始字符串。
 */
export function parsePyLiteral(src: string): unknown {
  const s = src
  let i = 0

  const value = parseValue()
  skipWs()
  if (i < s.length) throw new Error(`多余内容，位置 ${i}`)
  return value

  function skipWs(): void {
    while (i < s.length && /\s/.test(s[i])) i++
  }

  function parseValue(): unknown {
    const c = s[i]
    if (c === '{') return parseDict()
    if (c === '[') return parseList()
    if (c === "'" || c === '"') return parseString()
    if (c === '-' || (c >= '0' && c <= '9')) return parseNumber()
    const rest = s.slice(i)
    if (rest.startsWith('True')) { i += 4; return true }
    if (rest.startsWith('False')) { i += 5; return false }
    if (rest.startsWith('None')) { i += 4; return null }
    throw new Error(`意外的字符「${c}」，位置 ${i}`)
  }

  function parseDict(): Record<string, unknown> {
    i++ // {
    const out: Record<string, unknown> = {}
    skipWs()
    if (s[i] === '}') { i++; return out }
    for (;;) {
      skipWs()
      let key: string
      if (s[i] === "'" || s[i] === '"') {
        key = parseString()
      } else {
        const m = /^[A-Za-z_][A-Za-z0-9_]*/.exec(s.slice(i))
        if (!m) throw new Error(`非法的键，位置 ${i}`)
        key = m[0]
        i += m[0].length
      }
      skipWs()
      if (s[i] !== ':') throw new Error(`期望「:」，位置 ${i}`)
      i++
      skipWs()
      out[key] = parseValue()
      skipWs()
      if (s[i] === ',') { i++; continue }
      if (s[i] === '}') { i++; break }
      throw new Error(`期望「,」或「}」，位置 ${i}`)
    }
    return out
  }

  function parseList(): unknown[] {
    i++ // [
    const out: unknown[] = []
    skipWs()
    if (s[i] === ']') { i++; return out }
    for (;;) {
      skipWs()
      out.push(parseValue())
      skipWs()
      if (s[i] === ',') { i++; continue }
      if (s[i] === ']') { i++; break }
      throw new Error(`期望「,」或「]」，位置 ${i}`)
    }
    return out
  }

  function parseString(): string {
    const quote = s[i++]
    let out = ''
    while (i < s.length) {
      const c = s[i]
      if (c === '\\') {
        const n = s[i + 1]
        const escapes: Record<string, string> = {
          n: '\n', t: '\t', r: '\r', '\\': '\\', "'": "'", '"': '"',
        }
        if (n in escapes) {
          out += escapes[n]
          i += 2
          continue
        }
        // \uXXXX 等复杂转义：原样保留
        out += n
        i += 2
        continue
      }
      if (c === quote) { i++; return out }
      out += c
      i++
    }
    throw new Error('字符串未闭合')
  }

  function parseNumber(): number {
    const m = /^-?\d+(\.\d+)?([eE][+-]?\d+)?/.exec(s.slice(i))
    if (!m) throw new Error(`非法的数字，位置 ${i}`)
    i += m[0].length
    return Number(m[0])
  }
}
