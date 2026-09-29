#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数面板排布 · 缺省方案脚本 (Ver1.0, 源自 2026-08-10 历史 kit batch_optimize_cpt.py v4.1)

方案 (容器网格排布):
  容器 = Label + 输入控件 配对一个单元格
  - 输入控件统一 180x26 (ComboBox/ComboCheckBox/DateEditor/TextEditor/NumberEditor/TimeEditor)
  - Label 宽 = 文字自适应(中文11/ASCII6 + 10留白, ≥40), 同列取最大 → 同列左对齐成竖线
  - 间距: Label→控件 4px, 组间 15px, 按钮间 30px, 面板边距 12px, 行步距 26+15=41
  - 单行内容超 1200px 自动折行 (约5组/行); 内容+按钮超 1500px → 按钮独立行右对齐
  - 超宽控件(>240px, 如 CheckBoxGroup 复选组)及其label → 独立末行, 保留原宽
  - 面板 Design_Width / DesignAttr width/height = 按内容精确重算 (不匹配即换行根因)

按钮策略:
  查询 / 导出 = 默认按钮, 缺失自动补 (FreeButton + JS: parameterCommit / exportReportToExcel)
  其他自定义按钮 (提交/导入/ADJ等) = 按需保留, 排在默认按钮之后

用法:
  python layout_panel.py --cpt "X:\path\示例预算表.cpt" [--dry-run]
  python layout_panel.py --cpt a.cpt --cpt b.cpt

安全: 自动备份到 <所在目录>\_panel_layout_bak\<时间戳>\<文件名>; 原子写 (.tmp → ET.parse → move)
"""
import argparse, io, os, re, shutil, sys
import xml.etree.ElementTree as ET
from datetime import datetime

# ── 缺省常量 (与 LAYOUT_SPEC Ver0.4 对齐, 以老脚本 v4.1 实测值为准) ──
CTRL_W, CTRL_H = 180, 26          # 输入控件统一宽高
BTN_H = 26                        # 按钮高
LABEL_CTRL_GAP = 4                # Label → 控件
CTRL_GAP = 15                     # 组间 / 行步距附加
BTN_GAP = 30                      # 按钮间
MARGIN = 12                       # 面板内边距
MAX_ROW_WIDTH = 1200              # 单行内容宽 → 折行
SINGLE_ROW_MAX = 1500             # 内容+按钮 → 按钮独立行
WIDE_CTRL = 240                   # 控件宽超过此值 → 独立行(保留原宽)
ROW_STEP = CTRL_H + CTRL_GAP      # 行步距 41
QUERY_W, EXPORT_W = 70, 80        # 默认按钮宽

INPUT_CLS = {'ComboBox', 'ComboCheckBox', 'DateEditor', 'TextEditor', 'NumberEditor', 'TimeEditor'}
BTN_CLS = {'FreeButton', 'FormSubmitButton', 'Button'}

BLK = re.compile(r'<Widget class="com\.fr\.form\.ui\.container\.WAbsoluteLayout\$BoundsWidget">.*?</Widget>', re.S)


def text_w(s):
    if not s:
        return 40
    return max(40, sum(11 if ord(ch) > 0x2E80 else 6 for ch in s) + 10)


def load_panel(raw):
    m = re.search(r'<ParameterUI class="com\.fr\.form\.main\.parameter\.FormParameterUI">.*?</ParameterUI>', raw, re.S)
    return m


def parse_blocks(pxml):
    blocks = []
    for m in BLK.finditer(pxml):
        blk = m.group(0)
        cls = re.search(r'<InnerWidget class="com\.fr\.form\.ui\.(\w+)"', blk).group(1)
        wn = re.search(r'<WidgetName name="([^"]+)"/>', blk).group(1)
        b = re.search(r'<BoundsAttr x="(-?\d+)" y="(-?\d+)" width="(\d+)" height="(\d+)"/>', blk)
        tv = re.search(r'<widgetValue>\s*<O>\s*<!\[CDATA\[([^<]*)\]\]>', blk, re.S)
        blocks.append(dict(span=m.span(), cls=cls, wn=wn, x=int(b.group(1)), y=int(b.group(2)),
                           w=int(b.group(3)), h=int(b.group(4)), blk=blk,
                           txt=tv.group(1) if tv else None))
    return blocks


def btn_kind(b):
    """默认按钮识别: query / export; 其余 None=自定义"""
    body = b['blk']
    if b['wn'].lower() in ('search', 'query') or 'parameterCommit' in body:
        return 'query'
    if 'exportReportToExcel' in body or b['wn'].lower().startswith('export'):
        return 'export'
    t = (b['txt'] or '')
    if t in ('查询', 'Query'):
        return 'query'
    if t in ('导出', 'Export'):
        return 'export'
    return None


def make_btn(name, text, js, w):
    return ('<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">\n'
            '<InnerWidget class="com.fr.form.ui.FreeButton">\n'
            '<Listener event="click" name="click1">\n'
            '<JavaScript class="com.fr.js.JavaScriptImpl">\n<Parameters/>\n<Content>\n<![CDATA[%s]]></Content>\n'
            '</JavaScript>\n</Listener>\n'
            '<WidgetName name="%s"/>\n'
            '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">\n'
            '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>\n'
            '<PrivilegeControl/>\n</WidgetAttr>\n'
            '<Text>\n<![CDATA[%s]]></Text>\n<Hotkeys>\n<![CDATA[]]></Hotkeys>\n'
            '</InnerWidget>\n'
            '<BoundsAttr x="0" y="0" width="%d" height="26"/>\n</Widget>') % (js, name, text, w)


def relayout(path, dry=False):
    raw = io.open(path, encoding='utf-8').read()
    pm = load_panel(raw)
    if not pm:
        print('%s: 无 ParameterUI, 跳过' % os.path.basename(path))
        return
    pxml = pm.group(0)
    blocks = parse_blocks(pxml)

    # 行聚类(容差6) + 阅读序
    def row_key(b):
        return (b['y'] + 3) // 1  # placeholder
    ys = sorted(set(b['y'] for b in blocks))
    rows_y = []
    for y in ys:
        if not rows_y or y - rows_y[-1][-1] > 6:
            rows_y.append([y])
        else:
            rows_y[-1].append(y)
    ymap = {}
    for gi, g in enumerate(rows_y):
        for y in g:
            ymap[y] = gi
    for b in blocks:
        b['row'] = ymap[b['y']]
    # 阅读序: 行内按x; x相同(服务器y抖动致文件序颠倒)时 Label 优先, 保证 label→控件配对
    blocks.sort(key=lambda b: (b['row'], b['x'], 0 if b['cls'] == 'Label' else 1))

    # 分类
    btns = [b for b in blocks if b['cls'] in BTN_CLS]
    widgets = [b for b in blocks if b['cls'] not in BTN_CLS]
    for b in btns:
        b['kind'] = btn_kind(b)

    # 配对: 行内 label 与控件按 x 距离就近配对 (不分左右 — 设计器保存可能把label挤到控件右侧)
    pairs, orphans = [], []
    by_row = {}
    for b in widgets:
        by_row.setdefault(b['row'], {'lbl': [], 'ctl': []})
        by_row[b['row']]['lbl' if b['cls'] == 'Label' else 'ctl'].append(b)
    for r in sorted(by_row):
        g = by_row[r]
        used = set()
        row_pairs = []
        for lbl in g['lbl']:
            best, bd = None, None
            for c in g['ctl']:
                if id(c) in used:
                    continue
                d = abs(c['x'] - lbl['x'])
                if bd is None or d < bd:
                    best, bd = c, d
            if best is None:
                orphans.append((lbl, None))
            else:
                used.add(id(best))
                row_pairs.append((lbl, best))
        for c in g['ctl']:
            if id(c) not in used:
                if c['w'] > WIDE_CTRL or c['cls'] not in INPUT_CLS:
                    orphans.append((None, c))
                else:
                    row_pairs.append((None, c))
        # 宽控件对 → 独立行; 普通对 → 流式网格
        for lbl, ctl in row_pairs:
            if ctl['w'] > WIDE_CTRL or ctl['cls'] not in INPUT_CLS:
                orphans.append((lbl, ctl))
            else:
                pairs.append((lbl, ctl))
        # 行内顺序按控件x
        pairs[-len(row_pairs):] = sorted(pairs[-len(row_pairs):], key=lambda p: p[1]['x'])

    # 默认按钮补齐
    have = set(b['kind'] for b in btns)
    added = []
    if 'query' not in have:
        added.append(('query', make_btn('query', '查询', '_g().parameterCommit()', QUERY_W), QUERY_W))
    if 'export' not in have:
        added.append(('export', make_btn('exportBtn', '导出', "_g().exportReportToExcel('simple')", EXPORT_W), EXPORT_W))
    # 按钮顺序: query, export, 自定义(原序); 缺省按钮以 _new 标记后插
    btn_list = [b for b in btns if b['kind'] == 'query']
    for kind, xmls, w in added:
        if kind == 'query':
            btn_list.append(dict(kind='query', wn='query', w=w, blk=None, _xml=xmls, _new=True))
    btn_list += [b for b in btns if b['kind'] == 'export']
    for kind, xmls, w in added:
        if kind == 'export':
            btn_list.append(dict(kind='export', wn='exportBtn', w=w, blk=None, _xml=xmls, _new=True))
    btn_list += [b for b in btns if b['kind'] is None]

    # 折行 (按各容器自身宽估算)
    def pair_w(p):
        lw = text_w(p[0]['txt']) if p[0] else 0
        return (lw if lw else CTRL_W) + (LABEL_CTRL_GAP if p[0] else 0) + CTRL_W
    flow_rows, cur, cur_w = [], [], 0
    for p in pairs:
        w = pair_w(p)
        add = w + (CTRL_GAP if cur else 0)
        if cur and cur_w + add > MAX_ROW_WIDTH:
            flow_rows.append(cur)
            cur, cur_w, add = [], 0, w
        cur.append(p)
        cur_w += add
    if cur:
        flow_rows.append(cur)

    # 列宽 = 各列最大 label 宽
    ncols = max(len(r) for r in flow_rows) if flow_rows else 0
    col_lw = [0] * ncols
    for r in flow_rows:
        for j, (lbl, _) in enumerate(r):
            if lbl is not None:
                col_lw[j] = max(col_lw[j], text_w(lbl['txt']))
    col_lw = [max(w, 40) for w in col_lw]
    label_x, ctrl_x = [], []
    cx = MARGIN
    for j in range(ncols):
        label_x.append(cx)
        ctrl_x.append(cx + col_lw[j] + LABEL_CTRL_GAP)
        cx = ctrl_x[j] + CTRL_W + CTRL_GAP
    all_right = ctrl_x[-1] + CTRL_W if ncols else MARGIN

    # 布点坐标
    for ri, r in enumerate(flow_rows):
        y = MARGIN + ri * ROW_STEP
        for j, (lbl, ctl) in enumerate(r):
            if lbl is not None:
                lbl['nx'], lbl['ny'], lbl['nw'], lbl['nh'] = label_x[j], y, col_lw[j], CTRL_H
            ctl['nx'], ctl['ny'], ctl['nw'], ctl['nh'] = ctrl_x[j], y, CTRL_W, CTRL_H

    # 按钮: 末内容行右侧; 超宽 → 独立行右对齐
    btn_total = sum(b['w'] for b in btn_list) + BTN_GAP * max(0, len(btn_list) - 1)
    last_row_y = MARGIN + (len(flow_rows) - 1) * ROW_STEP if flow_rows else MARGIN
    if all_right + CTRL_GAP + btn_total + MARGIN <= SINGLE_ROW_MAX:
        bx, btn_y = all_right + CTRL_GAP, last_row_y
        panel_w = bx + btn_total
    else:
        btn_y = MARGIN + len(flow_rows) * ROW_STEP
        bx = max(all_right, MARGIN + btn_total) - btn_total  # 右对齐到内容右缘
        panel_w = max(all_right, bx + btn_total)
    for b in btn_list:
        b['nx'], b['ny'], b['nw'], b['nh'] = bx, btn_y, b['w'], BTN_H
        bx += b['w'] + BTN_GAP

    # 独立行 (宽控件组, 如 CheckBoxGroup 复选组)
    if btn_y > last_row_y:
        oy = btn_y + ROW_STEP
    else:
        oy = last_row_y + ROW_STEP if flow_rows else MARGIN
    max_w, orphan_maxh = panel_w, CTRL_H
    for lbl, ctl in orphans:
        if lbl is not None:
            lbl['nx'], lbl['ny'], lbl['nw'], lbl['nh'] = MARGIN, oy, text_w(lbl['txt']), lbl['h']
            max_w, orphan_maxh = max(max_w, MARGIN + lbl['nw']), max(orphan_maxh, lbl['h'])
        if ctl is not None:
            ctl['nx'] = MARGIN if lbl is None else MARGIN + text_w(lbl['txt']) + LABEL_CTRL_GAP
            ctl['ny'], ctl['nw'], ctl['nh'] = oy, ctl['w'], ctl['h']
            max_w, orphan_maxh = max(max_w, ctl['nx'] + ctl['w']), max(orphan_maxh, ctl['h'])
        oy += ROW_STEP
    panel_w = max_w + MARGIN
    panel_h = (oy - ROW_STEP) + orphan_maxh + MARGIN if orphans else (btn_y + BTN_H + MARGIN)

    # 报告
    print('── %s' % os.path.basename(path))
    for ri, r in enumerate(flow_rows):
        seg = []
        for lbl, ctl in r:
            tag = ctl['wn'] + ('(+%s)' % lbl['txt'] if lbl else '')
            seg.append('%s@%d' % (tag, ctl['nx']))
        print('   行%d y=%d: %s' % (ri + 1, MARGIN + ri * ROW_STEP, ' | '.join(seg)))
    print('   按钮行 y=%d: %s' % (btn_y, ' '.join('%s@%d' % (b['wn'], b['nx']) for b in btn_list)))
    for lbl, ctl in orphans:
        print('   独立行 y=%d: %s' % (lbl['ny'] if lbl else ctl['ny'], (lbl['txt'] if lbl else '') + ' → ' + (ctl['wn'] if ctl else '-')))
    print('   面板 %dx%d | 补默认按钮: %s' % (panel_w, panel_h, [k for k, _, _ in added] or '无'))

    if dry:
        return

    # 备份
    bdir = os.path.join(os.path.dirname(path), '_panel_layout_bak', datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(bdir, exist_ok=True)
    shutil.copy2(path, os.path.join(bdir, os.path.basename(path)))

    # 重写 bounds (块内容唯一, 按块原文精确替换)
    def rewrite(blk, nx, ny, nw, nh):
        return re.sub(r'<BoundsAttr x="-?\d+" y="-?\d+" width="\d+" height="\d+"/>',
                      '<BoundsAttr x="%d" y="%d" width="%d" height="%d"/>' % (nx, ny, nw, nh), blk, count=1)

    for item in [b for p in pairs for b in p if b] + \
                [b for o in orphans for b in o if b] + btn_list:
        if item.get('_new'):
            continue
        item['blk'] = rewrite(item['blk'], item['nx'], item['ny'], item['nw'], item['nh'])

    for m in list(BLK.finditer(pxml)):
        blk = m.group(0)
        wn = re.search(r'<WidgetName name="([^"]+)"/>', blk).group(1)
        item = next((it for it in [b for p in pairs for b in p if b] + [b for o in orphans for b in o if b] + btn_list
                     if not it.get('_new') and it['blk'] and re.search(r'<WidgetName name="%s"/>' % re.escape(wn), it['blk'])), None)
        if item and item['blk'] != blk:
            pxml = pxml.replace(blk, item['blk'], 1)

    # 新按钮: 插到最后一个 </Widget> 后 & MobileWidgetList 登记
    for kind, xmls, w in added:
        last_end = pxml.rfind('</Widget>')
        pxml = pxml[:last_end + len('</Widget>')] + '\n' + xmls + pxml[last_end + len('</Widget>'):]
        mm = re.search(r'(<MobileWidgetList>)(.*?)(</MobileWidgetList>)', pxml, re.S)
        if mm:
            nm = 'query' if kind == 'query' else 'exportBtn'
            pxml = pxml[:mm.start(2)] + '<Widget widgetName="%s"/>\n' % nm + pxml[mm.start(2):]

    # 面板尺寸 (精确重算, 只增不减的旧逻辑是换行根因)
    pxml = re.sub(r'(<Design_Width design_width=")\d+(")', r'\g<1>%d\g<2>' % panel_w, pxml)
    pxml = re.sub(r'(<DesignAttr width=")\d+(" height=")\d+("/>)', r'\g<1>%d\g<2>%d\g<3>' % (panel_w, panel_h), pxml)

    raw2 = raw[:pm.start()] + pxml + raw[pm.end():]
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.write(raw2)
    ET.parse(tmp)
    shutil.move(tmp, path)
    print('   ✓ 已写入 (备份: %s)' % bdir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cpt', action='append', required=True, help='.cpt 路径 (可多次)')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    for p in a.cpt:
        relayout(p, a.dry_run)


if __name__ == '__main__':
    main()
