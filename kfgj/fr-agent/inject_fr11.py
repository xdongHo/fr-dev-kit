#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FR11 一键注入脚本 —— 把 fr-agent.jar 动态 attach 到运行中的 FineReport 11.0 设计器 JVM

用法:
    python inject_fr11.py                # 自动找 FR11 PID → attach → 验证 18999/19000 端口
    python inject_fr11.py --start        # 设计器没起? 先拉起 designer.bat 再等它就绪后注入
    python inject_fr11.py --pid 1234     # 手动指定 PID
    python inject_fr11.py --exec "var c=java.lang.Class.forName('com.fr.locale.InterProviderFactory'); c.getName()"
                                          # 注入成功后直接在 19000 端口跑一段 Nashorn 脚本

与 FR10 inject.py 的差异(2026-08 实测, 见 ckzl/lc/fr11_knowledge/practice_verification.md):
    1. FR11 自带 JRE = OpenJDK 1.8.0_191 (Red Hat), 且 jre\\lib\\tools.jar 齐全 ——
       Attacher 必须用 FR11 自带 JRE 跑(同源 JVM, attach 协议最稳);
       混用 Corretto/Oracle JDK 会报 "jvm.dll not loaded" / attach 握手失败。
    2. PID 识别: 命令行含 "FineReport_11.0"(精确区分 FR10 的 FineReport_10.0)。
    3. 设计器主类 com.fr.start.Designer, designer.bat 为纯 classpath 启动(无 -javaagent)。

陷阱(继承 fr-agent/README.md):
    - 每个设计器 JVM 只能注入一次(18999 绑定后旧 agent 不释放); 重注入需重启设计器
    - 绝不用 -javaagent 启动(FR License 校验会失败), 只走动态 attach
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

FR11_HOME = r"C:\FineReport_11.0"
FR11_JAVA = os.path.join(FR11_HOME, "jre", "bin", "java.exe")
FR11_TOOLS = os.path.join(FR11_HOME, "jre", "lib", "tools.jar")
FR11_DESIGNER_BAT = os.path.join(FR11_HOME, "bin", "designer.bat")
AGENT_JAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fr-agent.jar")

# 端口配置 —— 默认 19100/19101 避开 FR10 的 18999/19000
# 可通过 --port-base 参数或环境变量 FR_AGENT_PORT_BASE 覆盖
DEFAULT_PORT_BASE = 19100


def get_ports(port_base=None):
    """获取 HTTP 端口和 Exec 端口，优先级: 参数 > 环境变量 > 默认值"""
    if port_base is None:
        port_base = int(os.environ.get("FR_AGENT_PORT_BASE", DEFAULT_PORT_BASE))
    return port_base, port_base + 1


def get_urls(port_base=None):
    """获取 ping 和 exec URL"""
    http_port, exec_port = get_ports(port_base)
    return {
        "ping_http": f"http://localhost:{http_port}/ping",
        "ping_exec": f"http://localhost:{exec_port}/ping",
        "exec": f"http://localhost:{exec_port}/exec",
        "http_port": http_port,
        "exec_port": exec_port,
    }


def http_json(url, timeout=3):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def agent_alive(port_base=None):
    """检查是否已有存活 agent(可能已注入过)。
    双 FR 共存防误判: ping 通后必须校验返回 pid 是 FR11 JVM——
    FR10 设计器的 agent 同样占 18999/19000,不校验会把 FR10 当 FR11(2026-08-23 夜实测踩坑)。"""
    urls = get_urls(port_base)
    ping_url = urls["ping_http"]
    try:
        info = http_json(ping_url)
    except Exception:
        return None
    if not info:
        return None
    pid = info.get("pid")
    if pid:
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command",
                 "(Get-CimInstance Win32_Process -Filter \"ProcessId=%d\").CommandLine" % int(pid)],
                text=True, timeout=15)
            cl = out or ""
            if "FineReport_11.0" not in cl:
                print("⚠ 端口 %d 被 FR10 JVM(pid=%s) 的 agent 占用——FR11 agent 无法绑定同端口。" % (urls["http_port"], pid))
                print("  处置: 关闭 FR10 设计器后重跑本脚本,或使用 --port-base 19200 指定不同端口。")
                return None
        except Exception:
            pass  # 校验失败保守放行(ping 结构已像本 agent)
    return info


def find_fr11_pid():
    """找 FR11 设计器 java 进程: 命令行同时含 FineReport_11.0 与 com.fr.start(排除 FR10)"""
    # 首选 wmi(与 FR10 inject.py 同路), 失败退 PowerShell CIM
    try:
        import wmi  # noqa
        c = wmi.WMI()
        for p in c.Win32_Process():
            cl = str(p.CommandLine or "")
            if "FineReport_11.0" in cl and "com.fr.start" in cl and p.ProcessId != os.getpid():
                return p.ProcessId
    except ImportError:
        pass
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | "
             "Where-Object {$_.CommandLine -like '*FineReport_11.0*' -and $_.CommandLine -like '*com.fr.start*'} | "
             "Select-Object -ExpandProperty ProcessId"],
            text=True, timeout=15)
        for line in out.split():
            try:
                return int(line)
            except ValueError:
                continue
    except Exception:
        pass
    return None


def wait_designer_ready(timeout=180):
    """--start 模式: 拉起设计器并等 java 进程出现 + GUI 初始化"""
    print(f"[1/4] 拉起 FR11 设计器: {FR11_DESIGNER_BAT}")
    subprocess.Popen(["cmd", "/c", "start", "/min", "", FR11_DESIGNER_BAT],
                     cwd=os.path.dirname(FR11_DESIGNER_BAT))
    t0 = time.time()
    while time.time() - t0 < timeout:
        pid = find_fr11_pid()
        if pid:
            print(f"      设计器进程就绪 PID={pid}, 再等 25s GUI 初始化...")
            time.sleep(25)
            return pid
        time.sleep(3)
    return None


def attach(pid, port_base=None):
    """用 FR11 自带 JRE + 自带 tools.jar 跑 Attacher，注入时传入端口配置"""
    if not os.path.exists(FR11_JAVA):
        print(f"[FAIL] 找不到 FR11 JRE: {FR11_JAVA}"); sys.exit(2)
    if not os.path.exists(FR11_TOOLS):
        print(f"[FAIL] FR11 JRE 缺 tools.jar: {FR11_TOOLS}"); sys.exit(2)
    if not os.path.exists(AGENT_JAR):
        print(f"[FAIL] 找不到 {AGENT_JAR} (先跑 fr-agent/build.cmd)"); sys.exit(2)

    urls = get_urls(port_base)
    # 通过 agent_args 传入端口系统属性，Attacher 会将其作为参数传给目标 JVM
    agent_args = f"-Dfr.agent.http.port={urls['http_port']} -Dfr.agent.exec.port={urls['exec_port']}"
    print(f"[3/4] attach: {FR11_JAVA} -cp .;tools.jar Attacher {pid} fr-agent.jar {agent_args}")
    r = subprocess.run([FR11_JAVA, "-cp", f".;{FR11_TOOLS}", "Attacher", str(pid), AGENT_JAR, agent_args],
                       cwd=os.path.dirname(os.path.abspath(__file__)),
                       capture_output=True, text=True, timeout=60)
    out = (r.stdout or "") + (r.stderr or "")
    if out.strip():
        print("      " + out.strip().replace("\n", "\n      "))
    return r.returncode == 0


def verify(port_base=None):
    urls = get_urls(port_base)
    print(f"[4/4] 验证 agent 端口 (HTTP:{urls['http_port']}, Exec:{urls['exec_port']})...")
    ok = False
    for i in range(10):
        try:
            p = http_json(urls["ping_http"])
            print(f"      ✅ {urls['http_port']} /ping: {json.dumps(p, ensure_ascii=False)}")
            ok = True
            break
        except Exception:
            time.sleep(1.5)
    if not ok:
        print(f"      ❌ {urls['http_port']} 未响应(attach 可能失败, 看设计器控制台/重启设计器重试)")
        return False
    try:
        time.sleep(1)
        print(f"      ✅ {urls['exec_port']} /ping: {json.dumps(http_json(urls['ping_exec']), ensure_ascii=False)}")
    except Exception as e:
        print(f"      ⚠ {urls['exec_port']} 未响应: {e}")
    return True


def run_exec(script, port_base=None):
    urls = get_urls(port_base)
    body = json.dumps({"script": script}).encode("utf-8")
    req = urllib.request.Request(urls["exec"], data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        print(json.dumps(json.loads(r.read().decode("utf-8")), ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description="FR11 fr-agent 注入探针")
    ap.add_argument("--start", action="store_true", help="设计器未启动时先拉起 designer.bat")
    ap.add_argument("--pid", type=int, default=None, help="手动指定 FR11 设计器 PID")
    ap.add_argument("--exec", dest="js", default=None, help="注入后跑一段 Nashorn 脚本")
    ap.add_argument("--port-base", type=int, default=None, help="端口基数 (默认 19100,避开 FR10 的 18999/19000)")
    args = ap.parse_args()

    port_base = args.port_base
    urls = get_urls(port_base)

    alive = agent_alive(port_base)
    if alive:
        print(f"✅ agent 已在运行(无需重复注入): {json.dumps(alive, ensure_ascii=False)}")
        if args.js:
            run_exec(args.js, port_base)
        return 0

    pid = args.pid
    if pid is None:
        print("[2/4] 定位 FR11 设计器进程...")
        pid = find_fr11_pid()
        if pid is None and args.start:
            pid = wait_designer_ready()
    if pid is None:
        print("[FAIL] 未找到 FR11 设计器进程。先启动 C:\\FineReport_11.0\\bin\\designer.bat 或加 --start")
        return 1
    print(f"      FR11 PID = {pid}")

    if not attach(pid, port_base):
        return 1
    if not verify(port_base):
        return 1
    print(f"🎉 FR11 注入完成: 事件流 http://localhost:{urls['http_port']}/events | 脚本执行 POST http://localhost:{urls['exec_port']}/exec")
    if args.js:
        run_exec(args.js, port_base)
    return 0


if __name__ == "__main__":
    sys.exit(main())
