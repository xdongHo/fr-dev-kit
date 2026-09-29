# -*- coding: utf-8 -*-
"""明细报表单元格格式化（通配规则，用户定稿 2026-08-06）
规则：
  字体默认 微软雅黑 9号(size=72)
  数值      → 右对齐  #,##0.00        （判断依据：数据库建表 numeric 列，或标签含 累计/月/金额类词）
  百分比    → 右对齐  #0.00%          （标签含 % 或 Rate）
  文本      → 左对齐
  序号      → 居中    （标签为 序号/Seq/SEQ）
  日期      → 左对齐  yyyy-MM-dd      （标签含 Date/日期）

用法：python fmt_detail_cells.py <cpt路径> [--numeric-labels 标签1,标签2,...]
  --numeric-labels: 数值列标签清单（建议从建表 SQL 的 numeric 列提取，最准）
"""
import re, sys, shutil
from datetime import datetime
from pathlib import Path

FONT = '<FRFont name="微软雅黑" style="0" size="72" foreground="-13421773"/>'
BORDER = ('<Border>\n<Top style="1" color="-1841172"/>\n<Bottom style="1" color="-1841172"/>\n'
          '<Left style="1" color="-1841172"/>\n<Right style="1" color="-1841172"/>\n</Border>')
BG = '<Background name="ColorBackground" color="-1"/>'


def make_style(h_align, fmt_inner):
    """构造 Style 块。fmt_inner: ('class', 'CDATA内容') 或 None(TextFormat)"""
    if fmt_inner is None:
        fmt = '<Format class="com.fr.base.TextFormat"/>'
    else:
        cls, pat = fmt_inner
        fmt = f'<Format class="{cls}">\n<![CDATA[{pat}]]>\n</Format>'
    return (f'<Style horizontal_alignment="{h_align}" imageLayout="1" paddingLeft="4" paddingRight="4">\n'
            f'{fmt}\n{FONT}\n{BG}\n{BORDER}\n</Style>')


def classify(label, numeric_labels):
    """按用户通配规则分类 → ('text'|'num'|'pct'|'date'|'seq', 左对齐码)"""
    if numeric_labels and label in numeric_labels:
        return 'num', '2'
    up = label.upper()
    if '%' in up or 'RATE' in up:
        return 'pct', '2'
    if 'DATE' in up or '日期' in label:
        return 'date', '0'
    if label in ('序号', 'Seq', 'SEQ') or up in ('SEQ',):
        return 'seq', '1'
    return 'text', '0'


def main():
    fp = Path(sys.argv[1])
    numeric_labels = set()
    if '--numeric-labels' in sys.argv:
        i = sys.argv.index('--numeric-labels')
        numeric_labels = {x.strip() for x in sys.argv[i + 1].split(',') if x.strip()}

    c = fp.read_text(encoding='utf-8')

    # 收集数据行(约定 r="2")单元格 label → s
    cells = {}
    for m in re.finditer(r'<C c="(\d+)" r="2" s="(\d+)">[\s\S]*?columnName="([^"]*)"', c):
        col, s, label = int(m.group(1)), m.group(2), m.group(3)
        cells[col] = (s, label)
    if not cells:
        print('❌ 未找到 r=2 数据行 DSColumn 单元格'); return 1
    print(f'数据单元格 {len(cells)} 个')

    # 分类
    new_s = {}          # col -> 新 s 索引
    n_cls = {'text': 0, 'num': 0, 'pct': 0, 'date': 0, 'seq': 0}
    for col, (s, label) in cells.items():
        kind, _ = classify(label, numeric_labels)
        n_cls[kind] += 1
    print('分类统计:', n_cls)

    # 新样式: s=1 文本左(改造现有), s=2 数值右, s=3 百分比右, s=4 日期, s=5 序号居中
    styles_add = []
    num_fmt = ('com.fr.base.CoreDecimalFormat', '#,##0.00')
    pct_fmt = ('com.fr.base.CoreDecimalFormat', '#0.00%')
    date_fmt = ('com.fr.general.date.FineDateFormat', 'yyyy-MM-dd')
    style_map = {
        'num': ('2', make_style('2', num_fmt)),   # 数值 居右(2)
        'pct': ('3', make_style('2', pct_fmt)),   # 百分比 居右(2)
        'date': ('4', make_style('0', date_fmt)), # 日期 居中(0)
        'seq': ('5', make_style('0', None)),      # 序号 居中(0)
    }
    for kind, (idx, xml) in style_map.items():
        if n_cls[kind]:
            styles_add.append(xml)
            for col, (s, label) in cells.items():
                if classify(label, numeric_labels)[0] == kind:
                    new_s[col] = idx

    # 文本左: 现有 s=1 改 horizontal_alignment 2→1 (2=居右, 1=居左)
    if n_cls['text']:
        style1_old = re.search(r'<Style horizontal_alignment="2" imageLayout="1" paddingLeft="4" paddingRight="4">\n<Format class="com.fr.base.TextFormat"/>\n' + FONT.replace('"', r'\"').replace('\\', '') + '.*?</Style>', c, re.DOTALL)
        # 简单方式: 替换第一个含 TextFormat+size=72 的 Style 的对齐
        c = c.replace('<Style horizontal_alignment="2" imageLayout="1" paddingLeft="4" paddingRight="4">\n<Format class="com.fr.base.TextFormat"/>',
                      '<Style horizontal_alignment="1" imageLayout="1" paddingLeft="4" paddingRight="4">\n<Format class="com.fr.base.TextFormat"/>', 1)
        for col, (s, label) in cells.items():
            if classify(label, numeric_labels)[0] == 'text':
                new_s[col] = '1'

    # 插入新样式到 StyleList
    assert '</StyleList>' in c, '无 StyleList'
    c = c.replace('</StyleList>', '\n'.join(styles_add) + '\n</StyleList>', 1)

    # 改单元格 s
    for col, idx in new_s.items():
        old = f'<C c="{col}" r="2" s="1">'
        new = f'<C c="{col}" r="2" s="{idx}">'
        assert c.count(old) == 1, f'col{col} 单元格锚点异常'
        c = c.replace(old, new, 1)

    bak = fp.parent / ('_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    bak.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fp, bak / fp.name)
    fp.write_text(c, encoding='utf-8')

    import xml.etree.ElementTree as ET
    ET.parse(fp)
    print(f'✅ 完成: 新样式 {len(styles_add)} 个, 单元格 s 更新 {len(new_s)} 个, 备份 {bak}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
