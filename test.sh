#!/usr/bin/env bash
# 云游 Wander 数据链路诊断脚本
# 用法: bash test.sh [后端地址] [测试端口]
# 逐段验证: 后端 -> 直连 SSE -> serve.py 代理 -> 前端同款解析逻辑
set -u

BACKEND="${1:-http://127.0.0.1:3000}"
PORT="${2:-8001}"
BASE="http://127.0.0.1:$PORT"
MSG="测试一下连接，请简短回复"
PASS=0
FAIL=0

ok()   { PASS=$((PASS + 1)); echo "  [PASS] $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  [FAIL] $1"; }

# Windows Git Bash 下可能只有 python，没有 python3
PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

echo "=== 1. 环境检查 ==="
command -v "$PY" >/dev/null 2>&1 && ok "$PY 可用" || { fail "没有 $PY"; exit 1; }
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' \
    && ok "Python >= 3.12" || fail "Python 版本 < 3.12"
if env | grep -qiE '^(http|https|all)_proxy='; then
    echo "  [警告] 检测到代理环境变量（常见丢数据原因）:"
    env | grep -iE '^(http|https|all)_proxy='
    echo "         serve.py 已强制直连本机后端，不受影响；但请留意下面第 4 步结果。"
else
    ok "无代理环境变量干扰"
fi

echo "=== 2. 后端健康检查 ==="
if curl -s --noproxy '*' -m 3 "$BACKEND/" | grep -q '"status":"Ok"'; then
    ok "后端存活 $BACKEND"
else
    fail "后端无响应 $BACKEND（请先启动后端: python main.py）"
fi

echo "=== 3. 直连后端 /web（原始 SSE，会调用一次模型） ==="
DIRECT=$(mktemp)
curl -s --noproxy '*' -m 120 -N --get "$BACKEND/web" --data-urlencode "content=$MSG" > "$DIRECT"
if [ -s "$DIRECT" ]; then
    ok "直连收到 $(wc -c < "$DIRECT") 字节"
    echo "--- 原始内容前 500 字节 ---"
    head -c 500 "$DIRECT"; echo; echo "---"
else
    fail "直连无任何输出（后端没有吐数据）"
fi

echo "=== 4. 经 serve.py 代理 /web（原始 SSE，会调用一次模型） ==="
cd "$(dirname "$0")"
AGENT_BACKEND="$BACKEND" FRONTEND_PORT="$PORT" "$PY" serve.py > /tmp/test_serve.log 2>&1 &
SERVE_PID=$!
trap 'kill "$SERVE_PID" 2>/dev/null' EXIT
sleep 1
PROXIED=$(mktemp)
HTTP_CODE=$(curl -s --noproxy '*' -m 120 -N -o "$PROXIED" -w '%{http_code}' --get "$BASE/web" --data-urlencode "content=$MSG")
if [ "$HTTP_CODE" = "200" ] && [ -s "$PROXIED" ]; then
    ok "经 serve.py 收到 $(wc -c < "$PROXIED") 字节"
else
    fail "经 serve.py 请求失败（HTTP $HTTP_CODE，$(wc -c < "$PROXIED") 字节）"
    echo "--- serve.py 日志尾部 ---"; tail -5 /tmp/test_serve.log
fi
kill "$SERVE_PID" 2>/dev/null
trap - EXIT

echo "=== 5. 模拟前端解析（与 web/src/lib/sse.ts 的 SseDecoder 同逻辑） ==="
"$PY" - "$DIRECT" "$PROXIED" << 'PYEOF'
import sys

def decode(raw):
    """与前端 SseDecoder.push/flush 相同的容错逻辑"""
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

for name, path in (('直连', sys.argv[1]), ('代理', sys.argv[2])):
    try:
        raw = open(path, encoding='utf-8', errors='replace').read()
    except OSError:
        print(f"{name}: 捕获文件不存在，跳过")
        continue
    events = decode(raw)
    text = sum(1 for e in events if not e.startswith('[ToolUse]'))
    tools = sum(1 for e in events if e.startswith('[ToolUse]'))
    print(f"{name}: 解析出 {len(events)} 条事件（文本 {text} / 工具 {tools}），共 {sum(len(e) for e in events)} 字符")
    for e in events[:3]:
        print("   -", e[:80].replace('\n', '⏎'))
PYEOF

echo "=== 结论 ==="
echo "  PASS $PASS / FAIL $FAIL"
if [ "$FAIL" -eq 0 ]; then
    echo "  数据链路正常。若浏览器仍收不到：请 Ctrl+F5 强刷（serve.py 已加 no-cache），"
    echo "  或检查浏览器控制台 Network 里 /web 请求的状态。"
else
    echo "  请把上面的 FAIL 项和对应输出发出来，逐段定位。"
fi
