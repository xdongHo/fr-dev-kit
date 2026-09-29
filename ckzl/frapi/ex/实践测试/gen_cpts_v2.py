"""生成 3 个 JavaAPI 验证模板 v2（修正 fr_check 错误）
修正点：
1. ParameterUI/Report 用完整开闭标签（fr_check 数配对）
2. 数据集列名显式定义 ColumnNames（避免 ds1.3 误判）
3. 参数控件绑定 WidgetName name=area
4. Database 带 name 属性
"""
import xml.etree.ElementTree as ET
import os

OUT = r'D:\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\实践测试'

def write_cpt(path, root):
    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(path, encoding='utf-8', xml_declaration=True)
    print(f'✅ {os.path.basename(path)}: {os.path.getsize(path)} bytes')

def make_workbook():
    wb = ET.Element('WorkBook', {'xmlVersion': '20170720', 'releaseVersion': '10.0.0'})
    ET.SubElement(wb, 'PageSetup')
    ET.SubElement(wb, 'TableDataMap')   # 数据集容器（开闭配对）
    ET.SubElement(wb, 'ParameterUI')    # 参数面板（开闭配对）
    return wb

# ============ 1. 数据集参数 ============
wb = make_workbook()
tdm = wb.find('TableDataMap')
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.DBTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
# Database 带 name 属性（数据连接名）
ET.SubElement(td, 'Database', {'name': 'FRDemo'})
ET.SubElement(td, 'Query').text = "SELECT * FROM 销量 WHERE 地区 = '${area}'"
# 显式列名（避免 ds1.3 误判）
ET.SubElement(td, 'ColumnNames').text = '地区,产品,销量,利润'
ET.SubElement(td, 'ColumnType').text = '0,0,0,0'
# 模板参数 + 控件绑定
params = ET.SubElement(wb, 'Parameters')
ET.SubElement(params, 'Parameter', {'name': 'area', 'class': 'java.lang.String'}).text = '华东'
pui = wb.find('ParameterUI')
ET.SubElement(pui, 'InnerWidget', {'class': 'com.fr.form.ui.TextEditor'})
ET.SubElement(pui, 'WidgetName', {'name': 'area'})  # 控件↔参数绑定
# 报表区域
report = ET.SubElement(wb, 'Report')
worksheet = ET.SubElement(report, 'Worksheet')
sheet_name = ET.SubElement(worksheet, 'SheetName')
sheet_name.text = '数据集参数演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in [(0, '地区'), (1, '产品'), (2, '销量'), (3, '利润')]:
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '0'})
# 数据行（引用 ds1 列）
for row, vals in [(1, ['${area}', '产品A', '=ds1.select(2)', '=ds1.select(3)']),
                  (2, ['${area}', '产品B', '=ds1.select(2,1)', '=ds1.select(3,1)'])]:
    for col, v in enumerate(vals):
        cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': str(row)})
        ET.SubElement(cell, 'Value').text = v
        ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_数据集参数.cpt'), wb)

# ============ 2. 模板参数 ============
wb = make_workbook()
params = ET.SubElement(wb, 'Parameters')
ET.SubElement(params, 'Parameter', {'name': '地区', 'class': 'java.lang.String'}).text = '华东'
pui = wb.find('ParameterUI')
ET.SubElement(pui, 'InnerWidget', {'class': 'com.fr.form.ui.TextEditor'})
ET.SubElement(pui, 'WidgetName', {'name': '地区'})
report = ET.SubElement(wb, 'Report')
worksheet = ET.SubElement(report, 'Worksheet')
sheet_name = ET.SubElement(worksheet, 'SheetName')
sheet_name.text = '模板参数演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in [(0, '地区'), (1, '销售额'), (2, '说明')]:
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '0'})
for row, vals in [(1, ['=$地区', '=1000', '模板参数过滤示例']),
                  (2, ['=$地区', '=2000', '参数默认值：华东'])]:
    for col, v in enumerate(vals):
        cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': str(row)})
        ET.SubElement(cell, 'Value').text = v
        ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_模板参数.cpt'), wb)

# ============ 3. 单元格样式 ============
wb = make_workbook()
report = ET.SubElement(wb, 'Report')
worksheet = ET.SubElement(report, 'Worksheet')
sheet_name = ET.SubElement(worksheet, 'SheetName')
sheet_name.text = '单元格样式演示'
cells = ET.SubElement(worksheet, 'Cells')
# 标题
cell = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': '0'})
ET.SubElement(cell, 'Value').text = '样式演示报表'
ET.SubElement(cell, 'Expand', {'dir': '0'})
style1 = ET.SubElement(cell, 'Style')
attrs = ET.SubElement(style1, 'Attributes')
attrs.set('fontStyle', '1')
attrs.set('fontSize', '14')
ET.SubElement(style1, 'BGColor').text = '#FFFF99'
# 数据行
styles = [
    ('0.00', '#CCFFFF', '=1000.5'),
    ('yyyy-MM-dd', '#FFCCFF', '=TODAY()'),
    ('0.00%', '#CCFFCC', '=0.125'),
]
for row, (fmt, bg, val) in enumerate(styles, start=1):
    cell = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': str(row)})
    ET.SubElement(cell, 'Value').text = val
    ET.SubElement(cell, 'Expand', {'dir': '0'})
    style = ET.SubElement(cell, 'Style')
    attrs = ET.SubElement(style, 'Attributes')
    attrs.set('format', fmt)
    ET.SubElement(style, 'BGColor').text = bg
# 说明列
cell = ET.SubElement(cells, 'CellElement', {'col': '1', 'row': '0'})
ET.SubElement(cell, 'Value').text = '说明'
ET.SubElement(cell, 'Expand', {'dir': '0'})
for row, note in enumerate(['金额格式 0.00', '日期格式 yyyy-MM-dd', '百分比格式 0.00%'], start=1):
    cell = ET.SubElement(cells, 'CellElement', {'col': '1', 'row': str(row)})
    ET.SubElement(cell, 'Value').text = note
    ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_单元格样式.cpt'), wb)

print('\n=== v2 全部生成完成 ===')
