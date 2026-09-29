#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebKit 页面体检 — 坏页夹具验收驱动（只依赖 probe.py 的 CLI 约定，不碰其内部）
==============================================================================
证明 probe.py 能抓到 guardrails / fr_check 静态闸拦不住的两类坏页:
  1) bad_runtime_sql  运行期数据集错误(查询不存在的表) → 期待 error 级 finding 且 check 含 runtime
  2) bad_overlap      参数面板控件重叠(两 ComboBox/两 Label 完全同位) → 期待 error 级
                      finding(message 含"重叠/overlap" 或 check 含 widgets/overlap)

流程: 部署(加 WKTEST_ 前缀, 部署前查重防覆盖) → 逐夹具子进程跑 probe → 断言 → finally 清理
退出码: 0=两坏页都被抓 / 1=有未抓 / 3=部署目标已存在同名文件(环境问题) / 4=probe.py 未就绪
运行: C:/Users/<你的用户名>/AppData/Local/Programs/Python/Python311/python.exe -X utf8 web_kit/tests/run_acceptance.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

PY = sys.executable
TESTS_DIR = Path(__file__).resolve().parent
WEB_KIT_DIR = TESTS_DIR.parent
REPO_DIR = WEB_KIT_DIR.parent
PROBE = WEB_KIT_DIR / "probe.py"
DEPLOY_DIR = Path(os.environ.get("FR_REPORTLETS",
                                 r"C:/Program Files/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/示例报表工程/明细报表"))
PREFIX = "WKTEST_"
PROBE_TIMEOUT = 240  # 秒

# (夹具文件名, 期待的检测维度, 判定规则人话版)
FIXTURES = [
    ("bad_runtime_sql.cpt", "runtime",
     "error级finding>=1 且 check含runtime(或message命中数据集错误/加载失败)"),
    ("bad_overlap.cpt", "widgets",
     'error级finding 且(message含"重叠/overlap" 或 check含widgets/overlap)'),
]

ProcResult = namedtuple("ProcResult", "returncode stdout stderr")

SEV_KEYS = ("severity", "level", "sev")
CHECK_KEYS = ("check", "checker", "type", "rule", "category")
MSG_KEYS = ("message", "msg", "desc", "detail", "text")


def _first(d, keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, (str, int)):
            return str(v)
    return ""


def walk_findings(obj):
    """在任意形状的 JSON 里递归收集'像 finding 的 dict'(含 severity/level 且含 check/message)。"""
    out = []
    if isinstance(obj, dict):
        if any(k in obj for k in SEV_KEYS) and any(k in obj for k in CHECK_KEYS + MSG_KEYS):
            out.append(obj)
        else:
            for v in obj.values():
                out.extend(walk_findings(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(walk_findings(v))
    return out


def _is_error(f):
    sev = _first(f, SEV_KEYS).strip().lower()
    return sev in ("e", "err", "error", "fatal", "critical")


def load_findings(proc):
    """读 probe 结果: stdout 直接/内嵌 JSON → _runs/webprobe/ 下最新 *.json 兜底。
    返回 (findings列表, 来源说明)。"""
    texts = []
    stdout = (proc.stdout or "").strip()
    if stdout:
        texts.append(stdout)
        m = re.search(r"[\[{].*[\]}]", stdout, re.S)
        if m:
            texts.append(m.group(0))
    best = ([], "none")
    for i, text in enumerate(texts):
        try:
            data = json.loads(text)
        except (ValueError, TypeError):
            continue
        f = walk_findings(data)
        if f:
            return f, "stdout-json"
        if best[0:2] == ([], "none"):
            best = ([], "stdout-json(无finding)")
    base = REPO_DIR / "_runs" / "webprobe"
    if base.is_dir():
        jsons = sorted(base.glob("*/*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        for p in jsons:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            f = walk_findings(data)
            if f:
                return f, "file:" + str(p.relative_to(REPO_DIR))
    return best


def judge(expect, findings, stdout, rc):
    """返回 (是否按预期被抓, 证据摘要)。匹配刻意宽松，细则见 tests/README.md。"""
    err_findings = [f for f in findings if _is_error(f)]

    def hit_runtime(f):
        blob = (_first(f, CHECK_KEYS) + " " + _first(f, MSG_KEYS)).lower()
        kw = _first(f, MSG_KEYS)
        return "runtime" in blob or any(k in kw for k in ("数据集", "加载失败", "Exception", "错误弹窗"))

    def hit_overlap(f):
        blob = (_first(f, CHECK_KEYS) + " " + _first(f, MSG_KEYS)).lower()
        return "重叠" in blob or "overlap" in blob or "widgets" in _first(f, CHECK_KEYS).lower()

    hits = [f for f in err_findings if (hit_runtime if expect == "runtime" else hit_overlap)(f)]
    if hits:
        f = hits[0]
        ev = "[%s][%s] %s" % (_first(f, SEV_KEYS), _first(f, CHECK_KEYS) or "-",
                              _first(f, MSG_KEYS) or "-")
        return True, ev[:90]

    # JSON 没读到 finding 时的文本兜底: 靠 stdout 关键词
    text = stdout or ""
    if expect == "runtime":
        loose = (re.search(r"(?is)(error|错误|exception)[^\n]{0,80}(runtime|数据集|加载失败)", text)
                 or re.search(r"(?is)runtime[^\n]{0,80}(error|错误|exception|数据集|加载失败)", text))
        if rc == 1 and loose:
            return True, "stdout关键词命中(rc=1): " + loose.group(0)[:80]
    else:
        m = re.search(r"(?is)(重叠|overlap)", text)
        if m:
            return True, "stdout关键词命中: " + m.group(0)
    if findings:
        f = findings[0]
        return False, "未命中期待维度(最近finding): [%s][%s] %s" % (
            _first(f, SEV_KEYS) or "-", _first(f, CHECK_KEYS) or "-",
            (_first(f, MSG_KEYS) or "-")[:60])
    return False, "未获得任何 finding(JSON/落盘报告均无)"


def run_probe(cpt_path):
    cmd = [PY, "-X", "utf8", str(PROBE), str(cpt_path)]
    print("[probe] %s" % " ".join(cmd))
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=PROBE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return ProcResult(124, "[probe 超时 %ds]" % PROBE_TIMEOUT, "")
    except OSError as e:
        return ProcResult(127, "[probe 启动失败] %s" % e, "")


def print_table(rows):
    print()
    print("═" * 78)
    print("WebKit 体检验收结论表")
    print("─" * 78)
    print("%-28s %-6s %-8s %-34s %s" % ("夹具", "期待", "判定", "证据", "probe_rc"))
    print("─" * 78)
    for name, expect, ok, ev, rc, _src in rows:
        print("%-28s %-6s %-8s %-34s %s" % (name, expect, "CAUGHT" if ok else "MISS",
                                            ev.replace("\n", " ")[:34], rc))
    print("═" * 78)


def main():
    if not PROBE.exists():
        print("[NOT-READY] 未找到 %s" % PROBE)
        print("等待核心分支集成后重跑")
        return 4
    for name, _, _ in FIXTURES:
        if not (TESTS_DIR / name).exists():
            print("[FAIL] 缺少夹具: %s" % (TESTS_DIR / name))
            return 1
    plan = []
    for name, _, _ in FIXTURES:  # 部署前统一查重, 防覆盖人工文件
        dst = DEPLOY_DIR / (PREFIX + name)
        if dst.exists():
            print("[ABORT] 部署目标已存在, 拒绝覆盖: %s" % dst)
            print("请人工确认并清理遗留 WKTEST_*.cpt 后重跑。")
            return 3
        plan.append((TESTS_DIR / name, dst))

    deployed = []
    try:
        DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
        for src, dst in plan:
            shutil.copy2(src, dst)
            deployed.append(dst)
            print("[部署] %s" % dst)

        rows, any_miss = [], False
        for (src, dst), (name, expect, rule) in zip(plan, FIXTURES):
            print("[断言] %s → %s" % (name, rule))
            proc = run_probe(dst)
            findings, source = load_findings(proc)
            ok, ev = judge(expect, findings, proc.stdout or "", proc.returncode)
            any_miss |= not ok
            rows.append((PREFIX + name, expect, ok, ev, proc.returncode, source))
            if findings:
                print("       findings=%d (来源 %s)" % (len(findings), source))
        print_table(rows)
        print("验收结论: %s" % ("PASS 两坏页均被抓" if not any_miss else "FAIL 有坏页未被抓"))
        return 1 if any_miss else 0
    finally:  # 清理铁律: 无论成败都删部署件
        for dst in deployed:
            try:
                dst.unlink()
                print("[清理] 已删除 %s" % dst)
            except OSError as e:
                print("[清理失败] %s: %s  ← 请手动删除!" % (dst, e))


if __name__ == "__main__":
    sys.exit(main())
