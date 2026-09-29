#!/usr/bin/env python3
"""
FR 报表批量优化脚本 v4.1 — 全量一键优化
包含以下独立功能（也可单独运行）:
  add_query_btn.py        — 缺 Query 自动补
  add_export_btn.py       — 缺 Export 自动补 (exportReportToExcel)
  cancel_params_template  — 取消常用参数组合
  widen_all.py            — 自动分行 + 跨行列对齐
  add_para_init_event.py  — CSS 注入
  set_write_no_toolbar.py — 填报无工具栏
详见 README.md
"""
import os, re, shutil
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# ═══════════════ 配置 ═══════════════
# 目录自适应：FR_REPORTLETS 环境变量 > 默认安装路径（示例工程，按你的环境替换）
BASE_DIR = Path(os.environ.get("FR_REPORTLETS",
                               r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程"))
if not BASE_DIR.is_dir():
    raise SystemExit(f"[!] 目标目录不存在: {BASE_DIR}\n    设置 FR_REPORTLETS=<你的 reportlets 路径> 后重跑。")
BACKUP_DIR = BASE_DIR / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
EXCLUDE_DIRS = {"权限配置", "_backup", "_backup_v2", "明细报表 - 副本", "数据权限bak",
                "_backup_20260730_165934"}

def _is_excluded(dirname, exclude_set):
    for ex in exclude_set:
        if dirname == ex or dirname.startswith(ex + '_'):
            return True
    return False

# 控件尺寸
LABEL_H = "26"
CTRL_W, CTRL_H = "180", "26"
BTN_W, BTN_H = "80", "26"
IMPORT_W = "120"   # Import 按钮特殊宽度
BTN_GAP = 30       # 按钮间距
CTRL_GAP = 15      # 控件列间距
LABEL_CTRL_GAP = 4 # Label 与关联控件间距

# 布局约束
MAX_ROW_WIDTH = 1200   # 单行最大宽度
SINGLE_ROW_MAX = 1500  # 单行总宽度阈值
RIGHT_ALIGN_MAX = 1200 # 末行右对齐阈值（小于此值右对齐）
MARGIN = 12            # 面板内边距

# 行高 (FU) — FR XML 序列化: 1mm ≈ 144,200 FU
H_HEADER = "1442289"   # 10mm
H_DETAIL = "1153643"   # 8mm

FONT_NAME = "微软雅黑"

# 按钮顺序定义
BTN_ORDER = ["Query", "Export", "Submit", "Import", "Adj Data"]


def find_files():
    files = []
    for root, dirs, filenames in os.walk(str(BASE_DIR)):
        dirs[:] = [d for d in dirs if not _is_excluded(d, EXCLUDE_DIRS)]
        for f in filenames:
            if f.endswith('.cpt'):
                files.append(Path(root) / f)
    return sorted(files)


def btn_function(inner_xml):
    """识别按钮功能: Query/Export/Submit/Import/Adj Data"""
    body = inner_xml
    t_match = re.search(r'<Text>\s*<!\[CDATA\[(.*?)\]\]>\s*</Text>', body, re.DOTALL)
    text = t_match.group(1).strip() if t_match else ''
    w_match = re.search(r'<WidgetName\s+name="([^"]*)"', body)
    wname = w_match.group(1) if w_match else ''

    if text in ('Query', '查询') or wname == 'search':
        return 'Query'
    if 'exportReportToExcel' in body or text == 'Export':
        return 'Export'
    if 'verifyAndWriteReport' in body or 'writeReport' in body or text in ('Submit', '保存', '提交', 'Confirm'):
        return 'Submit'
    if 'Import' in text or 'import' in wname.lower():
        return 'Import'
    if 'Adj' in text or 'ADJ' in wname or 'adj' in wname.lower():
        return 'Adj Data'

    # 模糊匹配
    tl = text.lower()
    if 'query' in tl or '查询' in tl: return 'Query'
    if 'export' in tl or '导出' in tl: return 'Export'
    if 'submit' in tl or '保存' in tl: return 'Submit'
    if 'import' in tl or '导入' in tl: return 'Import'
    if 'adj' in tl: return 'Adj Data'

    return None  # 无法识别


def has_ds_cell(cell_body):
    o_tag = re.search(r'<O\b([^>]*)>', cell_body)
    if not o_tag: return False
    o_attrs = o_tag.group(1)
    if 't="DSColumn"' in o_attrs: return True
    cd_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', cell_body[o_tag.end():])
    if cd_match and re.match(r'^ds\d+\.(G|S)\(', cd_match.group(1).strip()):
        return True
    return False


def has_formula(cell_body):
    o_tag = re.search(r'<O\b([^>]*)>', cell_body)
    if not o_tag: return False
    o_attrs = o_tag.group(1)
    if 'class="com.fr.base.Formula"' in o_attrs: return True
    if 't="XMLable"' in o_attrs: return True
    cd_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', cell_body[o_tag.end():])
    if cd_match and cd_match.group(1).strip().startswith('='): return True
    return False


def classify_rows(content):
    cell_match = re.search(r'<CellElementList>(.*?)</CellElementList>', content, re.DOTALL)
    if not cell_match: return {}
    cells_xml = cell_match.group(1)
    cell_re = re.compile(r'<C[^>]*\br="(\d+)"[^>]*>(.*?)</C>', re.DOTALL)
    has_any_ds = False
    row_info = {}
    for m in cell_re.finditer(cells_xml):
        row = int(m.group(1)); body = m.group(2)
        is_ds = has_ds_cell(body); is_fm = has_formula(body)
        if row not in row_info: row_info[row] = {'ds': False, 'formula': False}
        if is_ds: row_info[row]['ds'] = True; has_any_ds = True
        if is_fm: row_info[row]['formula'] = True
    row_types = {}
    for row, info in row_info.items():
        if has_any_ds:
            row_types[row] = 'data' if info['ds'] else 'header'
        else:
            row_types[row] = 'data' if info['formula'] else 'header'
    # Row 0 保护
    if 0 in row_types: row_types[0] = 'header'
    # 原高度 ≥1.8M 保护
    rh_ov = re.search(r'<RowHeight\s+defaultValue="\d+"\s*>\s*<!\[CDATA\[([^\]]*?)\]\]>', content, re.DOTALL)
    if rh_ov:
        for i, h in enumerate(rh_ov.group(1).split(',')):
            try:
                if int(h.strip()) >= 1800000 and i in row_types:
                    row_types[i] = 'header'
            except: pass
    return row_types


def fix_row_heights(content):
    row_types = classify_rows(content)
    if not row_types: return content
    rh_re = re.compile(r'(<RowHeight\s+defaultValue=")(\d+)("\s*>\s*<!\[CDATA\[)([^\]]*?)(\]\]>\s*</RowHeight>)', re.DOTALL)
    def repl(m):
        p1, d, p3, hs, p5 = m.groups()
        heights = [h.strip() for h in hs.split(',') if h.strip()]
        if not heights: return m.group(0)
        nh = [H_HEADER if row_types.get(i, 'header') == 'header' else H_DETAIL for i in range(len(heights))]
        return f"{p1}{H_DETAIL}{p3}{','.join(nh)}{p5}"
    return rh_re.sub(repl, content)


def fix_parameter_controls(content):
    param_re = re.compile(r'(<ParameterUI.*?</ParameterUI>)', re.DOTALL)
    param_match = param_re.search(content)
    if not param_match: return content
    param_xml = param_match.group(1)
    original = param_xml

    # --- 1. Label 宽度根据文本自适应, 贴在控件左侧 ---
    def _calc_label_width(text):
        """根据文本估算 Label 宽度"""
        if not text: return 40
        # 中文 ~10px, ASCII ~6px, 留白 8px
        w = 8
        for ch in text:
            if '\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f':
                w += 10
            else:
                w += 6
        return max(w, 40)

    label_re = re.compile(
        r'(<InnerWidget class="com\.fr\.form\.ui\.Label">(.*?)</InnerWidget>\s*)'
        r'<BoundsAttr\s+x="(\d+)"\s+y="(\d+)"\s+width="\d+"\s+height="\d+"',
        re.DOTALL)

    def _fix_label(m):
        prefix = m.group(1)
        inner = m.group(2)
        x, y = m.group(3), m.group(4)
        # 提取文本
        txt_m = re.search(r'<widgetValue>.*?<!\[CDATA\[(.*?)\]\]>.*?</widgetValue>', inner, re.DOTALL)
        text = txt_m.group(1).strip() if txt_m else ''
        w = _calc_label_width(text)
        return f'{prefix}<BoundsAttr x="{x}" y="{y}" width="{w}" height="{LABEL_H}"'

    param_xml = label_re.sub(_fix_label, param_xml)

    # --- 2. 输入控件 → 180x26 ---
    for itype in ['ComboCheckBox', 'ComboBox', 'DateEditor', 'TextEditor', 'NumberEditor', 'TimeEditor']:
        param_xml = re.sub(
            rf'(<InnerWidget class="com\.fr\.form\.ui\.{itype}">.*?</InnerWidget>\s*)'
            rf'<BoundsAttr\s+x="(\d+)"\s+y="(\d+)"\s+width="\d+"\s+height="\d+"',
            rf'\1<BoundsAttr x="\2" y="\3" width="{CTRL_W}" height="{CTRL_H}"',
            param_xml, flags=re.DOTALL)

    # --- 3. 年/日期控件转换: ComboCheckBox → YearControl / DateEditor ---
    YEAR_KEYS = ['year', '年', 'yr', '年份', '年度']
    DATE_KEYS = ['date', '日期', 'period', '期间', 'month', '月', '月份']

    def _is_year_ctrl(inner):
        combined = inner.lower()
        return any(k in combined for k in YEAR_KEYS)

    def _is_date_ctrl(inner):
        combined = inner.lower()
        return any(k in combined for k in DATE_KEYS)

    def _make_yearcontrol(inner_xml):
        wname = re.search(r'<WidgetName\s+name="[^"]*"\s*/>', inner_xml)
        wid = re.search(r'<WidgetID\s+[^>]*/>', inner_xml)
        wattr = re.search(r'(<WidgetAttr[^>]*>.*?</WidgetAttr>)', inner_xml, re.DOTALL)
        wval = re.search(r'(<widgetValue>.*?</widgetValue>)', inner_xml, re.DOTALL)
        # 年份控件默认值 = year(now()) 公式（Ver0.5：不写死静态年份）
        year_default = ('<widgetValue>\n'
                        '<O t="XMLable" class="com.fr.base.Formula">\n'
                        '<Attributes>\n'
                        '<![CDATA[=year(now())]]></Attributes>\n'
                        '</O>\n'
                        '</widgetValue>')
        parts = []
        if wname: parts.append(wname.group(0))
        if wid: parts.append(wid.group(0))
        if wattr: parts.append(wattr.group(1))
        parts.append('<YearAttr/>')
        if wval:
            inner_val = wval.group(1)
            # 原值若为空（CDATA[] 或自闭合）→ 换成 year(now()) 公式
            if '<![CDATA[]]>' in inner_val or '<widgetValue/>' in inner_val:
                inner_val = year_default
            parts.append(inner_val)
        else:
            parts.append(year_default)
        return f'<InnerWidget class="com.fr.plugin.widget.year.YearControl" pluginID="com.fr.plugin.widget.year.all" plugin-version="3.2.6.6">\n' + '\n'.join(parts) + '\n</InnerWidget>'

    def _make_dateeditor(inner_xml):
        wname = re.search(r'<WidgetName\s+name="[^"]*"\s*/>', inner_xml)
        wid = re.search(r'<WidgetID\s+[^>]*/>', inner_xml)
        wattr = re.search(r'(<WidgetAttr[^>]*>.*?</WidgetAttr>)', inner_xml, re.DOTALL)
        wval = re.search(r'(<widgetValue>.*?</widgetValue>)', inner_xml, re.DOTALL)
        parts = []
        if wname: parts.append(wname.group(0))
        if wid: parts.append(wid.group(0))
        if wattr: parts.append(wattr.group(1))
        parts.append('<DateAttr format="yyyy-MM-dd"/>')
        if wval: parts.append(wval.group(1))
        else: parts.append('<widgetValue/>')
        return f'<InnerWidget class="com.fr.form.ui.DateEditor">\n' + '\n'.join(parts) + '\n</InnerWidget>'

    cb_re = re.compile(
        r'<InnerWidget class="com\.fr\.form\.ui\.ComboCheckBox">(.*?)</InnerWidget>',
        re.DOTALL)
    for m in cb_re.finditer(param_xml):
        inner = m.group(1)
        old_full = m.group(0)
        # 年份控件（含 year/年/yr/年份/年度）→ YearControl（默认 =year(now())）
        # 日期/月份控件（含 date/日期/period/期间/month/月/月份）→ DateEditor(yyyy-MM-dd)
        if _is_year_ctrl(inner):
            new_full = _make_yearcontrol(inner)
            param_xml = param_xml.replace(old_full, new_full)
        elif _is_date_ctrl(inner):
            new_full = _make_dateeditor(inner)
            param_xml = param_xml.replace(old_full, new_full)

    # --- 4. 按钮 → 根据功能设宽度 (Import=120, 其他=80) ---
    import_re = re.compile(
        r'(<InnerWidget class="com\.fr\.form\.(?:parameter\.)?(?:ui\.)?'
        r'(FreeButton|FormSubmitButton|Button)">(.*?)</InnerWidget>\s*)'
        r'<BoundsAttr\s+x="(\d+)"\s+y="(\d+)"\s+width="\d+"\s+height="\d+"',
        re.DOTALL)

    def _btn_width(inner):
        func = btn_function(inner)
        return IMPORT_W if func == 'Import' else BTN_W

    def _fix_btn_size(m):
        prefix = m.group(1)
        x, y = m.group(4), m.group(5)
        w = _btn_width(m.group(2))
        return f'{prefix}<BoundsAttr x="{x}" y="{y}" width="{w}" height="{BTN_H}"'

    param_xml = import_re.sub(_fix_btn_size, param_xml)

    # --- 3.5 缺 Query 查询按钮自动补充 ---
    has_search = bool(re.search(
        r'<WidgetName\s+name="search"',
        param_xml)) or 'Query' in param_xml

    if not has_search:
        # 构造 Query 按钮
        query_btn = (
            '<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">\n'
            '<InnerWidget class="com.fr.form.parameter.FormSubmitButton">\n'
            '<WidgetName name="search"/>\n'
            '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">\n'
            '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>\n'
            '<PrivilegeControl/>\n'
            '</WidgetAttr>\n'
            '<Text><![CDATA[Query]]></Text>\n'
            '<Hotkeys><![CDATA[enter]]></Hotkeys>\n'
            '</InnerWidget>\n'
            '<BoundsAttr x="1000" y="80" width="80" height="26"/>\n'
            '</Widget>'
        )
        # 插入到 </Layout> 之前（最后一个按钮/控件之后）
        layout_end = param_xml.rfind('</Layout>')
        if layout_end > 0:
            param_xml = param_xml[:layout_end] + query_btn + '\n' + param_xml[layout_end:]

        # 补充 MobileWidgetList
        mwl_match = re.search(r'(<MobileWidgetList>)(.*?)(</MobileWidgetList>)', param_xml, re.DOTALL)
        if mwl_match:
            new_entry = '<Widget widgetName="search"/>'
            param_xml = param_xml[:mwl_match.start(2)] + new_entry + '\n' + param_xml[mwl_match.start(2):]

    # --- 4. 收集所有控件，重新布局 ---
    all_re = re.compile(
        r'(<InnerWidget class="([^"]+)"[^>]*>(.*?)</InnerWidget>\s*)'
        r'<BoundsAttr\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"',
        re.DOTALL)

    ctrls = []
    for m in all_re.finditer(param_xml):
        cls = m.group(2)
        inner = m.group(3)
        x, y, w, h = int(m.group(4)), int(m.group(5)), int(m.group(6)), int(m.group(7))
        is_label = 'Label' in cls
        is_btn = 'Button' in cls or 'FormSubmit' in cls
        func = btn_function(inner) if is_btn else None
        ctrls.append({
            'x': x, 'y': y, 'w': w, 'h': h,
            'is_label': is_label, 'is_btn': is_btn, 'func': func,
            'full': m.group(0), 'inner': m.group(1)
        })

    if not ctrls:
        if param_xml != original:
            content = content[:param_match.start(1)] + param_xml + content[param_match.end(1):]
        return content

    # 获取面板设计宽度
    dw_match = re.search(r'<Design_Width\s+design_width="(\d+)"', param_xml)
    panel_w = int(dw_match.group(1)) if dw_match else 1400

    # --- 4a. 列对齐 ---
    ctrl_items = [c for c in ctrls if not c['is_btn'] and not c['is_label']]
    ctrl_items.sort(key=lambda c: c['x'])
    cols = []
    TOL = 80
    for c in ctrl_items:
        placed = False
        for col in cols:
            if abs(c['x'] - col[0]['x']) < TOL:
                col.append(c); placed = True; break
        if not placed: cols.append([c])

    for col in cols:
        target = max(c['x'] for c in col)
        for c in col:
            if c['x'] != target:
                new_full = re.sub(r'x="(\d+)"', f'x="{target}"', c['full'])
                param_xml = param_xml.replace(c['full'], new_full)
                c['x'] = target; c['full'] = new_full

    # --- 4b. 配对 Label→控件，按宽度约束分行 + 跨行列对齐 ---
    # 配对: Label 与紧跟的控件 (按 y 相近 + x 顺序)
    pairs = []  # [(label_name, ctrl_name, label_width), ...]
    lbl_ctrls = [c for c in ctrls if c['is_label']]
    in_ctrls = [c for c in ctrls if not c['is_label'] and not c['is_btn']]
    lbl_ctrls.sort(key=lambda c: (c['y'], c['x']))
    in_ctrls.sort(key=lambda c: (c['y'], c['x']))

    # 配对: Label x < Ctrl x 且 y 相近 (同行的配对)
    used_ctrl = set()
    for lbl in lbl_ctrls:
        best = None
        for c in in_ctrls:
            if id(c) in used_ctrl: continue
            if c['y'] == lbl['y'] and c['x'] > lbl['x']:
                best = c; break
        if best:
            used_ctrl.add(id(best))
        pairs.append((lbl, best))  # best may be None

    if pairs:
        CTRL_W_INT = int(CTRL_W)  # CTRL_W is "180" string
        # 每组宽度 = label_w + LABEL_CTRL_GAP + CTRL_W
        pair_w = [p[0]['w'] + LABEL_CTRL_GAP + CTRL_W_INT for p in pairs]

        btn_total_w = sum(b['w'] for b in ctrls if b['is_btn']) + BTN_GAP * max(0, sum(1 for c in ctrls if c['is_btn'])-1)
        total_w = sum(pair_w) + CTRL_GAP * (len(pair_w)-1)

        if total_w + CTRL_GAP + btn_total_w <= SINGLE_ROW_MAX:
            rows = [pairs]
            btn_new_row = False
        else:
            rows, cur, cur_w = [], [], 0
            for i, p in enumerate(pairs):
                w = pair_w[i]; add = w + (CTRL_GAP if cur else 0)
                if cur and cur_w + add > MAX_ROW_WIDTH:
                    rows.append(cur); cur = []; cur_w = 0; add = w
                cur.append(p); cur_w += add
            if cur: rows.append(cur)
            last_pairs = rows[-1]
            last_idx = pairs.index(last_pairs[0])
            last_n = len(last_pairs)
            last_w = sum(pair_w[last_idx:last_idx+last_n]) + CTRL_GAP*(last_n-1)
            btn_new_row = last_w + CTRL_GAP + btn_total_w > SINGLE_ROW_MAX  # 用 SINGLE_ROW_MAX 而非 RIGHT_ALIGN_MAX

        n_cols = max(len(r) for r in rows)

        # 跨行最大 label 宽度（保证同列 combo 左对齐）
        col_lw = [0]*n_cols
        for r in rows:
            for ci, (lbl, _) in enumerate(r):
                if ci < n_cols and lbl:
                    col_lw[ci] = max(col_lw[ci], lbl['w'])

        # 列坐标: label_x[ci], combo_x[ci]
        label_x = [MARGIN]
        combo_x = [MARGIN + col_lw[0] + LABEL_CTRL_GAP]
        for i in range(1, n_cols):
            label_x.append(combo_x[i-1] + CTRL_W_INT + CTRL_GAP)
            combo_x.append(label_x[i] + col_lw[i] + LABEL_CTRL_GAP)

        # 应用坐标
        for ri, r in enumerate(rows):
            y = MARGIN + ri * (26 + CTRL_GAP)
            for ci, (lbl, ctrl) in enumerate(r):
                lx = label_x[ci]
                if lbl:
                    n = re.sub(r'x="\d+"', f'x="{lx}"', lbl['full'])
                    n = re.sub(r'y="\d+"', f'y="{y}"', n)
                    param_xml = param_xml.replace(lbl['full'], n); lbl['full'] = n
                if ctrl:
                    cx = combo_x[ci]
                    n = re.sub(r'x="\d+"', f'x="{cx}"', ctrl['full'])
                    n = re.sub(r'y="\d+"', f'y="{y}"', n)
                    param_xml = param_xml.replace(ctrl['full'], n); ctrl['full'] = n

        all_right = max(combo_x[len(r)-1] + CTRL_W_INT for r in rows)
        last_row_right = combo_x[len(rows[-1])-1] + CTRL_W_INT
        panel_w = all_right + MARGIN

    # --- 4c. 按钮布局（基于 4b 的行结构） ---
    btns2 = [c for c in ctrls if c['is_btn']]
    if btns2 and pairs:
        # 按钮排序
        def _sort_key(b):
            try: return BTN_ORDER.index(b['func']) if b['func'] in BTN_ORDER else 99
            except: return 99
        btns2.sort(key=_sort_key)

        # 按钮布局
        btn_total = sum(b['w'] for b in btns2) + BTN_GAP * (len(btns2)-1)
        # 按钮放控件右侧 → 如超宽则换新行
        same_row_w = all_right + CTRL_GAP + btn_total + MARGIN
        btn_new_row = same_row_w > SINGLE_ROW_MAX

        if btn_new_row:
            btn_y = MARGIN + len(rows) * (26 + CTRL_GAP)
            n_rows_total = len(rows) + 1
            bx = all_right  # 新行右对齐
            for b in reversed(btns2):
                bx = bx - b['w']
                n = re.sub(r'x="\d+"', f'x="{bx}"', b['full'])
                n = re.sub(r'y="\d+"', f'y="{btn_y}"', n)
                param_xml = param_xml.replace(b['full'], n)
                bx = bx - BTN_GAP
            panel_w = max(all_right, bx) + MARGIN  # 新行按钮的最右端可能超出 all_right
        else:
            btn_y = MARGIN + (len(rows)-1) * (26 + CTRL_GAP)
            n_rows_total = len(rows)
            bx = all_right + CTRL_GAP  # 同行放右侧
            for b in btns2:
                n = re.sub(r'x="\d+"', f'x="{bx}"', b['full'])
                n = re.sub(r'y="\d+"', f'y="{btn_y}"', n)
                param_xml = param_xml.replace(b['full'], n)
                bx += b['w'] + BTN_GAP
            panel_w = (bx - BTN_GAP) + MARGIN

    # --- 4d. 调整参数面板宽度和高度 ---
    # 使用 4b 计算的 panel_w
    if pairs:
        new_panel_w = panel_w
        n_rows_total = len(rows) + (1 if btns2 and btn_new_row else 0)
        new_panel_h = MARGIN + (n_rows_total-1)*(26+CTRL_GAP) + 26 + MARGIN

    dw_re = re.compile(r'(<Design_Width\s+design_width=")(\d+)(")')
    dw_match = dw_re.search(param_xml)
    if dw_match and pairs:
        if new_panel_w > int(dw_match.group(2)):
            param_xml = dw_re.sub(rf'\g<1>{new_panel_w}\g<3>', param_xml)
        da_re = re.compile(r'(<DesignAttr\s+width=")(\d+)(")')
        da_match = da_re.search(param_xml)
        if da_match:
            param_xml = da_re.sub(rf'\g<1>{new_panel_w}\g<3>', param_xml)
        dah_re = re.compile(r'(<DesignAttr\s+width="\d+"\s+height=")(\d+)(")')
        dah_match = dah_re.search(param_xml)
        if dah_match:
            param_xml = dah_re.sub(rf'\g<1>{new_panel_h}\g<3>', param_xml)

    if param_xml != original:
        content = content[:param_match.start(1)] + param_xml + content[param_match.end(1):]
    return content


def fix_styles(content):
    content = content.replace('name="SimSun"', f'name="{FONT_NAME}"')
    def add_padding(m):
        tag = m.group(0); inner = m.group(1)
        if 'paddingLeft=' not in inner: tag = tag.replace('<Style ', '<Style paddingLeft="6" ')
        if 'paddingRight=' not in inner: tag = tag.replace('<Style ', '<Style paddingRight="6" ')
        return tag
    content = re.sub(r'<Style\s([^>]*)>', add_padding, content)
    return content


def process_file(filepath):
    rel = filepath.relative_to(BASE_DIR)
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    modified = original
    modified = fix_styles(modified)
    modified = re.sub(r'useParamsTemplate="true"', r'useParamsTemplate="false"', modified)
    modified = fix_parameter_controls(modified)
    modified = fix_row_heights(modified)
    if modified != original:
        bak = BACKUP_DIR / rel
        bak.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, bak)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(modified)
        return True
    return False


def main():
    print("=" * 60)
    print("FR .cpt 批量优化 v4")
    print(f"按钮排序: {' → '.join(BTN_ORDER)}")
    print("=" * 60)
    files = find_files()
    print(f"\n{len(files)} 个文件\n")
    mod = skp = err = 0
    for f in files:
        try:
            if process_file(f):
                print(f"  ✓ {f.relative_to(BASE_DIR)}")
                mod += 1
            else:
                print(f"  - {f.relative_to(BASE_DIR)}")
                skp += 1
        except Exception as e:
            print(f"  ✗ {f.relative_to(BASE_DIR)}: {e}")
            err += 1
    print(f"\n修改: {mod}  无变化: {skp}  错误: {err}")
    print(f"备份: {BACKUP_DIR}")

if __name__ == "__main__":
    main()
