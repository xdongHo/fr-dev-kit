"""生成 3 个 JavaAPI 验证模板（混合方案：Java 编译验证 API + 真实 XML Schema）
基于 javap 验证的真实 API 对应 XML 节点：
- DBTableData → <TableData class="com.fr.data.impl.DBTableData"><Database>FRDemo</Database><Query>
- Parameter → <Parameter name="area" class="java.lang.String">华东</Parameter>
- 单元格样式 → <CellElement> 内 Style 属性
"""
import xml.etree.ElementTree as ET
import os

OUT = r'D:\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\实践测试'

def write_cpt(path, root):
    tree = ET.ElementTree(root)
    # 需要缩进美化
    ET.indent(tree, space='  ')
    tree.write(path, encoding='utf-8', xml_declaration=True)
    print(f'✅ {os.path.basename(path)}: {os.path.getsize(path)} bytes')

def make_workbook(title_note):
    """创建 WorkBook 根骨架（含必要节点）"""
    wb = ET.Element('WorkBook', {'xmlVersion': '20170720', 'releaseVersion': '10.0.0'})
    # 页设置
    ET.SubElement(wb, 'PageSetup')
    # 数据集容器
    ET.SubElement(wb, 'TableDataMap')
    # 参数面板
    ET.SubElement(wb, 'ParameterUI')
    return wb

# ============ 1. 数据集参数 ============
wb = make_workbook('数据集参数')
tdm = wb.find('TableDataMap')
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.DBTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'Database').text = 'FRDemo'
ET.SubElement(td, 'Query').text = "SELECT * FROM 销量 WHERE 地区 = '${area}'"
params = ET.SubElement(wb, 'Parameters')
ET.SubElement(params, 'Parameter', {'name': 'area', 'class': 'java.lang.String'}).text = '华东'
# 报表区域
report = ET.SubElement(wb, 'Report')
worksheet = ET.SubElement(report, 'Worksheet')
sheet_name = ET.SubElement(worksheet, 'SheetName')
sheet_name.text = '数据集参数演示'
# 表头
cells = ET.SubElement(worksheet, 'Cells')
for col, text in [(0, '地区'), (1, '产品'), (2, '销量'), (3, '利润')]:
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '0'})
# 数据行（ds1 绑定演示）
for row, vals in [(1, ['${area}', '产品A', '=ds1.select(3)', '=ds1.select(4)']),
                  (2, ['${area}', '产品B', '=ds1.select(3,2)', '=ds1.select(4,2)'])]:
    for col, v in enumerate(vals):
        cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': str(row)})
        ET.SubElement(cell, 'Value').text = v
        ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_数据集参数.cpt'), wb)

# ============ 2. 模板参数 ============
wb = make_workbook('模板参数')
params = ET.SubElement(wb, 'Parameters')
ET.SubElement(params, 'Parameter', {'name': '地区', 'class': 'java.lang.String'}).text = '华东'
pui = wb.find('ParameterUI')
widget = ET.SubElement(pui, 'InnerWidget', {'class': 'com.fr.form.ui.TextEditor', 'widgetName': '地区'})
report = ET.SubElement(wb, 'Report')
worksheet = ET.SubElement(report, 'Worksheet')
sheet_name = ET.SubElement(worksheet, 'SheetName')
sheet_name.text = '模板参数演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in [(0, '地区'), (1, '销售额'), (2, '说明')]:
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '0'})
# 参数引用行
for row, vals in [(1, ['=$地区', '=1000', '模板参数过滤示例']),
                  (2, ['=$地区', '=2000', '参数默认值：华东'])]:
    for col, v in enumerate(vals):
        cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': str(row)})
        ET.SubElement(cell, 'Value').text = v
        ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_模板参数.cpt'), wb)

# ============ 3. 单元格样式 ============
wb = make_workbook('单元格样式')
report = ET.SubElement(wb, 'Report')
worksheet = ET.SubElement(report, 'Worksheet')
sheet_name = ET.SubElement(worksheet, 'SheetName')
sheet_name.text = '单元格样式演示'
cells = ET.SubElement(worksheet, 'Cells')
# 标题（加粗居中、背景色）
cell = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': '0'})
ET.SubElement(cell, 'Value').text = '样式演示报表'
ET.SubElement(cell, 'Expand', {'dir': '0'})
style1 = ET.SubElement(cell, 'Style')
ET.SubElement(style1, 'Attributes', {'fontStyle': '1', 'fontSize': '14'})
ET.SubElement(style1, 'BGColor').text = '#FFFF99'
# 数据行（不同格式：金额/日期/百分比）
styles = [
    ('0.00', '#CCFFFF'),   # 金额
    ('yyyy-MM-dd', '#FFCCFF'),  # 日期
    ('0.00%', '#CCFFCC'),  # 百分比
]
for row, (fmt, bg) in enumerate(styles, start=1):
    cell = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': str(row)})
    ET.SubElement(cell, 'Value').text = f'=row*1000'
    ET.SubElement(cell, 'Expand', {'dir': '0'})
    style = ET.SubElement(cell, 'Style')
    ET.SubElement(style, 'Attributes', {'format': fmt})
    ET.SubElement(style, 'BGColor').text = bg
# 说明
cell = ET.SubElement(cells, 'CellElement', {'col': '1', 'row': '0'})
ET.SubElement(cell, 'Value').text = '说明'
ET.SubElement(cell, 'Expand', {'dir': '0'})
for row, note in enumerate(['金额格式 0.00', '日期格式 yyyy-MM-dd', '百分比格式 0.00%'], start=1):
    cell = ET.SubElement(cells, 'CellElement', {'col': '1', 'row': str(row)})
    ET.SubElement(cell, 'Value').text = note
    ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_单元格样式.cpt'), wb)

print('\n=== 全部生成完成 ===')
