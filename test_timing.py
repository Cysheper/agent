"""诊断 SSE 是否被缓冲：逐块记录到达时间。

用法:
  python test_timing.py                          # 直连后端 127.0.0.1:3000
  python test_timing.py http://127.0.0.1:8001/web?content=...   # 指定 URL（可走 serve.py 代理）

每块数据到达时打印时间戳和大小，可以看出：
  - 数据是边产生边到（时间戳分散）=> 链路没缓冲，是后端一轮一轮吐
  - 全部挤在最后同一秒到达 => 中间某层缓冲了
"""
import sys
import time
import urllib.parse
import urllib.request

MSG = "帮我规划一个成都一日游"
URL = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "http://127.0.0.1:3000/web?" + urllib.parse.urlencode({"content": MSG})
)

# 和 serve.py 一样强制直连，不走系统代理
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

t0 = time.time()
print(f"请求: {URL.split('?')[0]}")
with OPENER.open(URL) as resp:
    print(f"HTTP {resp.status}，响应头到达: {time.time() - t0:.2f}s")
    blocks = 0
    while True:
        chunk = resp.read(1024)  # 小块读取，观察逐块到达时间
        if not chunk:
            break
        dt = time.time() - t0
        text = chunk.decode("utf-8", errors="replace").replace("\n", "⏎")
        print(f"[{dt:7.2f}s] {len(chunk):5d}B  {text[:50]}")
        blocks += 1
    print(f"结束: 共 {blocks} 块，总耗时 {time.time() - t0:.2f}s")
