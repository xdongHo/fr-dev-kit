# -*- coding: utf-8 -*-
"""
auto_layout_watermark.py — 参数面板自动布局（区块模型 Ver1.1, 2026-08-05）

区块概念（用户定稿：区块 = 兼容 Label 的布局单元）：
  【X】可编辑控件：年月日/文本/下拉/单选等（ComboCheckBox/YearControl/DateEditor/
                   TextEditor/NumberEditor/ComboBox/CheckBox/RadioGroup/TreeEditor）
  【Y】不可编辑控件：按钮/超链接文本等（FreeButton/FormSubmitButton/Button/
                   SubmitButton/ToggleButton/Hyperlink）；Label 除外
       区块宽 = max(80, 中文×15 + 字母符号×8)，间隔 20，行高 26

三种区块形态（--mode）：
  watermark  无 Label（默认）：区块 = 控件宽+20 宽 × 26 高
             （控件宽按类：YearControl=100，其余 180；窄控件后面紧跟不占虚位）
  label-h    Label 在左水平：区块 = 100(Label) + 控件宽 + 20(留白) 宽 × 26 高
  label-v    Label 在上：区块 = 控件宽+20 宽 × 40 高（上 14 Label + 下 26 控件），
             区块间留白 20 → 行距 60

全局约束（用户定稿）：
  每行最宽 < 1500（per 取 数量规则 5/6/7 与 宽度上限 的较小值）
  总高度 < 300（布局后检查，超限打印警告）

布局算法（同 Ver1.0）：
  1. ΣX区块 + ΣY区块 < 1500 → 全部放一行
  2. 否则按 X 数量分行（每行容量受宽度上限约束）
  3. 最后一行剩余空间够 → Y 并入最后一行贴右；不够 → Y 新行右对齐
  4. 行间隔：watermark/label-h = 10，label-v = 20（区块内 14+26=40）

边界修正（对用户规范的实现注记）：
  - X 数量整除每行数（余数 0）时最后一行已满 → Y 强制新行
  - 区块宽含尾部间隔；摆放时最后一个 Y 贴右缘去掉尾间隔

用法:
  python auto_layout_watermark.py <cpt路径> [cpt路径...] [--mode watermark|label-h|label-v] [--dry-run]
"""
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

CTRL_W, CTRL_H = 180, 26
X_W_BY_CLS = {'YearControl': 100}   # 窄控件：年份 4 位数字 100 够，其余 180
LABEL_W = 100                # label-h 模式：Label 固定 100 宽（用户定稿）
LABEL_H_V, CTRL_H_V = 14, 26 # label-v 模式：区块内 Label 高 14 / 控件高 26
X_BLOCK_DEF = 200        # 标准 X 区块（Y 并入的剩余空间估算基准）
Y_MIN_W = 80
Y_CJK_W, Y_ASCII_W = 15, 8   # Y 宽度 = 中文×15 + 字母符号×8
Y_GAP = 20
ROW_GAP = 10             # 行间隔（watermark/label-h）
ROW_GAP_V = 20           # label-v 行间隔（区块间留白）
MARGIN = 12
SINGLE_ROW_MAX = 1500    # 每行最宽约束
PANEL_H_MAX = 300        # 总高约束（用户定稿）

INPUT_CLS = ('ComboCheckBox', 'YearControl', 'DateEditor', 'TextEditor',
             'NumberEditor', 'ComboBox', 'CheckBox', 'RadioGroup', 'TreeEditor')
BTN_CLS = ('FreeButton', 'FormSubmitButton', 'Button', 'SubmitButton',
           'ToggleButton', 'Hyperlink', 'LinkField')

BOUNDS_WIDGET_RE = re.compile(
    r'<Widget class="com\.fr\.form\.ui\.container\.WAbsoluteLayout\$BoundsWidget">\s*'
    r'<InnerWidget class="([^"]*)"[^>]*>(.*?)</InnerWidget>\s*'
    r'(<BoundsAttr\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"/>)',
    re.DOTALL)


class W:
    __slots__ = ('name', 'cls', 'old_bounds', 'x', 'y', 'w', 'h', 'new', 'inner')

    def __init__(self, name, cls, old_bounds, x, y, w, h, inner=''):
        self.name, self.cls = name, cls
        self.old_bounds = old_bounds
        self.x, self.y, self.w, self.h = x, y, w, h
        self.new = None
        self.inner = inner


def btn_text(inner):
    """提取按钮文字（Y 宽度依据）；取不到用控件名。"""
    m = re.search(r'<Text>\s*<!\[CDATA\[(.*?)\]\]>', inner, re.DOTALL)
    if m and m.group(1).strip():
        return m.group(1).strip()
    nm = re.search(r'<WidgetName name="([^"]+)"', inner)
    return nm.group(1) if nm else 'btn'


def y_width(text):
    """Y 区块宽 = max(80, 中文×15 + 字母符号×8)"""
    w = sum(Y_CJK_W if ord(ch) > 127 else Y_ASCII_W for ch in text)
    return max(Y_MIN_W, w)


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
                         int(m.group(6)), int(m.group(7)), inner))
    return pm.group(0), widgets


def pair_labels(labels, xs):
    """Label 与紧随的输入控件配对（按 y/x 排序）。返回 [(label, input)] 或 None。"""
    if not labels or not xs:
        return None
    ordered = sorted(labels + xs, key=lambda w: (w.y, w.x))
    pairs = []
    i = 0
    while i < len(ordered) - 1:
        if 'Label' in ordered[i].cls and ordered[i + 1].cls in INPUT_CLS:
            pairs.append((ordered[i], ordered[i + 1]))
            i += 2
        else:
            i += 1
    return pairs or None


def auto_layout(widgets, mode='watermark', verbose=True):
    """区块模型布局。返回 (panel_w, panel_h, info)。"""
    labels = [w for w in widgets if 'Label' in w.cls]
    xs = [w for w in widgets if w.cls in INPUT_CLS]
    ys = [w for w in widgets if w.cls in BTN_CLS]
    xs.sort(key=lambda w: (w.y, w.x))
    ys.sort(key=lambda w: w.x)
    pairs = pair_labels(labels, xs) if mode != 'watermark' else None
    if pairs is None and mode != 'watermark':
        mode = 'watermark'  # 无 Label 可配对 → 退化水印式

    # 模式参数（区块网格固定宽；控件在区块内可窄化，区块左/底对齐）
    if mode == 'label-h':
        block_w, block_h, row_gap = LABEL_W + CTRL_W + Y_GAP, CTRL_H, ROW_GAP
        def place_item(pair, x, y):
            lbl, ctrl = pair
            lbl.new = (x, y, LABEL_W, CTRL_H)
            ctrl.new = (x + LABEL_W, y, X_W_BY_CLS.get(ctrl.cls, CTRL_W), CTRL_H)
    elif mode == 'label-v':
        block_w, block_h, row_gap = CTRL_W + Y_GAP, LABEL_H_V + CTRL_H_V, ROW_GAP_V
        def place_item(pair, x, y):
            lbl, ctrl = pair
            cw = X_W_BY_CLS.get(ctrl.cls, CTRL_W)
            lbl.new = (x, y, cw, LABEL_H_V)
            ctrl.new = (x, y + LABEL_H_V, cw, CTRL_H)
    else:  # watermark
        block_w, block_h, row_gap = CTRL_W + Y_GAP, CTRL_H, ROW_GAP
        def place_item(ctrl, x, y):
            cw = X_W_BY_CLS.get(ctrl.cls, CTRL_W)
            ctrl.new = (x, y, cw, CTRL_H)

    units = pairs if pairs is not None else xs          # 布局单元
    unit_w = [block_w] * len(units)                     # 网格：区块宽统一
    y_widths = [y_width(btn_text(w.inner)) for w in ys]
    y_block_total = sum(y_widths) + Y_GAP * max(0, len(ys) - 1)
    total = sum(unit_w) + y_block_total
    info = {'mode': mode, 'xs': len(xs), 'ys': len(ys), 'pairs': len(pairs) if pairs else 0,
            'y_widths': y_widths, 'total': total, 'block_w': block_w,
            'single_row': total < SINGLE_ROW_MAX,
            'per': None, 'rows': 0, 'y_in_last': False, 'y_new_row': False,
            'h_ok': True}

    if total < SINGLE_ROW_MAX:
        info['single_row'] = True
        y = MARGIN
        x = MARGIN
        for u in units:
            place_item(u, x, y)
            x += block_w
        y_btn = y + (LABEL_H_V if mode == 'label-v' else 0)   # label-v：按钮与控件垂直对齐
        for w, yw in zip(ys, y_widths):
            w.new = (x, y_btn, yw, CTRL_H)
            x += yw + Y_GAP
        panel_w = x - Y_GAP + MARGIN
        panel_h = MARGIN + block_h + MARGIN
        if panel_h > PANEL_H_MAX:
            info['h_ok'] = False
        return panel_w, panel_h, info

    n = len(units)
    per_rule = 5 if n < 15 else (6 if n <= 24 else 7)
    max_block = max(unit_w)
    per_limit = max(1, (SINGLE_ROW_MAX - 2 * MARGIN) // max_block)   # 每行最宽 <1500
    per = min(per_rule, per_limit)
    info['per'] = per
    rows = (n + per - 1) // per
    last_cnt = n % per or per
    last_empty = n % per == 0
    info['rows'] = rows
    info['last_cnt'] = last_cnt
    info['last_empty'] = last_empty

    # Y 并入判断：剩余空间用标准区块(200)保守估算
    fit = False
    if not last_empty:
        fit = (last_cnt * X_BLOCK_DEF + y_block_total) < per * X_BLOCK_DEF
    info['fit'] = fit

    # X 布局：网格——列 x = MARGIN + col×区块宽，跨行同列左对齐；控件底部随行高对齐
    for i, u in enumerate(units):
        r, c = divmod(i, per)
        place_item(u, MARGIN + c * block_w, MARGIN + r * (block_h + row_gap))

    panel_w = per * block_w                            # 用户规范：面板宽 = 每行X数 × 区块宽
    right_edge = panel_w - MARGIN                     # Y 贴右侧基准

    def place_y(y_row):
        x = right_edge
        y_btn = y_row + (LABEL_H_V if mode == 'label-v' else 0)  # label-v：按钮与控件垂直对齐
        for w, yw in reversed(list(zip(ys, y_widths))):
            x -= yw
            w.new = (x, y_btn, yw, CTRL_H)
            x -= Y_GAP

    if fit:
        last_row_y = MARGIN + (rows - 1) * (block_h + row_gap)
        place_y(last_row_y)
        info['y_in_last'] = True
        total_rows = rows
    else:
        y_row = MARGIN + rows * (block_h + row_gap)
        place_y(y_row)
        info['y_new_row'] = True
        total_rows = rows + 1

    panel_h = MARGIN + (total_rows - 1) * (block_h + row_gap) + block_h + MARGIN
    if panel_h > PANEL_H_MAX:
        info['h_ok'] = False
    return panel_w, panel_h, info


def apply(xml, widgets, panel_w, panel_h):
    new_xml = xml
    for w in widgets:
        if w.new is None:
            continue
        nx, ny, nw, nh = w.new
        new_b = f'<BoundsAttr x="{nx}" y="{ny}" width="{nw}" height="{nh}"/>'
        assert xml.count(w.old_bounds) == 1, f"非唯一 BoundsAttr: {w.old_bounds}"
        new_xml = new_xml.replace(w.old_bounds, new_b, 1)
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
    dry = '--dry-run' in sys.argv
    mode = 'watermark'
    if '--mode' in sys.argv:
        try:
            mode = sys.argv[sys.argv.index('--mode') + 1]
        except IndexError:
            pass
    if mode not in ('watermark', 'label-h', 'label-v'):
        print(f"❌ 未知模式: {mode}（可选 watermark/label-h/label-v）")
        sys.exit(1)
    if not args:
        print(__doc__)
        sys.exit(1)
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
        panel_w, panel_h, info = auto_layout(widgets, mode)
        print(f"  模式={info['mode']}  X控件={info['xs']}  Label配对={info['pairs']}  "
              f"Y按钮={info['ys']}  Y宽={info['y_widths']}")
        print(f"  总区块宽={info['total']}  单行={'是' if info['single_row'] else '否'}")
        if not info['single_row']:
            print(f"  每行单元数={info['per']}（数量规则/宽度上限取小）  行数={info['rows']}  "
                  f"最后行单元数={info['last_cnt']}{'(满)' if info['last_empty'] else ''}")
            print(f"  Y并入最后行={'是' if info['y_in_last'] else '否'}  "
                  f"Y新行={'是' if info['y_new_row'] else '否'}")
        print(f"  → 面板 {panel_w} x {panel_h}"
              + ("" if info['h_ok'] else "  ⚠️ 超总高 300 约束！"))
        for w in widgets:
            if w.new:
                print(f"    {w.name:<22} {w.cls:<16} ({w.new[0]},{w.new[1]}) {w.new[2]}x{w.new[3]}")
        new_xml = apply(xml, widgets, panel_w, panel_h)
        check_xml(new_xml, 'after')
        if dry:
            print("  [dry-run] 未写入")
            continue
        bak = fp.parent / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        bak.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fp, bak / fp.name)
        fp.write_text(new_xml, encoding='utf-8')
        print(f"  备份: {bak / fp.name}")
        print(f"  面板 {panel_w}x{panel_h} 已写入")


if __name__ == '__main__':
    main()
