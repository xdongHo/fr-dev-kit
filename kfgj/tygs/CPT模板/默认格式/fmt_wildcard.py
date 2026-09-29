"""
通配格式化器 (通用版, 原 fmt_copa.py 泛化)
适用: 常规明细表 (行式展示) 的后处理

【通配规则分类, 用户定稿 2026-08-07】
A. 通用样式类 (所有报表默认执行):
   1. 参数面板 CSS 注入 (param_panel_style 完整样式)
   2. 参数面板紧凑单行重排
   3. 单元格样式 (对齐/格式/字体 微软雅黑9号)
B. 列表展示类 (常规明细表默认执行, 树形/透视报表不启用):
   4. 列宽内容自适应 (calc_col_width: max(数据×2.5mm, 表头×5mm) clamp[15,150], 默认20mm)
   5. 冻结表头 (FrozenColumnRow)
   6. 隔行换色 (row()%2 条件样式)

用法:
  python fmt_wildcard.py                  # dry-run：仅列出内置 targets，不写任何文件
  python fmt_wildcard.py --run            # 实际执行（对每个目标写 XML，写前自动备份）
  跨项目复用: import process_cpt 传参（header_row/custom_btns/add_export/row_style）
"""
import re, os, sys, shutil
from pathlib import Path
from datetime import datetime

# ============ param_panel_style.py 核心 CSS ============
# 按钮 ID 变量化选择器
def variants(name):
    return list(dict.fromkeys([name.upper(), name, name.lower()]))

def w_sel(name):
    return ', '.join(f'[widgetname="{v}"]' for v in variants(name))

def id_sel(name):
    return ', '.join(f'#fr-btn-{v}' for v in variants(name))

def build_btn_css(custom_btns, blue_ids, gray_ids):
    parts = []
    parts.append("/******自定义按钮（变量化，选择器大小写双写）******/")
    for name, w, rule in custom_btns:
        parts.append(f"{w_sel(name)} {{")
        parts.append(f"\twidth: {w}px !important;")
        if rule:
            key = 'float' if rule.startswith(('right', 'left')) else 'margin'
            parts.append(f"\t{key}: {rule};")
        parts.append("}")
        parts.append(f"{id_sel(name)} .fr-btn-text {{")
        parts.append("\tfont-size: 12px !important;")
        parts.append("}")
        parts.append("")
    for bid in blue_ids:
        parts.append(f"{id_sel(bid)} {{")
        parts.append("\tbackground: #3676C5 !important;")
        parts.append("}")
    parts.append("")
    for gid in gray_ids:
        parts.append(f"{id_sel(gid)} {{")
        parts.append("\tbackground: #e9e9e9 !important;")
        parts.append("}")
        parts.append(f"{id_sel(gid)} button {{")
        parts.append("\tcolor: #585858 !important;")
        parts.append("}")
    parts.append("")
    return "\n".join(parts)


STATIC_CSS = """
/*cpt模板*/
.fr-combo-list {
\toverflow: hidden !important;
}
.fr-combo-list:hover {
\toverflow: auto !important;
}
.fr-combo-list::-webkit-scrollbar {
\twidth: 6px;
\theight: 6px;
}
.fr-combo-list::-webkit-scrollbar-track-piece {
\tbackground-color: #ebebed;
}
.fr-combo-list::-webkit-scrollbar-thumb {
\tbackground-color: #c7c7c7;
\tborder-radius: 2px;
}
.fr-combo-list::-webkit-scrollbar-thumb:hover {
\tbackground-color: #888888;
}
.fr-combo-list-item {
\tfont-family: Microsoft YaHei !important;
}
.fr-combo-list-item.fr-combo-selected {
\tcolor: #0f82ef !important;
\tbackground-color: #c3def9 !important;
}
#popup_overlay {
\tbackground-color: #333333 !important;
\topacity: 0.3 !important;
}
#content-container {
\tleft: 20px !important;
}
.parameter-container .fr-horizontalboxlayout.ui-state-enabled {
\tbackground: white;
}
.parameter-container [widgetname=__layout4align__] {
\tbackground: transparent !important;
}
#content-container .slimScrollBarY {
\tright: 21px !important;
}
#frozen-center ~ .slimScrollBarX{
\theight: 22px !important;
}
.parameter-container-collapseimg-up {
\tdisplay: none !important;
}
#fr-btn-INSERT {
\tbackground: none !important;
}
#fr-btn-DELETE {
\tbackground: none !important;
}
#fDtop {
\tbackground-color: #3296f5 !important;
}
#fDleft {
\tbackground-color: #3296f5 !important;
}
#fDbottom {
\tbackground-color: #3296f5 !important;
}
#fDright {
\tbackground-color: #3296f5 !important;
}
.fr-trigger-text {
\tborder-radius: 4px 0 0 4px;
\tborder-right: 0px;
}
.fr-texteditor {
\tborder-radius: 4px;
}
.ui-state-enabled.fr-form-imgboard {
\tborder-radius: 4px;
}
.fr-trigger-btn-up {
\tborder-radius: 0 4px 4px 0;
\tbackground-color: rgba(255, 255, 255, 1);
\tbackground: rgba(255, 255, 255, 1);
}
.fr-trigger-btn-over {
\tborder-radius: 0 4px 4px 0;
\tbackground-color: rgba(255, 255, 255, 1);
\tbackground: rgba(255, 255, 255, 1);
}
.fr-trigger-btn-down {
\tborder-radius: 0 4px 4px 0;
\tbackground-color: rgba(255, 255, 255, 1);
\tbackground: rgba(255, 255, 255, 1);
}
.fr-trigger-center {
\tbackground: url(data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%2712%27%20height=%2712%27%20viewBox=%270%200%2012%2012%27%3E%3Cpath%20d=%27M2%204l4%204%204-4z%27%20fill=%27%238a8a8a%27/%3E%3C/svg%3E) no-repeat 0 0;
\tmargin-top: 25% !important;
\theight: 100%;
}
.fr-date-trigger-center {
\tbackground: url(data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%2712%27%20height=%2712%27%20viewBox=%270%200%2012%2012%27%3E%3Crect%20x=%272.5%27%20y=%272.5%27%20width=%277%27%20height=%277%27%20rx=%271%27%20fill=%27none%27%20stroke=%27%238a8a8a%27%20stroke-width=%271.2%27/%3E%3Cpath%20d=%27M2.5%205h7M4.5%202v2M7.5%202v2%27%20stroke=%27%238a8a8a%27%20stroke-width=%271.2%27%20fill=%27none%27/%3E%3C/svg%3E) no-repeat 0 0 !important;
\tmargin-top: 25% !important;
\theight: 100%;
}
.fr-tree ul, .fr-tree li {
\tfont-family: Microsoft YaHei !important;
}
.fr-label {
\tfont-family: Microsoft YaHei !important;
}
.fr-btn-text {
\tfont-size: 12px !important;
}
.fr-btn-up.fr-btn-noicon .fr-btn-text {
\theight: 20px !important;
}
#popup_message {
\tfont-family: Microsoft YaHei !important;
\tcolor: #333333 !important;
\tfont-weight: normal !important;
\tfont-size: 15px !important;
\ttext-align: left !important;
}
#popup_title {
\tfont-family: Microsoft YaHei !important;
\tfont-weight: normal !important;
\tfont-size: 15px !important;
}
#popup_header {
\tbackground-color: #3676C5 !important;
}
#popup_content {
\tbackground-position: left !important;
}
div.fr-core-btn-style-blue {
\tbackground: #3676C5 !important;
}
.fr-core-btn-inner .fr-core-btn-text {
\tfont-size: 13px !important;
}
.fr-core-panel-header.fr-core-panel-style-blue.fr-core-window-header {
\tbackground-color: #3676C5 !important;
}
.fr-core-panel-title {
\tfont-family: Microsoft YaHei !important;
\tfont-weight: normal !important;
\tfont-size: 14px !important;
}
.fr-core-panel-body.fr-core-panel-body-border.fr-core-window-body {
\tborder: none !important;
}
.x-toolbar.ui-state-enabled.fs-tab-content-top-toolbar>table {
\tmargin-left: 20px !important;
}
textarea,span,button,input,pre,.fr-combo-list-item {
\tfont-family: Microsoft YaHei !important;
}
.fr-tabpane-tabscontent-bg {
\tleft: 0px !important;
\twidth: 100% !important;
\tbackground: white !important;
}
.fr-sheetbutton-firstpart-top {
\tdisplay: none !important;
}
.ui-state-enabled.fr-sheetbutton-container {
\theight: 25px !important;
\tbackground: #EDEDED !important;
\tcolor: #555555 !important;
\tborder: 1px #ffffff solid !important;
}
.ui-state-enabled.fr-sheetbutton-container.fr-sheetbutton-container-active {
\tcolor: white !important;
\tbackground: #3676C5 !important;
}
.view-container {
\ttop: 6px !important;
}
.verify-error-s {
\ttop: -15px !important;
}
.verify-error-messages {
\tleft: 40px  !important;
}
.verify-error-info {
\tdisplay: none  !important;
}
.x-text.fr-widget-click {
\tfont-size: 13.33px !important;
\tcolor: #333 !important;
}
"""

def build_full_css(custom_btns=None, blue_ids=None, gray_ids=None):
    """构建完整 CSS"""
    default_btns = [
        ('search', 80, None),
        ('submit', 80, None),
        ('import', 80, None),
    ]
    default_blues = ['search', 'submit', 'import', 'SEARCH', 'SUBMIT', 'IMPORT']
    default_grays = []
    
    btns = custom_btns or default_btns
    blues = blue_ids or default_blues
    grays = gray_ids or default_grays
    
    return build_btn_css(btns, blues, grays) + STATIC_CSS


def build_afterinit_js(css_text):
    """构建 afterinit JS: jQuery 注入 style"""
    esc = (css_text.replace('\\', '\\\\')
              .replace("'", "\\'")
              .replace('\r', '\\r')
              .replace('\n', '\\n'))
    return (
        '$("body .x-toolbar.ui-state-enabled table").eq(0).css("margin-left", "15px");\n'
        '$("<style>" + \'' + esc + '\' + "</style>").appendTo("head");\n'
        '/* param_panel_style */'
    )


# ============ 列宽计算 ============
# 通配规则 (用户定稿 2026-08-07):
#   最小列宽 15mm, 最大列宽 150mm, 默认 20mm
#   在 [15,150] 范围内取 max(字段文本数×5mm/2, 表头文本数×5mm)
#   (即: 数据内容 2.5mm/字符, 表头 5mm/字符)
#   1mm ≈ 144229 FU

MM_PER_FU = 144229.0
MIN_COL_MM = 15.0
MAX_COL_MM = 150.0
DEFAULT_COL_MM = 20.0

# 数值列标签集合（用于自动判别 data_kind）
NUMERIC_LABELS = {'Sales', 'Material', 'EBIT', 'Sales_ADJ', 'Material_ADJ', 'EBIT_ADJ',
                  'Sales%', 'Rate', 'Task', 'After Task'}

# 表头 → 数据库列名映射 (Detail 填报页)
HEADER2COL = {
    "维护年份": "year_version", "版本": "version", "年份": "year",
    "年": "year", "Version": "version", "OEM": "oem", "OEM_F": "oem",
    "项目": "project_code", "产品类": "product_type", "BU": "bu",
    "DEMO-Plant": "hfm_plant", "工厂描述": "plant_desc", "客户代码": "customer_code",
    "客户描述": "customer_desc", "Sales": "sales", "Material": "material", "EBIT": "ebit",
    "Sales_ADJ": "sales_adj", "Material_ADJ": "material_adj", "EBIT_ADJ": "ebit_adj",
    "Comments": "comments", "备注": "comments",
}

# 数据库内容预估: (最长字符数, 内容类型)
# 类型: 'cn'=中文为主, 'en'=字母数字为主, 'num'=数值
# 数值来自数据库实测 (2026-08-13 psycopg2 直连 max(length()), 修正 08-07 硬编码低估)
DATA_LENS = {
    "year_version": (12, 'en'), "version": (7, 'en'), "year": (4, 'en'), "oem": (3, 'en'),
    "project_code": (12, 'en'), "product_type": (12, 'cn'), "bu": (2, 'en'), "hfm_plant": (9, 'en'),
    "plant_desc": (10, 'cn'), "customer_code": (13, 'en'), "customer_desc": (13, 'cn'),
    "sales": (13, 'num'), "material": (8, 'num'), "ebit": (8, 'num'),
    "sales_adj": (13, 'num'), "material_adj": (8, 'num'), "ebit_adj": (8, 'num'), "comments": (30, 'cn'),
}

def text_mm(text):
    """表头宽度: 中文字符 5mm/字, 英文字符 2.5mm/字 (纯英文如 DEMO-Plant 按 2.5mm)"""
    return sum(5.0 if ord(c) > 127 else 2.5 for c in text)

def content_mm(db_col):
    """数据内容宽度: 字段文本数×5mm/2 = 2.5mm/字符"""
    n, _ = DATA_LENS.get(db_col, (5, 'en'))
    return n * 2.5

def calc_col_width(text):
    """通配列宽 FU: clamp(max(数据2.5mm/字, 表头5mm/字), 15mm, 150mm), 默认20mm"""
    db_col = HEADER2COL.get(text, text.lower())
    d_mm = content_mm(db_col)
    h_mm = text_mm(text)
    mm = max(d_mm, h_mm)
    if mm < MIN_COL_MM or mm > MAX_COL_MM:
        mm = DEFAULT_COL_MM
    fu = int(mm * MM_PER_FU)
    return fu


def fix_column_widths(xml, header_row=0):
    """从表头单元格文本计算并替换列宽"""
    # 提取 ColumnWidth
    cw_match = re.search(r'<ColumnWidth defaultValue="(\d+)">\s*<!\[CDATA\[([^\]]*)\]\]>\s*</ColumnWidth>', xml)
    if not cw_match:
        print("  ⚠️ 未找到 ColumnWidth")
        return xml
    
    # 提取表头行单元格文本
    header_cells = re.findall(
        r'<C c="(\d+)" r="' + str(header_row) + r'"[^>]*>\s*<O><!\[CDATA\[([^\]]*)\]\]></O>',
        xml
    )
    if not header_cells:
        print(f"  ⚠️ 未找到 r={header_row} 表头单元格")
        return xml
    
    # 计算每列宽度
    col_widths = {}
    for col_str, text in header_cells:
        col = int(col_str)
        col_widths[col] = calc_col_width(text)
    
    # 构建新的列宽列表
    max_col = max(col_widths.keys()) if col_widths else 10
    default_w = int(cw_match.group(1))
    widths = []
    for i in range(max_col + 1):
        widths.append(str(col_widths.get(i, default_w)))
    # 补齐到至少 20 个
    while len(widths) < 20:
        widths.append(str(default_w))
    
    new_cw = f'<ColumnWidth defaultValue="{default_w}">\n<![CDATA[{",".join(widths)}]]>\n</ColumnWidth>'
    
    xml = xml[:cw_match.start()] + new_cw + xml[cw_match.end():]
    
    changed = sum(1 for col, w in col_widths.items())
    print(f"  ✅ 列宽更新: {changed} 列")
    for col, text in header_cells:
        if int(col) in col_widths:
            print(f"    Col {col} '{text}': {col_widths[int(col)]} FU")
    return xml


def inject_param_css(xml, css_text):
    """注入参数面板完整 CSS 到 afterinit 事件"""
    js_text = build_afterinit_js(css_text)
    
    # 查找现有的 afterinit Listener 中的 Content
    # 匹配: <Listener event="afterinit" ...> ... <Content><![CDATA[...]]></Content> ... </Listener>
    pattern = r'(<Listener event="afterinit"[^>]*>\s*<JavaScript[^>]*>\s*<Parameters/>\s*<Content><!\[CDATA\[)(.*?)(\]\]></Content>)'
    
    match = re.search(pattern, xml, re.DOTALL)
    if match:
        # 替换现有 CSS
        old_js = match.group(2)
        if '/* param_panel_style */' in old_js and 'EXPORT' in old_js:
            print("  ℹ️  已有 param_panel_style 标记(含 export 样式)，跳过注入")
            return xml
        xml = xml[:match.start(2)] + js_text + xml[match.end(2):]
        print(f"  ✅ 参数面板 CSS 注入完成 ({len(js_text)} chars)")
    else:
        print("  ⚠️ 未找到 afterinit 事件，跳过 CSS 注入")
    
    return xml


def relayout_panel_single_row(xml):
    """参数面板紧凑重排：如果所有控件+按钮能放一行，则紧凑排列。
    
    原多行布局逻辑不动（widen_all.py 负责），这里只做单行优化：
    - 控件宽度：短标签(年/BU/OEM等)缩到100px，中等的120px，长标签(工厂描述/项目等)保持180px
    - 控件间距：从区块间距20px 降到紧凑间距8px
    - 按钮仍保持80px + 10px间距
    """
    import re as _re
    
    # 提取 ParameterUI 区域
    pm = _re.search(r'(<ParameterUI.*?</ParameterUI>)', xml, _re.DOTALL)
    if not pm:
        return xml
    pui = pm.group(0)
    
    # 提取所有 BoundsWidget 的信息
    # 模式: <Widget class="...BoundsWidget"><InnerWidget ...><WidgetName name="X"/>...<BoundsAttr x="N" y="N" width="N" height="N"/>
    widget_re = _re.compile(
        r'(<Widget class="[^"]*BoundsWidget">\s*<InnerWidget class="([^"]*)"[^>]*>.*?'
        r'<WidgetName name="([^"]+)".*?'
        r'<BoundsAttr\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"\s*/>)',
        _re.DOTALL
    )
    
    widgets = []
    for m in widget_re.finditer(pui):
        full, cls, name, x, y, w, h = m.group(1), m.group(2), m.group(3), int(m.group(4)), int(m.group(5)), int(m.group(6)), int(m.group(7))
        widgets.append({
            'full': full, 'cls': cls, 'name': name,
            'x': x, 'y': y, 'w': w, 'h': h,
            'is_button': 'Button' in cls or 'FormSubmit' in cls,
        })
    
    if not widgets:
        return xml
    
    # 按 x 排序
    widgets.sort(key=lambda d: d['x'])
    
    # 分离控件和按钮
    controls = [w for w in widgets if not w['is_button']]
    buttons = [w for w in widgets if w['is_button']]
    
    if not controls:
        return xml
    
    # 计算紧凑模式下的控件宽度（按 watermark 内容估算）
    # 提取每个控件的 watermark
    wm_re = _re.compile(r'<watermark><!\[CDATA\[([^\]]*)\]\]></watermark>')
    # 固定 90px 的控件名: 年份/version/币种/单位
    FIXED_90 = ('para_year_version', 'para_version', 'para_currency', 'para_unit',
                'para_year', 'version', 'currency', 'unit')
    for w in controls:
        wm_m = wm_re.search(w['full'])
        wm_text = wm_m.group(1) if wm_m else w['name']
        if w['name'] in FIXED_90:
            w['compact_w'] = 90
        else:
            # 按内容定宽：中文每字14px, 英文每字7px, 最小90px, 最大180px
            text_w = 90  # 基础 padding + 下拉箭头
            for ch in wm_text:
                text_w += 14 if ord(ch) > 127 else 7
            w['compact_w'] = max(90, min(text_w, 180))
    
    # 紧凑布局参数
    MARGIN = 12
    GAP = 8        # 紧凑间距（替代区块20px）
    BTN_W = 80
    BTN_GAP = 10
    
    # 计算紧凑模式总宽度
    controls_total = sum(w['compact_w'] for w in controls) + GAP * (len(controls) - 1)
    buttons_total = sum(BTN_W for _ in buttons) + BTN_GAP * max(0, len(buttons) - 1)
    total_w = MARGIN + controls_total + (GAP + buttons_total if buttons else 0) + MARGIN
    
    MAX_PANEL_W = 1500  # 单行最大宽度
    
    if total_w > MAX_PANEL_W:
        # 不能一行放下，保持原布局不动
        return xml
    
    # 能放下！重排
    y = 4  # 统一 y
    x = MARGIN
    
    new_pui = pui
    changes = 0
    
    # 重排控件
    for w in controls:
        old_bounds = f'<BoundsAttr x="{w["x"]}" y="{w["y"]}" width="{w["w"]}" height="{w["h"]}"/>'
        new_bounds = f'<BoundsAttr x="{x}" y="{y}" width="{w["compact_w"]}" height="26"/>'
        if old_bounds in new_pui:
            new_pui = new_pui.replace(old_bounds, new_bounds, 1)
            changes += 1
        x += w['compact_w'] + GAP
    
    # 重排按钮（右对齐到 total_w - MARGIN）
    if buttons:
        bx = MARGIN + controls_total + GAP
        for w in buttons:
            old_bounds = f'<BoundsAttr x="{w["x"]}" y="{w["y"]}" width="{w["w"]}" height="{w["h"]}"/>'
            new_bounds = f'<BoundsAttr x="{bx}" y="{y}" width="{BTN_W}" height="26"/>'
            if old_bounds in new_pui:
                new_pui = new_pui.replace(old_bounds, new_bounds, 1)
                changes += 1
            bx += BTN_W + BTN_GAP
    
    # 更新面板宽度
    panel_w = total_w
    panel_h = 34
    new_pui = _re.sub(r'design_width="\d+"', f'design_width="{panel_w}"', new_pui)
    new_pui = _re.sub(r'(<DesignAttr width=")\d+(")', rf'\g<1>{panel_w}\g<2>', new_pui)
    new_pui = _re.sub(r'(<DesignAttr[^>]*height=")\d+(")', rf'\g<1>{panel_h}\g<2>', new_pui)
    
    xml = xml[:pm.start(1)] + new_pui + xml[pm.end(1):]
    
    details = ', '.join(f'{w["name"]}={w["compact_w"]}' for w in controls)
    print(f"  ✅ 单行紧凑重排: {changes}ch, 总宽{panel_w}px [{details}]")
    return xml


def add_export_button(xml):
    """检测缺导出按钮自动补充（FreeButton + exportReportToExcel）
    查看类报表需要，填报表不需要（有工具栏导出）。
    """
    if 'WidgetName name="formSubmit3"' in xml or 'exportReportToExcel' in xml:
        print("  ℹ️  已有导出按钮，跳过")
        return xml
    
    export_btn = (
        '<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">\n'
        '<InnerWidget class="com.fr.form.ui.FreeButton">\n'
        '<Listener event="click" name="Export_Click">\n'
        '<JavaScript class="com.fr.js.JavaScriptImpl">\n'
        '<Parameters/>\n'
        '<Content><![CDATA[_g().exportReportToExcel(\'simple\')]]></Content>\n'
        '</JavaScript>\n'
        '</Listener>\n'
        '<WidgetName name="formSubmit3"/>\n'
        '<WidgetID widgetID="exp1"/>\n'
        '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">\n'
        '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>\n'
        '<PrivilegeControl/>\n'
        '</WidgetAttr>\n'
        '<Text><![CDATA[导出]]></Text>\n'
        '<Hotkeys><![CDATA[]]></Hotkeys>\n'
        '</InnerWidget>\n'
        '<BoundsAttr x="1400" y="4" width="80" height="26"/>\n'
        '</Widget>\n'
    )
    
    # 插入到 </Layout> 之前
    idx = xml.rfind('</Layout>')
    if idx < 0:
        print("  ⚠️ 未找到 </Layout>")
        return xml
    xml = xml[:idx] + export_btn + xml[idx:]
    
    # 补充 MobileWidgetList
    mwl_marker = '<MobileWidgetList>'
    mwl_idx = xml.find(mwl_marker)
    if mwl_idx > 0:
        entry = '<Widget widgetName="formSubmit3"/>\n'
        xml = xml[:mwl_idx + len(mwl_marker)] + entry + xml[mwl_idx + len(mwl_marker):]
    
    # 蓝色按钮 CSS 补充
    print("  ✅ 已添加导出按钮(formSubmit3)")
    return xml


def configure_toolbar(xml):
    """配置 Web 属性工具栏: 取消翻页(查看), 保留 ExcelO(导出)+Print(打印)"""
    if '<WebPageContent>' in xml:
        print("  ℹ️  已有工具栏配置, 跳过")
        return xml
    toolbar = ('<WebPageContent><ToolBars><ToolBarManager><Location><Embed position="3"/></Location>'
               '<ToolBar><ShortCut name="ExcelO"/><ShortCut name="Print"/></ToolBar>'
               '</ToolBarManager></ToolBars></WebPageContent>')
    if '<ServerPrinter/></ReportWebAttr>' in xml:
        xml = xml.replace('<ServerPrinter/></ReportWebAttr>', '<ServerPrinter/>' + toolbar + '</ReportWebAttr>', 1)
        print("  ✅ 工具栏配置: 取消翻页, 保留 ExcelO(导出)+Print(打印)")
    else:
        print("  ⚠️ 未找到 <ServerPrinter/></ReportWebAttr> 锚点")
    return xml


def freeze_header(xml, rows=1):
    """冻结前 N 行表头 (行展示明细表用)"""
    if 'FrozenColumnRow' in xml:
        print("  ℹ️  已有冻结配置，跳过")
        return xml
    anchor = '<ReportSettings headerHeight="0" footerHeight="0">\n<PaperSetting/>'
    if anchor not in xml:
        import re as _re
        m = _re.search(r'<ReportSettings[^>]*>', xml)
        if not m:
            print("  ⚠️ 未找到 ReportSettings")
            return xml
        anchor = m.group(0)
    new = f'<ReportSettings headerHeight="0" footerHeight="0">\n<FrozenColumnRow columnrow="A{rows + 1}"/>\n<PaperSetting/>'
    xml = xml.replace(anchor, new, 1)
    print(f"  ✅ 冻结前 {rows} 行表头: A{rows + 1}")
    return xml


def add_alternate_color(xml, header_row=0, even_color="-657929", odd_color="-1"):
    """隔行换色: 数据行偶/奇交替背景 (行展示明细表用)
    even_color: 偶数行浅灰 #f5f5f7 = -657929 (⚠️ 不是 -651769! 那是红色 #F60E07), 奇数行白
    只给第一数据行首列加 ConditionAttr, FR 自动应用到所有同类型行
    """
    if 'row()%2' in xml:
        print("  ℹ️  已有隔行换色，跳过")
        return xml
    
    import re as _re
    cell_re = _re.compile(
        r'<C\s+c="(\d+)"\s+r="(\d+)"(?:\s+cs="\d+")?(?:\s+rs="\d+")?\s+s="(\d+)"[^>]*>(.*?)</C>',
        _re.DOTALL)
    
    data_rows = {}
    for m in cell_re.finditer(xml):
        col, row, style = m.group(1), m.group(2), m.group(3)
        inner = m.group(4)
        r = int(row)
        if r <= header_row:
            continue
        is_ds = ('t="DSColumn"' in inner) or ('ds1.G(' in inner) or ('ds1.S(' in inner)
        if r not in data_rows:
            data_rows[r] = []
        data_rows[r].append((col, style, m.group(0), is_ds))
    
    ds_rows = sorted([r for r, cells in data_rows.items() if any(c[3] for c in cells)])
    if not ds_rows:
        ds_rows = sorted([r for r in data_rows.keys() if r > header_row])
    if not ds_rows:
        print("  ⚠️ 未找到数据行")
        return xml
    
    first_row = ds_rows[0]
    # 隔行换色放到第二个数据列 (c=1), 避免与行后分页(c=0)挤同一单元格
    target_cell = None
    for cell_info in data_rows[first_row]:
        if cell_info[0] == '1':
            target_cell = cell_info
            break
    if not target_cell:
        target_cell = data_rows[first_row][0]  # 兜底用首列
    old = target_cell[2]
    if '<ConditionAttr>' in old or 'row()%2' in xml or '隔行换色' in xml:
        print("  ℹ️  已有隔行换色配置，跳过")
        return xml
    
    # 填报预览下 ConditionAttr 生效, HighlightList 不生效 (2026-08-07 实测)
    # 只改背景色, 不带 horizontal_alignment (避免覆盖数值列右对齐)
    # rowType=0 应用到整行
    cond = f'''<ConditionAttr><ConditionCollection><Condition class="com.fr.data.condition.CommonCondition"><ConditionAttrData><ConditionAttrRowColumn rowType="0"/></ConditionAttrData><FormulaExpr class="com.fr.base.Formula"><Attributes><![CDATA[row()%2=0]]></Attributes></FormulaExpr></Condition></ConditionCollection><Style imageLayout="1"><FRFont name="微软雅黑" style="0" size="72"/><Background name="ColorBackground" color="{even_color}"/><Border/></Style></ConditionAttr>'''
    new = old.replace('</C>', cond + '</C>')
    xml = xml.replace(old, new, 1)
    print(f"  ✅ 隔行换色: r={first_row} c={target_cell[0]} (偶行{even_color})")
    return xml


def process_cpt(cpt_path, header_row=0, custom_btns=None, blue_ids=None, gray_ids=None, add_export=False, row_style=False):
    """处理单个 CPT 文件"""
    fp = Path(cpt_path)
    if not fp.exists():
        print(f"❌ 不存在: {fp}")
        return False
    
    print(f"\n{'='*60}")
    print(f"处理: {fp.name}")
    print(f"{'='*60}")
    
    # 备份
    bak = fp.parent / f"_backup_fmt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    bak.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fp, bak / fp.name)
    
    xml = fp.read_text(encoding='utf-8')
    
    # 0. 补导出按钮（仅查看报表）
    if add_export:
        print("\n[0/3] 补导出按钮:")
        xml = add_export_button(xml)
        # CSS 补充 formSubmit3 蓝色
        if custom_btns is None:
            custom_btns = [('search', 80, None), ('formSubmit3', 80, None)]
        else:
            custom_btns = list(custom_btns) + [('formSubmit3', 80, None)]
        if blue_ids is None:
            blue_ids = ['search', 'submit', 'import', 'SEARCH', 'SUBMIT', 'IMPORT', 'formSubmit3', 'FORMSUBMIT3', 'export', 'EXPORT']
        else:
            blue_ids = list(blue_ids) + ['formSubmit3', 'FORMSUBMIT3', 'export', 'EXPORT']
    
    # 0.5 工具栏配置（Web 属性: 取消翻页, 保留导出/打印）
    print("\n[工具栏] Web 属性配置:")
    xml = configure_toolbar(xml)

    # 1. 列宽修复
    print("\n[1/3] 列宽修复:")
    xml = fix_column_widths(xml, header_row)
    
    # 2. 参数面板 CSS 注入
    print("\n[2/3] 参数面板 CSS:")
    css = build_full_css(custom_btns, blue_ids, gray_ids)
    xml = inject_param_css(xml, css)
    
    # 3. 参数面板紧凑重排（单行检测）
    print("\n[3/3] 参数面板紧凑重排:")
    xml = relayout_panel_single_row(xml)
    
    # 4. 行展示明细表专用: 冻结表头 + 隔行换色 (树形 Overview 不启用)
    if row_style:
        print("\n[4/4] 行样式 (冻结表头 + 隔行换色):")
        xml = freeze_header(xml, rows=1)
        xml = add_alternate_color(xml, header_row=header_row, even_color="-657929")
    
    # 写入
    fp.write_text(xml, encoding='utf-8')
    
    # XML 校验
    import xml.etree.ElementTree as ET
    try:
        ET.parse(fp)
        print(f"\n✅ XML 校验通过")
    except ET.ParseError as e:
        print(f"\n❌ XML 校验失败: {e}")
        return False
    
    print(f"备份: {bak}")
    return True


# ============ 主流程 ============
# 目录自适应：FR_REPORTLETS 环境变量 > 默认安装路径（换机/自定义安装时设 FR_REPORTLETS 即可）
BASE = os.environ.get("FR_REPORTLETS",
                      r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例驾驶舱工程")
if not os.path.isdir(BASE):
    sys.exit(f"[!] 目标目录不存在: {BASE}\n    设置 FR_REPORTLETS=<你的 reportlets 路径> 后重跑，"
             f"\n    并按你的报表工程改下方 targets（当前为示例工程结构）。")

# targets: (路径, header_row, add_export, row_style)
# row_style=True 的行展示明细表(Detail/Import)启用冻结表头+隔行换色; 树形 Overview 不启用
targets = [
    (os.path.join(BASE, "填报", "detail.cpt"), 0, True, True),
    (os.path.join(BASE, "导入", "import_detail.cpt"), 0, False, True),
    (os.path.join(BASE, "可视化", "overview_oem.cpt"), 0, True, False),
    (os.path.join(BASE, "可视化", "overview_bu.cpt"), 0, True, False),
    (os.path.join(BASE, "可视化", "overview_program.cpt"), 0, True, False),
]

if __name__ == "__main__":
    # 安全闸：默认 dry-run 只列目标，--run 才写文件（防误执行/防 --help 之类参数被吞后直接开跑）
    import argparse
    ap = argparse.ArgumentParser(
        description="通配格式化器（通用版）：对内置 targets 执行 A/B 类通配样式。默认 dry-run，--run 才实际写入（写前自动备份）。")
    ap.add_argument("--run", action="store_true", help="实际执行写入（每目标写前自动备份到 _backup_fmt_* 目录）")
    args = ap.parse_args()

    print("内置 targets（BASE 写死 示例驾驶舱 目录）:")
    for cpt_path, hdr_row, need_export, need_row_style in targets:
        status = "[存在]" if os.path.isfile(cpt_path) else "[缺失]"
        print(f"  {status} {cpt_path} (header_row={hdr_row}, add_export={need_export}, row_style={need_row_style})")
    if not args.run:
        print("\ndry-run：未写任何文件。确认无误后加 --run 执行。")
        sys.exit(0)

    for cpt_path, hdr_row, need_export, need_row_style in targets:
        process_cpt(cpt_path, header_row=hdr_row, add_export=need_export, row_style=need_row_style)

    print(f"\n{'='*60}")
    print("全部完成!")
