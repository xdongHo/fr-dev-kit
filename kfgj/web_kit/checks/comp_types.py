# -*- coding: utf-8 -*-
"""checks/comp_types.py — 全类型组件枚举与分布(2026-09-12 web_kit 扩容)。
对照 jsdoc 前端接口(http://dev.fanruan.com/jsdoc/ FR.*/FS.* 系列): 设计器渲染的组件容器
远不止文本/参数控件——表格块(ElementCaseEditor)、图表(ChartEditor)、Tab/手风琴/卡片容器、
标题容器(WTitleLayout)等都是大屏/决策报表的主力内容。本模块把它们全部枚举并对照运行期命中。

检查项:
  comptypes.skip            无声明控件 → info 跳过
  comptypes.distribution    类分布(声明 n / 运行期命中 n) → info
  comptypes.missing_types   某类声明控件运行期 0 命中 → warn(渲染缺失或类型不受 DOM/API 支持)
  comptypes.locate          jsdoc API 定位证明(getWidgetByName + [widgetname] DOM 双通道) → info

数据源: cpt_facts.widgets[].class(声明类, frm/cpt 通用) × fr_api.list_widgets/dom_widgets(运行期)。
"""
# --- console-safe guard ---
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

import collections
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from checks import widgets as _w
except Exception:
    import widgets as _w

try:
    from checks import fr_api
except Exception:
    import fr_api

CONTAINER_CLASSES = {
    "WTabLayout": "Tab容器", "WCardLayout": "卡片容器", "WAccordionLayout": "手风琴容器",
    "WFitLayout": "自适应布局", "WBorderLayout": "边框布局", "WGridLayout": "网格布局",
    "WHorizontalBoxLayout": "横向盒布局", "WVerticalBoxLayout": "纵向盒布局",
    "WTitleLayout": "标题容器", "WAbsoluteBodyLayout": "绝对布局体",
    "WParameterLayout": "参数面板", "WAbsoluteLayout": "绝对布局",
}

def classify(cls):
    short = (cls or "").split(".")[-1]
    if short in CONTAINER_CLASSES:
        return "容器:" + CONTAINER_CLASSES[short]
    if "Chart" in short:
        return "图表"
    if "ElementCase" in short:
        return "表格块"
    if short.endswith("Editor"):
        return "编辑器/参数控件"
    if "Button" in short:
        return "按钮"
    if short.endswith("Label"):
        return "文本"
    if "Tree" in short:
        return "树控件"
    if short.endswith("Layout"):
        return "容器:其他"
    return "其他:" + (short or "?")

def run(ctx):
    out = []
    facts = _w._fact(ctx)
    declared = facts.get("widgets") or []
    if not declared:
        out.append({"check": "comptypes.skip", "level": "info",
                    "message": "无声明控件, 跳过组件类型分布",
                    "evidence": _w._ev("cpt_facts.widgets 为空: %s" % facts.get("path", "?"))})
        return out

    page = ctx.page
    frame = _w._get_frame(ctx, page)
    names = [w["name"] for w in declared]
    lw = None
    try:
        lw = fr_api.list_widgets(frame, names) if frame is not None else None
        if lw is None and page is not None:
            lw = fr_api.list_widgets(page.main_frame, names)
    except Exception:
        lw = None
    dom = []
    try:
        dom = fr_api.dom_widgets(frame if frame is not None else page.main_frame) or []
    except Exception:
        dom = []
    dom_by = {str(d.get("name", "")).lower(): d for d in dom if d.get("name")}
    rt_found = {str(w.get("name", "")).lower() for w in (lw.get("widgets") or [])
                if w.get("name") and w.get("found", True)} | set(dom_by)

    dist_declared = collections.Counter()
    dist_runtime = collections.Counter()
    missing = collections.defaultdict(list)
    for d in declared:
        cat = classify(d.get("class"))
        dist_declared[cat] += 1
        nl = str(d.get("name", "")).lower()
        if nl in rt_found:
            dist_runtime[cat] += 1
        else:
            missing[cat].append(d.get("name", "?"))

    lines = ["%s: 声明%d/运行期%d" % (cat, n, dist_runtime.get(cat, 0))
             for cat, n in sorted(dist_declared.items())]
    out.append({"check": "comptypes.distribution", "level": "info",
                "message": "组件类型分布: %d 类 / %d 个控件(容器 %d)" % (
                    len(dist_declared), len(declared),
                    sum(n for cat, n in dist_declared.items() if cat.startswith("容器"))),
                "evidence": _w._ev(" | ".join(lines))})

    for cat, names in sorted(missing.items()):
        if names:
            out.append({"check": "comptypes.missing_types", "level": "warn",
                        "message": "类 '%s' 声明 %d 个运行期 0 命中" % (cat, len(names)),
                        "evidence": _w._ev(", ".join(names)[:280]),
                        "hint": "渲染缺失, 或该类控件不经 [widgetname]/getWidgetByName 通道(对照 jsdoc 定位 API)"})

    located = len([w for w in (lw.get("widgets") or []) if w.get("found")]) if lw else len(dom_by)
    out.append({"check": "comptypes.locate", "level": "info",
                "message": "jsdoc API 定位证明: getWidgetByName/DOM 命中 %d/%d" % (located, len(declared)),
                "evidence": _w._ev("contentPane.getWidgetByName + [widgetname] DOM 双通道; 容器类详见 containers 检查")})
    return out
