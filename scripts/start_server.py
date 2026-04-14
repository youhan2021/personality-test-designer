#!/usr/bin/env python3
"""
start_server.py — 启动临时 HTTP 预览服务器

用法：
  python3 start_server.py /path/to/问卷_xxx.html

行为：
  1. 读取同目录 ../config.env 获得 PREVIEW_PORT / PREVIEW_HOST
  2. 启动 HTTP 服务器，绑定指定地址和端口
  3. 输出 URL 到 stdout：PREVIEW_URL:http://host:port/filename
  4. 服务器在后台 daemon 线程运行，进程退出时不阻塞

配置文件（../config.env）：
  PREVIEW_PORT=3000   # 0 = 自动分配随机端口
  PREVIEW_HOST=0.0.0.0  # 0.0.0.0 = 局域网可访问
"""

import http.server
import socketserver
import socket
import sys
import threading
import pathlib

SKILL_DIR = pathlib.Path(__file__).parent
CONFIG_FILE = SKILL_DIR / "../config.env"


def read_config():
    port = 0
    host = "127.0.0.1"
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                if key == "PREVIEW_PORT":
                    try:
                        port = int(val)
                    except ValueError:
                        port = 0
                elif key == "PREVIEW_HOST":
                    host = val or "127.0.0.1"
    return host, port


def get_free_port():
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 start_server.py /path/to/问卷.html", file=sys.stderr)
        sys.exit(1)

    html_file = pathlib.Path(sys.argv[1]).resolve()
    if not html_file.exists():
        print(f"ERROR: file not found: {html_file}", file=sys.stderr)
        sys.exit(1)

    host, port = read_config()

    # 自动分配端口
    if port == 0:
        port = get_free_port()

    # 切换到 HTML 文件所在目录
    os_chdir = pathlib.Path(html_file).parent
    import os
    os.chdir(os_chdir)

    # 允许地址复用（快速重启）
    socketserver.TCPServer.allow_reuse_address = True
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((host, port), handler)

    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()

    url = f"http://{host}:{port}/{html_file.name}"
    print(f"PREVIEW_URL:{url}", flush=True)

    # 保持进程运行（服务器在 daemon 线程）
    try:
        while True:
            threading.Event().wait(86400)
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    main()
