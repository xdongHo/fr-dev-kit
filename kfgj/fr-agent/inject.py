# FR Agent 一键注入脚本（FR10）
import subprocess, sys, time, os
import urllib.request, json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fzpy"))
import userdir

# FR/JDK 定位：~/.fr_dev_kit/fr_env.toml > 环境变量 > 常见位置扫描（userdir.resolve_*）
_fr = userdir.resolve_fr_home()
_jdk = userdir.resolve_jdk_home()
FR_HOME = str(_fr) if _fr else r"C:\Program Files\FineReport_10.0"
JDK_HOME = str(_jdk) if _jdk else r"C:\Program Files\Java\jdk1.8.0_XXX"
AGENT_JAR = os.path.join(os.path.dirname(__file__), "fr-agent.jar")

# FR10 默认端口（可通过 --port-base 或环境变量覆盖）
DEFAULT_PORT_BASE = 18999


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
        "status": f"http://localhost:{http_port}/status",
        "http_port": http_port,
        "exec_port": exec_port,
    }


def find_fr_pid():
    """定位 FR10 Designer 主进程 PID。

    坑(2026-08-28 实测): 本机常有多个 java 进程同时带 'FineReport' 字样 ——
      * designer.bat 的 wrapper 进程 (绝对路径 ...\\FineReport_10.0\\jre\\bin\\java.exe)
      * AI Copilot 插件子进程 (-cp ...plugin-com.fr.plugin.aicopilot...)
      * Designer 主进程本体 —— 但它用**相对路径** .\\jre\\bin\\java 启动,
        CommandLine 里**不含** 'FineReport' 字样!
    因此「CommandLine 含 FineReport」会稳定命中错误的进程(插件/wrapper),
    必须用主窗口标题判定: 'FineReport <ver> release ... @<工作目录> mem://XXX'。
    不确定时请用 --pid 手动指定。
    """
    # 1) 主窗口标题匹配 —— 唯一可靠判据
    #    用 Get-Process 全量再过滤 ProcessName, 避免 `Get-Process java,javaw`
    #    在 javaw 不存在时报错导致 PowerShell 退出码非 0。
    ps_cmd = (
        "Get-Process -ErrorAction SilentlyContinue | "
        "Where-Object { $_.ProcessName -match '^javaw?$' "
        "-and $_.MainWindowTitle -match 'FineReport.*@' } | "
        "Select-Object -First 1 -ExpandProperty Id"
    )
    try:
        # 不用 check_output: PowerShell 退出码可能为 1(部分进程查不到),
        # 但 stdout 仍然有效; check_output 会因此抛 CalledProcessError。
        # errors="replace": 中文 GBK 代码页下输出可能夹带非 UTF-8 字节。
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, timeout=30,
        )
        raw = (res.stdout or b"").decode("utf-8", errors="replace").strip()
        digits = "".join(ch for ch in raw.splitlines()[0] if ch.isdigit()) if raw else ""
        if digits:
            return int(digits)
    except Exception:
        pass

    # 2) wmi: CommandLine 含 FineReport 但排除插件子进程
    try:
        import wmi
        c = wmi.WMI()
        for p in c.Win32_Process():
            cl = str(p.CommandLine or "")
            if "FineReport" in cl and "aicopilot" not in cl:
                return p.ProcessId
    except Exception:
        pass

    # 3) 最后回退到 tasklist(旧行为,可能拿到错误进程,仅保底)
    #    errors="replace": tasklist 在中文系统输出 GBK 表头("映像名称"等),
    #    严格 UTF-8 解码会抛 UnicodeDecodeError。
    out = subprocess.check_output(
        ['tasklist', '/fi', 'IMAGENAME eq java.exe', '/fo', 'csv'],
        text=True, errors="replace",
    )
    lines = [l for l in out.split('\n') if 'java' in l]
    if lines:
        return int(lines[-1].split(',')[1].strip('"'))
    return None


def attach(pid, port_base=None):
    """注入 agent 到目标 JVM"""
    java = f"{JDK_HOME}\\bin\\java.exe"
    tools = f"{JDK_HOME}\\lib\\tools.jar"

    urls = get_urls(port_base)
    agent_args = f"-Dfr.agent.http.port={urls['http_port']} -Dfr.agent.exec.port={urls['exec_port']}"

    print(f"Attaching with port config: {agent_args}")
    subprocess.run([java, "-cp", f".;{tools}", "Attacher", str(pid), AGENT_JAR, agent_args],
                   cwd=os.path.dirname(__file__))
    time.sleep(4)

    def _get_json(url, timeout=5):
        # 坑: urlopen() 返回 HTTPResponse, 必须先 .read() 再 json.loads(),
        # 直接 json.loads(resp) 会报 "must be str, bytes or bytearray, not HTTPResponse"
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))

    try:
        r = _get_json(urls["ping_http"])
        print(f"Agent injected: PID={r['pid']}")
        s = _get_json(urls["status"])
        print(f"Events: {s['events']}  Recording: {s['recording']}")
        if s.get("workbook"):
            print(f"Workbook: {s['workbook']}")
        return True
    except Exception as e:
        print(f"Agent check failed: {e}")
        return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="FR10 fr-agent 注入脚本")
    ap.add_argument("--pid", type=int, default=None, help="手动指定 FR10 设计器 PID")
    ap.add_argument("--port-base", type=int, default=None, help="端口基数 (默认 18999)")
    args = ap.parse_args()

    port_base = args.port_base
    urls = get_urls(port_base)

    pid = args.pid
    if pid is None:
        pid = find_fr_pid()
    if not pid:
        print("FR Designer not running. Start it first.")
        sys.exit(1)
    print(f"FR PID: {pid}")

    if not attach(pid, port_base):
        sys.exit(1)
