"""
泛化版参数面板排版：自动识别所有控件，按宽度约束分行，跨行列对齐。
用法: python widen_all.py <cpt路径>
"""
import sys, re, shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CTRL_W, CTRL_H = 180, 26
LABEL_GAP, CTRL_GAP, BTN_GAP = 5, 20, 40
MARGIN, ROW_H_GAP = 12, 8
MAX_ROW_W = 1300
MAX_ALL_W = 1500

def process(cpt_path):
    fp = Path(cpt_path)
    if not fp.exists():
        print(f"❌ 不存在: {fp}")
        return

    # 备份
    bak = fp.parent / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    bak.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fp, bak / fp.name)

    with open(fp, 'r', encoding='utf-8') as f:
        xml = f.read()

    pm = re.search(r'(<ParameterUI.*?</ParameterUI>)', xml, re.DOTALL)
    if not pm:
        print(f"⚠️  {fp.name}: 无 ParameterUI")
        return
    pui = pm.group(0)

    # 提取所有 Widget 的 bounds
    w_re = re.compile(
        r'<Widget class="[^"]*\x24BoundsWidget">.*?<WidgetName name="([^"]+)".*?'
        r'<BoundsAttr\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"',
        re.DOTALL)
    widgets = {}
    for m in w_re.finditer(pui):
        widgets[m.group(1)] = {
            'x':int(m.group(2)), 'y':int(m.group(3)),
            'w':int(m.group(4)), 'h':int(m.group(5)),
            'full':m.group(0)
        }

    # 分离 Label / 控件 / 按钮
    inner_re = re.compile(
        r'<InnerWidget class="([^"]+)"[^>]*>(.*?)</InnerWidget>',
        re.DOTALL)
    label_pairs = []  # [(label_name, ctrl_name), ...]
    btns = []         # [(name, func, width), ...]

    for wname, w in widgets.items():
        if 'label' in wname.lower():
            # 找对应的控件（下一个 widget）
            pass  # handle below

    # 按 y 分组，然后按 x 排序配对
    wlist = [(n, d) for n, d in widgets.items()]
    wlist.sort(key=lambda x: (x[1]['y'], x[1]['x']))

    # 配对: Label → 紧跟的控件
    pairs = []
    btns = []
    i = 0
    while i < len(wlist):
        n, d = wlist[i]
        inner_m = inner_re.search(d['full'])
        if not inner_m:
            i += 1; continue
        cls = inner_m.group(1)
        inner = inner_m.group(2)

        if 'Label' in cls:
            if i+1 < len(wlist):
                n2, d2 = wlist[i+1]
                inner_m2 = inner_re.search(d2['full'])
                if inner_m2 and 'Label' not in inner_m2.group(1):
                    pairs.append((n2, n))  # (ctrl, label)
                    i += 2; continue
            i += 1
        elif 'Button' in cls or 'FormSubmit' in cls:
            # 识别按钮功能 + 实际宽度（不能硬编码 80，IMPORT 按钮宽 120）
            txt_m = re.search(r'<Text><!\[CDATA\[(.*?)\]\]></Text>', inner)
            func = txt_m.group(1) if txt_m else '?'
            actual_w = d['w']  # 从 BoundsAttr 提取实际宽度
            btns.append({'name': n, 'func': func, 'w': actual_w, 'full': d['full']})
            i += 1
        else:
            i += 1

    if not pairs:
        print(f"⚠️  {fp.name}: 无控件对")
        return

    # 计算每组宽度
    grp_w = []
    for cn, ln in pairs:
        lw = widgets[ln]['w'] if ln in widgets else 50
        grp_w.append(lw + LABEL_GAP + CTRL_W)

    btn_total = sum(b['w'] for b in btns) + BTN_GAP * max(0, len(btns)-1)

    # 分行
    all_w = MARGIN + sum(grp_w) + CTRL_GAP*(len(grp_w)-1) + (CTRL_GAP + btn_total if btns else 0) + MARGIN
    if all_w <= MAX_ALL_W:
        rows = [pairs]
        btn_new_row = False
    else:
        rows, cur, cur_w = [], [], 0
        for i, g in enumerate(pairs):
            w = grp_w[i]; add = w + (CTRL_GAP if cur else 0)
            if cur and cur_w + add > MAX_ROW_W:
                rows.append(cur); cur = []; cur_w = 0; add = w
            cur.append(g); cur_w += add
        if cur: rows.append(cur)
        if btns:
            last_grps = rows[-1]
            last_idx = pairs.index(last_grps[0])
            last_n = len(last_grps)
            last_w = sum(grp_w[last_idx:last_idx+last_n]) + CTRL_GAP*(last_n-1)
            btn_new_row = last_w + CTRL_GAP + btn_total > MAX_ROW_W

    n_cols = max(len(r) for r in rows)

    # 跨行最大 label 宽度
    col_lw = [0]*n_cols
    for r in rows:
        for ci, (_, ln) in enumerate(r):
            if ci < n_cols and ln in widgets:
                col_lw[ci] = max(col_lw[ci], widgets[ln]['w'])

    # 列坐标
    label_x = [MARGIN]
    combo_x = [MARGIN + col_lw[0] + LABEL_GAP]
    for i in range(1, n_cols):
        label_x.append(combo_x[i-1] + CTRL_W + CTRL_GAP)
        combo_x.append(label_x[i] + col_lw[i] + LABEL_GAP)

    changes = 0
    for ri, r in enumerate(rows):
        y = MARGIN + ri * (CTRL_H + ROW_H_GAP)
        for ci, (cn, ln) in enumerate(r):
            lx = label_x[ci]; cx = combo_x[ci]
            if ln in widgets:
                n = re.sub(r'x="\d+"', f'x="{lx}"', widgets[ln]['full'])
                n = re.sub(r'y="\d+"', f'y="{y}"', n)
                if n != widgets[ln]['full']:
                    pui = pui.replace(widgets[ln]['full'], n); changes += 1
                    widgets[ln]['full'] = n
            if cn in widgets:
                n = re.sub(r'x="\d+"', f'x="{cx}"', widgets[cn]['full'])
                n = re.sub(r'y="\d+"', f'y="{y}"', n)
                if n != widgets[cn]['full']:
                    pui = pui.replace(widgets[cn]['full'], n); changes += 1
                    widgets[cn]['full'] = n

    all_right = max(combo_x[len(r)-1] + CTRL_W for r in rows)
    last_row_right = combo_x[len(rows[-1])-1] + CTRL_W

    # 按钮布局
    if btns:
        btn_total = sum(b['w'] for b in btns) + BTN_GAP * (len(btns)-1)
        # 判断按钮放最后一行还是新行：
        # 依据 = 最后一行右侧剩余空间能否容纳按钮组
        # last_row_right + CTRL_GAP + btn_total + MARGIN <= MAX_ALL_W
        same_row_w = last_row_right + CTRL_GAP + btn_total + MARGIN
        btn_new_row = same_row_w > MAX_ALL_W

        if btn_new_row:
            btn_y = MARGIN + len(rows) * (CTRL_H + ROW_H_GAP)
            n_rows_total = len(rows) + 1
            bx = all_right
            for b in reversed(btns):
                bw = b['w']
                bx = bx - bw
                n = re.sub(r'x="\d+"', f'x="{bx}"', b['full'])
                n = re.sub(r'y="\d+"', f'y="{btn_y}"', n)
                if n != b['full']:
                    pui = pui.replace(b['full'], n); changes += 1
                bx = bx - BTN_GAP
            btn_row_w = sum(b['w'] for b in btns) + BTN_GAP * max(0, len(btns)-1) + MARGIN
            panel_w = max(all_right + MARGIN, bx + MARGIN, btn_row_w)
        else:
            # 按钮放最后一行，右对齐到 all_right（最宽行右边界）
            btn_y = MARGIN + (len(rows)-1) * (CTRL_H + ROW_H_GAP)
            n_rows_total = len(rows)
            bx = all_right  # 右对齐起点
            for b in reversed(btns):
                bw = b['w']
                bx = bx - bw
                n = re.sub(r'x="\d+"', f'x="{bx}"', b['full'])
                n = re.sub(r'y="\d+"', f'y="{btn_y}"', n)
                if n != b['full']:
                    pui = pui.replace(b['full'], n); changes += 1
                bx = bx - BTN_GAP
            panel_w = all_right + MARGIN
    else:
        n_rows_total = len(rows)
        panel_w = all_right + MARGIN

    ph = MARGIN + (n_rows_total-1)*(CTRL_H+ROW_H_GAP) + CTRL_H + MARGIN

    pui = re.sub(r'design_width="\d+"', f'design_width="{panel_w}"', pui)
    pui = re.sub(r'(<DesignAttr width=")\d+(")', rf'\g<1>{panel_w}\g<2>', pui)
    pui = re.sub(r'(<DesignAttr[^>]*height=")\d+(")', rf'\g<1>{ph}\g<2>', pui)

    xml = xml[:pm.start(1)] + pui + xml[pm.end(1):]
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(xml)

    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(xml)
    except ET.ParseError as e:
        print(f"⚠️  {fp.name}: XML 验证失败: {e}")

    print(f"✅ {fp.name}: {panel_w}x{ph} {changes}ch rows={[len(r) for r in rows]} btn_new={btn_new_row}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python widen_all.py <cpt路径> [cpt路径...]")
        sys.exit(1)
    for path in sys.argv[1:]:
        process(path)
