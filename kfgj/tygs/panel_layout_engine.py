#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
panel_layout_engine.py — 参数面板标准布局引擎 v1.0（G2 双段式路线：描述写语义，像素交给引擎）

布局规格（用户裁决 2026-09-06）:
  · 标准容器 =【label + 控件】横排一组
  · 每行固定 7 个标准容器，超出换行
  · 按钮容器宽度 = 标准容器的一半
  · 触发式竖排: 当前 cpt 任一 label 文本 > 8 字符 → 全面板切竖排
    （label 在上高 15 + 控件在下高 25，容器高 40）

用法:
  python panel_layout_engine.py <in.cpt> [-o out.cpt] [--cols 7] [--ctrl-w 180]
  缺省 -o: 原名追加 _面板标准化.cpt（原文件不动）

口径:
  · 只处理 <ParameterUI>...</ParameterUI> 块；无面板则原样退出（no-op）
  · 面板布局由本引擎标准化，重建/评判不再逐像素对比（G2 双段式裁决）
"""
import argparse
import os
import re
import sys

MARGIN = 12
COL_GAP = 8          # 容器列间距
ROW_GAP = 5          # 容器行间上下间隙（用户规格 2026-09-06）
CTRL_W = 180         # 控件标准宽
CTRL_H = 26          # 控件标准高
LABEL_CTRL_GAP = 4   # 横排 label 与控件间距
LABEL_H_V = 15       # 竖排 label 高
CTRL_H_V = 25        # 竖排控件高
V_CONTAINER_H = 40   # 竖排容器高 = label15 + 控件25
V_TRIGGER_LABEL = 8  # 任一 label 超过 8 字符 → 竖排

LABEL_CLS = "com.fr.form.ui.Label"
BTN_RE = re.compile(r"(FreeButton|FormSubmitButton|Button)$")

INNER_BOUNDS_RE = re.compile(
    r'(<InnerWidget class="([^"]+)"[^>]*>.*?</InnerWidget>\s*)'
    r'<BoundsAttr\s+x="(-?\d+)"\s+y="(-?\d+)"\s+width="(\d+)"\s+height="(\d+)"',
    re.DOTALL)
WNAME_RE = re.compile(r'<WidgetName\s+name="([^"]*)"')
WVALUE_RE = re.compile(r'<widgetValue>(.*?)</widgetValue>', re.DOTALL)
CDATA_RE = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)


def label_text(inner):
    """FR10 Label 文本: <widgetValue><O><![CDATA[...]]></O></widgetValue>（兼容无 O 包装/无 CDATA）"""
    m = WVALUE_RE.search(inner)
    if not m:
        return ""
    inner_v = m.group(1)
    c = CDATA_RE.search(inner_v)
    return (c.group(1) if c else inner_v).strip()


def kind_of(cls):
    if cls == LABEL_CLS:
        return "label"
    if BTN_RE.search(cls.split(".")[-1]) or "FormSubmit" in cls:
        return "button"
    return "control"


def calc_label_w(text):
    if not text:
        return 40
    w = 8
    for ch in text:
        w += 10 if "\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f" else 6
    return max(w, 40)


def read_cpt(path):
    raw = open(path, "rb").read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk")


def layout(content, cols=7, ctrl_w=CTRL_W):
    m_ui = re.search(r"(<ParameterUI.*?</ParameterUI>)", content, re.DOTALL)
    if not m_ui:
        return content, {"status": "no-parameterui"}
    block = m_ui.group(1)
    original_block = block

    # ── 1. 解析控件 ──
    widgets = []
    for m in INNER_BOUNDS_RE.finditer(block):
        cls = m.group(2)
        kind = kind_of(cls)
        name_m = WNAME_RE.search(m.group(1))
        text = ""
        seg = m.group(0)
        if kind == "label":
            text = label_text(m.group(1))
            # 用户规格 2026-09-06: ①label 去尾冒号 ②居左 ③字号 8号(FRFont size=80)
            stripped = text.rstrip().rstrip("：:").rstrip()
            if stripped != text:
                seg = seg.replace("<![CDATA[%s]]>" % text, "<![CDATA[%s]]>" % stripped, 1)
            seg = re.sub(r'(<LabelAttr[^>]*textalign=")\d+(")', r"\g<1>2\g<2>", seg)  # LEFT=2
            seg = re.sub(r'(<FRFont[^>]*size=")\d+(")', r"\g<1>80\g<2>", seg)
            seg = re.sub(r'(<FRFont[^>]*style=")\d+(")', r"\g<1>0\g<2>", seg)
            if "<FRFont" not in seg:
                seg = seg.replace("</InnerWidget>",
                                  '<FRFont name="微软雅黑" style="0" size="80"/>\n</InnerWidget>', 1)
            if "<LabelAttr" not in seg:
                seg = seg.replace("</widgetValue>",
                                  '</widgetValue>\n<LabelAttr verticalcenter="true" textalign="0" autoline="true"/>', 1)
            text = stripped
        widgets.append({
            "kind": kind, "cls": cls,
            "name": name_m.group(1) if name_m else "",
            "text": text, "label_w": calc_label_w(text) if kind == "label" else 0,
            "seg0": m.group(0), "seg": seg, "x": int(m.group(3)), "y": int(m.group(4)),
        })
    if not widgets:
        return content, {"status": "no-widgets"}

    labels = [w for w in widgets if w["kind"] == "label"]
    controls = [w for w in widgets if w["kind"] == "control"]
    buttons = [w for w in widgets if w["kind"] == "button"]

    # ── 2. 竖排触发判定 ──
    max_label_len = max((len(w["text"]) for w in labels), default=0)
    vertical = max_label_len > V_TRIGGER_LABEL

    # ── 3. label↔控件 配对（同行 y、x 在右侧、最近者优先）──
    used = set()
    for lbl in sorted(labels, key=lambda w: (w["y"], w["x"])):
        cand = [c for c in controls
                if id(c) not in used and c["y"] == lbl["y"] and c["x"] > lbl["x"]]
        lbl["pair"] = min(cand, key=lambda c: c["x"]) if cand else None
        if lbl["pair"]:
            used.add(id(lbl["pair"]))
    for c in controls:
        if id(c) not in used:
            c["pair_label"] = None

    # ── 4. 容器序列（保持原阅读顺序 y,x）──
    containers = []  # {"widgets":[(role, w)], "order":(y,x)}
    for lbl in labels:
        if lbl.get("pair"):
            containers.append({"widgets": [("label", lbl), ("control", lbl["pair"])],
                               "order": (lbl["y"], lbl["x"])})
    paired_ids = {id(l["pair"]) for l in labels if l.get("pair")}
    for c in controls:
        if id(c) not in paired_ids:
            containers.append({"widgets": [("control", c)], "order": (c["y"], c["x"])})
    for l in labels:
        if not l.get("pair"):
            containers.append({"widgets": [("label", l)], "order": (l["y"], l["x"])})
    containers.sort(key=lambda c: c["order"])

    # ── 5. 容器统一宽度 ──
    max_label_w = max((w["label_w"] for w in labels), default=0)
    if vertical:
        cw = max(max_label_w, ctrl_w)
    else:
        cw = max_label_w + LABEL_CTRL_GAP + ctrl_w
    btn_w = cw // 2

    # ── 6. 打包：每行 cols 个容器 ──
    rows = [containers[i:i + cols] for i in range(0, len(containers), cols)]

    # ── 7. 逐容器写坐标 ──
    segs = []
    for ri, row in enumerate(rows):
        for ci, container in enumerate(row):
            x = MARGIN + ci * (cw + COL_GAP)
            pitch = (V_CONTAINER_H if vertical else CTRL_H) + ROW_GAP
            y = MARGIN + ri * pitch
            has_label = container_has_label(container)
            for role, w in container["widgets"]:
                if vertical:
                    if role == "label":
                        segs.append((w["seg0"], _bounds(w, x, y, cw, LABEL_H_V)))
                    else:
                        segs.append((w["seg0"], _bounds(w, x, y + LABEL_H_V, cw, CTRL_H_V)))
                else:
                    if role == "label":
                        segs.append((w["seg0"], _bounds(w, x, y, w["label_w"], CTRL_H)))
                    else:
                        off = (max_label_w + LABEL_CTRL_GAP) if has_label else 0
                        segs.append((w["seg0"], _bounds(w, x + off, y, ctrl_w, CTRL_H)))

    # 按钮继续打包（半宽，每容器槽 2 个）
    for bi, b in enumerate(buttons):
        slot = len(containers) + bi // 2
        ri, ci = divmod(slot, cols)
        x = MARGIN + ci * (cw + COL_GAP) + (bi % 2) * (btn_w + COL_GAP)
        y = MARGIN + ri * (V_CONTAINER_H if vertical else CTRL_H + ROW_GAP) + \
            (LABEL_H_V if vertical and b["kind"] != "x" else 0)
        segs.append((b["seg0"], _bounds(b, x, y, btn_w, CTRL_H)))

    for old, new in segs:
        block = block.replace(old, new, 1)

    # ── 8. 面板宽高自适应收回 ──
    n_rows = len(rows) + (1 if buttons else 0)
    panel_w = MARGIN * 2 + cols * cw + (cols - 1) * COL_GAP
    panel_h = MARGIN * 2 + n_rows * (V_CONTAINER_H if vertical else CTRL_H) + \
        max(0, n_rows - 1) * ROW_GAP
    block = re.sub(r'(<Design_Width\s+design_width=")\d+(")',
                   r"\g<1>%d\g<2>" % panel_w, block)
    block = re.sub(r'(<DesignAttr\s+width=")\d+(")',
                   r"\g<1>%d\g<2>" % panel_w, block)
    block = re.sub(r'(<DesignAttr\s+width="\d+"\s+height=")\d+(")',
                   r"\g<1>%d\g<2>" % panel_h, block)

    content = content[:m_ui.start(1)] + block + content[m_ui.end(1):]
    return content, {
        "status": "ok", "mode": "vertical" if vertical else "horizontal",
        "max_label_len": max_label_len, "containers": len(containers),
        "buttons": len(buttons), "rows": n_rows,
        "container_w": cw, "btn_w": btn_w, "panel_w": panel_w, "panel_h": panel_h,
    }


def container_has_label(container):
    return any(role == "label" for role, _ in container["widgets"])


def _bounds(w, x, y, wd, ht):
    return re.sub(
        r'<BoundsAttr\s+x="-?\d+"\s+y="-?\d+"\s+width="\d+"\s+height="\d+"',
        '<BoundsAttr x="%d" y="%d" width="%d" height="%d"' % (x, y, wd, ht),
        w["seg"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--cols", type=int, default=7)
    ap.add_argument("--ctrl-w", type=int, default=CTRL_W)
    args = ap.parse_args()

    content = read_cpt(args.input)
    new, info = layout(content, cols=args.cols, ctrl_w=args.ctrl_w)

    out = args.output or re.sub(r"\.cpt$", "", args.input) + "_面板标准化.cpt"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)

    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(new)
        wellform = "XML 合法 ✅"
    except ET.ParseError as e:
        wellform = "XML 解析失败 ❌ %s" % str(e)[:80]

    print("输入: %s" % args.input)
    print("输出: %s" % out)
    print("状态: %s | 模式: %s | 最长label: %s 字符" %
          (info["status"], info.get("mode", "-"), info.get("max_label_len", "-")))
    print("容器: %s 个 | 按钮: %s 个 | 行数: %s | 容器宽: %s | 面板: %sx%s" %
          (info.get("containers", "-"), info.get("buttons", "-"), info.get("rows", "-"),
           info.get("container_w", "-"), info.get("panel_w", "-"), info.get("panel_h", "-")))
    print(wellform)
    return 0


if __name__ == "__main__":
    sys.exit(main())
