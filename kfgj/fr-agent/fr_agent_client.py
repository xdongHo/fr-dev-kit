#!/usr/bin/env python3
"""
FR Agent Client — Python 客户端，连接 FR Designer 内的 Java Agent HTTP API

用法:
    python fr_agent_client.py ping              # 健康检查（默认端口 18999）
    python fr_agent_client.py --port 19100 ping # FR11 健康检查（端口 19100）
    python fr_agent_client.py status            # Agent 状态
    python fr_agent_client.py record start      # 开始录制
    python fr_agent_client.py record stop       # 停止录制，返回事件
    python fr_agent_client.py events            # 获取最近事件
    python fr_agent_client.py tree              # 获取组件树
    python fr_agent_client.py click 100 200     # 点击坐标
    python fr_agent_client.py type "hello"      # 输入文本
    python fr_agent_client.py shortcut ctrl+s   # 快捷键
    python fr_agent_client.py replay            # 回放最近录制
    python fr_agent_client.py eval com.fr.main.impl.WorkBook  # 反射探索 FR 类

环境变量:
    FR_AGENT_HTTP_PORT  覆盖默认端口（默认 18999）
"""

import json
import sys
import urllib.request
import urllib.error
import time
import os

# 默认端口，可通过环境变量或命令行参数覆盖
DEFAULT_AGENT_PORT = int(os.environ.get("FR_AGENT_HTTP_PORT", "18999"))
AGENT_URL = f"http://localhost:{DEFAULT_AGENT_PORT}"


def api(method, path, data=None):
    """调用 Agent API"""
    url = f"{AGENT_URL}{path}"
    try:
        if data is not None:
            req = urllib.request.Request(
                url, data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method=method
            )
        else:
            req = urllib.request.Request(url, method=method)

        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": f"Cannot connect to agent: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def cmd_ping():
    r = api("GET", "/ping")
    print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_status():
    r = api("GET", "/status")
    print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_events(n=50):
    r = api("GET", f"/events?n={n}")
    if "error" in r:
        print(f"Error: {r['error']}")
    else:
        events = json.loads(r) if isinstance(r, str) else r
        print(f"Total events: {len(events)}")
        for evt in events[-20:]:  # last 20
            print(json.dumps(evt, indent=2, ensure_ascii=False)[:300])
            print("---")


def cmd_record_start():
    r = api("POST", "/record/start")
    print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_record_stop(save_to=None):
    r = api("POST", "/record/stop")
    print(f"Status: {r.get('status')}, Events: {r.get('count', 0)}")
    if save_to and "events" in r:
        with open(save_to, "w", encoding="utf-8") as f:
            json.dump(r["events"], f, indent=2, ensure_ascii=False)
        print(f"Saved to {save_to}")
    elif "events" in r:
        for evt in r["events"]:
            print(json.dumps(evt, ensure_ascii=False)[:200])


def cmd_tree():
    r = api("GET", "/tree")
    if "tree" in r:
        print(r["tree"])
    else:
        print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_click(x, y):
    r = api("POST", "/click", {"x": int(x), "y": int(y)})
    print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_type(text):
    r = api("POST", "/type", {"text": text})
    print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_shortcut(keys):
    r = api("POST", "/shortcut", {"keys": keys})
    print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_replay(speed=1.0):
    r = api("POST", "/replay", {"speed": float(speed)})
    print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_eval(class_name):
    r = api("POST", "/eval", {"class": class_name, "method": "list"})
    if "result" in r:
        print(r["result"])
    else:
        print(json.dumps(r, indent=2, ensure_ascii=False))


def cmd_monitor(interval=2):
    """实时监控 — 每 N 秒拉取事件"""
    print(f"Monitoring agent events (Ctrl+C to stop)...")
    try:
        last_count = 0
        while True:
            r = api("GET", "/events?n=5")
            if isinstance(r, list):
                new_events = r
                for evt in new_events:
                    ts = time.strftime("%H:%M:%S", time.localtime(evt["ts"] / 1000))
                    print(f"[{ts}] {evt['type']:20s} | {evt['comp']['path'][:60]}")
                if new_events:
                    last_count += len(new_events)
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\nStopped. Total events seen: {last_count}")


def print_usage():
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # 支持 --port 参数覆盖默认端口
    if sys.argv[1] == "--port":
        if len(sys.argv) < 4:
            print("Usage: fr_agent_client.py --port PORT command [args...]")
            sys.exit(1)
        AGENT_URL = f"http://localhost:{sys.argv[2]}"
        cmd = sys.argv[3]
        sys.argv = [sys.argv[0]] + sys.argv[4:]  # 重新组织参数
    else:
        cmd = sys.argv[1]

    if cmd == "ping":
        cmd_ping()
    elif cmd == "status":
        cmd_status()
    elif cmd == "events":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        cmd_events(n)
    elif cmd == "record":
        sub = sys.argv[2] if len(sys.argv) > 2 else "status"
        if sub == "start":
            cmd_record_start()
        elif sub == "stop":
            save = sys.argv[3] if len(sys.argv) > 3 else None
            cmd_record_stop(save)
        else:
            r = api("GET", "/record/status")
            print(json.dumps(r, indent=2, ensure_ascii=False))
    elif cmd == "tree":
        cmd_tree()
    elif cmd == "click":
        x, y = int(sys.argv[2]), int(sys.argv[3])
        cmd_click(x, y)
    elif cmd == "type":
        text = " ".join(sys.argv[2:])
        cmd_type(text)
    elif cmd == "shortcut":
        keys = sys.argv[2]
        cmd_shortcut(keys)
    elif cmd == "replay":
        speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
        cmd_replay(speed)
    elif cmd == "eval":
        cls = sys.argv[2]
        cmd_eval(cls)
    elif cmd == "monitor":
        interval = float(sys.argv[2]) if len(sys.argv) > 2 else 2
        cmd_monitor(interval)
    else:
        print_usage()
