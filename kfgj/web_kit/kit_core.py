# -*- coding: utf-8 -*-
"""
kit_core — WebKit 页面体检"核心骨架"契约层。

所有 check 模块（本骨架的 entry/runtime，以及 B 分支后续插入的
widgets/grid/links 等）共用同一个上下文对象 ProbeCtx 与同一组辅助函数。

契约（B 分支必须遵守）:
  - ProbeCtx 字段: page / url / cpt_path / facts / params / out_dir / timeout / semantic
  - check 模块暴露 run(ctx) -> list[dict]
  - finding = {"check": "<模块>.<项>", "level": "error"|"warn"|"info",
               "message": str, "evidence": str(<=300字符机器证据), "hint": 可选}

probe.py 运行期会在 ctx 上附加两个动态属性（check 模块按需读取，缺失须容错）:
  ctx.entry      —— 入口响应信息 dict（entry.py 消费）
  ctx.js_events  —— 页面事件采集 dict（runtime.py 消费）:
                    {"pageerrors": [...], "console": [...], "requestfailed": [...]}
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
import re
import urllib.parse

# 报告区 frame 的识别标记（FR10 页面是 iframe 套壳）
_REPORT_FRAME_JS = """
() => !!(
    document.querySelector('.sheet')
 || document.querySelector('.x-table')
 || document.querySelector('#contentPane')
 || document.querySelector('.contentPane')
 || document.querySelector('[widgetname]')
 || document.querySelector('.fr-trigger-texteditor')
)
"""


class ProbeCtx(object):
    """体检上下文——check 模块的唯一输入。"""

    def __init__(self, page, url, cpt_path=None, facts=None, params=None,
                 out_dir=None, timeout=60, semantic=None):
        self.page = page            # Playwright Page（已导航到目标页）
        self.url = url              # 最终页面 URL
        self.cpt_path = cpt_path    # 本地 cpt 绝对路径（URL 直跑时为 None）
        self.facts = facts          # 模板静态事实 dict|None（cpt_facts 分支注入）
        self.params = params or {}  # --params 注入的报表参数
        self.out_dir = out_dir      # 本次体检报告输出目录
        self.timeout = timeout      # 单项探针超时（秒）
        self.semantic = semantic    # 语义层信息 dict|None（预留）
        # ---- probe.py 附加（可选，模块需容错）----
        self.entry = None
        self.js_events = None


def find_report_frame(page):
    """在 page.frames 里找含报表内容的 frame（.sheet/.x-table/contentPane 容器）。

    找不到（无 iframe 套壳或尚在加载）返回主 frame。
    """
    hits = []
    for fr in page.frames:
        if fr is page.main_frame:
            continue
        try:
            if fr.evaluate(_REPORT_FRAME_JS):
                hits.append(fr)
        except Exception:
            continue  # about:blank / 已销毁 / 跨域 frame
    if hits:
        return hits[-1]  # 取最内层命中
    return page.main_frame


def iter_probe_frames(page):
    """返回 [报告 frame, 主 frame]（去重）——探针需两处都查。"""
    out = []
    rep = find_report_frame(page)
    if rep is not page.main_frame:
        out.append(rep)
    out.append(page.main_frame)
    return out


def frame_label(frame):
    """frame 的可读标签（用于 finding message/evidence 定位）。"""
    try:
        u = (frame.url or "").strip()
    except Exception:
        u = ""
    if not u or u == "about:blank":
        return "frame(main)" if frame is frame.page.main_frame else "frame(?)"
    tail = re.split(r"[?#]", u)[0].rstrip("/").rsplit("/", 1)[-1]
    tag = "main" if frame is frame.page.main_frame else "iframe"
    return "frame(%s:%s)" % (tag, tail[:40])


def looks_like_login(page):
    """最终 URL/页面内容是否为登录页。"""
    url = (page.url or "").lower()
    if "/login" in url or "decision/login" in url:
        return True
    try:
        return bool(page.evaluate(
            "() => !!document.querySelector('input[type=password]')"))
    except Exception:
        return False


def login_jsonp(context, host, user="admin", pwd="admin", timeout_ms=10000):
    """JSONP 端点登录（同 fr_check.py login_fr 的浏览器版）。

    用 context.request 发请求——cookie 直接落进浏览器 context，
    之后 page.goto 即带登录态。成功返回 True。
    """
    url = host.rstrip("/") + "/webroot/decision/login/cross/domain?" + urllib.parse.urlencode({
        "fine_username": user, "fine_password": pwd, "validity": -1, "callback": "cb"})
    try:
        resp = context.request.get(url, timeout=timeout_ms)
        body = resp.text() if resp is not None else ""
    except Exception:
        return False
    return bool(re.search(r'"accessToken"\s*:\s*"', body or ""))
