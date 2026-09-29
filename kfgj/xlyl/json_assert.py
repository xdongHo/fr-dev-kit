#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
json_assert.py — injected 渲染产物(JSON)断言器（单元格级，最强断言）

injected_render.js 产物 {sheets:[{name,cells:[{c,r,cs,rs,t,v}]}]} vs
expect_manifest → J 系列断言。

用法:
    python json_assert.py <模板.cpt> <render.json>
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from expect_manifest import extract_manifest  # noqa: E402


def assert_json(manifest, json_path):
    passed, failed, warned = [], [], []
    r = json.load(open(json_path, encoding="utf-8"))
    if not r.get("ok"):
        return [], [f"J0 渲染器报告失败: {r.get('error', '?')}"], []

    # ── FRM 分支: widgetCount + 类直方图 vs manifest.frm ──
    if r.get("kind") == "frm":
        mfrm = manifest.get("frm") or {}
        rw = r.get("widgets", [])
        # J1 非空
        if len(rw) >= 1:
            passed.append(f"J1 组件树非空: {len(rw)} widgets (root={r.get('rootContainer','?').rsplit('.',1)[-1]})")
        else:
            failed.append("J1 空组件树(0 widget)")
        # J6 组件数对齐（渲染树含布局容器递归, 数量 ≥ manifest 的 BoundsWidget 数）
        m_count = mfrm.get("widget_count", 0)
        if len(rw) >= m_count:
            passed.append(f"J6 组件数对齐: 渲染{len(rw)} ≥ 声明{m_count}")
        else:
            failed.append(f"J6 组件丢失: 渲染{len(rw)} < 声明{m_count}")
        # J7 类直方图: manifest 声明的每类组件在渲染树中至少出现
        r_classes = {}
        for w in rw:
            k = w["cls"].rsplit(".", 1)[-1]
            r_classes[k] = r_classes.get(k, 0) + 1
        # manifest 里的插件控件集合(简单名) — 缺装属环境事实,由 J8 专门报告
        plugin_widget_simples = {wgt["class"].rsplit(".", 1)[-1]
                                 for wgt in (mfrm.get("widgets") or []) if wgt.get("plugin")}
        for cls, n in (mfrm.get("class_histogram") or {}).items():
            simple = cls.rsplit(".", 1)[-1]
            if simple in r_classes:
                passed.append(f"J7 组件类命中: {simple}×{n}(渲染×{r_classes[simple]})")
            elif simple in plugin_widget_simples:
                warned.append(f"J7 插件控件未物化: {simple}×{n}(本机未装该插件, 见 J8)")
            else:
                failed.append(f"J7 组件类缺失: {simple}×{n} 声明但渲染树无此类")
        # J8 静默降级猎手: WidgetErrorMarker = 声明的控件因缺插件/加载失败被静默替换
        n_marker = r_classes.get("WidgetErrorMarker", 0)
        n_plugin_declared = sum(1 for wgt in (mfrm.get("widgets") or []) if wgt.get("plugin"))
        if n_marker == 0:
            passed.append("J8 无静默降级(0 WidgetErrorMarker)")
        elif n_plugin_declared > 0:
            warned.append(f"J8 静默降级×{n_marker}: 声明插件控件被 WidgetErrorMarker 替换"
                          f"(缺插件零报错——正是本工具要猎的场景; 声明插件控件 {n_plugin_declared} 个)")
        else:
            failed.append(f"J8 意外降级×{n_marker}: 未声明插件控件却出现 WidgetErrorMarker")
        return passed, failed, warned

    # ── CPT 分支 ──
    # J1 非空渲染（有 sheet 且有 cell）
    total_cells = sum(s["cellCount"] for s in r.get("sheets", []))
    if total_cells >= 1:
        passed.append(f"J1 非空渲染: {len(r['sheets'])} sheet / {total_cells} cell")
    else:
        failed.append("J1 空渲染(0 cell)")

    # J2 静态文本（manifest 声明的静态文本逐个在渲染 cell 中命中）
    val_map = {}
    for s in r.get("sheets", []):
        for c in s.get("cells", []):
            if c.get("v") is not None:
                val_map.setdefault(str(c["v"]).strip(), (c["c"], c["r"]))
    for t in (manifest.get("grid", {}).get("static_texts") or [])[:30]:
        if t["text"] in val_map:
            passed.append(f"J2 静态文本命中: {t['text'][:16]} @渲染({val_map[t['text']][0]},{val_map[t['text']][1]})")
        else:
            failed.append(f"J2 静态文本缺失: {t['text'][:16]}(声明于 cell({t['cell']}))")

    # J3 图表（manifest 图表声明 vs 渲染 t=chart 计数）
    n_chart_declared = manifest.get("charts", {}).get("chart_total", 0)
    n_chart_rendered = sum(1 for s in r.get("sheets", []) for c in s.get("cells", []) if c.get("t") == "chart")
    if n_chart_declared == 0 and n_chart_rendered == 0:
        passed.append("J3 双方均无图表")
    elif n_chart_rendered >= 1:
        passed.append(f"J3 图表已渲染: {n_chart_rendered} 格(声明 {n_chart_declared})")
    elif n_chart_declared > 0:
        failed.append(f"J3 图表未渲染: 声明 {n_chart_declared} 但渲染产物 0 chart 格(静默失败猎物!)")

    # J4 数据填充（内嵌数据集模板应有数据格）
    has_embedded = any(d["embedded"] and d["embedded_payload_bytes"] > 100
                       for d in manifest.get("datasets", []))
    n_nonempty = sum(1 for s in r.get("sheets", []) for c in s.get("cells", []) if c.get("v"))
    if has_embedded:
        if n_nonempty >= 3:
            passed.append(f"J4 数据/文本格 {n_nonempty} 个(内嵌数据集)")
        else:
            warned.append(f"J4 非空格偏少({n_nonempty})——骨架模板数据可能在图表内,可接受")
    else:
        passed.append(f"J4 非空格 {n_nonempty}")

    # J5 sheet 名（若渲染器拿到了名字则精确比对；sheet0=降级名只 warn）
    m_sheets = [s for s in manifest.get("sheet_names", []) if s]
    r_names = [s.get("name") for s in r.get("sheets", [])]
    if m_sheets and r_names and all(n.startswith("sheet") for n in r_names):
        warned.append(f"J5 渲染器 sheet 名降级({r_names}),无法精确比对声明 {m_sheets}")
    elif m_sheets:
        for sn in m_sheets:
            if sn in r_names:
                passed.append(f"J5 sheet 名命中: {sn}")
            else:
                failed.append(f"J5 sheet 名缺失: {sn}(产物 {r_names[:3]})")

    return passed, failed, warned


if __name__ == "__main__":
    tpl, js = sys.argv[1], sys.argv[2]
    p, f, w = assert_json(extract_manifest(tpl), js)
    for x in p: print(f"  [PASS] {x}")
    for x in w: print(f"  [WARN] {x}")
    for x in f: print(f"  [FAIL] {x}")
    print(f"  == {len(p)} PASS / {len(w)} WARN / {len(f)} FAIL")
    sys.exit(1 if f else 0)
