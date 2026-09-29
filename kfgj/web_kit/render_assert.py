#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
render_assert.py — 无头渲染对拍闸门（R28, 配方源自 R13 渲染管线考古 L3-04/T2-02/T2-03）。

纯 HTTP（零浏览器）完成 cpt 参数化渲染并断言网格行列/关键字段——
fr_check（静态）/ probe（浏览器体检）/ 本工具（服务端渲染真相）之外的第三验证档位，
可挂 dsl 验收链（编译产物先过 guardrails → 本工具 → 上线）。

核心配方（2026-09-04 双泳道实证）:
  会话:  GET  /webroot/decision/view/report?viewlet=<v>&op=view[&params]   ← op=view 选 ViewActor
         （默认无 op 会话是 page 分支: 渲染链死 + view_content ClassCast，禁止用于对拍）
  取数:  POST op=fr_view&cmd=view_content&sessionID=<sid>&reportIndex=0&iid=0.1
         → JSON 信封 {"html": "<div class=sheet-container><table class=x-table>..."}
  分页:  POST op=page_content&cmd=html&sessionID=<sid>&reportIndex=0&pn=<页码>   （配方B）
  参数:  默认走 GET query；--by-post 走 __parameters__=encodeURIComponent(JSON) 表单
         （复刻主表 ReportletHyperlink byPost=true 生产语义，POST-first 建会话）

用法:
  python web_kit/render_assert.py <cpt绝对路径|viewlet> [--params k=v ...]
      [--by-post] [--sheet 0] [--recipe A|B|both]
      [--expect-rows 1] [--expect-tds 1] [--expect-text 关键词1,关键词2]
      [--json-out PATH] [--timeout 60]

退出码: 0=PASS / 1=FAIL（断言不过或引擎错误）

示例（dsl 验收链挂载）:
  python web_kit/render_assert.py "dsl/build/示例预算表-科目下钻.cpt" \
      --params p_code=PL1100 p_name=营业收入 para_year=2026 para_month=SEP \
      --expect-rows 1 --expect-text 科目下钻
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
import json
import os
import re
import sys
import urllib.parse

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

FR_HOST = os.environ.get("FR_HOST", "http://localhost:8075")
FR_USER = os.environ.get("FR_USER", "admin")
FR_PWD = os.environ.get("FR_PASSWORD", "admin")

_ERR_MARKERS = ("出错页面", "错误代码", "11300001", "cannot be cast")


def derive_viewlet(cpt_path):
    norm = os.path.abspath(cpt_path).replace("\\", "/")
    m = re.search(r"web-inf/reportlets/(.+\.cpt)$", norm, re.I)
    if m:
        return m.group(1)
    raise SystemExit("[fail] cpt 不在 reportlets 目录下, 无法推导 viewlet: %s\n"
                     "       dsl/build 产物请先以 WKTEST_ 前缀部署到 reportlets 再对拍" % cpt_path)


def login(s, timeout):
    url = FR_HOST + "/webroot/decision/login/cross/domain?" + urllib.parse.urlencode(
        {"fine_username": FR_USER, "fine_password": FR_PWD, "validity": -1, "callback": "cb"})
    r = s.get(url, timeout=timeout)
    return bool(re.search(r'"accessToken"\s*:\s*"', r.text or ""))


def extract_sid(html):
    m = re.search(r"sessionID=([0-9a-f-]{16,})", html or "")
    return m.group(1) if m else None


def open_session(s, viewlet, params, by_post, timeout):
    """创建 op=view 分析会话。返回 (sid, http状态, 页面长度, 被踢登录?)。"""
    if by_post:
        # 生产 byPost 语义: encodeURIComponent(JSON) 双层编码 POST __parameters__, POST-first
        para = urllib.parse.quote(json.dumps(params or {}, ensure_ascii=False),
                                  safe="-_.!~*'()")
        url = FR_HOST + "/webroot/decision/view/report?" + urllib.parse.urlencode(
            {"viewlet": viewlet, "op": "view"})
        r = s.post(url, data={"__parameters__": para}, timeout=timeout)
    else:
        q = {"viewlet": viewlet, "op": "view"}
        q.update(params or {})
        url = FR_HOST + "/webroot/decision/view/report?" + urllib.parse.urlencode(q)
        r = s.get(url, timeout=timeout)
    kicked = ("/login" in r.url) or ("出错页面" in r.text and "sessionID" not in r.text)
    return extract_sid(r.text), r.status_code, len(r.text), kicked


def _unwrap(t):
    """view_content/page_content 响应: JSON 信封 {html: ...} 或裸 HTML。"""
    html = t
    try:
        env = json.loads(t)
        if isinstance(env, dict) and env.get("html"):
            html = env["html"]
    except Exception:
        pass
    return html


def _engine_error_text(t):
    """从错误响应提取可读片段: 优先定位异常细节标记(11300001/错误代码/cannot be cast),
    仅在缺失时退回 title 级"出错页面"——避免截到 <title> 而丢真正的异常正文。"""
    pos = -1
    for m in ("11300001", "错误代码", "cannot be cast", "Exception"):
        p = t.find(m)
        if p >= 0 and (pos < 0 or p < pos):
            pos = p
    if pos < 0:
        for m in _ERR_MARKERS:
            p = t.find(m)
            if p >= 0 and (pos < 0 or p < pos):
                pos = p
    seg = t[max(0, pos - 80): pos + 420] if pos >= 0 else t[:300]
    seg = re.sub(r"<[^>]+>", " ", seg)
    return re.sub(r"\s+", " ", seg).strip()[:300]


def fetch_view_content(s, sid, report_index, timeout):
    """配方A: 分析会话取渲染网格。返回 (grid dict 或 None, engine_error 或 None)。"""
    r = s.post(FR_HOST + "/webroot/decision/view/report", data={
        "op": "fr_view", "cmd": "view_content", "sessionID": sid,
        "reportIndex": str(report_index), "iid": "0.1"}, timeout=timeout)
    t = r.text or ""
    if any(m in t for m in _ERR_MARKERS):
        return None, _engine_error_text(t)
    html = _unwrap(t)
    if "x-table" not in html and "sheet-container" not in html:
        return None, None
    return summarize_grid(html), None


def fetch_page_content(s, sid, report_index, pn, timeout):
    """配方B: 分页会话取页内容（R13 Tier2: cmd=html + pn）。返回 (grid dict 或 None, engine_error 或 None)。"""
    r = s.post(FR_HOST + "/webroot/decision/view/report", data={
        "op": "page_content", "cmd": "html", "sessionID": sid,
        "reportIndex": str(report_index), "pn": str(pn)}, timeout=timeout)
    t = r.text or ""
    if any(m in t for m in _ERR_MARKERS):
        return None, _engine_error_text(t)
    html = _unwrap(t)
    if "x-table" not in html and "sheet-container" not in html:
        return None, None
    g = summarize_grid(html)
    m = re.search(r'"totalPage"\s*:\s*(\d+)', t)
    if m:
        g["total_page"] = int(m.group(1))
    return g, None


def summarize_grid(html):
    trs = len(re.findall(r"<tr[\s>]", html, re.I))
    tds = len(re.findall(r"<td[\s>]", html, re.I))
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return {"html_len": len(html), "tr": trs, "td": tds, "text_head": text[:400],
            "text": text}


def main():
    ap = argparse.ArgumentParser(description="无头渲染对拍闸门（R13 配方封装）")
    ap.add_argument("target", help="cpt 绝对路径 或 reportlets 相对 viewlet")
    ap.add_argument("--params", nargs="*", default=[], help="渲染参数 k=v（可多个）")
    ap.add_argument("--by-post", action="store_true",
                    help="参数走 __parameters__ POST 通道（byPost 生产语义, POST-first）")
    ap.add_argument("--sheet", type=int, default=0, help="reportIndex（多 sheet 模板选页）")
    ap.add_argument("--pn", type=int, default=1, help="配方B 页码")
    ap.add_argument("--recipe", choices=["A", "B", "both"], default="A",
                    help="A=view_content(分析) B=page_content(分页) both=两者")
    ap.add_argument("--expect-rows", type=int, default=1, help="网格最少 tr 数")
    ap.add_argument("--expect-tds", type=int, default=1, help="网格最少 td 数")
    ap.add_argument("--expect-text", default="", help="网格文本必须包含的关键词, 逗号分隔")
    ap.add_argument("--json-out", default="", help="结果 JSON 落盘路径")
    ap.add_argument("--timeout", type=int, default=60, help="单请求超时秒")
    args = ap.parse_args()

    target = args.target
    if re.match(r"^https?://", target, re.I):
        viewlet = urllib.parse.parse_qs(
            urllib.parse.urlparse(target).query).get("viewlet", [""])[0]
        if not viewlet:
            raise SystemExit("[fail] URL 目标需带 viewlet 查询参数")
    elif os.path.isfile(target):
        viewlet = derive_viewlet(target)
    else:
        viewlet = target.lstrip("/")

    params = {}
    for kv in args.params:
        k, _, v = kv.partition("=")
        params[k] = v

    expects = [t for t in (x.strip() for x in args.expect_text.split(",")) if t]
    s = requests.Session()
    s.headers["User-Agent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "webkit-render-assert/1.0")

    report = {"target": target, "viewlet": viewlet, "params": params,
              "by_post": args.by_post, "recipe": args.recipe,
              "host": FR_HOST, "asserts": [], "verdict": None}

    def assert_item(name, ok, detail):
        report["asserts"].append({"assert": name, "pass": bool(ok), "detail": detail})
        print("  [%s] %-14s %s" % ("x" if ok else "!", name, str(detail)[:150]))
        return bool(ok)

    print("[render_assert] %s (viewlet=%s, by_post=%s)" % (target, viewlet, args.by_post))
    ok = login(s, args.timeout)
    assert_item("login", ok, "JSONP accessToken %s" % ("取得" if ok else "缺失"))
    sid, st, plen, kicked = open_session(s, viewlet, params, args.by_post, args.timeout)
    report["session"] = {"sid": sid, "http": st, "page_len": plen, "login_kicked": kicked}
    assert_item("session", bool(sid) and not kicked,
                "sid=%s http=%d page_len=%d kicked=%s" % ((sid or "NONE")[:8], st, plen, kicked))

    grid = None
    engine_err = None
    if sid and not kicked:
        if args.recipe in ("A", "both"):
            g, e = fetch_view_content(s, sid, args.sheet, args.timeout)
            if g:
                grid = g
                report["recipe_A"] = g
            elif e:
                engine_err = engine_err or e
        if grid is None and args.recipe in ("B", "both"):
            g, e = fetch_page_content(s, sid, args.sheet, args.pn, args.timeout)
            if g:
                grid = g
                report["recipe_B"] = g
            elif e:
                engine_err = engine_err or e

    if engine_err:
        assert_item("engine_error", False, engine_err)
    if grid:
        report["grid"] = {k: grid[k] for k in ("html_len", "tr", "td", "text_head")}
        assert_item("grid_rows", grid["tr"] >= args.expect_rows,
                    "tr=%d (expect>=%d)" % (grid["tr"], args.expect_rows))
        assert_item("grid_tds", grid["td"] >= args.expect_tds,
                    "td=%d (expect>=%d)" % (grid["td"], args.expect_tds))
        missing = [t for t in expects if t not in grid.get("text", "")]
        if expects:
            assert_item("expect_text", not missing,
                        "全部命中" if not missing else "缺失: %s" % ",".join(missing))
    else:
        if not engine_err:
            assert_item("grid_rows", False, "两配方均未取得网格")
            assert_item("grid_tds", False, "-")
            assert_item("expect_text", False, "-")

    hard_fail = any((not a["pass"]) for a in report["asserts"])
    report["verdict"] = "FAIL" if hard_fail else "PASS"
    print("=" * 56)
    print("  render_assert 结论: %s" % report["verdict"])
    print("=" * 56)
    if args.json_out:
        out_dir = os.path.dirname(os.path.abspath(args.json_out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
        print("  结果: %s" % args.json_out)
    sys.exit(0 if report["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
