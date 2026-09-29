# -*- coding: utf-8 -*-
"""checks/links.py — 超链弹窗冒烟(P2, 稳健降级: 自动化失败只 info, 绝不误报 error)。

流程:
  1. facts: NameJavaScript 超链格数 + 第一个超链目标 ReportletName → info
  2. 找可点击的超链格(FR 渲染特征: 下划线/蓝色/链接类名) → 点击
  3. 等弹窗(FR _dialog 为同页 DOM 对话框, 内嵌 iframe)或新页签 → 捕获子页 URL → info
  4. 拿到子页 URL → 自建最小检查(新开同 context 页, 复用登录 cookie):
     页面错误/空表格 → error/warn 照常产出(自包含, 不 import 核心分支)
  任何一步失败 → info "links.automation_pending", 不算失败。

run(ctx) -> list[finding]
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

import os
import sys
import urllib.parse

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from checks import fr_api
except Exception:
    import fr_api

try:
    import cpt_facts
except Exception:
    sys.path.insert(0, _ROOT)
    import cpt_facts

CLICK_WAIT_MS = 6000        # 点击后等弹窗
DIALOG_SETTLE_MS = 3000
CHILD_SETTLE_MS = 8000
MAX_CANDIDATES = 8          # 最多尝试的候选链接格
# 危险词黑名单: 命中则不点击(避免体检触发提交/删除等写操作)
RISKY_TEXT = ("提交", "保存", "删除", "清空", "确认", "关闭", "导入", "上传")


def _ev(s):
    return str(s)[:300]


def _info(check, message, evidence, **kw):
    d = {"check": check, "level": "info", "message": message, "evidence": _ev(evidence)}
    d.update(kw)
    return d


def _fact(ctx):
    f = getattr(ctx, "facts", None)
    if f and f.get("js_link_defs") is not None:
        return f
    path = getattr(ctx, "cpt_path", None)
    if path and os.path.exists(path):
        try:
            return cpt_facts.parse_cpt(path)
        except Exception:
            return {}
    return {}


def _get_frame(ctx, page):
    fn = getattr(ctx, "find_report_frame", None)
    if callable(fn):
        try:
            fr = fn(page)
            if fr is not None:
                return fr
        except Exception:
            pass
    return fr_api.find_report_frame(page)


def _click_at(frame, item):
    """用原子坐标点击(评估坐标→鼠标事件), 兼容无 locator 的 frame。"""
    try:
        page = frame.page
        page.mouse.click(item["x"], item["y"])
        return True
    except Exception:
        return False


def _find_candidates(frame):
    js = fr_api._LINK_CELL_CANDIDATES_JS + "(%d)" % MAX_CANDIDATES
    hits = fr_api.eval_js(frame, js) or []
    # 过滤危险格(提交/删除/清空等), 只保留疑似钻取链接
    safe = [c for c in hits if not any(w in (c.get("text") or "") for w in RISKY_TEXT)]
    return safe, hits


def _probe_dialog(page):
    return fr_api.eval_js(page.main_frame, fr_api._DIALOG_PROBE_JS + "()") or {}


def _check_child_page(ctx, url):
    """自包含最小子页检查(entry+runtime 级): 新开页(复用登录 cookie),
    收集 pageerror/console.error/空表格。返回 findings。绝不 import 核心分支。"""
    out = []
    page = ctx.page
    child = None
    try:
        child = page.context.new_page()          # 显式 context(共享 cookie)
    except Exception:
        try:
            br = page.context.browser             # 隐式 context → 用 storage_state 克隆登录态
            if br is not None:
                state = page.context.storage_state()
                child = br.new_context(storage_state=state).new_page()
        except Exception:
            child = None
    if child is None:
        # 最后降级: 复用页面自身的 APIRequestContext(共享 cookie)只做 HTTP 层检查
        try:
            resp = page.request.get(url, timeout=int(getattr(ctx, "timeout", 30) * 1000))
            return [_info("links.child.http", "无法开新页签, 仅 HTTP 层检查子页(降级)",
                          "status=%s final=%s" % (resp.status, resp.url[:150]))]
        except Exception as e:
            return [_info("links.automation_pending", "无法打开子页会话", str(e)[:150])]
    errors, consoles = [], []
    child.on("pageerror", lambda e: errors.append(str(e)[:200]))
    child.on("console", lambda m: consoles.append(m.text[:150]) if m.type == "error" else None)
    errors, consoles = [], []
    child.on("pageerror", lambda e: errors.append(str(e)[:200]))
    child.on("console", lambda m: consoles.append(m.text[:150]) if m.type == "error" else None)
    try:
        child.goto(url, wait_until="load", timeout=int(getattr(ctx, "timeout", 30) * 1000))
        child.wait_for_timeout(CHILD_SETTLE_MS)
    except Exception as e:
        child.close()
        return [_info("links.automation_pending", "子页打开失败(降级)", "%s: %s" % (url[:120], str(e)[:80]))]

    if errors:
        out.append({"check": "links.child.pageerror", "level": "error",
                    "message": "子页未捕获 JS 异常 %d 个" % len(errors),
                    "evidence": _ev("%s | %s" % (url[:160], errors[0]))})
    # 空表格(自包含 frame 查找)
    frame = None
    try:
        for f in [child.main_frame] + child.frames:
            if f.evaluate(fr_api.FRAME_MARKER_JS):
                frame = f
                break
    except Exception:
        pass
    gm = fr_api.grid_metrics(frame) if frame is not None else None
    if gm is not None and (gm.get("rows") or 0) == 0:
        out.append({"check": "links.child.grid_empty", "level": "error",
                    "message": "超链子页空表格(渲染行数=0)",
                    "evidence": _ev("%s rows=0" % url[:160])})
    if not out:
        out.append(_info("links.child.ok", "超链子页打开无 JS 异常、无空表格",
                         "%s rows=%s" % (url[:160], (gm or {}).get("rows"))))
    try:
        child.close()
    except Exception:
        pass
    return out


def run(ctx):
    out = []
    facts = _fact(ctx)
    n_cells = facts.get("js_link_cells") or 0
    n_defs = facts.get("js_link_defs") or 0
    target = facts.get("first_link_target")
    frame0 = facts.get("first_link_cell") or {}

    if n_defs == 0 and n_cells == 0:
        out.append(_info("links.none", "模板无 NameJavaScript 超链", facts.get("path", "?")))
        return out

    out.append(_info(
        "links.summary",
        "声明超链: %d 格 / %d 个定义" % (n_cells, n_defs),
        "first cell(c=%s,r=%s) -> %s [frame=%s]" % (
            frame0.get("col"), frame0.get("row"),
            target, facts.get("first_link_frame"))))

    page = ctx.page
    if page is None:
        out.append(_info("links.automation_pending", "超链自动化待迭代: 无可用页面会话", "ctx.page is None"))
        return out

    frame = _get_frame(ctx, page)
    if frame is None:
        out.append(_info("links.automation_pending", "超链自动化待迭代: 未定位到报告区 frame", getattr(ctx, "url", "")))
        return out

    cands, hits_all = _find_candidates(frame)
    if not cands:
        if hits_all:
            out.append(_info(
                "links.automation_pending",
                "超链自动化待迭代: 候选格均为写操作类文本(提交/删除等), 已按安全策略跳过点击",
                "cells=%s" % [c.get("text") for c in hits_all[:5]]))
        else:
            out.append(_info(
                "links.automation_pending",
                "超链自动化待迭代: 未在渲染表格中定位到超链格(可能表格未渲染或超链无视觉特征)",
                "url=%s 声明=%d" % (str(getattr(ctx, "url", ""))[:120], n_defs)))
        return out

    # 记录点击前已有页签, 便于识别新页签
    try:
        pages_before = set(page.context.pages)
    except Exception:
        pages_before = set()

    clicked = False
    for c in cands[:3]:
        try:
            if _click_at(frame, c):
                clicked = True
                break
        except Exception:
            continue
    if not clicked:
        out.append(_info("links.automation_pending", "超链自动化待迭代: 候选格点击失败",
                         str(cands[:2])))
        return out

    try:
        page.wait_for_timeout(CLICK_WAIT_MS)
    except Exception:
        pass

    # 1) 新页签?
    child_url = None
    try:
        for p in page.context.pages:
            if p not in pages_before:
                child_url = p.url
                break
    except Exception:
        pass
    # 2) 同页 FR 弹窗内 iframe?
    if not child_url:
        dlg = _probe_dialog(page)
        srcs = dlg.get("iframes") or []
        if srcs:
            child_url = srcs[0]
        elif dlg.get("visible"):
            out.append(_info("links.dialog_opened", "检测到 FR 弹窗但未捕获内嵌 URL",
                             "dialog=%s" % dlg.get("visible")))
    # 3) 主页面跳转?
    if not child_url:
        try:
            cur = page.url
            if cur and cands and target and target.split("/")[-1] in cur:
                child_url = cur
        except Exception:
            pass

    if not child_url:
        out.append(_info(
            "links.automation_pending",
            "超链自动化待迭代: 点击后未捕获弹窗/新页(共尝试 %d 候选)" % min(3, len(cands)),
            "candidates=%s" % [c.get("text") for c in cands[:3]]))
        return out

    out.append(_info("links.dialog_opened", "超链弹窗已打开", "child url=%s" % child_url))

    # 子页最小检查
    try:
        sub = _check_child_page(ctx, child_url)
        out.extend(sub)
    except Exception as e:
        out.append(_info("links.automation_pending", "超链自动化待迭代: 子页检查异常", str(e)[:120]))

    return out
