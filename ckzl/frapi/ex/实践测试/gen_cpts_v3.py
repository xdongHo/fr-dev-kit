"""生成 3 个 JavaAPI 验证模板 v3（对齐 fr_check 通过的真实格式）
参考已验证模板 参数控件基础_batch2.cpt 的结构：
- <Report class="com.fr.report.worksheet.WorkSheet" name="...">
- <TableDataMap>...</TableDataMap>（完整开闭）
- <ParameterUI class="com.fr.form.main.parameter.FormParameterUI">
- 空容器插入占位文本避免自闭合
"""
import xml.etree.ElementTree as ET
import os

OUT = r'D:\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\实践测试'

def write_cpt(path, root):
    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(path, encoding='utf-8', xml_declaration=True)
    print(f'✅ {os.path.basename(path)}: {os.path.getsize(path)} bytes')

def add_pair(parent, tag, **attrs):
    """创建完整开闭标签（ET 空标签会自闭合，加文本避免）"""
    el = ET.SubElement(parent, tag, attrs)
    return el

def make_workbook():
    wb = ET.Element('WorkBook', {'xmlVersion': '20170720', 'releaseVersion': '10.0.0'})
    ET.SubElement(wb, 'PageSetup')
    tdm = ET.SubElement(wb, 'TableDataMap')  # 有子元素则不会自闭合
    pui = ET.SubElement(wb, 'ParameterUI', {'class': 'com.fr.form.main.parameter.FormParameterUI'})
    ET.SubElement(pui, 'Visible')
    return wb, tdm, pui

# ============ 1. 数据集参数 ============
wb, tdm, pui = make_workbook()
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.DBTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'Database', {'name': 'FRDemo'})
ET.SubElement(td, 'Query').text = "SELECT * FROM 销量 WHERE 地区 = '${area}'"
ET.SubElement(td, 'ColumnNames').text = '地区,产品,销量,利润'
ET.SubElement(td, 'ColumnType').text = '0,0,0,0'
# 参数
params = ET.SubElement(wb, 'Parameters')
ET.SubElement(params, 'Parameter', {'name': 'area', 'class': 'java.lang.String'}).text = '华东'
ET.SubElement(pui, 'InnerWidget', {'class': 'com.fr.form.ui.TextEditor'})
ET.SubElement(pui, 'WidgetName', {'name': 'area'})
# 报表
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '数据集参数演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '数据集参数演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in [(0, '地区'), (1, '产品'), (2, '销量'), (3, '利润')]:
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '0'})
for row, vals in [(1, ['=ds1.select(地区)', '=ds1.select(产品)', '=ds1.select(销量)', '=ds1.select(利润)']),
                  (2, ['=ds1.select(地区,1)', '=ds1.select(产品,1)', '=ds1.select(销量,1)', '=ds1.select(利润,1)'])]:
    for col, v in enumerate(vals):
        cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': str(row)})
        ET.SubElement(cell, 'Value').text = v
        ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_数据集参数.cpt'), wb)

# ============ 2. 模板参数 ============
wb, tdm, pui = make_workbook()
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'ColumnNames').text = '地区,销售额'
ET.SubElement(td, 'ColumnType').text = '0,0'
ET.SubElement(td, 'RowData').text = '华东,1000\n华北,2000\n华南,1500'
params = ET.SubElement(wb, 'Parameters')
ET.SubElement(params, 'Parameter', {'name': '地区', 'class': 'java.lang.String'}).text = '华东'
ET.SubElement(pui, 'InnerWidget', {'class': 'com.fr.form.ui.TextEditor'})
ET.SubElement(pui, 'WidgetName', {'name': '地区'})
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '模板参数演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '模板参数演示'
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
wb, tdm, pui = make_workbook()
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'ColumnNames').text = '项目,数值'
ET.SubElement(td, 'ColumnType').text = '0,0'
ET.SubElement(td, 'RowData').text = '金额,1000.5\n日期,20240101\n比例,0.125'
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '单元格样式演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '单元格样式演示'
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
styles = [('0.00', '#CCFFFF', '=ds1.select(1,0)'),
          ('yyyy-MM-dd', '#FFCCFF', '=ds1.select(1,1)'),
          ('0.00%', '#CCFFCC', '=ds1.select(1,2)')]
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

print('\n=== v3 全部生成完成 ===')
