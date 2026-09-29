# -*- coding: utf-8 -*-
"""
checks/runtime.py — 运行期体检：JS 异常 / console / 请求失败 / FR 业务信号。

数据来源两路:
  A. probe.py 在 goto 前挂好的页面事件（ctx.js_events）:
     pageerror / console(error|warning) / requestfailed
  B. 本模块在 find_report_frame 找到的 frame（+主 frame）上自动执行探针:
     加载遮罩消失轮询 / 数据集错误弹窗 / ErrorMarkWidget / _g()·contentPane 可用性
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
import time

# ---- 探针 JS（改造自 fr_check.py check_browser_signals，改为自动执行）----

_JS_VISIBLE_LOADING = """
() => {
  const els = document.querySelectorAll('.loading-div, .fr-loading, #loading-div, [class*="loading"]');
  const vis = [];
  els.forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
    if (!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)) return;
    vis.push((el.className || '').toString().slice(0, 80));
  });
  return vis;
}
"""

_JS_ERROR_DIALOGS = """
() => {
  const kw = ['错误', 'Exception', '数据集'];
  const sel = '.fr-msg-container, .fr-toast, .fr-alert, .fr-window, '
            + '[class*="dialog"], [class*="popup"], [class*="Dialog"]';
  const out = [];
  document.querySelectorAll(sel).forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    if (!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)) return;
    const t = (el.innerText || el.textContent || '').trim();
    if (!t) return;
    if (kw.some(k => t.indexOf(k) >= 0)) {
      out.push(t.replace(/\\s+/g, ' ').slice(0, 200));
    }
  });
  return out.slice(0, 5);
}
"""

_JS_ERROR_MARK = """
() => {
  const dom = document.querySelectorAll('[class*="error-mark"], [class*="errorMark"], [class*="errormark"]');
  let inst = 0;
  try { inst = (window.FR && FR.ErrorMarkWidget) ? 1 : 0; } catch (e) {}
  return {dom: dom.length, inst: inst};
}
"""

_JS_GLOBALS = """
() => ({
  g: typeof _g === 'function',
  fr: typeof FR !== 'undefined',
  cp: typeof contentPane !== 'undefined'
})
"""

# 网格挂载状态 + 会话ID（主动 view_content 探针的输入）
_JS_GRID_STATE = """
() => ({
  sheets: document.querySelectorAll('.sheet-container').length,
  sheetLen: ((document.querySelector('.sheet-container') || {innerHTML: ''}).innerHTML || '').length,
  hasViewPane: !!(window.contentPane && contentPane.viewPane),
  sid: (window.contentPane && contentPane.currentSessionID)
        ? String(contentPane.currentSessionID)
        : ((typeof _g === 'function' && _g() && _g().currentSessionID)
            ? String(_g().currentSessionID) : null),
  servletURL: (window.FR && FR.servletURL) || null
})
"""


def _ev(frame, js, default=None):
    try:
        return frame.evaluate(js)
    except Exception as e:
        return default if default is not None else {"err": str(e)[:120]}


def run(ctx):
    findings = []
    page = ctx.page
    frames = []
    try:
        import kit_core
        frames = kit_core.iter_probe_frames(page)
    except Exception:
        frames = [page.main_frame]

    events = getattr(ctx, "js_events", None) or {}

    # ---- A1. pageerror 未捕获异常 ----
    for ev in events.get("pageerrors", []):
        evidence = str(ev.get("error", ""))[:300]
        stack = str(ev.get("stack", "") or "")
        if stack:
            # 堆栈里取首个 at 行（定位 eval/脚本崩溃点，如 cpt:209:51）
            first_at = next((ln.strip() for ln in stack.splitlines() if ln.strip().startswith("at")), "")
            if first_at:
                evidence = (evidence + " @ " + first_at)[:300]
        findings.append({
            "check": "runtime.pageerror",
            "level": "error",
            "message": "页面未捕获 JS 异常",
            "evidence": evidence,
        })

    # ---- A2. console error / warning 逐条 ----
    for ev in events.get("console", []):
        t = ev.get("type", "")
        if t == "error":
            level = "error"
        elif t in ("warning", "warn"):
            level = "warn"
        else:
            continue
        findings.append({
            "check": "runtime.console",
            "level": level,
            "message": "console.%s" % t,
            "evidence": str(ev.get("text", ""))[:200],
            "location": ev.get("location", "")[:100],
        })

    # ---- A3. requestfailed ----
    failed = events.get("requestfailed", [])
    if failed:
        urls = [str(f.get("url", ""))[:90] for f in failed[:3]]
        findings.append({
            "check": "runtime.requestfailed",
            "level": "warn",
            "message": "失败请求 %d 个（前 3 条见证据）" % len(failed),
            "evidence": " | ".join(urls)[:300],
        })

    # ---- B1. 加载遮罩（报告 frame 优先）----
    if frames:
        for fr in frames:
            label = _label(fr)
            vis = _wait_mask_gone(fr, ctx.timeout)
            if vis is None:
                continue  # frame 不可用（已销毁/跨域），跳过
            if vis:
                findings.append({
                    "check": "runtime.loadmask",
                    "level": "error",
                    "message": "加载遮罩 %ds 未消失——加载卡死（%s）" % (ctx.timeout, label),
                    "evidence": ("visible loading: %s" % "; ".join(vis))[:300],
                })

        # ---- B2. 数据集错误弹窗 ----
        seen_dialog = set()
        for fr in frames:
            res = _ev(fr, _JS_ERROR_DIALOGS, [])
            if isinstance(res, dict):  # evaluate 出错
                continue
            for t in res:
                key = t[:80]
                if key in seen_dialog:
                    continue
                seen_dialog.add(key)
                findings.append({
                    "check": "runtime.dataset_dialog",
                    "level": "error",
                    "message": "探测到数据集/错误弹窗（%s）" % _label(fr),
                    "evidence": t[:300],
                })

        # ---- B3. ErrorMarkWidget ----
        for fr in frames:
            res = _ev(fr, _JS_ERROR_MARK, {})
            if not isinstance(res, dict):
                continue
            n = int(res.get("dom", 0) or 0)
            if n > 0:
                findings.append({
                    "check": "runtime.errormark",
                    "level": "error",
                    "message": "ErrorMarkWidget 实例 %d 个（%s）" % (n, _label(fr)),
                    "evidence": "selector=[class*=error-mark/errorMark/errormark] dom=%d FR.ErrorMarkWidget=%s"
                                % (n, bool(res.get("inst"))),
                })

        # ---- B5. 网格挂载 + 主动 view_content 探针（FR10 前端会静默吞掉
        #          服务端渲染错误：无弹窗/无JS报错/网格不挂载，只能主动验证）----
        _grid_probe(findings, ctx, frames)

        # ---- B4. _g()/contentPane 可用性（info）----
        for fr in frames:
            res = _ev(fr, _JS_GLOBALS, {})
            if not isinstance(res, dict) or "err" in res:
                continue
            if not (res.get("g") or res.get("cp")):
                findings.append({
                    "check": "runtime.globals",
                    "level": "info",
                    "message": "_g/contentPane 部分不可用（%s）" % _label(fr),
                    "evidence": "_g=%s FR=%s contentPane=%s"
                                % (res.get("g"), res.get("fr"), res.get("cp")),
                })

    if not findings and not events:
        findings.append({
            "check": "runtime.collector",
            "level": "info",
            "message": "未采集到任何运行期信号（事件监听缺失或页面未加载）",
            "evidence": "js_events=%s" % ("present" if events else "missing"),
        })
    return findings


def _label(frame):
    try:
        import kit_core
        return kit_core.frame_label(frame)
    except Exception:
        try:
            return "frame:" + (frame.url or "")[:40]
        except Exception:
            return "frame(?)"


# ════════════ B5: 网格挂载 + 主动 view_content 探针 ════════════

_ERR_MARKERS = ("出错页面", "错误代码", "11300001")


def _grid_probe(findings, ctx, frames):
    """被动查网格挂载；网格为空时主动 POST op=fr_view&cmd=view_content 复核。"""
    import re as _re
    try:
        import urllib.parse as _up
    except Exception:
        return

    page = ctx.page
    state = None
    for fr in frames:
        st = _ev(fr, _JS_GRID_STATE, None)
        if isinstance(st, dict) and st.get("sid"):
            state = st
            break
        if state is None and isinstance(st, dict):
            state = st
    if not isinstance(state, dict):
        return  # 非 FR view 页面（登录页等），静默跳过

    grid_empty = (state.get("sheets", 0) or 0) == 0 and (state.get("sheetLen", 0) or 0) == 0
    sid = state.get("sid")
    servlet = state.get("servletURL") or "/webroot/decision/view/report"
    if not grid_empty or not sid:
        return

    # 主动复核（与服务端渲染链路同款请求）
    server_err = None
    server_ok = False
    server_artifact = None   # Oops/ClassCastException：页面未进入渲染会话的探针伪影（必填参数被拦/初始化 JS 崩溃）
    try:
        abs_url = _up.urljoin(page.url, servlet)
        resp = page.context.request.post(abs_url, form={
            "op": "fr_view", "cmd": "view_content",
            "sessionID": sid, "reportIndex": "0", "iid": "0.1"})
        body = resp.text() if resp is not None else ""
        if body:
            import html as _html
            text = _html.unescape(_re.sub(r"<[^>]+>", " ", body))
            text = _re.sub(r"\s+", " ", text)
            if any(m in text for m in _ERR_MARKERS):
                # 2026-09-04 L7 修复分类顺序: 真实数据集错误(11300001/配置错误)必须优先于
                # Oops/ClassCast 判定——此前所有 Oops 页都被吞进"探针伪影"，真实 SQL 错误被掩蔽
                if ("11300001" in text) or ("配置错误" in text) or ("数据集" in text and "错误" in text):
                    m = _re.search(r"(错误代码.{0,200})", text)
                    server_err = (m.group(1) if m else text)[:300]
                elif ("cannot be cast to com.fr.report.report.AnalyReport" in text):
                    # 已知伪影: 分页会话(PageRWorkSheet)撞分析模式命令(view_content→AnalyReport),
                    # 2026-09-04 服务器日志+finereport.js 双重证实, 与页面健康无关
                    server_artifact = text[:300]
                elif ("cannot be cast" in text) or ("非常抱歉" in text) or ("Oops" in text):
                    server_artifact = text[:300]
                else:
                    m = _re.search(r"(错误代码.{0,200})", text)
                    server_err = (m.group(1) if m else text)[:300]
            elif "sheet-container" in body or len(body) > 2000:
                server_ok = True
    except Exception as e:
        server_err = None
        findings.append({
            "check": "runtime.grid",
            "level": "info",
            "message": "主动 view_content 复核请求失败",
            "evidence": str(e)[:300],
        })

    if grid_empty and server_artifact:
        findings.append({
            "check": "runtime.grid",
            "level": "info",
            "message": "view_content 复核撞到分页/分析模式 ClassCast（FR10 已知探针伪影，非页面问题）",
            "evidence": server_artifact,
            "hint": "PageRWorkSheet→AnalyReport 为分页会话×分析命令错配（2026-09-04 L7 服务器日志证实）；页面定性看 pageerror/数据集类 findings",
        })
    elif grid_empty and server_err:
        findings.append({
            "check": "runtime.grid",
            "level": "error",
            "message": "报告网格未渲染——服务端渲染失败（数据集/SQL 错误，前端静默吞掉无弹窗）",
            "evidence": server_err,
            "hint": "先核对必填参数是否空参直访（空参代入 SQL 常致语法/列错），生产带参复验；若带参仍错则修数据集 SQL",
        })
    elif grid_empty and server_ok:
        findings.append({
            "check": "runtime.grid",
            "level": "error",
            "message": "报告网格未渲染——但服务端内容可取（前端 viewPane 挂载失败）",
            "evidence": "sheets=0 sheetLen=0 hasViewPane=%s view_content=200(len>2000)" % state.get("hasViewPane"),
            "hint": "检查浏览器端 JS 初始化链路/插件冲突",
        })
    elif grid_empty:
        findings.append({
            "check": "runtime.grid",
            "level": "warn",
            "message": "报告网格未渲染（服务端复核未能定性）",
            "evidence": "sheets=0 sheetLen=0 hasViewPane=%s" % state.get("hasViewPane"),
            "hint": "可能需要点击查询/带参渲染，人工核对截图确认",
        })


def _wait_mask_gone(frame, timeout_s):
    """轮询直到无可见加载元素；返回 None=frame 不可用, []=已消失, list=仍在加载。

    到期后追加 3s 宽限复查一次，仍可见才判定卡死（防瞬时动画误报）。
    """
    deadline = time.time() + timeout_s
    last = []
    while time.time() < deadline:
        last = _ev(frame, _JS_VISIBLE_LOADING, None)
        if last is None:
            return None
        if isinstance(last, dict):  # evaluate 异常包装
            time.sleep(0.5)
            continue
        if not last:
            return []
        time.sleep(0.5)
    time.sleep(3.0)  # 宽限
    last = _ev(frame, _JS_VISIBLE_LOADING, None)
    if last is None or isinstance(last, dict):
        return None
    return last
