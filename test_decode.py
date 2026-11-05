"""test.bat 的辅助脚本：用与前端 SseDecoder 完全相同的容错逻辑解析 SSE 捕获文件。

用法: python test_decode.py direct.txt proxied.txt
"""
import sys


def decode(raw: str):
    """与 web/src/lib/sse.ts 的 SseDecoder.push/flush 同逻辑"""
    buf = raw.replace('\r\n', '\n')
    pending, out = None, []
    while '\n\n' in buf:
        raw_ev, buf = buf.split('\n\n', 1)
        lines = raw_ev.split('\n')
        di = next((i for i, l in enumerate(lines) if l.startswith('data:')), -1)
        if di == -1:
            if pending is not None:
                cont = '\n'.join(l for l in lines if not l.startswith(':')).strip('\n')
                if cont:
                    pending += '\n' + cont
            continue
        if pending is not None:
            out.append(pending)
        first = lines[di][5:].lstrip()
        rest = '\n'.join(lines[di + 1:])
        pending = first + ('\n' + rest if rest else '')
    if pending is not None:
        out.append(pending)
    return out


def main():
    ok_all = True
    for name, path in (('直连', sys.argv[1]), ('代理', sys.argv[2])):
        try:
            raw = open(path, encoding='utf-8', errors='replace').read()
        except OSError:
            print(f'{name}: 捕获文件不存在，跳过')
            ok_all = False
            continue
        events = decode(raw)
        text = sum(1 for e in events if not e.startswith('[ToolUse]'))
        tools = sum(1 for e in events if e.startswith('[ToolUse]'))
        print(f'{name}: 解析出 {len(events)} 条事件（文本 {text} / 工具 {tools}），共 {sum(len(e) for e in events)} 字符')
        for e in events[:3]:
            print('   -', e[:80].replace('\n', '⏎'))
        if not events:
            ok_all = False
    sys.exit(0 if ok_all else 1)


if __name__ == '__main__':
    main()
