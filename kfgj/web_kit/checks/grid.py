# -*- coding: utf-8 -*-
"""checks/grid.py — 报告区表格体检: 行列数/行高采样/文本溢出。

检查项:
  grid.empty            渲染行数=0 → error "空表格"(若模板声明了查询按钮, 先自动触发一次查询再复测)
  grid.row_height       行高采样 vs cpt 声明 RowHeight 偏差>5% → warn(evidence 带行号 声明/实测)
  grid.overflow         单元格文本溢出(scrollWidth>clientWidth+2)计数>0 → warn
  grid.runtime_only     facts 缺失 → 只报运行期指标(info)

单位: cpt RowHeight 为 EMU, px = emu/914400*96。渲染行可能因数据扩展多于声明,
故对采样行取"与任一声明行高 5% 内匹配", 全不匹配才 warn(避免扩展展开误报)。
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

import json
import os
import sys

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

EMU_PER_INCH = 914400.0
REF_DPI = 96.0
ROW_TOL = 0.05          # 行高偏差 5%
MAX_ROW_WARNS = 5       # 行高 warn 上限
SAMPLE_ROWS = 20
QUERY_WAIT_MS = 20000   # 触发查询后等待渲染


def _ev(s):
    return str(s)[:300]


def _fact(ctx):
    f = getattr(ctx, "facts", None)
    if f and f.get("row_heights") is not None:
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


def _has_query_button(facts):
    return any(not w["name"].startswith("lb_") and w["class"] in ("FreeButton", "FormSubmitButton")
               for w in (facts.get("widgets") or []))


def _click_query(frame_or_page):
    """触发查询: 优先 FR API contentPane.parameterCommit() / _g().parameterCommit(),
    兜底点 FR 自定义按钮 #fr-btn-QUERY / [widgetname=QUERY]。返回 True 表示已尝试。"""
    js = """() => { try {
        var cp = window.contentPane;
        if (cp && typeof cp.parameterCommit === 'function') { cp.parameterCommit(); return 'api'; }
        if (typeof window._g === 'function') { var g = _g(); if (g && g.parameterCommit) { g.parameterCommit(); return 'api-g'; } }
      } catch(e) {}
      try {
        var btn = document.querySelector('#fr-btn-QUERY') || document.querySelector('[widgetname=QUERY]');
        if (btn) { btn.click(); return 'dom'; }
      } catch(e) {}
      return 'none'; }"""
    try:
        target = frame_or_page
        res = target.evaluate(js)
        return res in ("api", "api-g", "dom")
    except Exception:
        return False


def run(ctx):
    out = []
    facts = _fact(ctx)
    declared = facts.get("row_heights") or []
    page = ctx.page
    timeout_ms = int(getattr(ctx, "timeout", 30) * 1000)

    frame = _get_frame(ctx, page)
    gm = fr_api.grid_metrics(frame, SAMPLE_ROWS) if frame is not None else None
    if gm is None and page is not None:
        gm = fr_api.grid_metrics(page.main_frame, SAMPLE_ROWS)

    if gm is None:
        out.append({"check": "grid.probe_failed", "level": "info",
                    "message": "无法测取报告区表格指标(页面未渲染或脚本不可达)",
                    "evidence": _ev("frame=%s url=%s" % ("-" if frame is None else frame.url[:80],
                                                        str(getattr(ctx, "url", ""))[:120]))})
        return out

    rows = gm.get("rows") or 0

    # 空表格: 先自动触发一次查询再复测。
    # 2026-09-04 迭代: 不再要求模板声明查询按钮——无按钮的参数面板页(delayPlaying/showWindow)
    # 同样需要 parameterCommit 才首渲染(实测下钻页 bu/region/plant 必填校验拦截首渲, 提交后 21 格渲染)。
    if rows == 0:
        target = frame if frame is not None else page.main_frame
        tried = _click_query(target)
        if not tried and page is not None:
            # contentPane 可能不在报告 frame——逐 frame 尝试提交（2026-09-04 实测多 frame 场景）
            for f in page.frames:
                try:
                    if f.evaluate("typeof contentPane !== 'undefined' || (typeof _g === 'function' && _g && _g().parameterCommit)"):
                        tried = _click_query(f)
                        if tried:
                            target = f
                            break
                except Exception:
                    continue
        if tried:
            try:
                page.wait_for_timeout(min(QUERY_WAIT_MS, max(timeout_ms, 5000)))
            except Exception:
                pass
            gm2 = fr_api.grid_metrics(target, SAMPLE_ROWS)
            if gm2:
                gm = gm2
                rows = gm.get("rows") or 0

    if rows == 0:
        out.append({"check": "grid.empty", "level": "error",
                    "message": "空表格: 报告区渲染行数=0",
                    "evidence": _ev("url=%s rows=0 tds=%d%s" % (
                        str(getattr(ctx, "url", ""))[:120],
                        gm.get("td_total") or 0,
                        "(已自动触发查询仍为空)" if _has_query_button(facts) else ""))})
        return out

    # 行高采样 vs 声明(先估整体缩放: FR 自适应会把整表等比缩放, 需补偿后再判偏差)
    if declared:
        declared_px = [cpt_facts.emu_to_px(v) for v in declared]
        declared_px = [d for d in declared_px if d]
        sampled = gm.get("row_heights") or []
        # 全(h,d)对比值做直方图, 取最密 bin 中心 = 页面缩放估计(避免逐行"最近声明"错配)
        ratios = [h / d for h in sampled for d in declared_px if 0.3 <= h / d <= 1.6]
        scale = 1.0
        if ratios:
            best_bin, best_cnt = 1.0, -1
            step = 0.02
            for r in ratios:
                lo = max(0.3, r - 0.05)
                cnt = sum(1 for x in ratios if lo <= x <= r + 0.05)
                if cnt > best_cnt or (cnt == best_cnt and abs(r - 1.0) < abs(best_bin - 1.0)):
                    best_cnt, best_bin = cnt, r
            scale = best_bin
        scaled_note = ""
        if ratios and abs(scale - 1.0) > 0.08:
            scaled_note = "(页面等比缩放~%.2f, 已补偿)" % scale
        bad = []
        for i, h in enumerate(sampled):
            ok = any(abs(h - d * scale) <= max(d * scale * ROW_TOL, 1.0) for d in declared_px)
            if not ok:
                dpx_near = min(declared_px, key=lambda d: abs(h - d * scale), default=None) if declared_px else None
                bad.append((i, h, dpx_near if dpx_near else 0.0))
        if bad:
            out.append({"check": "grid.row_height", "level": "warn",
                        "message": "行高与声明偏差>5%%: 采样 %d 行中 %d 行不匹配%s" % (
                            len(sampled), len(bad), scaled_note),
                        "evidence": _ev("; ".join("行%d 实测%.1fpx 声明%.1fpx(缩放后%.1f)" % (
                            i, h, dpx, dpx * scale) for i, h, dpx in bad[:MAX_ROW_WARNS])),
                        "hint": "若为数据扩展行则可能是模板扩展行高; 若为首行请对照 RowHeight CDATA"})
    else:
        out.append({"check": "grid.runtime_only", "level": "info",
                    "message": "facts 缺失, 仅报运行期指标",
                    "evidence": _ev("rows=%d cols=%s row_heights=%s" % (
                        rows, gm.get("cols"), json.dumps((gm.get("row_heights") or [])[:10])))})

    # 文本溢出
    ovf = gm.get("overflow_count") or 0
    if ovf > 0:
        samples = "; ".join("行%d列%d'%s'" % (s["row"], s["col"], s["text"]) for s in gm.get("overflow_samples") or [])
        out.append({"check": "grid.overflow", "level": "warn",
                    "message": "单元格文本溢出 %d 处(scrollWidth>clientWidth+2)" % ovf,
                    "evidence": _ev("样例: %s" % samples),
                    "hint": "调列宽/缩小字号/开启单元格缩淡"})

    if not out or all(o["check"] == "grid.runtime_only" for o in out):
        out.append({"check": "grid.ok", "level": "info",
                    "message": "表格体检通过: %d 行 %d 列, 无溢出%s" % (
                        rows, gm.get("cols") or 0,
                        ", 行高与声明一致" if declared else ""),
                    "evidence": _ev("rows=%d tds=%d 采样行高=%s" % (
                        rows, gm.get("td_total") or 0, json.dumps((gm.get("row_heights") or [])[:8])))})
    return out
