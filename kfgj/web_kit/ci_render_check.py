#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ci_render_check.py — 渲染对拍 CI 化：批量无头渲染断言 + 汇总矩阵（夜间作战 R60）。

配方来源（全部复用，不重造）:
  - 登录/会话/取数配方 = R13 无头配方A/B（ckzl/bb/外部依赖与归档声明.md渲染管线原理-20260905.md §三），
    实现在 _runs/night/R38/render_expect.py（RenderClient / parse_grid / check_cell），
    本脚本 import 复用；R38 缺失时退化用内置等价实现（同配方拷贝，标注 Fallback）。
  - viewlet 推导复用同目录 render_assert.derive_viewlet（web-inf/reportlets 绝对路径→viewlet）。

批量模式:
  清单文件（utf-8 文本，# 注释，空行跳过），每行最多 3 段用 | 分隔:
      viewlet或绝对cpt路径 [| k=v,k=v 参数] [| 断言表达式;分号分隔]
  断言表达式:
      rows==N / rows>=N / cols==N / cols>=N / tr>=N / tds>=N     页面级行列
      totalpage==N                                               总页数(配方B元数据)
      text*=关键词 / text~=正则                                   网格全文
      rRcC==文本 / rRcC*=包含 / rRcC!*=排除 / rRcC~=正则          关键格值(视觉坐标0起)
  也可以 --dir <目录> 递归扫 *.cpt 代替清单（配合 --limit 控制批量）。

每模板流程: 登录(一次) → op=view 建会话 → view_content(配方A) → 解析网格 → 断言
  → 网格为空且无引擎错误时 --recipe auto 再走配方B(默认分页会话 page_content)兜底
  → closesessionid 释放（R13 §四-3 会话池纪律）。模板间 sleep（默认 2s）限速。

范围说明: R13 配方实证载体为 cpt（view/report 栈）；清单中 .frm 记 SKIP 不渲染（见 R60 报告⑥）。

用法:
  python ci_render_check.py --list ci_manifest.txt [--out-dir DIR] [--host URL]
      [--sheet 0] [--recipe A|auto] [--sleep 2] [--limit N] [--quiet]
  python ci_render_check.py --dir <目录> [--limit N] ...
  python ci_render_check.py --selftest          # 离线自检（清单解析/断言引擎，零网络）

退出码: 0=全部 PASS  1=有断言 FAIL/引擎错误  2=执行错误（登录失败/清单不可读）
产物: <out-dir>/results.jsonl（逐模板） + summary.json + summary.md（汇总矩阵）
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
import importlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DEFAULT_HOST = "http://localhost:8075"
DEFAULT_USER = "admin"
DEFAULT_PWD = "admin"

# ---- 复用 R38 渲染断言引擎（登录/配方/网格解析/元素断言）--------------------
R38_DIR = os.path.join(ROOT, "_runs", "night", "R38")
_rx = None          # render_expect 模块（R38）
_FALLBACK_NOTE = None


def _load_render_expect():
    """优先 import R38 render_expect；失败时注入内置等价实现并标注。"""
    global _rx, _FALLBACK_NOTE
    if _rx is not None:
        return _rx
    try:
        if R38_DIR not in sys.path:
            sys.path.insert(0, R38_DIR)
        _rx = importlib.import_module("render_expect")
        return _rx
    except Exception as e:  # requests/yaml 缺失或文件缺失
        _FALLBACK_NOTE = "R38 render_expect import 失败(%s)，使用内置 Fallback 配方" % e
        sys.modules["ci_render_check_fallback"] = _build_fallback()
        _rx = sys.modules["ci_render_check_fallback"]
        return _rx


class _FallbackClient(object):
    """等价最小客户端（配方逐句拷贝自 R38 render_expect.RenderClient，零 yaml 依赖）。"""

    def __init__(self, host=DEFAULT_HOST, user=DEFAULT_USER, pwd=DEFAULT_PWD, timeout=120):
        import urllib.parse
        self._up = urllib.parse
        self.base = host.rstrip("/") + "/webroot/decision/view/report"
        self.host = host.rstrip("/")
        self.user, self.pwd, self.timeout = user, pwd, timeout
        import requests
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "Mozilla/5.0 ci_render_check/1.0"

    def login(self):
        u = self.host + "/webroot/decision/login/cross/domain?" + self._up.urlencode(
            {"fine_username": self.user, "fine_password": self.pwd,
             "validity": -1, "callback": "cb"})
        r = self.s.get(u, timeout=15)
        return bool(re.search(r'"accessToken"\s*:\s*"', r.text)) and r.status_code == 200

    def open_session(self, viewlet, params=None, op="view"):
        q = {"viewlet": viewlet}
        if op:
            q["op"] = op
        if params:
            q.update({k: "" if v is None else str(v) for k, v in params.items()})
        r = self.s.get(self.base + "?" + self._up.urlencode(q), timeout=self.timeout)
        m = re.search(r"sessionID=([0-9a-f-]{16,})", r.text)
        return (m.group(1) if m else None), r.text

    def view_content(self, sid, report_index=0, iid=None):
        r = self.s.post(self.base, data={"op": "fr_view", "cmd": "view_content",
                                         "sessionID": sid,
                                         "reportIndex": str(report_index),
                                         "iid": iid if iid else "%d.1" % report_index},
                        timeout=self.timeout)
        return r.text

    def page_content(self, sid, pn=1):
        r = self.s.post(self.base, data={"op": "page_content", "cmd": "html",
                                         "sessionID": sid, "pn": str(pn)},
                        timeout=self.timeout)
        return r.text

    def close(self, sid):
        try:
            self.s.get(self.base, params={"op": "closesessionid", "sessionID": sid},
                       timeout=15)
        except Exception:
            pass


def _build_fallback():
    """Fallback 模块：复用 R38 的网格解析/断言函数（直接拷贝实现，签名一致）。"""
    import html as htmllib
    import types
    from html.parser import HTMLParser

    class _P(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.tables, self._stack, self._tr, self._td = [], [], None, None

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "table":
                self._stack.append({"rows": []})
            elif tag == "tr" and self._stack:
                self._tr = {"cells": []}
                self._stack[-1]["rows"].append(self._tr)
            elif tag == "td" and self._tr is not None:
                self._td = {"text": [],
                            "rowspan": int(a.get("rowSpan", a.get("rowspan", 1)) or 1),
                            "colspan": int(a.get("colSpan", a.get("colspan", 1)) or 1)}

        def handle_startendtag(self, tag, attrs):
            if tag != "tr":
                self.handle_starttag(tag, attrs)
                self.handle_endtag(tag)

        def handle_data(self, d):
            if self._td is not None:
                self._td["text"].append(d)

        def handle_endtag(self, tag):
            if tag == "td" and self._td is not None:
                self._td["text"] = htmllib.unescape("".join(self._td["text"])).strip()
                self._tr["cells"].append(self._td)
                self._td = None
            elif tag == "tr":
                self._tr = None
            elif tag == "table" and self._stack:
                self.tables.append(self._stack.pop())

    def parse_tables(html_str):
        p = _P()
        try:
            p.feed(html_str)
            p.close()
        except Exception:
            pass
        return p.tables

    def table_to_matrix(table):
        occ, maxcol = {}, [0]
        for ri, tr in enumerate(table["rows"]):
            ci = 0
            for cell in tr["cells"]:
                while (ri, ci) in occ:
                    ci += 1
                for rr in range(ri, ri + cell["rowspan"]):
                    for cc in range(ci, ci + cell["colspan"]):
                        occ.setdefault((rr, cc), cell["text"])
                        maxcol[0] = max(maxcol[0], cc + 1)
                ci += cell["colspan"]
        if not occ:
            return [], {}
        nr = max(r for r, _ in occ) + 1
        nc = maxcol[0]
        return [[occ.get((r, c), "") for c in range(nc)] for r in range(nr)], {}

    def parse_grid(envelope_text):
        meta, html_str = {}, envelope_text
        try:
            env = json.loads(envelope_text)
            if isinstance(env, dict):
                html_str = env.get("html", "")
        except Exception:
            pass
        m = re.search(r"reportTotalPage=(\d+)", html_str, re.I)
        if m:
            meta["totalpage"] = int(m.group(1))
        tables = parse_tables(html_str)
        best, bmx = None, []
        for t in tables:
            mx, _ = table_to_matrix(t)
            if len(mx) * (len(mx[0]) if mx else 0) > len(bmx) * (len(bmx[0]) if bmx else 0):
                best, bmx = t, mx
        return bmx, {}, meta

    def check_cell(matrix, r, c, spec):
        loc = {"row": r, "col": c}
        if matrix is None:
            return "ERROR", {"actual": None, "why": "无网格", "locator": loc}
        if r < 0 or c < 0 or r >= len(matrix) or c >= len(matrix[0] if matrix else []):
            return "FAIL", {"actual": None,
                            "why": "坐标越界（网格 %dx%d）" % (len(matrix), len(matrix[0]) if matrix else 0),
                            "locator": loc}
        actual = matrix[r][c]
        d = {"actual": actual, "locator": loc}
        if "equals" in spec and str(actual).strip() != str(spec["equals"]).strip():
            return "FAIL", dict(d, why="equals %r" % spec["equals"])
        if "contains" in spec and str(spec["contains"]) not in str(actual):
            return "FAIL", dict(d, why="contains %r" % spec["contains"])
        if "not_contains" in spec and str(spec["not_contains"]) in str(actual):
            return "FAIL", dict(d, why="not_contains %r" % spec["not_contains"])
        if "regex" in spec and not re.search(spec["regex"], str(actual).strip()):
            return "FAIL", dict(d, why="regex /%s/" % spec["regex"])
        return "PASS", d

    mod = types.ModuleType("ci_render_check_fallback")
    mod.RenderClient = _FallbackClient
    mod.parse_grid = parse_grid
    mod.check_cell = check_cell
    mod.ERROR_MARKERS = ("错误代码", "11300001", "出错页面", "SessionID not exist",
                         "数据集配置错误")
    return mod


def _error_snippet(text):
    """从错误响应提取可读片段（优先复用 render_assert._engine_error_text，另做实体反解码）。"""
    if not text:
        return ""
    try:
        import html as _h
        import render_assert
        return _h.unescape(render_assert._engine_error_text(text))[:300]
    except Exception:
        seg = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", seg).strip()[:300]


def derive_viewlet(target):
    """绝对 cpt 路径 → viewlet（复用 web_kit/render_assert 规则）；已是 viewlet 原样返回。"""
    if re.match(r"^https?://", target, re.I) or target.replace("\\", "/").startswith("/"):
        return target.replace("\\", "/").lstrip("/")
    norm = os.path.abspath(target).replace("\\", "/")
    m = re.search(r"web-inf/reportlets/(.+\.cpt)$", norm, re.I)
    if m:
        return m.group(1)
    raise ValueError("cpt 不在 reportlets 下且不是 /viewlet 形式: %s" % target)


# ---------------------------------------------------------------- 清单解析
def parse_manifest(path):
    """清单 → [ {target, params, expects_raw} ]；# 注释/空行跳过。"""
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for ln, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            item = {"target": parts[0], "params": {}, "expects_raw": "", "line": ln}
            if len(parts) > 1 and parts[1]:
                for kv in parts[1].split(","):
                    k, _, v = kv.partition("=")
                    if k.strip():
                        item["params"][k.strip()] = v.strip()
            if len(parts) > 2:
                item["expects_raw"] = parts[2]
            items.append(item)
    return items


def scan_dir_manifest(root, limit=0):
    """--dir 模式：递归收集 cpt 生成隐式清单。"""
    items = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if fn.lower().endswith(".cpt"):
                items.append({"target": os.path.join(dirpath, fn), "params": {},
                              "expects_raw": "", "line": 0})
                if limit and len(items) >= limit:
                    return items
    return items


_CELL_RE = re.compile(r"^r(\d+)c(\d+)(==|\*=|!\*=|~=)(.+)$", re.S)


def parse_expects(expects_raw):
    """断言表达式 → {'cells': [...], 'page': [...]}；无法解析的记 raw_error。"""
    cells, page, bad = [], [], []
    for expr in (e.strip() for e in expects_raw.split(";")):
        if not expr:
            continue
        m = _CELL_RE.match(expr)
        if m:
            r, c, op, val = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
            spec = {"cell": "r%dc%d" % (r, c)}
            if op == "==":
                spec["equals"] = val
            elif op == "*=":
                spec["contains"] = val
            elif op == "!*=":
                spec["not_contains"] = val
            else:
                spec["regex"] = val
            cells.append(spec)
            continue
        pm = re.match(r"^(rows|cols)(==|>=)(\d+)$", expr)
        if pm:
            page.append(("page." + pm.group(1), pm.group(2), int(pm.group(3))))
            continue
        pm = re.match(r"^(tr|tds)>=(\d+)$", expr)
        if pm:
            page.append(("grid." + ("tr" if pm.group(1) == "tr" else "td"),
                         ">=", int(pm.group(2))))
            continue
        pm = re.match(r"^totalpage==(\d+)$", expr)
        if pm:
            page.append(("page.totalpage", "==", int(pm.group(1))))
            continue
        pm = re.match(r"^text\*=(.+)$", expr, re.S)
        if pm:
            page.append(("grid.text", "contains", pm.group(1)))
            continue
        pm = re.match(r"^text~=(.+)$", expr, re.S)
        if pm:
            page.append(("grid.text", "regex", pm.group(1)))
            continue
        bad.append(expr)
    return cells, page, bad


# ---------------------------------------------------------------- 批量执行
def run_batch(items, host=DEFAULT_HOST, user=DEFAULT_USER, pwd=DEFAULT_PWD,
              sheet=0, recipe="auto", sleep_s=2.0, out_dir=".", quiet=False,
              timeout=120, limit=0):
    rx = _load_render_expect()
    os.makedirs(out_dir, exist_ok=True)
    results_path = os.path.join(out_dir, "results.jsonl")
    cli = rx.RenderClient(host, user=user, pwd=pwd, timeout=timeout)
    t0 = time.time()
    if not cli.login():
        print("[ci_render_check] 登录失败: %s" % host)
        return 2, None
    if _FALLBACK_NOTE:
        print("[warn] %s" % _FALLBACK_NOTE)

    if limit:
        items = items[:limit]
    results = []
    n_fail = 0
    try:
        for i, item in enumerate(items, 1):
            rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                   "target": item["target"], "manifest_line": item.get("line", 0),
                   "params": item["params"], "engine": "R38" if not _FALLBACK_NOTE else "fallback"}
            t_t0 = time.time()
            try:
                viewlet = derive_viewlet(item["target"])
            except ValueError as e:
                rec.update(verdict="SKIP", why=str(e),
                           elapsed_s=round(time.time() - t_t0, 1))
                results.append(rec)
                _write_jsonl(results_path, [rec])
                if not quiet:
                    print("[%d/%d] SKIP %s (%s)" % (i, len(items), item["target"], rec["why"]))
                continue
            if viewlet.lower().endswith(".frm"):
                rec.update(viewlet=viewlet, verdict="SKIP",
                           why="frm 非本配方实证载体(见 R60 报告⑥-3)",
                           elapsed_s=round(time.time() - t_t0, 1))
                results.append(rec)
                _write_jsonl(results_path, [rec])
                if not quiet:
                    print("[%d/%d] SKIP %s (frm)" % (i, len(items), viewlet))
                continue

            rec["viewlet"] = viewlet
            cells_spec, page_spec, bad_spec = parse_expects(item["expects_raw"])
            if bad_spec:
                rec["expect_parse_errors"] = bad_spec
            asserts = []

            def add(name, ok, detail):
                asserts.append({"assert": name, "pass": bool(ok), "detail": str(detail)[:220]})

            sid = sid_b = None
            engine_error = None
            grid, meta, envelope, page_html = None, {}, "", ""
            try:
                sid, page_html = cli.open_session(viewlet, item["params"] or None, op="view")
                if not sid:
                    add("session", False, "op=view 会话创建失败（无 sessionID）")
                else:
                    envelope = cli.view_content(sid, sheet)
                    grid, _cef, meta = rx.parse_grid(envelope)
                    if grid is None and recipe == "auto":
                        # 配方A 无网格且无引擎错误 → 配方B 兜底（新开默认分页会话）
                        hit = [m for m in rx.ERROR_MARKERS if m in envelope]
                        if not hit:
                            sid_b, _ph = cli.open_session(viewlet, item["params"] or None, op=None)
                            if sid_b:
                                envelope_b = cli.page_content(sid_b, 1)
                                g2, _c2, m2 = rx.parse_grid(envelope_b)
                                if g2:
                                    grid, meta, envelope = g2, m2, envelope_b
                                    rec["recipe_used"] = "B"
                    rec.setdefault("recipe_used", "A")
            except Exception as e:
                engine_error = "%s: %s" % (type(e).__name__, str(e)[:200])
            finally:
                for s_ in (sid, sid_b):
                    if s_:
                        cli.close(s_)

            nrows = len(grid) if grid else 0
            ncols = len(grid[0]) if grid and grid[0] else 0
            rec["grid"] = {"rows": nrows, "cols": ncols,
                           "td": sum(len(r_) for r_ in grid) if grid else 0}
            rec["meta"] = {k: meta.get(k) for k in ("totalpage", "currentPageIndex")
                           if meta.get(k) is not None}

            # 断言1: 无引擎错误页（页面+信封+网格全文）
            hay = page_html + envelope + json.dumps(meta or {}, ensure_ascii=False)
            if grid:
                hay += "\n".join("\x01".join(r_) for r_ in grid)
            hit = [m for m in rx.ERROR_MARKERS if m in hay]
            if hit or engine_error:
                rec["engine_error_snippet"] = _error_snippet(envelope or page_html)
            add("no_error_page", not hit and not engine_error,
                engine_error or (hit or "干净"))
            # 断言2: 网格非空（行列数>0）
            add("grid_nonempty", bool(grid) and nrows >= 1 and ncols >= 1
                and rec["grid"]["td"] >= 1,
                "%d行×%d列 td=%d" % (nrows, ncols, rec["grid"]["td"]))
            # 断言3+: 页面级用户断言
            for name, op, want in page_spec:
                if name == "page.rows":
                    add(name, (nrows == want) if op == "==" else (nrows >= want),
                        "rows=%d" % nrows)
                elif name == "page.cols":
                    add(name, (ncols == want) if op == "==" else (ncols >= want),
                        "cols=%d" % ncols)
                elif name == "grid.tr":
                    add(name, nrows >= want, "tr=%d" % nrows)
                elif name == "grid.td":
                    add(name, rec["grid"]["td"] >= want, "td=%d" % rec["grid"]["td"])
                elif name == "page.totalpage":
                    add(name, meta.get("totalpage") == want,
                        "totalpage=%s" % meta.get("totalpage"))
                elif name == "grid.text":
                    text = re.sub(r"<[^>]+>", " ", envelope)
                    if op == "contains":
                        add(name, want in text, "关键词 %r" % want)
                    else:
                        add(name, bool(re.search(want, text)), "正则 /%s/" % want)
            # 断言4+: 关键格值
            for spec in cells_spec:
                r_, c_ = int(spec["cell"][1:spec["cell"].index("c")]), \
                    int(spec["cell"][spec["cell"].index("c") + 1:])
                status, detail = rx.check_cell(grid, r_, c_, spec)
                add("cell %s" % spec["cell"], status == "PASS",
                    detail.get("why") or "actual=%r" % detail.get("actual"))

            n_pass = sum(1 for a in asserts if a["pass"])
            rec["asserts"] = asserts
            rec["verdict"] = "PASS" if n_pass == len(asserts) and asserts else "FAIL"
            rec["elapsed_s"] = round(time.time() - t_t0, 1)
            if rec["verdict"] == "FAIL":
                n_fail += 1
            results.append(rec)
            _write_jsonl(results_path, [rec])
            if not quiet:
                bad = [a for a in asserts if not a["pass"]]
                line = "[%d/%d] %-4s %s  %d行×%d列 td=%d (%.1fs)" % (
                    i, len(items), rec["verdict"], viewlet, nrows, ncols,
                    rec["grid"]["td"], rec["elapsed_s"])
                if bad:
                    line += "  !! " + "; ".join("%s:%s" % (a["assert"], a["detail"][:60])
                                                for a in bad)
                print(line)
            if sleep_s and i < len(items):
                time.sleep(sleep_s)
    finally:
        summary = build_summary(results, host=host, elapsed=round(time.time() - t0, 1))
        with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
        with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
            f.write(render_summary_md(summary))
        if not quiet:
            print("=" * 72)
            for row in summary["matrix"]:
                print("  %-4s %-52s %s" % (row["verdict"], row["viewlet"][:52],
                                           "%d行×%d列 td=%d" % (row["rows"], row["cols"],
                                                               row["td"])))
            print("汇总: %d/%d PASS, %d FAIL, %d SKIP (引擎=%s, %.1fs)"
                  % (summary["pass"], summary["total"], summary["fail"],
                     summary["skip"], summary["engine"],
                     summary["elapsed_s"]))
            print("产物: %s" % os.path.abspath(out_dir))
    code = 2 if results is None else 0
    if n_fail:
        code = 1
    return code, summary


def build_summary(results, host="", elapsed=0):
    matrix = [{"viewlet": r.get("viewlet") or r.get("target", ""),
               "verdict": r["verdict"],
               "rows": (r.get("grid") or {}).get("rows", 0),
               "cols": (r.get("grid") or {}).get("cols", 0),
               "td": (r.get("grid") or {}).get("td", 0),
               "totalpage": (r.get("meta") or {}).get("totalpage"),
               "fail_asserts": [a["assert"] for a in (r.get("asserts") or []) if not a["pass"]],
               "why": r.get("why", "")} for r in results]
    return {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "host": host,
            "engine": "fallback" if _FALLBACK_NOTE else "R38.render_expect",
            "total": len(results),
            "pass": sum(1 for r in results if r["verdict"] == "PASS"),
            "fail": sum(1 for r in results if r["verdict"] == "FAIL"),
            "skip": sum(1 for r in results if r["verdict"] == "SKIP"),
            "elapsed_s": elapsed, "matrix": matrix}


def render_summary_md(summary):
    L = ["# ci_render_check 汇总矩阵", "",
         "- 时间: %s ｜ host: %s ｜ 引擎: %s" % (summary["ts"], summary["host"],
                                                summary["engine"]),
         "- 结论: **%d PASS / %d FAIL / %d SKIP**（共 %d，耗时 %.1fs）"
         % (summary["pass"], summary["fail"], summary["skip"], summary["total"],
            summary["elapsed_s"]),
         "",
         "| # | viewlet | 结论 | 网格 | td | totalpage | 未过断言 |",
         "|---|---------|------|------|----|-----------|----------|"]
    for i, r in enumerate(summary["matrix"], 1):
        L.append("| %d | %s | %s | %dx%d | %d | %s | %s |" % (
            i, r["viewlet"], r["verdict"], r["rows"], r["cols"], r["td"],
            r["totalpage"] if r["totalpage"] is not None else "-",
            "; ".join(r["fail_asserts"]) or (r["why"] if r["verdict"] == "SKIP" else "-")))
    return "\n".join(L) + "\n"


def _write_jsonl(path, records):
    with open(path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- selftest
def selftest():
    """离线自检：清单解析 / 断言解析 / 网格解析与元素断言（零网络）。"""
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        print("  [%s] %s %s" % ("x" if cond else "!", name, detail))
        ok = ok and cond

    mf = os.path.join(ROOT, "_runs", "night", "R60", "_selftest_manifest.txt")
    items = parse_manifest(mf)
    chk("manifest 行数", len(items) == 3, "got=%d" % len(items))
    chk("manifest 参数", items[0]["params"] == {"p_code": "PLH01", "para_year": "2026"},
        str(items[0]["params"]))
    cells, page, bad = parse_expects(items[0]["expects_raw"])
    chk("expect cells", len(cells) == 2 and cells[0]["cell"] == "r3c1"
        and cells[0].get("equals") == "上年YTD", str(cells))
    chk("expect page", ("page.rows", "==", 9) in [(a, b, c) for a, b, c in page], str(page))
    chk("expect 无坏表达式", not bad, str(bad))
    rx = _load_render_expect()
    chk("引擎来源", not _FALLBACK_NOTE, _FALLBACK_NOTE or "R38.render_expect")
    grid, _cef, meta = rx.parse_grid(
        '{"html":"<div><table><tr><td>A</td><td rowSpan=\\"2\\">B</td></tr>'
        '<tr><td>C</td></tr></table></div>","__x":1}')
    chk("parse_grid 展开rowSpan",
        grid == [["A", "B"], ["C", "B"]],
        "r1c1 应继承 rowSpan 的 B, got=%s" % (grid,))
    st, _d = rx.check_cell(grid, 0, 0, {"equals": "A"})
    chk("check_cell equals", st == "PASS")
    st, d = rx.check_cell(grid, 5, 0, {"equals": "A"})
    chk("check_cell 越界=FAIL", st == "FAIL", d.get("why", ""))
    print("SELFTEST: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="渲染对拍 CI 化批量无头断言（R60）")
    ap.add_argument("--list", default=None, help="清单文件（#注释, 每行 target|k=v,k=v|断言）")
    ap.add_argument("--dir", default=None, help="递归扫描目录下 *.cpt 代替清单")
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "_runs", "night", "R60", "ci"))
    ap.add_argument("--host", default=os.environ.get("FR_HOST", DEFAULT_HOST))
    ap.add_argument("--user", default=os.environ.get("FR_USER", DEFAULT_USER))
    ap.add_argument("--pwd", default=os.environ.get("FR_PASSWORD", DEFAULT_PWD))
    ap.add_argument("--sheet", type=int, default=0, help="reportIndex")
    ap.add_argument("--recipe", choices=["A", "auto"], default="auto",
                    help="A=仅配方A; auto=A无网格时配方B兜底")
    ap.add_argument("--sleep", type=float, default=2.0, help="模板间隔秒（限速纪律）")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="离线自检（零网络）")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.selftest:
        return selftest()
    if args.list:
        items = parse_manifest(args.list)
    elif args.dir:
        items = scan_dir_manifest(args.dir, limit=args.limit)
    else:
        ap.error("需要 --list <清单> 或 --dir <目录> 或 --selftest")
        return 2
    if not items:
        print("[ci_render_check] 清单为空")
        return 2
    code, _summary = run_batch(items, host=args.host, user=args.user, pwd=args.pwd,
                               sheet=args.sheet, recipe=args.recipe, sleep_s=args.sleep,
                               out_dir=args.out_dir, quiet=args.quiet,
                               timeout=args.timeout, limit=args.limit)
    return code


if __name__ == "__main__":
    sys.exit(main())
