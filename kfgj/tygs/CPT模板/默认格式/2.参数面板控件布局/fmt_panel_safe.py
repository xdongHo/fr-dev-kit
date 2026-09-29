# -*- coding: utf-8 -*-
"""
fmt_panel_safe.py — 参数面板坐标级安全格式化（Ver1.0, 2026-08-05）

⚠️ 弃用警示（2026-09-29）：本脚本为 LAYOUT_SPEC Ver0.5 时代实现，已被 Ver0.7
区块模型权威实现 auto_layout_watermark.py（同目录）取代——行距 10（本脚本 8）、
1500/300 约束、三形态（watermark/label-h/label-v）、YearControl 窄化均只有
新脚本有。run_defaults.py 默认链已改挂新脚本。本文件仅存档供回溯，勿用于新任务。

设计原则（解决正则脚本损坏模板完整性问题）：
  1. 只改坐标数值：仅替换每个控件的 <BoundsAttr x/y/width/height> 数值，
     以及面板 <DesignAttr>/<Design_Width> 尺寸。不增删任何节点、
     不触碰 CDATA / Listener / JS 内容 / 结构顺序。
  2. 每处 BoundsAttr 原串在面板内唯一 → 全局 replace 绝对安全。
  3. 改前/改后均做 XML 合法性校验；自动备份；支持幂等自检。

两种方案（LAYOUT_SPEC Ver0.5）：
  --mode watermark  (默认) 无 Label 水印式：输入控件均布 180px 网格，
                             按钮右对齐 40px 间距
  --mode label      分支    Label+控件配对：Label 左对齐 + Label→5px +
                             跨行 Label 列对齐（Label 宽度按文本估算）

用法:
  python fmt_panel_safe.py <cpt路径> [--mode watermark|label] [--dry-run]
"""
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

CTRL_W, CTRL_H = 180, 26
LABEL_GAP, CTRL_GAP, BTN_GAP = 5, 20, 40
MARGIN, ROW_GAP = 12, 8
BTN_W, IMPORT_W = 80, 120
LABEL_MIN_W = 40

INPUT_CLS = ('ComboCheckBox', 'YearControl', 'DateEditor', 'TextEditor',
             'NumberEditor', 'ComboBox', 'CheckBox', 'RadioGroup', 'TreeEditor')
BTN_CLS = ('FreeButton', 'FormSubmitButton', 'Button', 'ToggleButton')

BOUNDS_WIDGET_RE = re.compile(
    r'<Widget class="com\.fr\.form\.ui\.container\.WAbsoluteLayout\$BoundsWidget">\s*'
    r'<InnerWidget class="([^"]*)"[^>]*>(.*?)</InnerWidget>\s*'
    r'(<BoundsAttr\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"/>)',
    re.DOTALL)


class W:
    __slots__ = ('name', 'cls', 'old_bounds', 'x', 'y', 'w', 'h', 'new')

    def __init__(self, name, cls, old_bounds, x, y, w, h):
        self.name, self.cls = name, cls
        self.old_bounds = old_bounds
        self.x, self.y, self.w, self.h = x, y, w, h
        self.new = None


def label_width(text):
    """按文本估算 Label 宽度（px），中文按 14px/字、英文按 8px/字符 + padding"""
    if not text:
        return LABEL_MIN_W
    w = 0
    for ch in text:
        w += 14 if ord(ch) > 127 else 8
    return max(LABEL_MIN_W, w + 16)


def parse_panel(xml):
    pm = re.search(r'<ParameterUI[\s\S]*?</ParameterUI>', xml)
    if not pm:
        return None, []
    widgets = []
    for m in BOUNDS_WIDGET_RE.finditer(pm.group(0)):
        cls = m.group(1).split('.')[-1]
        inner = m.group(2)
        nm = re.search(r'<WidgetName name="([^"]+)"', inner)
        nm = nm.group(1) if nm else '?'
        widgets.append(W(nm, cls, m.group(3),
                         int(m.group(4)), int(m.group(5)),
                         int(m.group(6)), int(m.group(7))))
    return pm.group(0), widgets


def layout_watermark(widgets):
    inputs = [w for w in widgets if w.cls in INPUT_CLS]
    btns = [w for w in widgets if w.cls in BTN_CLS]
    # group inputs by original y (tolerance), keep row order by original x
    groups = []
    for w in sorted(inputs, key=lambda w: (w.y, w.x)):
        if not groups or abs(w.y - groups[-1][0]) > 5:
            groups.append((w.y, []))
        groups[-1][1].append(w)
    rows = [g[1] for g in groups]
    right = MARGIN
    for ri, row in enumerate(rows):
        y = MARGIN + ri * (CTRL_H + ROW_GAP)
        for ci, w in enumerate(row):
            x = MARGIN + ci * (CTRL_W + CTRL_GAP)
            w.new = (x, y, CTRL_W, CTRL_H)
            right = max(right, x + CTRL_W)
    # buttons: right-aligned, keep original left-to-right order
    btns_sorted = sorted(btns, key=lambda w: w.x)
    btn_y = MARGIN + len(rows) * (CTRL_H + ROW_GAP) if rows else MARGIN
    x = right
    for w in reversed(btns_sorted):
        bw = IMPORT_W if w.name in ('Import', 'import') else BTN_W
        w.new = (x - bw, btn_y, bw, CTRL_H)
        x = x - bw - BTN_GAP
    btn_right = right if not btns else right
    panel_w = max(right, x + MARGIN) + MARGIN
    panel_h = btn_y + CTRL_H + 13
    return panel_w, panel_h


def layout_label(widgets):
    """Label 式：Label+控件配对。Label 类名含 'Label'，配对后紧邻的输入控件。"""
    inputs = [w for w in widgets if w.cls in INPUT_CLS]
    labels = [w for w in widgets if 'Label' in w.cls]
    btns = [w for w in widgets if w.cls in BTN_CLS]
    # pair: label followed by input (same visual row, left-to-right)
    ordered = sorted(widgets, key=lambda w: (w.y, w.x))
    pairs = []
    i = 0
    while i < len(ordered):
        w = ordered[i]
        if 'Label' in w.cls and i + 1 < len(ordered) and ordered[i + 1].cls in INPUT_CLS:
            pairs.append((w, ordered[i + 1]))
            i += 2
        else:
            i += 1
    if not pairs:
        return layout_watermark(widgets)
    # group pairs by original y
    groups = []
    for lbl, ctrl in sorted(pairs, key=lambda p: (p[0].y, p[0].x)):
        if not groups or abs(lbl.y - groups[-1][0]) > 5:
            groups.append((lbl.y, []))
        groups[-1][1].append((lbl, ctrl))
    rows = [g[1] for g in groups]
    n_cols = max(len(r) for r in rows)
    # column label widths (max per column)
    col_lw = [0] * n_cols
    for r in rows:
        for ci, (lbl, ctrl) in enumerate(r):
            col_lw[ci] = max(col_lw[ci], label_width(lbl.name))
    right = MARGIN
    for ri, row in enumerate(rows):
        y = MARGIN + ri * (CTRL_H + ROW_GAP)
        x = MARGIN
        for ci, (lbl, ctrl) in enumerate(row):
            lx = x
            lbl.new = (lx, y, col_lw[ci], CTRL_H)
            cx = lx + col_lw[ci] + LABEL_GAP
            ctrl.new = (cx, y, CTRL_W, CTRL_H)
            x = x + col_lw[ci] + LABEL_GAP + CTRL_W + CTRL_GAP
        right = max(right, x - CTRL_GAP)
    btns_sorted = sorted(btns, key=lambda w: w.x)
    btn_y = MARGIN + len(rows) * (CTRL_H + ROW_GAP) if rows else MARGIN
    bx = right
    for w in reversed(btns_sorted):
        bw = IMPORT_W if w.name in ('Import', 'import') else BTN_W
        w.new = (bx - bw, btn_y, bw, CTRL_H)
        bx = bx - bw - BTN_GAP
    panel_w = max(right, bx + MARGIN) + MARGIN
    panel_h = btn_y + CTRL_H + 13
    return panel_w, panel_h


def apply(xml, widgets, panel_w, panel_h):
    new_xml = xml
    for w in widgets:
        if w.new is None:
            continue
        nx, ny, nw, nh = w.new
        new_b = f'<BoundsAttr x="{nx}" y="{ny}" width="{nw}" height="{nh}"/>'
        assert xml.count(w.old_bounds) == 1, f"非唯一 BoundsAttr: {w.old_bounds}"
        new_xml = new_xml.replace(w.old_bounds, new_b, 1)
    # panel size
    new_xml = re.sub(r'<Design_Width design_width="\d+"/>',
                     f'<Design_Width design_width="{panel_w}"/>', new_xml, count=1)
    new_xml = re.sub(r'<DesignAttr width="\d+" height="\d+"/>',
                     f'<DesignAttr width="{panel_w}" height="{panel_h}"/>', new_xml, count=1)
    return new_xml


def check_xml(text, label):
    import xml.etree.ElementTree as ET
    ET.fromstring(text)
    print(f"  ✓ XML valid ({label})")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = set(a for a in sys.argv[1:] if a.startswith('--'))
    if not args:
        print(__doc__)
        sys.exit(1)
    mode = 'label' if '--mode' in flags else 'watermark'
    if '--mode' in sys.argv:
        try:
            mode = sys.argv[sys.argv.index('--mode') + 1]
        except IndexError:
            pass
    dry = '--dry-run' in flags
    for path in args:
        fp = Path(path)
        if not fp.exists():
            print(f"❌ 不存在: {fp}")
            continue
        print(f"== {fp.name}  (mode={mode})")
        xml = fp.read_text(encoding='utf-8')
        check_xml(xml, 'before')
        pui, widgets = parse_panel(xml)
        if not widgets:
            print("  ⚠ 无 BoundsWidget 控件，跳过")
            continue
        if mode == 'label':
            panel_w, panel_h = layout_label(widgets)
        else:
            panel_w, panel_h = layout_watermark(widgets)
        new_xml = apply(xml, widgets, panel_w, panel_h)
        check_xml(new_xml, 'after')
        if dry:
            print(f"  [dry-run] 面板 {panel_w}x{panel_h}, 控件 {len(widgets)} 个")
            continue
        bak = fp.parent / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        bak.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fp, bak / fp.name)
        fp.write_text(new_xml, encoding='utf-8')
        print(f"  备份: {bak / fp.name}")
        print(f"  面板 {panel_w}x{panel_h} 已写入")
        # idempotency: re-parse and confirm same bounds
        xml2 = fp.read_text(encoding='utf-8')
        pui2, w2 = parse_panel(xml2)
        changed = 0
        for w in w2:
            for w0 in widgets:
                if w0.name == w.name and w0.new:
                    if (w.x, w.y, w.w, w.h) != w0.new:
                        changed += 1
        print(f"  幂等检查: {'OK' if changed == 0 else f'{changed} 处偏移'}")


if __name__ == '__main__':
    main()
