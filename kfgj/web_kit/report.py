# -*- coding: utf-8 -*-
"""
report.py — 体检报告落盘（full_page.png / report.md / result.json）与控制台摘要。

输出目录: <仓库根>/_runs/webprobe/<yyyyMMdd_HHmmss>_<页面名>/
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
import datetime
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_BASE = os.path.join(ROOT, "_runs", "webprobe")


def new_out_dir(page_name):
    """创建并返回本次体检的输出目录。"""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r'[\\/:*?"<>|\s]+', "_", page_name or "page").strip("_")[:60] or "page"
    d = os.path.join(OUT_BASE, "%s_%s" % (ts, safe))
    os.makedirs(d, exist_ok=True)
    return d


def screenshot(page, path):
    """全页截图；失败降级视口截图。返回实际路径或 None。"""
    try:
        page.screenshot(path=path, full_page=True)
        return path
    except Exception:
        try:
            page.screenshot(path=path)
            return path
        except Exception:
            return None


def _summary(findings):
    s = {"error": 0, "warn": 0, "info": 0}
    for f in findings:
        lvl = f.get("level", "info")
        s[lvl] = s.get(lvl, 0) + 1
    return s


def write(out_dir, page_name, url, findings, meta=None):
    """写 report.md + result.json，返回 (md_path, json_path)。"""
    meta = meta or {}
    s = _summary(findings)
    shot = os.path.join(out_dir, "full_page.png")

    # ---- result.json ----
    payload = {
        "page": page_name,
        "url": url,
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "summary": s,
        "meta": meta,
        "screenshot": shot if os.path.exists(shot) else None,
        "findings": findings,
    }
    json_path = os.path.join(out_dir, "result.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # ---- report.md ----
    lines = []
    lines.append("# WebKit 页面体检报告 — %s" % page_name)
    lines.append("")
    lines.append("- URL: %s" % url)
    lines.append("- 时间: %s" % payload["generated_at"])
    lines.append("- 结论: **%d error / %d warn / %d info**" % (s["error"], s["warn"], s["info"]))
    for k, v in meta.items():
        lines.append("- %s: %s" % (k, v))
    shot_rel = "full_page.png" if os.path.exists(shot) else "（截图失败）"
    lines.append("- 截图: %s" % shot_rel)
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    if findings:
        lines.append("| # | check | level | message | evidence | hint |")
        lines.append("|---|-------|-------|---------|----------|------|")
        for i, fd in enumerate(findings, 1):
            lines.append("| %d | %s | %s | %s | `%s` | %s |" % (
                i, fd.get("check", "?"), fd.get("level", "?"),
                str(fd.get("message", "")).replace("|", "\\|"),
                str(fd.get("evidence", ""))[:300].replace("|", "\\|"),
                str(fd.get("hint", "") or "").replace("|", "\\|")))
    else:
        lines.append("（无发现）")
    lines.append("")
    md_path = os.path.join(out_dir, "report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return md_path, json_path


def print_summary(page_name, findings, out_dir=None):
    """控制台同步打印摘要表。"""
    s = _summary(findings)
    print("")
    print("=" * 60)
    print("  体检摘要: %s" % page_name)
    print("  error=%d  warn=%d  info=%d" % (s["error"], s["warn"], s["info"]))
    print("-" * 60)
    for fd in findings:
        icon = {"error": "x", "warn": "!", "info": "-"}.get(fd.get("level"), "-")
        msg = str(fd.get("message", ""))[:70]
        ev = str(fd.get("evidence", ""))[:60].replace("\n", " ")
        print("  [%s] %-22s %s" % (icon, fd.get("check", "?"), msg))
        if ev:
            print("        evidence: %s" % ev)
    if out_dir:
        print("  报告目录: %s" % out_dir)
    print("=" * 60)


# ══════════════════ 批量矩阵汇总 ══════════════════

def write_matrix(rows, path, meta=None):
    """批量体检矩阵汇总（页 × 检测项）→ markdown。

    rows: run_batch 收集的每页结果 list[dict]（page/rc/summary/findings/...）。
    单元格 = 该页该检测项的最差级别（E/W/I，无发现为 -）。
    同时附 error 定性清单（message+evidence+hint，保证每个 error 可定性）。
    """
    meta = meta or {}
    checks = []
    for r in rows:
        for f in r.get("findings", []):
            c = f.get("check", "?")
            if c not in checks:
                checks.append(c)
    checks.sort()

    worst = {}  # (page, check) -> level rank
    rank = {"error": 3, "warn": 2, "info": 1}
    for r in rows:
        for f in r.get("findings", []):
            key = (r["page"], f.get("check", "?"))
            lv = f.get("level", "info")
            if rank.get(lv, 1) > rank.get(worst.get(key, ""), 0):
                worst[key] = lv

    def cell(page, check):
        lv = worst.get((page, check))
        if not lv:
            return "-"
        return {"error": "E", "warn": "W", "info": "I"}[lv]

    lines = []
    lines.append("# WebKit 批量体检矩阵")
    lines.append("")
    lines.append("- 目录: %s" % meta.get("dir", "-"))
    lines.append("- 页数: %d | 检测项: %d" % (len(rows), len(checks)))
    lines.append("- 选项: op=%s params=%s by_post=%s flags=%s" % (
        meta.get("op", "-") or "-", meta.get("params", "-"),
        meta.get("by_post"), ",".join(meta.get("flags", [])) or "-"))
    lines.append("- 时间: %s" % datetime.datetime.now().isoformat(timespec="seconds"))
    lines.append("- 单元格: E=error W=warn I=info -=无发现")
    lines.append("")

    # ---- 摘要表 ----
    lines.append("| 页面 | E | W | I | rc |")
    lines.append("|------|---|---|---|----|")
    for r in rows:
        s = r.get("summary", {})
        lines.append("| %s | %d | %d | %d | %d |" % (
            r["page"], s.get("error", 0), s.get("warn", 0), s.get("info", 0), r.get("rc", 0)))
    lines.append("")

    # ---- 页 × 检测项 矩阵 ----
    lines.append("## 页 × 检测项矩阵")
    lines.append("")
    lines.append("| 页面 | " + " | ".join(checks) + " |")
    lines.append("|------|" + "|".join(["---"] * len(checks)) + "|")
    for r in rows:
        lines.append("| %s | %s |" % (r["page"], " | ".join(cell(r["page"], c) for c in checks)))
    lines.append("")

    # ---- error 定性清单 ----
    lines.append("## Error 定性清单")
    lines.append("")
    n_err = 0
    for r in rows:
        for f in r.get("findings", []):
            if f.get("level") != "error":
                continue
            n_err += 1
            lines.append("### %s — %s" % (r["page"], f.get("check", "?")))
            lines.append("")
            lines.append("- message: %s" % f.get("message", ""))
            lines.append("- evidence: `%s`" % str(f.get("evidence", ""))[:280])
            hint = f.get("hint", "") or ""
            if hint:
                lines.append("- 定性hint: %s" % hint)
            lines.append("")
    if not n_err:
        lines.append("（无 error）")
        lines.append("")

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path
