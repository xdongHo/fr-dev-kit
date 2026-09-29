#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preview_skeleton.py — 结构预览生成器（skeleton backend）

从模板 XML 生成**布局骨架 HTML**（非引擎渲染）：
- FRM: BoundsAttr(x,y,w,h) → 绝对定位 div（含组件类名/名称）
- CPT: CellElementList → 表格网格（静态文本直出、图表格渲染占位框）
- 参数面板: ParameterUI 控件盒

⚠ 定位声明: 这是「结构预览」——不执行公式/数据集计算，图表只画占位框。
真实验证请用 java/injected backend（引擎渲染）。本产物用于:
1) 离线快速目检布局  2) render_check.py 断言层的已知产物校准
"""
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from expect_manifest import extract_manifest, _local  # noqa: E402

CSS = """<!DOCTYPE html><html><head><meta charset="utf-8">
<title>%(title)s — 结构预览(skeleton)</title>
<style>
 body{font:12px "Microsoft YaHei",sans-serif;margin:16px;background:#f5f6f8}
 h1{font-size:15px} .note{color:#888;font-size:11px;margin-bottom:10px}
 .canvas{position:relative;background:#fff;border:1px solid #ccc;box-shadow:0 1px 3px rgba(0,0,0,.12)}
 .wgt{position:absolute;border:1px solid #4a90d9;background:#eaf3fc;overflow:hidden;
      display:flex;align-items:center;justify-content:center;text-align:center;
      font-size:11px;color:#246;word-break:break-all}
 .wgt.chart{border-color:#d97a4a;background:#fdf0e9;color:#842}
 .wgt.layout{border-style:dashed;border-color:#aaa;background:#fafafa;color:#666}
 table.cpt{border-collapse:collapse;table-layout:fixed}
 td{border:1px solid #c8d4e0;height:24px;min-width:64px;vertical-align:top;padding:2px 4px;font-size:11px}
 td.chart{background:#fdf0e9;color:#842;text-align:center}
 .panel{border:1px dashed #7a4ad9;background:#f3edfc;padding:6px;margin:8px 0;color:#543}
 .panel .ctl{display:inline-block;border:1px solid #7a4ad9;background:#fff;margin:3px;padding:2px 8px;font-size:11px}
</style></head><body>
<h1>%(title)s</h1>
<div class="note">skeleton 结构预览 — 非引擎渲染：不做公式/数据计算，图表为占位框。
数据集 %(nds)d 个（内嵌 %(emb)d）· 图表 %(charts)d · 参数 %(nparams)d</div>
"""


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_frm(m, root):
    """FRM: 绝对定位画布"""
    if not m.get("frm") or not m["frm"]["widgets"]:
        return '<div class="note">（无 BoundsWidget 组件）</div>'
    maxw = max(w["bounds"]["x"] + w["bounds"]["width"] for w in m["frm"]["widgets"] if w["bounds"])
    maxh = max(w["bounds"]["y"] + w["bounds"]["height"] for w in m["frm"]["widgets"] if w["bounds"])
    parts = ['<div class="canvas" style="width:%dpx;height:%dpx">' % (maxw, maxh)]
    for w in m["frm"]["widgets"]:
        b = w["bounds"]
        if not b:
            continue
        is_chart = "chart" in (w["class"] or "").lower() or "ChartEditor" in (w["full_class"] or "")
        cls = "wgt chart" if is_chart else ("wgt layout" if "Layout" in (w["class"] or "") else "wgt")
        label = esc(w["name"] or w["class"])
        if w.get("plugin"):
            label += "<br><small>%s</small>" % esc(w["plugin"].rsplit(".", 1)[-1])
        parts.append('<div class="%s" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">%s</div>'
                     % (cls, b["x"], b["y"], b["width"], b["height"], label))
    parts.append("</div>")
    return "".join(parts)


def render_cpt(m, root):
    """CPT: 单元格网格表（静态文本/图表占位/空格）"""
    grid = m["grid"]
    chart_cells = set()
    for el in root.iter():
        if _local(el.tag) == "C":
            has_chart = any(_local(x.tag) in ("Chart", "ChartCollection", "ChartAttr") for x in el.iter())
            if has_chart:
                chart_cells.add((int(el.get("c", "-1")), int(el.get("r", "-1"))))
    texts = {tuple(int(x) for x in t["cell"].split(",")): t["text"] for t in grid["static_texts"]}
    parts = ['<table class="cpt">']
    for r in range(min(grid["max_row"], 60)):
        parts.append("<tr>")
        for c in range(min(grid["max_col"], 40)):
            if (c, r) in chart_cells:
                parts.append('<td class="chart" colspan="2">📊 图表</td>')
            elif (c, r) in texts:
                parts.append("<td><b>%s</b></td>" % esc(texts[(c, r)]))
            else:
                parts.append("<td></td>")
        parts.append("</tr>")
    parts.append("</table>")
    return "".join(parts)


def render_panel(m, root):
    """参数面板控件盒"""
    if not m["params"]["parameter_ui"]:
        return ""
    ctrls = []
    for el in root.iter():
        if _local(el.tag) == "Widget" and el.get("class"):
            nm = el.find("WidgetName")
            ctrls.append((el.get("class", "").rsplit(".", 1)[-1], nm.get("name") if nm is not None else ""))
    if not ctrls:
        return ""
    parts = ['<div class="panel">参数面板(%d 控件): ' % len(ctrls)]
    parts.extend('<span class="ctl">%s%s</span>' % (esc(t), (" :" + esc(n)) if n else "")
                 for t, n in ctrls[:30])
    parts.append("</div>")
    return "".join(parts)


def generate(tpl_path):
    content = open(tpl_path, encoding="utf-8").read()
    import re
    root = ET.fromstring(re.sub(r"<!DOCTYPE[^>]*>", "", content))
    m = extract_manifest(tpl_path)
    nds = len(m["datasets"]); emb = sum(1 for d in m["datasets"] if d["embedded"])
    html = [CSS % {"title": esc(m["file"]), "nds": nds, "emb": emb,
                   "charts": m["charts"]["chart_total"], "nparams": len(m["params"]["parameters"])}]
    html.append(render_panel(m, root))
    html.append(render_frm(m, root) if m["kind"] == "frm" else render_cpt(m, root))
    html.append("</body></html>")
    return "".join(html)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python preview_skeleton.py <cpt|frm> [out.html]"); sys.exit(2)
    out = generate(sys.argv[1])
    dest = sys.argv[2] if len(sys.argv) > 2 else None
    if dest:
        open(dest, "w", encoding="utf-8").write(out)
        print(f"skeleton 预览: {dest} ({len(out)}B)")
    else:
        sys.stdout.write(out)
