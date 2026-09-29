#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bring_up.py — 感知环境一键就绪（P1 感知四件套之一）

一条命令保证: FR 设计器 JVM 在跑 + fr-agent 注入 + 端口归属正确(可执行 /exec)。

与 inject.py / inject_fr11.py 的差异 — 补上踩过的两个坑:
  1. PID 归属校验(2026-08-22 实证): 双设计器并跑时 agent 端口只归先占的 JVM,
     attach 成功 ≠ 端口易主。本脚本 ping 到的 PID ≠ 目标 PID 时自动 shutdown 旧 agent 再重绑。
  2. 版本自适应: --fr10 / --fr11 / 默认自动(优先已在跑的, 都没跑按 --fr10 拉起)。

用法:
  python bring_up.py                 # 自动: 谁在跑绑谁; 都没跑拉 FR10
  python bring_up.py --fr11          # 指定 FR11(在跑则绑; 没跑拉起)
  python bring_up.py --no-start      # 只绑在跑的, 不拉起新设计器
  python bring_up.py --check         # 只诊断不动手(输出状态报告)
退出码: 0 就绪 / 1 失败 / 2 参数错
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
HERE = __file__ and __import__("os").path.dirname(__import__("os").path.abspath(__file__))

FR = {
    "fr10": {
        "home": r"C:\Program Files\FineReport_10.0",
        "bat": r"C:\Program Files\FineReport_10.0\designer.bat",
        "mark": "FineReport_10.0",
        "wait": 60,   # FR10 启动较慢
    },
    "fr11": {
        "home": r"C:\FineReport_11.0",
        "bat": r"C:\FineReport_11.0\bin\designer.bat",
        "mark": "FineReport_11.0",
        "wait": 40,
    },
}
PING = "http://localhost:18999/ping"
SHUTDOWN = "http://localhost:18999/shutdown"


def http_json(url, timeout=3, method="GET"):
    req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def find_pid(mark):
    """找命令行含版本标记的 java 进程(与 inject_fr11 同路, wmi 优先 CIM 兜底)"""
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | "
             f"Where-Object {{$_.CommandLine -like '*{mark}*'}} | "
             "Select-Object ProcessId | ConvertTo-Json"],
            text=True, timeout=15)
        txt = (out or "").strip()
        if not txt:
            return None
        j = json.loads(txt)
        items = j if isinstance(j, list) else [j]
        pids = [int(x["ProcessId"]) for x in items if x and x.get("ProcessId")]
        return pids[0] if pids else None
    except Exception:
        return None


def start_designer(ver):
    cfg = FR[ver]
    print("  拉起 %s 设计器: %s" % (ver.upper(), cfg["bat"]))
    subprocess.Popen(["cmd", "/c", "start", "/min", "", cfg["bat"]],
                     cwd=cfg["home"] if ver == "fr11" else None)
    t0 = time.time()
    while time.time() - t0 < 240:
        pid = find_pid(cfg["mark"])
        if pid:
            print("  设计器就绪 PID=%s, 等 %ds GUI 初始化..." % (pid, cfg["wait"]))
            time.sleep(cfg["wait"])
            return pid
        time.sleep(3)
    return None


def attach(ver, pid):
    cfg = FR[ver]
    java = cfg["home"] + r"\jre\bin\java.exe"
    tools = cfg["home"] + r"\jre\lib\tools.jar"
    jar = HERE + r"\fr-agent.jar"
    import os
    for p in (java, tools, jar):
        if not os.path.isfile(p):
            print("  ❌ 缺文件: %s" % p)
            return False
    r = subprocess.run([java, "-cp", ".;" + tools, "Attacher", str(pid), jar],
                       cwd=HERE, capture_output=True, text=True, timeout=90)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if out:
        print("  attach: " + out.splitlines()[-1][:100])
    return r.returncode == 0


def agent_pid():
    """ping 到的 agent 归属 PID(无 pid 字段返回 None)"""
    try:
        return http_json(PING).get("pid")
    except Exception:
        return None


def wait_agent(timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            return http_json(PING)
        except Exception:
            time.sleep(1.5)
    return None


def ensure(ver, want_start=True):
    """核心: 目标 JVM 有 agent 且归属正确。返回 True=就绪"""
    cfg = FR[ver]
    pid = find_pid(cfg["mark"])
    if pid is None:
        if not want_start:
            print("  %s 设计器未在跑(--no-start 不拉起)" % ver.upper())
            return False
        pid = start_designer(ver)
        if pid is None:
            print("  ❌ 240s 内未见 %s java 进程" % ver.upper())
            return False
    print("  目标 %s PID=%s" % (ver.upper(), pid))

    # ── PID 归属校验(核心差异) ──
    cur = agent_pid()
    if cur is not None:
        if cur == pid:
            print("  ✅ agent 已注入且归属正确(pid=%s)" % pid)
            return True
        print("  ⚠ 端口被旧 JVM(pid=%s)占用 → shutdown 旧 agent 重绑" % cur)
        try:
            http_json(SHUTDOWN, method="POST", timeout=5)
        except Exception as e:
            print("    shutdown: %s(可能已退出, 继续)" % e)
        time.sleep(3)
        if agent_pid() is not None:
            print("  ❌ 旧 agent 未释放(需重启旧设计器 JVM)")
            return False

    if not attach(ver, pid):
        return False
    info = wait_agent()
    if info is None:
        print("  ❌ attach 后 20s 内 18999 未响应")
        return False
    # 复核归属(防竞争)
    if info.get("pid") != pid:
        print("  ❌ 重绑后归属仍不对: agent pid=%s != 目标 %s" % (info.get("pid"), pid))
        return False
    print("  ✅ 注入成功且归属正确: %s" % json.dumps(info, ensure_ascii=False))
    return True


def main():
    import os
    ap = argparse.ArgumentParser(description="感知环境一键就绪(含 PID 归属校验)")
    ap.add_argument("--fr10", action="store_true", help="指定 FR10")
    ap.add_argument("--fr11", action="store_true", help="指定 FR11")
    ap.add_argument("--no-start", action="store_true", help="不拉起新设计器, 只绑在跑的")
    ap.add_argument("--check", action="store_true", help="只诊断不动手")
    a = ap.parse_args()
    if a.fr10 and a.fr11:
        print("❌ --fr10 与 --fr11 互斥")
        return 2

    # ── check 模式: 纯诊断报告 ──
    if a.check:
        print("═══ 环境诊断 ═══")
        p10, p11 = find_pid(FR["fr10"]["mark"]), find_pid(FR["fr11"]["mark"])
        print("  FR10 JVM: %s" % (p10 or "未运行"))
        print("  FR11 JVM: %s" % (p11 or "未运行"))
        cur = agent_pid()
        print("  agent 18999: %s" % ("未响应" if cur is None else "pid=%s(%s)" % (
            cur, "FR10" if cur == p10 else "FR11" if cur == p11 else "未知 JVM")))
        return 0

    if a.fr10:
        ver = "fr10"
    elif a.fr11:
        ver = "fr11"
    else:
        # 自动: 谁在跑绑谁; 都没跑拉 FR10(皮肤/渲染工具链主环境)
        p10, p11 = find_pid(FR["fr10"]["mark"]), find_pid(FR["fr11"]["mark"])
        if p11 and not p10:
            ver = "fr11"
        elif p10 and not p11:
            ver = "fr10"
        elif p10 and p11:
            cur = agent_pid()
            ver = "fr10" if cur == p10 else "fr11" if cur == p11 else "fr10"
            print("  双版本在跑, 选 %s(agent 归属/默认)" % ver.upper())
        else:
            ver = "fr10" if not a.no_start else None
            if ver is None:
                print("  无设计器在跑且 --no-start")
                return 1
    ok = ensure(ver, want_start=not a.no_start)
    if ok:
        print("🎉 环境就绪: 渲染 render_check / page2tpl 可用(/exec@19000)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
