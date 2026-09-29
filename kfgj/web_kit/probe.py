#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
probe.py — WebKit 页面快速体检 CLI（FineReport 10 报表运行期体检）。

用法:
  python probe.py <cpt绝对路径|完整URL> [--params k=v ...] [--op write]
                  [--layout] [--links] [--timeout 60] [--skip-login] [--by-post]
  python probe.py --batch <cpt目录> [--matrix-out matrix.md] [--jsonl-out results.jsonl] [同上选项]

行为:
  cpt 路径 → 自动推导 viewlet URL 并按候选格式链导航（404 自动降级，
  最终可用格式缓存到 ~/.fr_dev_kit/runs/webprobe/url_format.json，结论见 README）；
  被踢到登录页 → 用 JSONP 端点登录（fr_check 同款）→ storage_state 缓存复用；
  --by-post → 参数走 POST 表单通道（复刻 FR10 doHyperlinkByPost 生产语义:
  encodeURIComponent(JSON(para)) → 隐藏域 __parameters__ → form.submit()，
  同主表 cpt NameJavaScript ReportletHyperlink byPost=true 的传参通道），
  用于绕过 GET 注入被参数面板必填校验拦截的页面；
  --batch → 对目录内全部 cpt 逐页跑体检矩阵，输出 matrix.md（页×检测项）+
  results.jsonl（每行一页），供夜间批量体检消费；
  动态发现 checks/*.py（无 run 属性的纯库模块自动跳过）按文件名序执行；
  报告落 ~/.fr_dev_kit/runs/webprobe/<时间戳>_<页面名>/（用户目录）（full_page.png + report.md + result.json）。

退出码: 0=干净 / 2=仅 warn / 1=有 error（与 fr_check 对齐）
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
import importlib.util
import json
import os
import re
import sys
import time
from urllib.parse import quote, urlencode

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHECKS_DIR = os.path.join(HERE, "checks")


def _user_runs(*sub):
    """运行痕迹归用户目录（随人走不随套件走，2026-09-29 约定）；不可写时回退套件内 _runs"""
    base = os.path.join(os.path.expanduser("~"), ".fr_dev_kit", "runs")
    try:
        os.makedirs(os.path.join(base, *sub), exist_ok=True)
        return os.path.join(base, *sub)
    except Exception:
        return os.path.join(ROOT, "_runs", *sub)


RUNS_DIR = _user_runs("webprobe")
STATE_FILE = os.path.join(RUNS_DIR, "state.json")
FMT_CACHE = os.path.join(RUNS_DIR, "url_format.json")
BASELINE_FILE = os.path.join(HERE, "baseline.yaml")

sys.path.insert(0, HERE)

FR_HOST = os.environ.get("FR_HOST", "http://localhost:8075")
FR_USER = os.environ.get("FR_USER", "admin")
FR_PWD = os.environ.get("FR_PASSWORD", "admin")
FR_REPORTLETS = os.environ.get(
    "FR_REPORTLETS",
    r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets")

# 候选 URL 格式链（实测结论见 README；缓存命中的排最前）
# 2026-09-11 P1: 扩 .frm —— 决策报表走 decision/view/form 路由（ckzl/lc/06 实测记录），
# 候选链按扩展名分流: .frm → fr10_view_form；.cpt → 原三链不变
def _fmt_candidates(ext=".cpt"):
    if ext.lower() == ".frm":
        return [
            ("fr10_view_form", lambda v, q: "/webroot/decision/view/form?" + urlencode(q)),
        ]
    return [
        ("fr10_view_report", lambda v, q: "/webroot/decision/view/report?" + urlencode(q)),
        ("fr10_reportview", lambda v, q: "/webroot/decision/view/ReportView?" + urlencode(q)),
        ("legacy_webreport", lambda v, q: "/WebReport/ReportServer?" + urlencode(q)),
    ]


def derive_viewlet(path):
    """cpt/frm 绝对路径 → reportlets 相对 viewlet 路径（正斜杠）。推导失败返回 None。"""
    norm = os.path.abspath(path).replace("\\", "/")
    m = re.search(r"web-inf/reportlets/(.+\.(?:cpt|frm))$", norm, re.I)
    return m.group(1) if m else None


def page_name_of(target):
    if re.match(r"^https?://", target, re.I):
        tail = re.split(r"[?#]", target)[0].rstrip("/").rsplit("/", 1)[-1]
        return tail or "page"
    return os.path.splitext(os.path.basename(target))[0]


# ══════════════════ 事件采集（goto 前挂好）══════════════════

def attach_events(page, cap=300):
    ev = {"pageerrors": [], "console": [], "requestfailed": []}

    def on_pageerror(exc):
        if len(ev["pageerrors"]) < cap:
            # 2026-09-04 L7: 仅 message 无法定位 eval 内崩溃点(如模板控件 setTimeout
            # 内 this 丢失)，补 stack 供 checks/runtime.py 与矩阵定性使用
            stack = ""
            try:
                stack = str(getattr(exc, "stack", "") or "")
            except Exception:
                pass
            ev["pageerrors"].append({"error": str(exc), "stack": stack[:600]})

    def on_console(msg):
        if msg.type in ("error", "warning") and len(ev["console"]) < cap:
            loc = ""
            try:
                if msg.location:
                    loc = "%s:%s" % (msg.location.get("url", ""), msg.location.get("lineNumber", ""))
            except Exception:
                pass
            ev["console"].append({"type": msg.type, "text": msg.text, "location": loc})

    def on_reqfailed(req):
        if len(ev["requestfailed"]) < cap:
            failure = ""
            try:
                failure = req.failure or ""
            except Exception:
                pass
            ev["requestfailed"].append({"url": req.url, "failure": failure})

    page.on("pageerror", on_pageerror)
    page.on("console", on_console)
    page.on("requestfailed", on_reqfailed)
    return ev


# ══════════════════ 导航（候选格式链 + 登录 + by-post）══════════════════

def build_query(params, op, fmt):
    q = {}
    if op and fmt in ("fr10_view_report", "fr10_reportview"):
        q["op"] = op
    for kv in params or []:
        k, _, v = kv.partition("=")
        q[k] = v
    return q


# FR10 doHyperlinkByPost 生产语义（finereport.js 实测 2026-09-04）:
#   para = encodeURIComponent(FR.jsonEncode(para))
#   → <form method='post'><input type=hidden name='__parameters__' value=para></form>
#   → form.submit()
# 注: form 提交时浏览器再做一层 urlencoded 编码，与生产行为一致（双层编码，服务端解两层）
_BY_POST_JS = """
(cfg) => {
  const form = document.createElement('form');
  form.method = 'post';
  form.action = cfg.action;
  form.style.display = 'none';
  const input = document.createElement('input');
  input.type = 'hidden';
  input.name = '__parameters__';
  input.value = cfg.para;
  form.appendChild(input);
  document.body.appendChild(form);
  form.submit();
}
"""


def _post_para_value(params):
    """--params k=v 列表 → encodeURIComponent(JSON(para))（对齐 FR.jsonEncode+encodeURIComponent）。"""
    kv = {}
    for item in params or []:
        k, _, v = item.partition("=")
        kv[k] = v
    return quote(json.dumps(kv, ensure_ascii=False), safe="-_.!~*'()")


def _mount_server_grid(page, notes, timeout_s):
    """by-post/op=view 页面前端挂载链被模板 JS 缺陷打断时（pageerror 'reading form'），
    主动取服务端已渲染网格（view_content, 参数已种子化的会话）注入 DOM 供 checks 测量。
    返回 True 表示注入成功（页面此后含 .x-table 真实渲染网格）。"""
    js = """async () => {
      try {
        let sid = null;
        try {
          sid = (window.contentPane && contentPane.currentSessionID)
                ? String(contentPane.currentSessionID)
                : ((typeof _g === 'function' && _g() && (_g().currentSessionID || _g().sessionID))
                   ? String(_g().currentSessionID || _g().sessionID) : null);
        } catch(e) {}
        if (!sid) return {err: 'no-sid'};
        const servlet = (window.FR && FR.servletURL) || '/webroot/decision/view/report';
        const r = await fetch(servlet, {method: 'POST', credentials: 'include',
          headers: {'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'},
          body: new URLSearchParams({op: 'fr_view', cmd: 'view_content', sessionID: sid,
                                     reportIndex: '0', iid: '0.1'}).toString()});
        const t = await r.text();
        let html = t;
        try { const env = JSON.parse(t); if (env && env.html) html = env.html; } catch(e) {}
        if (!html || html.indexOf('x-table') < 0) return {err: 'no-grid', len: t.length,
                                                          marker: (t.indexOf('11300001') >= 0 ? 'dataset-error' : 'other')};
        const div = document.createElement('div');
        div.id = 'wktest-server-grid';
        div.style.position = 'absolute';
        div.style.top = '0';
        div.style.left = '0';
        div.style.background = '#fff';
        div.innerHTML = html;
        document.body.appendChild(div);
        return {ok: 1, len: html.length};
      } catch(e) { return {err: String(e).slice(0, 140)}; }
    }"""
    try:
        res = page.evaluate(js)
        if isinstance(res, dict) and res.get("ok"):
            notes.append("服务端网格已注入 DOM (html %dB): 前端挂载链被模板JS缺陷打断, "
                         "byPost 会话与服务端渲染均为真" % int(res.get("len") or 0))
            return True
        notes.append("服务端网格注入未成功: %s" % json.dumps(res, ensure_ascii=False)[:120])
    except Exception as e:
        notes.append("服务端网格注入异常: %s" % str(e)[:120])
    return False


def submit_by_post(page, context, action_url, params, timeout_s, skip_login, notes):
    """把 params 打进 __parameters__ 隐藏域后 POST 表单提交到 action_url。

    复刻主表 cpt NameJavaScript ReportletHyperlink byPost=true 的传参通道，
    用于绕过 GET 注入被参数面板必填校验拦截的页面。
    返回 (entry, final_url) 或 (None, err_msg)。
    """
    import kit_core
    cfg = {"action": action_url, "para": _post_para_value(params)}
    status = None
    try:
        with page.expect_navigation(wait_until="domcontentloaded",
                                    timeout=timeout_s * 1000) as nav:
            page.evaluate(_BY_POST_JS, cfg)
        resp = nav.value
        status = resp.status if resp is not None else None
    except Exception as e:
        return None, "by-post 表单提交失败: %s" % str(e)[:140]
    try:
        page.wait_for_load_state("load", timeout=timeout_s * 1000)
    except Exception:
        pass
    page.wait_for_timeout(1200)

    if kit_core.looks_like_login(page) and not skip_login:
        notes.append("by-post 提交后被踢到登录页，JSONP 登录后重提交")
        if kit_core.login_jsonp(context, FR_HOST, FR_USER, FR_PWD):
            try:
                context.storage_state(path=STATE_FILE)
            except Exception:
                pass
            try:
                page.goto(action_url, timeout=timeout_s * 1000, wait_until="domcontentloaded")
                page.wait_for_load_state("load", timeout=timeout_s * 1000)
            except Exception:
                pass
            try:
                with page.expect_navigation(wait_until="domcontentloaded",
                                            timeout=timeout_s * 1000) as nav:
                    page.evaluate(_BY_POST_JS, cfg)
                resp = nav.value
                status = resp.status if resp is not None else None
            except Exception as e:
                return None, "by-post 登录后重提交失败: %s" % str(e)[:140]
            try:
                page.wait_for_load_state("load", timeout=timeout_s * 1000)
            except Exception:
                pass
            page.wait_for_timeout(1200)

    entry = {
        "status": status,
        "final_url": page.url,
        "elapsed_ms": 0,
        "url_format": "bypost_form",
        "login_kicked": bool(kit_core.looks_like_login(page)),
        "by_post": True,
    }
    return entry, page.url


def navigate(page, context, target, op, params, timeout_s, skip_login, notes, by_post=False):
    """导航到目标页。返回 (entry_dict, final_url) 或 (None, err_msg)。

    by_post=True 时: 先按候选链走一遍无参 URL 建立会话/拿到可达 action，
    再把 params 经 POST 表单（__parameters__ 通道）提交导航。
    """
    post_params = None
    if by_post and params:
        post_params = params
        params = []  # 参数不再走 GET query

    is_url = bool(re.match(r"^https?://", target, re.I))
    if is_url:
        url = target
        if params:
            url += ("&" if "?" in url else "?") + urlencode(build_query(params, op, "direct"))
        entry, err = _goto_and_check(page, context, url, "direct", timeout_s, skip_login, notes)
        if entry is None:
            return None, err
        if post_params:
            pentry, perr = submit_by_post(page, context, page.url, post_params,
                                          timeout_s, skip_login, notes)
            if pentry is None:
                return None, perr
            return pentry, page.url
        return entry, page.url

    viewlet = derive_viewlet(target)
    if not viewlet:
        return None, "模板不在 reportlets 目录下，无法推导 viewlet: %s" % target

    ext = os.path.splitext(target)[1]
    fmts = _fmt_candidates(ext)
    try:
        with open(FMT_CACHE, "r", encoding="utf-8") as f:
            cached = json.load(f).get("format")
        if cached:
            fmts.sort(key=lambda x: 0 if x[0] == cached else 1)
    except Exception:
        pass

    # by_post: 参数经 __parameters__ POST 通道进入会话（复刻主表 NameJavaScript
    # ReportletHyperlink byPost=true 生产语义）。
    # 2026-09-04 夜战修正: 必须 ①POST-first 建会话（参数在会话创建时刻进入，
    # 先 GET 会建出无参旧会话致参数被无视）；②入口带 op=view 选 ViewActor 分析会话——
    # 默认 page 会话渲染链死（parameterCommit 空转+view_content ClassCast，
    # R13 L3-03/L3-04 与本夜实验双重证实）。实测 tr=9/td=54 且 p_name 进入渲染标题。
    if post_params and ext.lower() != ".frm":
        last_err = ""
        for fmt, build in fmts:
            viewlet_arg = ("/" + viewlet) if fmt == "fr10_reportview" else viewlet
            q = {"viewlet": viewlet_arg, "op": "view"}
            url = FR_HOST.rstrip("/") + build(viewlet_arg, q)
            notes.append("by-post POST-first → %s (op=view)" % fmt)
            pentry, perr = submit_by_post(page, context, url, post_params,
                                          timeout_s, skip_login, notes)
            if pentry is not None:
                try:
                    with open(FMT_CACHE, "w", encoding="utf-8") as f:
                        json.dump({"format": fmt}, f)
                except Exception:
                    pass
                pentry["url_format"] = "bypost_op_view"
                # 前端挂载兜底: 会话在, 服务端渲染在, 仅页面 JS 链断时补齐 DOM
                _mount_server_grid(page, notes, timeout_s)
                return pentry, page.url
            last_err = perr
        return None, last_err or "by-post 所有 URL 格式均失败"

    last_err = ""
    for fmt, build in fmts:
        viewlet_arg = ("/" + viewlet) if fmt == "fr10_reportview" else viewlet
        q = {"viewlet": viewlet_arg}
        q.update(build_query(params, op, fmt))
        url = FR_HOST.rstrip("/") + build(viewlet_arg, q)
        entry, err = _goto_and_check(page, context, url, fmt, timeout_s, skip_login, notes)
        if entry is not None:
            if entry.get("status") != 404:
                try:
                    with open(FMT_CACHE, "w", encoding="utf-8") as f:
                        json.dump({"format": fmt}, f)
                except Exception:
                    pass
                return entry, page.url
            last_err = err or ("HTTP 404 @ %s" % fmt)
            continue
        last_err = err
    return None, last_err or "所有 URL 格式均失败"


def _goto_and_check(page, context, url, fmt, timeout_s, skip_login, notes):
    t0 = time.time()
    try:
        resp = page.goto(url, timeout=timeout_s * 1000, wait_until="domcontentloaded")
    except Exception as e:
        return None, "goto 失败(%s): %s" % (fmt, str(e)[:120])
    status = resp.status if resp else None
    if status == 404:
        return None, "HTTP 404 @ %s" % fmt
    try:
        page.wait_for_load_state("load", timeout=timeout_s * 1000)
    except Exception:
        pass
    page.wait_for_timeout(1000)  # 留给 JS 重定向（登录跳转）
    elapsed_ms = int((time.time() - t0) * 1000)

    import kit_core
    login_kicked = kit_core.looks_like_login(page)
    if login_kicked and not skip_login:
        notes.append("检测到登录页，尝试 JSONP 登录（%s）" % fmt)
        if kit_core.login_jsonp(context, FR_HOST, FR_USER, FR_PWD):
            try:
                context.storage_state(path=STATE_FILE)
                notes.append("登录态已缓存: %s" % STATE_FILE)
            except Exception:
                pass
            t0 = time.time()
            try:
                resp = page.goto(url, timeout=timeout_s * 1000, wait_until="domcontentloaded")
            except Exception as e:
                return None, "登录后 goto 失败(%s): %s" % (fmt, str(e)[:120])
            status = resp.status if resp else None
            if status == 404:
                return None, "HTTP 404 @ %s" % fmt
            try:
                page.wait_for_load_state("load", timeout=timeout_s * 1000)
            except Exception:
                pass
            page.wait_for_timeout(1000)
            elapsed_ms = int((time.time() - t0) * 1000)
            login_kicked = kit_core.looks_like_login(page)

    entry = {
        "status": status,
        "final_url": page.url,
        "elapsed_ms": elapsed_ms,
        "url_format": fmt,
        "login_kicked": bool(login_kicked),
    }
    return entry, page.url


# ══════════════════ checks 动态发现 ══════════════════

def discover_checks(flags):
    """按文件名序发现 checks/*.py。返回 [(模块名, run)]；跳过情况打印提示。"""
    mods = []
    if not os.path.isdir(CHECKS_DIR):
        print("  [warn] checks/ 目录不存在: %s" % CHECKS_DIR)
        return mods
    for fn in sorted(os.listdir(CHECKS_DIR)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        name = fn[:-3]
        if name == "fr_api":
            continue  # 纯库模块（无 run），按契约跳过
        gated_by = None
        if name.startswith("layout"):
            gated_by = "--layout"
        elif name.startswith("links"):
            gated_by = "--links"
        if gated_by and gated_by not in flags:
            print("  [skip] %s（未开启 %s）" % (name, gated_by))
            continue
        path = os.path.join(CHECKS_DIR, fn)
        try:
            spec = importlib.util.spec_from_file_location("webprobe_check_" + name, path)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
        except Exception as e:
            print("  [warn] 模块 %s 加载失败: %s" % (name, str(e)[:100]))
            continue
        if not hasattr(m, "run"):
            print("  [skip] %s（无 run()，视为纯库模块）" % name)
            continue
        mods.append((name, m.run))
    if "layout" in flags or "links" in flags:
        have = {n for n, _ in mods}
        for want, flag in (("layout", "--layout"), ("links", "--links")):
            if flag in flags and not any(n.startswith(want) for n in have):
                print("  [note] %s 已开启，但 checks/ 中不存在 %s 模块（B 分支未交付）" % (flag, want))
    return mods


# ══════════════════ baseline 豁免 ══════════════════

def load_baseline():
    try:
        import yaml
        with open(BASELINE_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        print("  [warn] baseline.yaml 读取失败（不豁免）: %s" % str(e)[:80])
        return {"global": [], "pages": {}}
    return {"global": data.get("global") or [], "pages": data.get("pages") or {}}


def apply_baseline(findings, baseline, page_name):
    rules = list(baseline.get("global") or [])
    page_rules = baseline.get("pages") or {}
    for key in (page_name, re.sub(r'[\\/:*?"<>|\s]+', "_", page_name)):
        rules += list(page_rules.get(key) or [])
    rx = []
    for r in rules:
        try:
            rx.append((re.compile(r.get("match", "")), r.get("reason", "")))
        except re.error:
            continue
    if not rx:
        return findings
    for f in findings:
        # 2026-09-04 L7 扩展: 除 console 外, requestfailed 同样可按基线豁免(如 unload 期
        # closesessionid 心跳失败等已知噪声); 其余 check 类(grid/widgets/pageerror)不豁免
        if f.get("check") not in ("runtime.console", "runtime.requestfailed"):
            continue
        blob = "%s %s" % (f.get("message", ""), f.get("evidence", ""))
        for pat, reason in rx:
            if pat.search(blob):
                f["level"] = "info"
                f["hint"] = "baseline 豁免: %s" % reason
                break
    return findings


# ══════════════════ 主流程 ══════════════════

def _run_checks(context, target, op, params, timeout_s, skip_login, flags, by_post):
    """对单页执行导航+全部体检+报告落盘。返回 (findings, out_dir, entry)。"""
    import kit_core
    import report as report_mod

    name = page_name_of(target)
    notes = []
    findings = []
    t_start = time.time()  # L-LOGFB: 预览窗口起点
    out_dir = report_mod.new_out_dir(name)
    page = context.new_page()
    try:
        events = attach_events(page)

        entry, url_or_err = navigate(page, context, target, op, params,
                                     timeout_s, skip_login, notes, by_post=by_post)
        for n in notes:
            print("  [note] %s" % n)

        if entry is None:
            findings.append({
                "check": "entry.navigate",
                "level": "error",
                "message": "导航失败：%s" % url_or_err,
                "evidence": "target=%s host=%s" % (target, FR_HOST),
                "hint": "确认 FR 服务器已启动且 cpt 在 reportlets 目录下",
            })
        else:
            ctx = kit_core.ProbeCtx(page=page, url=page.url, cpt_path=(target if os.path.isfile(target) else None),
                                    facts=None, params={k: v for k, v in
                                                        (kv.partition("=")[::2] for kv in params)},
                                    out_dir=out_dir, timeout=timeout_s, semantic=None)
            ctx.entry = entry
            ctx.js_events = events

            if entry.get("login_kicked"):
                findings.append({
                    "check": "entry.login",
                    "level": "error",
                    "message": "停在登录页（自动登录失败或 --skip-login）",
                    "evidence": "final_url=%s" % entry.get("final_url", "")[:280],
                    "hint": "去掉 --skip-login 或检查凭据；本次仅执行入口层检查",
                })
                mods = [(n, r) for n, r in discover_checks(flags) if n == "entry"]
            else:
                mods = discover_checks(flags)
                if os.path.splitext(target)[1].lower() == ".frm":
                    mods = [(n, r) for n, r in mods if n != "grid"]  # frm 无 cpt 网格, grid 类检查不适用(2026-09-11)

            for mod_name, run in mods:
                t0 = time.time()
                try:
                    res = run(ctx)
                except Exception as e:
                    res = [{"check": "%s.crashed" % mod_name, "level": "error",
                            "message": "check 模块执行异常", "evidence": str(e)[:300]}]
                print("  [check] %-10s %2d findings (%.1fs)" % (mod_name, len(res or []), time.time() - t0))
                findings.extend(res or [])

        # 截图 + 报告（即使导航失败也落盘留证）
        shot = report_mod.screenshot(page, os.path.join(out_dir, "full_page.png"))
        findings = apply_baseline(findings, load_baseline(), name)
        meta = {"host": FR_HOST, "op": op, "params": params or "-",
                "by_post": bool(by_post),
                "url_format": (entry or {}).get("url_format", "-"),
                "screenshot": "full_page.png" if shot else "截图失败"}
        report_mod.write(out_dir, name, page.url, findings, meta)
        report_mod.print_summary(name, findings, out_dir)

        # L-LOGFB: 预览时间窗内的 FR 运行期日志反馈（best-effort，不影响体检结论）
        try:
            import log_feedback
            lf = log_feedback.probe_hook(out_dir, name, target, t_start)
            print("  [logfb] 运行期日志反馈: 命中 %d 行 (ERROR %d, WARN %d)"
                  % (lf["hits"], lf["errors"], lf["warns"]))
        except Exception as _lfe:
            print("  [logfb] 日志反馈不可用(不影响体检): %s" % str(_lfe)[:80])
    finally:
        try:
            page.close()
        except Exception:
            pass
    return findings, out_dir, entry


def run_batch(args):
    """批量模式: 对目录内全部 *.cpt 逐页体检 → 矩阵 md + results.jsonl。"""
    import report as report_mod

    d = os.path.abspath(args.batch)
    if not os.path.isdir(d):
        print("[fail] 批量目录不存在: %s" % d)
        return 1
    # WKTEST_ 前缀 = 验收夹具部署件，不进矩阵
    cpts = sorted(fn for fn in os.listdir(d)
                  if fn.lower().endswith((".cpt", ".frm")) and not fn.upper().startswith("WKTEST_"))
    if not cpts:
        print("[fail] 目录内无 cpt: %s" % d)
        return 1
    print("[batch] 目录 %s 共 %d 个 cpt" % (d, len(cpts)))
    flags = [f for f, on in (("--layout", args.layout), ("--links", args.links)) if on]

    rows = []
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx_kw = {"viewport": {"width": 1600, "height": 900}, "locale": "zh-CN"}
        if os.path.exists(STATE_FILE):
            ctx_kw["storage_state"] = STATE_FILE
        context = browser.new_context(**ctx_kw)
        for i, fn in enumerate(cpts, 1):
            path = os.path.join(d, fn)
            t0 = time.time()
            crashed = False
            try:
                findings, out_dir, entry = _run_checks(
                    context, path, args.op, args.params, args.timeout,
                    args.skip_login, flags, args.by_post)
            except Exception as e:
                crashed = True
                findings = [{"check": "batch.crashed", "level": "error",
                             "message": "批量体检异常", "evidence": str(e)[:300]}]
                out_dir, entry = "-", None
            s = report_mod._summary(findings)
            rc = 1 if s.get("error") else (2 if s.get("warn") else 0)
            rows.append({
                "page": fn[:-4],
                "file": path,
                "rc": rc,
                "seconds": round(time.time() - t0, 1),
                "crashed": crashed,
                "summary": s,
                "out_dir": out_dir,
                "meta": {"op": args.op, "params": args.params or "-",
                         "by_post": bool(args.by_post), "flags": flags},
                "findings": [{"check": f.get("check", "?"), "level": f.get("level", "info"),
                              "message": str(f.get("message", ""))[:200],
                              "evidence": str(f.get("evidence", ""))[:280],
                              "hint": str(f.get("hint", "") or "")[:200]}
                             for f in findings],
            })
            print("  [batch %d/%d] %s → rc=%d (%.1fs)" % (i, len(cpts), fn, rc, time.time() - t0))
        browser.close()

    matrix_path = args.matrix_out or os.path.join(
        RUNS_DIR, "matrix_%s.md" % time.strftime("%Y%m%d_%H%M%S"))
    report_mod.write_matrix(rows, matrix_path,
                            meta={"dir": d, "flags": flags, "op": args.op,
                                  "params": args.params or "-", "by_post": bool(args.by_post)})
    jsonl_path = args.jsonl_out or os.path.join(
        RUNS_DIR, "results_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S"))
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_err = sum(1 for r in rows if r["rc"] == 1)
    n_warn = sum(1 for r in rows if r["rc"] == 2)
    n_ok = sum(1 for r in rows if r["rc"] == 0)
    print("")
    print("[batch] 完成: %d 页 | 干净=%d 仅warn=%d 有error=%d" % (len(rows), n_ok, n_warn, n_err))
    print("[batch] 矩阵: %s" % matrix_path)
    print("[batch] 结果: %s" % jsonl_path)
    return 1 if n_err else (2 if n_warn else 0)


def main():
    ap = argparse.ArgumentParser(description="WebKit 页面快速体检（FR10 运行期）")
    ap.add_argument("target", nargs="?", default="", help="cpt/frm 绝对路径 或 完整 URL（批量模式可省）")
    ap.add_argument("--batch", default="", help="批量模式: 对该目录下全部 *.cpt/*.frm 跑体检矩阵")
    ap.add_argument("--matrix-out", default="", help="批量矩阵 md 输出路径（默认 ~/.fr_dev_kit/runs/webprobe/matrix_*.md）")
    ap.add_argument("--jsonl-out", default="", help="批量 results.jsonl 输出路径")
    ap.add_argument("--params", nargs="*", default=[], help="报表参数 k=v（可多个）")
    ap.add_argument("--op", default="", help="查看方式：默认空=分析视图(不拼 op 参数)；write=填报模式")
    ap.add_argument("--layout", action="store_true", help="启用 layout 类 check 模块")
    ap.add_argument("--links", action="store_true", help="启用 links 类 check 模块")
    ap.add_argument("--by-post", action="store_true",
                    help="参数走 POST 表单通道（复刻 ReportletHyperlink byPost=true 生产语义）")
    ap.add_argument("--timeout", type=int, default=60, help="导航/单项探针超时秒数")
    ap.add_argument("--skip-login", action="store_true", help="不做自动登录")
    args = ap.parse_args()

    if args.batch:
        return run_batch(args)

    target = args.target
    if not target:
        print("[fail] 缺少目标: <cpt路径|URL> 或 --batch <目录>")
        return 1
    target = os.path.abspath(target) if not re.match(r"^https?://", target, re.I) else target
    if not re.match(r"^https?://", target, re.I) and not os.path.isfile(target):
        print("[fail] 文件不存在: %s" % target)
        return 1

    flags = [f for f, on in (("--layout", args.layout), ("--links", args.links)) if on]

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx_kw = {"viewport": {"width": 1600, "height": 900}, "locale": "zh-CN"}
        if os.path.exists(STATE_FILE):
            ctx_kw["storage_state"] = STATE_FILE
        context = browser.new_context(**ctx_kw)
        findings, out_dir, entry = _run_checks(
            context, target, args.op, args.params, args.timeout,
            args.skip_login, flags, args.by_post)
        browser.close()

    has_err = any(f.get("level") == "error" for f in findings)
    has_warn = any(f.get("level") == "warn" for f in findings)
    return 1 if has_err else (2 if has_warn else 0)


if __name__ == "__main__":
    sys.exit(main())
