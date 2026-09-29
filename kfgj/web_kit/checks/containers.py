# -*- coding: utf-8 -*-
"""checks/containers.py — 布局/面板容器感知检查(2026-09-12 web_kit 扩容)。
对照 jsdoc 前端接口 FR.*/FS.* 容器系列(FR.CardLayout/FR.TableLayout/FR.PagePane/FR.Panel/
FS.Accordion/FS.LTabPane/FS.InsideTabPane/FS.QuickTab/FS.TablePane): 决策报表大屏的
主体内容由这些容器承载, 原有检查(几何/运行时错误)对它们零覆盖。

检查项:
  containers.skip          目标无容器类控件(纯 cpt 表格) → info 跳过
  containers.inventory     容器清单(类/控件名/渲染矩形) → info
  containers.title         WTitleLayout 标题文本为空 → warn
  containers.tab           WTabLayout: DOM tab 页计数 → info
  containers.chart         ChartEditor 声明数 vs fr_api.chart_list 运行期图数 → warn 失配
  containers.elementcase   ElementCaseEditor 声明数 vs 渲染矩形 → warn 零尺寸

数据源: cpt_facts.widgets[].class × fr_api.dom_widgets/chart_list。
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

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from checks import widgets as _w
    from checks import fr_api
except Exception:
    import widgets as _w
    import fr_api

LAYOUTS = ("WTabLayout", "WCardLayout", "WAccordionLayout", "WFitLayout",
           "WBorderLayout", "WGridLayout", "WTitleLayout", "WAbsoluteBodyLayout",
           "WParameterLayout", "WAbsoluteLayout")

def _short(cls):
    return (cls or "").split(".")[-1]

def run(ctx):
    out = []
    facts = _w._fact(ctx)
    declared = facts.get("widgets") or []
    containers = [d for d in declared if _short(d.get("class")) in LAYOUTS]
    charts = [d for d in declared if "Chart" in _short(d.get("class"))]
    cases = [d for d in declared if "ElementCase" in _short(d.get("class"))]
    if not containers and not charts and not cases:
        out.append({"check": "containers.skip", "level": "info",
                    "message": "无容器/图表/表格块类控件(经典 cpt 表格), 容器检查跳过",
                    "evidence": _w._ev("cpt=%s" % facts.get("path", "?"))})
        return out

    page = ctx.page
    frame = _w._get_frame(ctx, page)
    dom = []
    try:
        dom = fr_api.dom_widgets(frame if frame is not None else page.main_frame) or []
    except Exception:
        dom = []
    dom_by = {str(d.get("name", "")).lower(): d for d in dom if d.get("name")}

    def rect_of(name):
        d = dom_by.get(str(name).lower())
        if not d:
            return None
        try:
            return (int(d.get("x", 0)), int(d.get("y", 0)), int(d.get("w", 0)), int(d.get("h", 0)))
        except Exception:
            r = d.get("rect")
            return tuple(r) if r else None

    # inventory
    inv = []
    for d in containers + charts + cases:
        r = rect_of(d.get("name"))
        inv.append("%s[%s] %s" % (_short(d.get("class")), d.get("name", "?"),
                                  ("渲染@%s" % (r,)) if r else "未命中DOM"))
    out.append({"check": "containers.inventory", "level": "info",
                "message": "容器/图表/表格块清单: 容器 %d · 图表 %d · 表格块 %d" % (
                    len(containers), len(charts), len(cases)),
                "evidence": _w._ev(" | ".join(inv))})

    # WTitleLayout 标题文本
    for d in containers:
        if _short(d.get("class")) != "WTitleLayout":
            continue
        wn = d.get("name", "")
        if wn.lower().startswith("chart"):
            out.append({"check": "containers.title", "level": "info",
                        "message": "图表标题容器 [%s] 文本为空——图表自带标题栏, 属正常" % wn,
                        "evidence": _w._ev("FR 图表命名惯例: chart0/chart1=图表容器")})
            continue
        txt = ""
        try:
            txt = (frame.evaluate("(n)=>{const e=document.querySelector('[widgetname=\"'+n.toUpperCase()+'\"]');"
                                  "return e?(e.innerText||'').trim():'';}", wn) if frame is not None else "")
        except Exception:
            txt = ""
        if txt:
            out.append({"check": "containers.title", "level": "info",
                        "message": "标题容器 [%s] 文本: %s" % (wn, txt[:60]),
                        "evidence": _w._ev(wn)})
        else:
            out.append({"check": "containers.title", "level": "warn",
                        "message": "标题容器 [%s] 文本为空(标题容器应有文案)" % wn,
                        "hint": "WTitleLayout 需绑定标题文本或引用参数"})

    # WTabLayout: DOM tab 计数
    for d in containers:
        if _short(d.get("class")) != "WTabLayout":
            continue
        wn = str(d.get("name", ""))
        try:
            n_tabs = frame.evaluate("(n)=>{const e=document.querySelector('[widgetname=\"'+n.toUpperCase()+'\"]');"
                                    "return e?e.querySelectorAll('.fr-tab-pane,[class*=tabpane],[class*=tab-pane]').length:-1;}", wn) \
                if frame is not None else -1
            out.append({"check": "containers.tab", "level": "info",
                        "message": "Tab容器 [%s] DOM tab 页数: %s" % (wn, n_tabs),
                        "evidence": _w._ev("jsdoc FS.LTabPane/FS.InsideTabPane 对应容器")})
        except Exception:
            pass

    # ChartEditor: 声明数 vs 运行期图数
    if charts:
        declared_n = len(charts)
        runtime_n = None
        try:
            cl = fr_api.chart_list(frame if frame is not None else page.main_frame)
            runtime_n = len(cl) if cl is not None else None
        except Exception:
            runtime_n = None
        if runtime_n is None:
            out.append({"check": "containers.chart", "level": "info",
                        "message": "图表: 声明 %d 个, 运行期图数不可得(FR.Chart API 受限)" % declared_n,
                        "evidence": _w._ev("jsdoc FR.Chart.WebUtils.getChart")})
        elif runtime_n < declared_n:
            out.append({"check": "containers.chart", "level": "warn",
                        "message": "图表加载失配: 声明 %d, 运行期 %d" % (declared_n, runtime_n),
                        "hint": "图表容器未渲染/图表 id 未注册(FR.Chart.WebUtils.getChart 逐个定位)"})
        else:
            out.append({"check": "containers.chart", "level": "info",
                        "message": "图表: 声明 %d, 运行期 %d 全部加载" % (declared_n, runtime_n)})

    # ElementCaseEditor: 零尺寸检测
    for d in cases:
        r = rect_of(d.get("name"))
        if r is None:
            out.append({"check": "containers.elementcase", "level": "warn",
                        "message": "表格块 [%s] 未命中 DOM 渲染" % d.get("name", "?"),
                        "hint": "ElementCaseEditor 需在决策报表内渲染(检查所属容器是否隐藏)"})
        elif r[2] == 0 or r[3] == 0:
            out.append({"check": "containers.elementcase", "level": "warn",
                        "message": "表格块 [%s] 零尺寸渲染 %r" % (d.get("name", "?"), r)})
        else:
            out.append({"check": "containers.elementcase", "level": "info",
                        "message": "表格块 [%s] 渲染 %r" % (d.get("name", "?"), r)})
    return out
