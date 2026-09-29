#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""layout_check.py — 布局几何合理性断言 (L1-L4)

设计迭代自辅助的核心: 渲染产物不只要 round-trip 一致, 还要几何上"合理"。
L1 重叠: 任意两叶子控件/合并格像素矩形相交(真实布局坏味, 设计器里必然叠放)
L2 越界/负坐标: 控件超出画布合理范围(>8000px)或坐标为负
L3 零尺寸/极小: w或h<=0 (FAIL, 不可见控件); <4px (WARN)
L4 图表区过小: cpt 图表格按真实 colW/rowH 求和 < 120×90px (WARN, 可读性差 — 用户实测发现的"图表太小"类问题)

输入: injected_render.js 产物 JSON (cpt: cells+colW/rowH+params; frm: widgets)
输出: (pass, fail, warn) 三列消息。纯函数, 被 render_check/page2tpl/tpl2page 复用。
CLI: python layout_check.py <render.json>
"""
import json
import sys

# 阈值(可调; 单位=px, 来源: 单位换算实证.md)
OVERLAP_MIN_AREA = 4      # 相交面积超过此值才算重叠(抗浮点/贴边)
STACK_RATIO = 0.85        # 相交 ≥ 较小者面积×此比例 → 视为"层叠卡片"(Tab/条件显示, 合法)
FLOAT_BTN_CLASSES = ("FreeButton", "FormSubmitButton")  # 悬浮按钮豁免(常叠在内容上)
FLOAT_MAX_RATIO = 0.25    # 浮钮重叠 < 对方面积×此比例 → 豁免
CANVAS_MAX = 8000         # 单维度合理上限
WIDGET_MIN_WARN = 4       # 小于此值警告(可能看不见)
CHART_MIN_W, CHART_MIN_H = 120, 90  # 图表最小可读尺寸


def _rects_intersect(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    iy = max(0, min(ay + ah, by + bh) - max(ay, by))
    return ix * iy


def _leaf_widgets(ws):
    """剔除包装器/布局容器, 留真实叶子(带坐标)"""
    out = []
    for w in ws or []:
        cls = (w.get("cls") or "").rsplit(".", 1)[-1]
        if "BoundsWidget" in cls or "Layout" in cls:
            continue
        if w.get("x") is None:
            continue
        out.append((w.get("name") or cls, w["x"], w["y"], w.get("w") or 0, w.get("h") or 0, cls))
    return out


def check_layout(rjson):
    P, F, W = [], [], []
    kind = rjson.get("kind")

    # ── 组件矩形集合(frm 主体 / cpt+frm 参数面板) ──
    rects = []  # (label, x, y, w, h)
    if kind == "frm":
        leaves = _leaf_widgets(rjson.get("widgets"))
        grp = "frm控件"
    else:
        leaves = _leaf_widgets(rjson.get("params"))
        grp = "参数控件"
    for name, x, y, w, h, cls in leaves:
        rects.append((f"{grp} {name}({cls.rsplit('.',1)[-1]})", x, y, w, h))

    # L2 越界/负坐标 + L3 零尺寸/极小
    zero, tiny, oob = [], [], []
    for label, x, y, w, h in rects:
        if w <= 0 or h <= 0:
            zero.append(label)
        elif w < WIDGET_MIN_WARN or h < WIDGET_MIN_WARN:
            tiny.append(f"{label} {w}×{h}px")
        if x < 0 or y < 0 or x + w > CANVAS_MAX or y + h > CANVAS_MAX:
            oob.append(f"{label} @({x},{y}) {w}×{h}")
    if rects:
        if not zero and not tiny:
            P.append(f"L3 控件尺寸合理: {len(rects)} 件无零尺寸/极小")
        if zero:
            F.append(f"L3 零尺寸控件 {len(zero)}: {zero[:5]}(不可见, 布局坏味)")
        if tiny:
            W.append(f"L3 极小控件(<{WIDGET_MIN_WARN}px) {len(tiny)}: {tiny[:5]}")
        if oob:
            F.append(f"L2 越界/负坐标 {len(oob)}: {oob[:5]}")
        else:
            P.append(f"L2 无越界/负坐标: {len(rects)} 件全在 {CANVAS_MAX}px 画域内")

    # L1 重叠(区分: 层叠卡片组合法 / 浮钮豁免 / 真意外重叠)
    # 先按"近似全叠"并查集聚合成层叠组(同位置 Tab/条件显示卡片)
    parent = list(range(len(rects)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    stack_pairs = 0
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            la, ax, ay, aw, ah = rects[i]
            lb, bx, by, bw, bh = rects[j]
            ia = _rects_intersect((ax, ay, aw, ah), (bx, by, bw, bh))
            if ia <= OVERLAP_MIN_AREA:
                continue
            min_area = min(aw * ah, bw * bh)
            if min_area > 0 and ia >= min_area * STACK_RATIO:
                parent[find(i)] = find(j)  # 近似全叠 → 同层叠组
                stack_pairs += 1
    groups = {}
    for i in range(len(rects)):
        groups.setdefault(find(i), []).append(rects[i][0])
    stack_groups = [m for m in groups.values() if len(m) > 1]

    overlaps = []
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if find(i) == find(j):
                continue  # 同层叠组内部不报
            la, ax, ay, aw, ah = rects[i]
            lb, bx, by, bw, bh = rects[j]
            area = _rects_intersect((ax, ay, aw, ah), (bx, by, bw, bh))
            if area <= OVERLAP_MIN_AREA:
                continue
            # 浮钮豁免: 按钮悬浮在内容上是常见合法设计
            is_float = la.rsplit("(", 1)[-1][:-1] in FLOAT_BTN_CLASSES or \
                       lb.rsplit("(", 1)[-1][:-1] in FLOAT_BTN_CLASSES
            big_area = max(aw * ah, bw * bh)
            if is_float and big_area > 0 and area < big_area * FLOAT_MAX_RATIO:
                continue
            overlaps.append(f"{la} ∩ {lb} = {area}px²")
    if rects:
        if stack_groups:
            desc = "; ".join(f"[{'|'.join(g[:4])}{'…' if len(g) > 4 else ''}]×{len(g)}" for g in stack_groups[:3])
            P.append(f"L1 层叠卡片组 {len(stack_groups)} 组({stack_pairs} 对近似全叠, Tab/条件显示合法): {desc}")
        if overlaps:
            W.append(f"L1 意外重叠 {len(overlaps)}: {overlaps[:4]}(非层叠组非浮钮, 布局坏味候选)")
        else:
            P.append(f"L1 无意外重叠: {len(rects)} 件控件(层叠组/浮钮豁免后两两不相交)")

    # L4 图表区过小(cpt: 按真实 colW/rowH 求和; frm: 图表类叶子尺寸)
    small_charts = []
    if kind == "cpt":
        for s in rjson.get("sheets", []):
            cw, rh = s.get("colW") or [], s.get("rowH") or []
            for c in s.get("cells", []):
                if c.get("t") != "chart":
                    continue
                if cw and rh:
                    px_w = sum(cw[c["c"]:c["c"] + (c.get("cs") or 1)])
                    px_h = sum(rh[c["r"]:c["r"] + (c.get("rs") or 1)])
                else:  # 无尺寸数据(旧产物) → 按格数粗估(每格~72×30px 默认)
                    px_w = (c.get("cs") or 1) * 72
                    px_h = (c.get("rs") or 1) * 30
                if px_w < CHART_MIN_W or px_h < CHART_MIN_H:
                    small_charts.append(f"格({c['c']},{c['r']}) {px_w:.0f}×{px_h:.0f}px")
        n_charts = sum(1 for s in rjson.get("sheets", []) for c in s.get("cells", []) if c.get("t") == "chart")
        if n_charts == 0:
            P.append("L4 无图表区")
        elif small_charts:
            W.append(f"L4 图表区过小(<{CHART_MIN_W}×{CHART_MIN_H}px) {len(small_charts)}/{n_charts}: "
                     f"{small_charts[:4]} — 可读性差, 建议扩大图表格或画布")
        else:
            P.append(f"L4 图表区尺寸达标: {n_charts} 个均 ≥{CHART_MIN_W}×{CHART_MIN_H}px")
    else:
        chart_leaves = [(l, w, h) for l, x, y, w, h in rects if "Chart" in l or "chart" in l.lower()]
        for l, w, h in chart_leaves:
            if w < CHART_MIN_W or h < CHART_MIN_H:
                small_charts.append(f"{l} {w}×{h}px")
        if chart_leaves and not small_charts:
            P.append(f"L4 图表组件尺寸达标: {len(chart_leaves)} 件")
        elif small_charts:
            W.append(f"L4 图表组件过小 {len(small_charts)}: {small_charts[:4]}")

    return P, F, W


if __name__ == "__main__":
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    p, f, w = check_layout(d)
    for x in p:
        print(f"  [PASS] {x}")
    for x in w:
        print(f"  [WARN] {x}")
    for x in f:
        print(f"  [FAIL] {x}")
    sys.exit(1 if f else 0)
