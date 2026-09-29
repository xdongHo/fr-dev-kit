#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
log_feedback.py — FR 运行时日志 → 模板开发"预览"环节的反馈源（带预览时间窗筛选）。

把 fanruan.log 等运行日志中"预览时间段内"的会话/数据集/异常反馈提取出来，
作为 probe.py 页面体检报告的"运行期日志反馈"节（L-LOGFB 泳道交付）。

用法:
  CLI:
    python web_kit/log_feedback.py --template "示例预算表.cpt" \
        --start "2026-09-07 09:30:00" --end "2026-09-07 09:45:00" \
        [-o 报告.md] [--json out.json] [--sinks sinks.json] [--list-sinks]
  模块:
    from log_feedback import scan, probe_hook
    result = scan("示例预算表.cpt", start_dt, end_dt)
    probe_hook(out_dir, page_name, target, t_start)   # probe.py 收尾接线

日志汇(sinks): 缺省自动发现——已确认汇 fanruan.log(+同目录滚动 .gz 按需解压) +
候选 glob(WEB-INF/logs|log 等, 不存在自动跳过); --sinks 指定 sinks.json 可覆盖,
发现逻辑集中在 discover_sinks()/resolve_sinks(), R79 四路排查结果回填 sinks.json 即可。

时间窗: 行级时间戳解析, 兼容四种历史格式——
  ① [2026-09-07 09:38:56] 带日期方括号
  ② 2026-09-07 09:38:56 | 日期+时间管道
  ③ 09:38:56 裸时间(带/不带管道), 日期继承前文 (用户样例格式)
  ④ 2026/09/07 09:38:56 log4j 常规格式 (fanruan.log 当前格式)
  无时间戳的续行(SQL/堆栈)继承上一条目的时间与级别。

模板相关性三层:
  ① 行内含模板文件名/viewlet 路径  ② 行内含 ERROR/WARN/异常堆栈
  ③ 会话相关性(窗口内 Session closed/opened 的 uuid, 行含同 uuid)

退出码: 窗口内 ERROR=1, 仅 WARN/INFO=0。
大日志(10MB+)流式逐行处理(两遍流式: 一遍收会话 uuid, 一遍出命中), 不整读入内存。
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji/符号不再 UnicodeEncodeError) ---
try:
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass
# --- end guard ---
import argparse
import datetime as dt
import glob
import io
import json
import os
import re
import sys
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ── 日志汇配置（R79 四路排查回填：_runs/night/R79_logprobe/sinks.json）────
# 设计器汇路径在安装目录上一级（FineReport_10.0/..，LC 泳道 appender 反查确认）
DESIGNER_LOG = "C:/Program Files/logs/fanruan.log"
SERVER_LOG = "C:/Program Files/FineReport_10.0/logs/fanruan.log"
# 伪协议：设计器 JVM 内存缓冲（fr-agent 19000/exec 只读，LC_内存日志_报告.md）
DESIGNER_MEM_PREFIX = "designer-memory://"
DEFAULT_CONFIRMED = [
    DESIGNER_LOG,
    SERVER_LOG,
    "C:/Program Files/FineReport_10.0/bin/out.log",      # 上一会话 stdout 汇(85MB, 08:34 停)
    "C:/Program Files/FineReport_10.0/error.txt",        # 当前会话 stderr/JUL 汇(活跃,无时间戳)
    DESIGNER_MEM_PREFIX + "19000",
]
DEFAULT_GLOBS = [
    "C:/Program Files/logs/*.log",
    "C:/Program Files/FineReport_10.0/logs/*.log",
    "C:/Program Files/FineReport_10.0/webapps/webroot/WEB-INF/logs/*.log*",
    "C:/Program Files/FineReport_10.0/webapps/webroot/WEB-INF/log/*.log*",
    "C:/Program Files/FineReport_10.0/bin/logs/*.log*",
    os.path.join(os.path.expanduser("~"), ".FineReport10", "logs", "*.log*"),
    os.path.join(os.path.expanduser("~"), "AppData", "Local", "FineReport", "**", "*.log*"),
]

# ── 四种历史时间格式（借鉴 kfgj/watchdog.py TS_BRACKET/TS_PIPE_* + log4j 常规）────
_TS_BRACKET = re.compile(r"^\[(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\]")
_TS_DATEPIPE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})\s*\|")
_TS_LOG4J = re.compile(r"^(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}):(\d{2})\s")
_TS_PLAINDT = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})\s*$")  # 独立日期行(设计器面板)
_TS_BARE = re.compile(r"^(\d{2}):(\d{2}):(\d{2})(?:\s*\|\s*|\s+)")
# 设计器日志面板行前缀：正常:/错误:/警告: = FR 已算好的级别标签（LC 泳道确认）
_DGN_PREFIX = re.compile(r"^(正常|错误|警告)\s*:")
_DGN_SEV = {"正常": None, "错误": "error", "警告": "warn"}

_RX_ERR = re.compile(r"\b(ERROR|FATAL|SEVERE)\b")
_RX_WARN = re.compile(r"\b(WARN|WARNING)\b")
_RX_EXC = re.compile(r"\bCaused by:|\b\w+(Exception|Error)\b")
_RX_STACK = re.compile(r"^\s+(at\s|\.\.\.\s*\d+\s+more)")
_RX_SESS = re.compile(r"Session (?:closed|opened)|report session|sessionID", re.I)
_RX_UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                      r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
_RX_ROLL_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})\.gz$")

MAX_LINE_KEEP = 1000  # JSON/样例里单行最大保留字符


# ════════════════ 时间戳解析（四种格式 + 续行继承）════════════════

def parse_head_ts(line, cur_date):
    """行首时间戳解析。返回 (ts|None, 新 cur_date)。
    带日期的格式更新 cur_date；裸时间格式继承 cur_date；无匹配返回 (None, cur_date)。"""
    m = (_TS_BRACKET.match(line) or _TS_DATEPIPE.match(line)
         or _TS_LOG4J.match(line) or _TS_PLAINDT.match(line))
    if m:
        g = [int(x) for x in m.groups()]
        try:
            return dt.datetime(g[0], g[1], g[2], g[3], g[4], g[5]), dt.date(g[0], g[1], g[2])
        except ValueError:  # 非法日期(如 02:60)当普通行
            return None, cur_date
    m = _TS_BARE.match(line)
    if m and cur_date is not None:
        g = [int(x) for x in m.groups()]
        try:
            return (dt.datetime(cur_date.year, cur_date.month, cur_date.day,
                                g[0], g[1], g[2])), cur_date
        except ValueError:
            return None, cur_date
    return None, cur_date


def _head_sev(line):
    if _RX_ERR.search(line):
        return "error"
    if _RX_WARN.search(line):
        return "warn"
    if _RX_EXC.search(line):
        return "error"
    return "info"


def _stream(path):
    """按扩展名选择普通/gzip 流式打开（按需解压）。"""
    if path.lower().endswith(".gz"):
        import gzip
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return io.open(path, "r", encoding="utf-8", errors="replace")


def window_entries(src, start, end, force_ts=None):
    """流式产出窗口内的生效条目 (ts, is_head, sev, line)。
    src: 文件路径(普通/gz 流式) 或 行列表(设计器内存缓冲，体量有界可整取)。
    无时间戳续行继承上一条目的 ts 与 sev；设计器面板前缀(正常:/错误:/警告:)归一。
    force_ts: 无时间戳汇(error.txt 等 stderr/JUL)的整档归属时间戳(取 mtime)，
    非空时所有行视为该 ts 的独立条目（不再做行级解析/继承）。"""
    cur_date = None
    last_ts = None
    last_head_sev = "info"  # 仅 head 行更新；堆栈/异常续行按所属 head 定级
    fh = _stream(src) if isinstance(src, str) else src
    try:
        for raw in fh:
            line = raw.rstrip("\r\n")
            sev_hint = None
            mp = _DGN_PREFIX.match(line)
            if mp:
                sev_hint = _DGN_SEV.get(mp.group(1))
                line = line[mp.end():]
            if force_ts is not None:
                if not line.strip():
                    continue
                sev = sev_hint or _head_sev(line)
                if start <= force_ts <= end:
                    yield force_ts, True, sev, line
                continue
            ts, cur_date = parse_head_ts(line, cur_date)
            if ts is not None:
                last_ts = ts
                sev = sev_hint or _head_sev(line)
                last_head_sev = sev
                is_head = True
            else:
                ts, is_head = last_ts, False
                # 续行只在堆栈帧/异常名行继承 head 级别(SQL 等普通续行不虚增 ERROR 计数)
                if _RX_STACK.match(line) or _RX_EXC.search(line):
                    sev = last_head_sev if last_head_sev in ("error", "warn") else "info"
                else:
                    sev = "info"
            if ts is None or not (start <= ts <= end):
                continue
            yield ts, is_head, sev, line
    finally:
        if isinstance(src, str):
            fh.close()


UNDATED_GRACE_S = 300  # 无时间戳汇 mtime 落窗判定 ±5 分钟宽限


def undated_sink_ts(p, start, end):
    """无时间戳汇(error.txt 类 stderr/JUL)处理判定，返回 (mode, force_ts)：
    - ("normal", None): 采样行里存在可解析时间戳 → 正常行级窗口过滤
    - ("skip", None):   全档无时间戳且 mtime 不在窗口±宽限 → 本汇跳过(窗口外)
    - ("force", ts):    全档无时间戳且 mtime 落窗±宽限 → 整档以 mtime 归入窗口"""
    mtime = dt.datetime.fromtimestamp(os.path.getmtime(p))
    hit = False
    with _stream(p) as fh:
        for i, raw in enumerate(fh):
            if parse_head_ts(raw.rstrip("\r\n"), None)[0] is not None:
                hit = True
                break
            if i >= 2000:
                break
    if hit:
        return "normal", None
    lo = start - dt.timedelta(seconds=UNDATED_GRACE_S)
    hi = end + dt.timedelta(seconds=UNDATED_GRACE_S)
    if lo <= mtime <= hi:
        return "force", mtime
    return "skip", None


# ── designer-memory sink（fr-agent 19000/exec 只读，LC p8 脚本实证）────────

_DGN_SCRIPT = """
var H = java.lang.Class.forName('com.fr.design.mainframe.loghandler.DesignerLogHandler');
var gi = H.getDeclaredMethod('getInstance'); gi.setAccessible(true);
var inst = gi.invoke(null);
var fLogArea = H.getDeclaredField('logHandlerArea'); fLogArea.setAccessible(true);
var area = fLogArea.get(inst);
var fTA = area.getClass().getDeclaredField('jTextArea'); fTA.setAccessible(true);
var ta = fTA.get(area);
var doc = ta.getDocument();
doc.getText(0, doc.getLength());
"""


def fetch_designer_buffer(port=19000, timeout=5):
    """经 fr-agent /exec 只读取设计器内存日志缓冲全文（StyledDocument.getText）。
    返回行列表；agent 未注入/未启动抛异常（调用方按汇级错误记录，不中断扫描）。"""
    import urllib.request
    url = "http://localhost:%d/exec" % port
    req = urllib.request.Request(
        url, data=json.dumps({"script": _DGN_SCRIPT}).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.load(r)
    if resp.get("status") != "ok":
        raise RuntimeError("exec status=%s" % resp.get("status"))
    return str(resp.get("result") or "").split("\n")


# ════════════════ 日志汇发现（可扩展，R79 回填点）════════════════

def discover_sinks():
    """缺省自动发现：已确认汇 + 候选 glob。返回 (confirmed, globs)。"""
    return list(DEFAULT_CONFIRMED), list(DEFAULT_GLOBS)


def load_sinks(path):
    """读 sinks.json（{"confirmed":[路径|{path}], "candidates":[glob|{glob}]}），返回 (confirmed, globs)。"""
    with io.open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    def _vals(seq, key):
        out = []
        for x in seq or []:
            out.append(x[key] if isinstance(x, dict) else str(x))
        return out

    confirmed = [_abs(p) for p in _vals(data.get("confirmed"), "path")]
    globs = [_abs(g) for g in _vals(data.get("candidates") or data.get("globs"), "glob")]
    return confirmed, globs


def _abs(p):
    return p if os.path.isabs(p) else os.path.normpath(os.path.join(ROOT, p))


def resolve_sinks(confirmed, globs, start, end):
    """confirmed + glob → 实际存在的文件清单（去重，保序）。
    滚动归档 *.YYYY-MM-DD.gz 按需纳入：文件名日期落在窗口 ±1 天内才解压。"""
    lo = (start - dt.timedelta(days=1)).date()
    hi = (end + dt.timedelta(days=1)).date()
    files = []
    seen = set()

    def _add(p):
        if str(p).startswith(DESIGNER_MEM_PREFIX):
            if p not in seen:
                seen.add(p)
                files.append(p)  # 伪汇，扫描期经 fr-agent 校验
            return
        p = os.path.normpath(p)
        if p not in seen and os.path.isfile(p):
            seen.add(p)
            files.append(p)

    for base in confirmed:
        _add(base)
        for sib in glob.glob(base + ".*.gz") + glob.glob(base + ".*.log"):
            m = _RX_ROLL_DATE.search(sib)
            if m:
                try:
                    d = dt.datetime.strptime(m.group(1), "%Y-%m-%d").date()
                except ValueError:
                    continue
                if not (lo <= d <= hi):
                    continue
            _add(sib)
    for g in globs:
        for p in glob.glob(g, recursive=True):
            if p.lower().endswith(".gz"):
                m = _RX_ROLL_DATE.search(p)
                if m:
                    try:
                        d = dt.datetime.strptime(m.group(1), "%Y-%m-%d").date()
                    except ValueError:
                        continue
                    if not (lo <= d <= hi):
                        continue
            _add(p)
    return files


# ════════════════ 相关性扫描（两遍流式）════════════════

def _needles(template):
    """模板 → 匹配 needle 集：完整路径 / 文件名(带扩展) / 去扩展名。"""
    norm = str(template).replace("\\", "/").strip()
    base = os.path.basename(norm)
    out = []
    for n in (norm if "/" in norm else "", base):
        if n and len(n) >= 2 and n not in out:
            out.append(n)
    stem = base.rsplit(".", 1)[0] if "." in base else base
    if len(stem) >= 2 and stem not in out:
        out.append(stem)
    return out


def _sink_source(p):
    """汇路径 → 行来源：伪协议 designer-memory://端口 → 拉内存缓冲行列表；否则原样路径。"""
    if str(p).startswith(DESIGNER_MEM_PREFIX):
        port = int(str(p)[len(DESIGNER_MEM_PREFIX):] or 19000)
        return fetch_designer_buffer(port=port)
    return p


def _sink_error_entry(p, msg):
    """取源失败的汇占位记录（不中断整体扫描）。"""
    return {"path": p, "bytes": 0, "window_lines": 0, "hits": 0,
            "errors": 0, "warns": 0, "timeline": [], "samples": [],
            "hit_lines": [], "error": msg}


def scan(template, start, end, sinks=None, max_hits=5000, max_samples=8):
    """主扫描。sinks=None 自动发现；也可传 (confirmed, globs) 或 sinks.json 路径。"""
    if sinks is None:
        confirmed, globs = discover_sinks()
    elif isinstance(sinks, str):
        confirmed, globs = load_sinks(sinks)
    else:
        confirmed, globs = sinks
    files = resolve_sinks(confirmed, globs, start, end)
    needles = _needles(template)

    sessions = set()
    sources = {}  # path → 行来源（str 路径惰性流式 / list 内存缓冲 / None=取失败）
    forced = {}   # path → 无时间戳汇的整档 mtime 归属 ts
    per_pass1 = []
    for p in files:  # 第一遍：收窗口内会话 uuid
        try:
            fts = None
            if isinstance(p, str) and os.path.isfile(p) and not p.lower().endswith(".gz"):
                mode, fts = undated_sink_ts(p, start, end)
                if mode == "skip":
                    sources[p] = None
                    per_pass1.append((p, None,
                                      _sink_error_entry(
                                          p, "无时间戳且 mtime 不在窗口±%ds, 按窗口外跳过"
                                          % UNDATED_GRACE_S)))
                    continue
            src = _sink_source(p)
            sources[p] = src
            if fts is not None:
                forced[p] = fts
            n = 0
            for _ts, _h, _sev, line in window_entries(src, start, end, force_ts=fts):
                n += 1
                if _RX_SESS.search(line):
                    sessions.update(_RX_UUID.findall(line))
        except Exception as e:
            sources[p] = None
            per_pass1.append((p, None,
                              _sink_error_entry(p, "会话收集失败: %s" % str(e)[:120])))
            continue
        per_pass1.append((p, n))

    sink_reports = []
    total = {"window": 0, "hits": 0, "errors": 0, "warns": 0}
    truncated = False
    for item in per_pass1:  # 第二遍：出命中
        if len(item) == 3:  # 取源失败的汇（错误占位已带明细）
            sink_reports.append(item[2])
            continue
        p, n_win = item
        src = sources.get(p)
        fts = forced.get(p)
        hits = []
        n_hit = n_err = n_warn = 0
        timeline = {}
        try:
            for ts, _h, sev, line in window_entries(src, start, end, force_ts=fts):
                layers = []
                if any(nd in line for nd in needles):
                    layers.append("template")
                if sev == "error":
                    layers.append("severity")
                elif sev == "warn":
                    layers.append("severity")
                if sessions and any(u in line for u in sessions):
                    layers.append("session")
                if not layers:
                    continue
                n_hit += 1
                if sev == "error":
                    n_err += 1
                elif sev == "warn":
                    n_warn += 1
                key = ts.strftime("%H:%M")
                b = timeline.setdefault(key, [0, 0, 0])
                b[0] += 1
                if sev == "error":
                    b[1] += 1
                elif sev == "warn":
                    b[2] += 1
                if len(hits) < max_hits:
                    hits.append({"ts": ts.strftime("%Y-%m-%d %H:%M:%S"), "sev": sev,
                                 "layers": layers, "line": line[:MAX_LINE_KEEP],
                                 **({"undated": True} if fts is not None else {})})
                else:
                    truncated = True
        except Exception as e:
            sink_reports.append(_sink_error_entry(p, "扫描失败: %s" % str(e)[:120]))
            continue
        rep = {
            "path": p,
            "bytes": os.path.getsize(p) if isinstance(src, str) and os.path.exists(p) else 0,
            "window_lines": n_win, "hits": n_hit, "errors": n_err, "warns": n_warn,
            "timeline": [[k] + v for k, v in sorted(timeline.items())],
            "samples": _samples(hits, max_samples),
            "hit_lines": hits,
        }
        if fts is not None:
            rep["undated_mtime"] = fts.strftime("%Y-%m-%d %H:%M:%S")
            rep["note"] = "无时间戳汇(stderr/JUL), 整档按 mtime 归属窗口"
        sink_reports.append(rep)
        total["window"] += n_win
        total["hits"] += n_hit
        total["errors"] += n_err
        total["warns"] += n_warn

    return {
        "template": str(template),
        "start": start.strftime("%Y-%m-%d %H:%M:%S"),
        "end": end.strftime("%Y-%m-%d %H:%M:%S"),
        "sessions": sorted(sessions),
        "generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sinks": sink_reports,
        "total": dict(total, **{"truncated": truncated}),
        "exit_level": "error" if total["errors"] else "clean",
    }


def _samples(hits, cap):
    """样例：error 优先，其次 warn，再 info。"""
    pri = {"error": 0, "warn": 1, "info": 2}
    ranked = sorted(hits, key=lambda h: pri.get(h["sev"], 3))
    return ranked[:cap]


# ════════════════ 输出（md / json / probe 接线）════════════════

def render_md(result, heading="##"):
    L = ["%s 运行期日志反馈（log_feedback, 预览时间窗）" % heading,
         "",
         "- 模板: `%s` ｜ 窗口: %s ~ %s ｜ 生成: %s"
         % (result["template"], result["start"], result["end"], result["generated"]),
         "- 会话 uuid ×%d: %s" % (len(result["sessions"]),
                                  ", ".join(result["sessions"][:5]) or "-")]
    for s in result["sinks"]:
        L.append("- 汇 `%s` (%.1fMB): 窗口内 %d 行, 命中 %d 行 (ERROR %d / WARN %d)"
                 % (s["path"], s["bytes"] / 1048576.0, s["window_lines"],
                    s["hits"], s["errors"], s["warns"]))
        tl = " ".join("%s×%d(e%d,w%d)" % (t[0], t[1], t[2], t[3]) for t in s["timeline"][:24])
        if tl:
            L.append("  - 时间线: %s" % tl)
        if s["samples"]:
            L.append("  - 样例(原行, error 优先):")
            for h in s["samples"]:
                L.append("    - `%s`" % h["line"][:200].replace("`", "'"))
    t = result["total"]
    L.append("- 结论: %s（窗口内 ERROR %d, WARN %d；命中合计 %d/%d 行%s）"
             % ("存在 ERROR, 建议排查" if result["exit_level"] == "error" else "无 ERROR",
                t["errors"], t["warns"], t["hits"], t["window"],
                ", 超上限已截断" if t.get("truncated") else ""))
    return "\n".join(L)


def _fmt_arg(s, default=None):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def probe_hook(out_dir, page_name, target, t_start):
    """probe.py 接线：预览窗口 [t_start, now] 扫日志，追加报告节 + 落 json。
    返回摘要 dict（hits/errors/warns/window_lines）；任何失败由调用方兜底。"""
    template = target
    if re.match(r"^https?://", str(target or ""), re.I):
        try:
            q = parse_qs(urlparse(str(target)).query)
            template = os.path.basename((q.get("viewlet") or [""])[0]) or page_name
        except Exception:
            template = page_name
    else:
        template = os.path.basename(str(target).replace("\\", "/"))
    start = dt.datetime.fromtimestamp(t_start)
    end = dt.datetime.now()
    if end <= start:
        end = start + dt.timedelta(seconds=1)
    result = scan(template, start, end)
    md_path = os.path.join(out_dir, "report.md")
    with io.open(md_path, "a", encoding="utf-8") as f:
        f.write("\n\n" + render_md(result) + "\n")
    with io.open(os.path.join(out_dir, "log_feedback.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    t = result["total"]
    return {"hits": t["hits"], "errors": t["errors"], "warns": t["warns"],
            "window_lines": t["window"], "sinks": len(result["sinks"])}


# ════════════════ CLI ═════════════════

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="FR 运行日志 → 预览时间窗反馈")
    ap.add_argument("--template", required=True, help="模板文件名或 viewlet 路径")
    ap.add_argument("--start", required=True, help="窗口起 2026-09-07 09:30:00")
    ap.add_argument("--end", required=True, help="窗口止")
    ap.add_argument("-o", "--out", default="", help="md 报告输出路径")
    ap.add_argument("--json", dest="json_out", default="", help="JSON 输出路径")
    ap.add_argument("--sinks", default="", help="sinks.json（缺省自动发现）")
    ap.add_argument("--max-samples", type=int, default=8)
    ap.add_argument("--max-hits", type=int, default=5000)
    ap.add_argument("--list-sinks", action="store_true", help="只列解析后的日志汇清单")
    a = ap.parse_args()

    start, end = _fmt_arg(a.start), _fmt_arg(a.end)
    if end < start:
        print("[fail] --end 早于 --start")
        return 1
    if a.sinks:
        confirmed, globs = load_sinks(a.sinks)
    else:
        confirmed, globs = discover_sinks()
    files = resolve_sinks(confirmed, globs, start, end)
    if a.list_sinks:
        for p in files:
            print(p)
        return 0
    if not files:
        print("[log_feedback] 未发现可用日志汇（检查 sinks.json / 安装目录）")
        return 0

    result = scan(a.template, start, end, sinks=(confirmed, globs),
                  max_hits=a.max_hits, max_samples=a.max_samples)
    t = result["total"]
    print("[log_feedback] 模板: %s" % result["template"])
    print("[log_feedback] 窗口: %s ~ %s ｜ 日志汇 %d 个"
          % (result["start"], result["end"], len(result["sinks"])))
    for s in result["sinks"]:
        print("[log_feedback]   %s: 窗口内 %d 行, 命中 %d 行 (ERROR %d, WARN %d)"
              % (s["path"], s["window_lines"], s["hits"], s["errors"], s["warns"]))
        if s.get("error"):
            print("[log_feedback]     ⚠ %s" % s["error"])
        tl = " ".join("%s×%d(e%d,w%d)" % (x[0], x[1], x[2], x[3]) for x in s["timeline"][:24])
        if tl:
            print("[log_feedback] 时间线[%s]: %s" % (os.path.basename(s["path"]), tl))
        for h in s["samples"]:
            print("[log_feedback]   %s | %s | %s"
                  % (h["ts"], h["sev"].upper(), h["line"][:160]))
    print("[log_feedback] 会话 uuid ×%d" % len(result["sessions"]))
    if a.out:
        with io.open(a.out, "w", encoding="utf-8") as f:
            f.write(render_md(result, heading="#") + "\n")
        print("[log_feedback] md 报告: %s" % a.out)
    if a.json_out:
        with io.open(a.json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
        print("[log_feedback] json: %s" % a.json_out)
    if result["exit_level"] == "error":
        print("[log_feedback] 结论: 窗口内存在 ERROR %d 条 → rc=1" % t["errors"])
        return 1
    print("[log_feedback] 结论: 无 ERROR (WARN %d, 命中 %d 行) → rc=0" % (t["warns"], t["hits"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
