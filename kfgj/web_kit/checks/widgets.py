# -*- coding: utf-8 -*-
"""checks/widgets.py — 参数面板体检: 声明(cpt_facts) vs 运行期(fr_api) 对照。

检查项:
  widgets.skip          无参数面板 → info 跳过
  widgets.api_failed    FR API+DOM 都无法枚举 → info(环境受限, 不误报)
  widgets.missing       声明了但页面找不到 → error
  widgets.zero_size     宽或高=0(声明或渲染) → error
  widgets.overlap       两两矩形相交面积>4px² → error(evidence 带两名+坐标); 完全包含对(容器含子件)跳过
  widgets.label_shift   label(lb_*) 与相邻控件 y 差>4px → warn
  widgets.out_of_panel  越出面板可视宽 → error

run(ctx) -> list[finding]; finding = {check, level, message, evidence(≤300), hint?}
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
    from checks import fr_api  # 包模式
except Exception:
    import fr_api  # 平铺模式

try:
    import cpt_facts
except Exception:
    sys.path.insert(0, _ROOT)
    import cpt_facts

MAX_OVERLAP_ERRORS = 10          # 重叠 error 上限, 其余并入 summary
LABEL_TOL_PX = 4.0
OVERLAP_MIN_AREA = 4.0           # px²
PANEL_TOL_PX = 2.0


def _fact(ctx):
    """取 facts; 缺失时按 cpt_path 现场解析(鸭子类型自包含)。"""
    f = getattr(ctx, "facts", None)
    if f and f.get("widgets") is not None:
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


def _inter_area(a, b):
    dx = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    dy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return dx * dy if dx > 0 and dy > 0 else 0.0


def _ev(s):
    return str(s)[:300]


def run(ctx):
    out = []
    facts = _fact(ctx)
    declared = facts.get("widgets") or []
    if not declared:
        out.append({"check": "widgets.skip", "level": "info",
                    "message": "无参数面板声明控件, 跳过面板体检",
                    "evidence": _ev("cpt_facts.widgets 为空: %s" % facts.get("path", "?"))})
        return out

    page = ctx.page
    frame = _get_frame(ctx, page)
    names = [w["name"] for w in declared]
    # 依次试报告 frame / 主页面
    lw = fr_api.list_widgets(frame, names) if frame is not None else None
    if lw is None and page is not None:
        lw = fr_api.list_widgets(page.main_frame, names)

    # 运行期校验状态(FR getErrorMsg): 必填未填/值不在字典内等——页面级体检高价值信号
    # (2026-09-04 实测: 下钻页 bu/region/plant"不能为空"、entity"值不在下拉列表内"拦截首渲染)
    # 2026-09-05 R27: 声明名注入 fr_api(cpt facts → names 参数), 替代原硬编码 para_* 兜底名单
    try:
        verrs = fr_api.widget_validation_errors(
            frame if frame is not None else page.main_frame, names)
        for wname, emsg in (verrs or []):
            out.append({"check": "widgets.validation", "level": "warn",
                        "message": "控件 [%s] 运行期校验未过: %s" % (wname, emsg),
                        "evidence": "widget=%s errMsg=%s" % (wname, emsg),
                        "hint": "必填控件需先填值/URL 注入值需在字典内, 否则面板拦截首渲染"})
    except Exception:
        pass
    if lw is None or not lw.get("widgets"):
        out.append({"check": "widgets.api_failed", "level": "info",
                    "message": "无法枚举面板控件(FR API getWidgetByName 与 DOM [widgetname] 均未命中)",
                    "evidence": _ev("frame=%s 声明=%d" % (getattr(frame, "url", "-")[:80], len(declared)))})
        return out

    rt = {w["name"].lower(): w for w in lw["widgets"] if w.get("name")}
    dom = fr_api.dom_widgets(frame if frame is not None else page.main_frame) or []
    dom_by_name = {d["name"].lower(): d for d in dom}

    panel_rect = (lw.get("panel") or {}).get("rect")
    panel_w = (lw.get("panel") or {}).get("width")
    if panel_rect is None and dom:
        dom_panel = fr_api.panel_rect(frame if frame is not None else page.main_frame)
        panel_rect = dom_panel

    missing, zero, oop = [], [], []
    rects = {}
    for d in declared:
        n, nl = d["name"], d["name"].lower()
        r = rt.get(nl)
        if not r or not r.get("found"):
            dd = dom_by_name.get(nl)
            if dd:
                r = {"name": n, "found": True, "rect": dd.get("rect"), "type": "dom"}
            else:
                missing.append(n)
                continue
        rect = r.get("rect")
        if rect:
            rects[n] = rect
        # 零尺寸: 声明或运行期
        dw, dh = d.get("w"), d.get("h")
        if rect and (rect["w"] <= 0 or rect["h"] <= 0):
            zero.append("%s 渲染 %dx%d" % (n, rect["w"], rect["h"]))
        elif not rect and (dw == 0 or dh == 0):
            zero.append("%s 声明 %gx%g" % (n, dw, dh))
        # 越出面板可视宽
        if rect and panel_rect:
            if rect["x"] + rect["w"] > panel_rect["x"] + panel_rect["w"] + PANEL_TOL_PX:
                oop.append("%s 右缘%d > 面板右缘%d" % (n, rect["x"] + rect["w"],
                                                     panel_rect["x"] + panel_rect["w"]))

    for n in missing:
        out.append({"check": "widgets.missing", "level": "error",
                    "message": "控件声明于模板但页面未找到: %s" % n,
                    "evidence": _ev("声明控件 %s 不在运行期 getWidgetByName/DOM [widgetname] 中" % n)})

    if zero:
        out.append({"check": "widgets.zero_size", "level": "error",
                    "message": "控件零尺寸 %d 个" % len(zero),
                    "evidence": _ev("; ".join(zero[:5]))})

    # 两两相交（2026-09-11: 完全包含对跳过——frm 布局容器(body 等)包含子件是正常结构,
    # 只有兄弟件部分相交才是真缺陷; 全包含判据含 2px 容差）
    def _contains(big, small):
        tol = 2
        return (big["x"] - tol <= small["x"] and big["y"] - tol <= small["y"]
                and big["x"] + big["w"] + tol >= small["x"] + small["w"]
                and big["y"] + big["h"] + tol >= small["y"] + small["h"])

    names2 = list(rects)
    overlaps = []
    for i in range(len(names2)):
        for j in range(i + 1, len(names2)):
            a, b = rects[names2[i]], rects[names2[j]]
            area = _inter_area(a, b)
            if area > OVERLAP_MIN_AREA and not (_contains(a, b) or _contains(b, a)):
                overlaps.append((names2[i], names2[j], area, a, b))
    for k, (na, nb, area, a, b) in enumerate(overlaps):
        if k >= MAX_OVERLAP_ERRORS:
            out.append({"check": "widgets.overlap", "level": "error",
                        "message": "控件重叠共 %d 对(仅展示前 %d)" % (len(overlaps), MAX_OVERLAP_ERRORS),
                        "evidence": _ev("; ".join("%s×%s %.0fpx²" % (x[0], x[1], x[2]) for x in overlaps[:MAX_OVERLAP_ERRORS]))})
            break
        out.append({"check": "widgets.overlap", "level": "error",
                    "message": "控件重叠: %s × %s (相交 %.0fpx²)" % (na, nb, area),
                    "evidence": _ev("%s(%d,%d,%dx%d) %s(%d,%d,%dx%d)" % (
                        na, a["x"], a["y"], a["w"], a["h"], nb, b["x"], b["y"], b["w"], b["h"]))})

    # label 与相邻控件 y 错位
    label_shifts = []
    for d in declared:
        if not d["name"].startswith("lb_"):
            continue
        lr = rects.get(d["name"])
        if not lr:
            continue
        lc_y = lr["y"] + lr["h"] / 2.0
        best, best_d = None, None
        for d2 in declared:
            if d2["name"] == d["name"] or d2["name"].startswith("lb_"):
                continue
            cr = rects.get(d2["name"])
            if not cr:
                continue
            cc_y = cr["y"] + cr["h"] / 2.0
            dist = abs(cc_y - lc_y)
            if best_d is None or dist < best_d:
                best, best_d = (d2["name"], cc_y, cr), dist
        if best is not None and best_d > LABEL_TOL_PX:
            label_shifts.append("%s vs %s Δy=%.0fpx" % (d["name"], best[0], best_d))
    if label_shifts:
        out.append({"check": "widgets.label_shift", "level": "warn",
                    "message": "label 与相邻控件垂直错位>%.0fpx 共 %d 个" % (LABEL_TOL_PX, len(label_shifts)),
                    "evidence": _ev("; ".join(label_shifts[:5])),
                    "hint": "对齐 lb_* 与控件 y(声明 BoundsAttr y 应同排)"})

    for s in oop:
        out.append({"check": "widgets.out_of_panel", "level": "error",
                    "message": "控件越出面板可视宽: %s" % s,
                    "evidence": _ev("panel.rect=%s" % json.dumps(panel_rect) if panel_rect else "panel 不可测")})

    if not any(o["check"] != "widgets.skip" for o in out):
        out.append({"check": "widgets.ok", "level": "info",
                    "message": "面板体检通过: %d 声明控件全部找到, 无重叠/零尺寸/越界/错位" % len(declared),
                    "evidence": _ev("declared=%d found=%d rects=%d" % (len(declared), len(rt), len(rects)))})
    return out
