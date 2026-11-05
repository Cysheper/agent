"""云游 Wander 前端静态服务器（纯标准库，无需 Node/npm）。

直接服务 web/dist 编译产物，并把 /web /clear /qq /qq_offical
反向代理到 Agent 后端（默认 http://127.0.0.1:3000），SSE 流式透传。

环境变量：
  AGENT_BACKEND  后端地址，默认 http://127.0.0.1:3000
  FRONTEND_PORT  前端端口，默认 8000
"""
import http.server
import os
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "web", "dist")
BACKEND = os.environ.get("AGENT_BACKEND", "http://127.0.0.1:3000").rstrip("/")
PORT = int(os.environ.get("FRONTEND_PORT", "8000"))

# 转发到后端的接口
PROXY_PATHS = {"/web", "/clear", "/qq", "/qq_offical"}
# 透传给后端的请求头（不传 Host，让 urllib 自己设置）
PASS_HEADERS = ("accept", "user-agent", "accept-language")
# 不逐条转发的响应头（由 http.server 自己处理）
SKIP_RESPONSE_HEADERS = ("transfer-encoding", "connection", "content-length")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST, **kwargs)

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path in PROXY_PATHS:
            self._proxy()
            return
        super().do_GET()

    def _proxy(self):
        url = BACKEND + self.path
        headers = {k: v for k, v in self.headers.items() if k.lower() in PASS_HEADERS}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() not in SKIP_RESPONSE_HEADERS:
                        self.send_header(k, v)
                self.end_headers()
                # SSE 流式透传：边读边写
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    self.wfile.flush()
        except Exception as e:  # 后端未启动等
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"backend unreachable ({BACKEND}): {e}".encode())

    def log_message(self, fmt, *args):
        pass  # 静默，不打请求日志


def main():
    if not os.path.isfile(os.path.join(DIST, "index.html")):
        print(f"[警告] 未找到前端产物 {os.path.join(DIST, 'index.html')}")
        print("       页面将无法打开。可在 web/ 目录执行 npm install && npm run build 编译。")
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[云游前端] http://127.0.0.1:{PORT}  (接口代理 -> {BACKEND})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
