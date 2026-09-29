"""生成 9 个 JavaAPI 验证模板的 .cpt（混合方案：Java 编译验证 API + XML Schema 生成）
基于 javap 验证的真实 API 对应 XML 节点（fr_check 通过格式）：
- WorkBook 根: xmlVersion="20170720" releaseVersion="10.0.0"
- Report class="com.fr.report.worksheet.WorkSheet"
- TableDataMap 完整开闭 + TableData 数据集
- ParameterUI class="com.fr.form.main.parameter.FormParameterUI"
"""
import xml.etree.ElementTree as ET
import os

OUT = r'D:\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\实践测试'

def write_cpt(path, root):
    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')
    tree.write(path, encoding='utf-8', xml_declaration=True)
    print(f'✅ {os.path.basename(path)}: {os.path.getsize(path)} bytes')

def make_wb(name, with_ds=True, ds_type='EmbeddedTableData'):
    wb = ET.Element('WorkBook', {'xmlVersion': '20170720', 'releaseVersion': '10.0.0'})
    ET.SubElement(wb, 'PageSetup')
    tdm = ET.SubElement(wb, 'TableDataMap')
    if with_ds:
        td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': f'com.fr.data.impl.{ds_type}'})
        ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
    else:
        td = ET.SubElement(tdm, 'TableData', {'name': 'ds_demo', 'class': 'com.fr.data.impl.EmbeddedTableData'})
        ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
        ET.SubElement(td, 'ColumnNames').text = '名称'
        ET.SubElement(td, 'ColumnType').text = '0'
        ET.SubElement(td, 'RowData').text = '演示数据'
    pui = ET.SubElement(wb, 'ParameterUI', {'class': 'com.fr.form.main.parameter.FormParameterUI'})
    ET.SubElement(pui, 'Visible')
    return wb, tdm, pui

def add_cells(report, headers, data_rows):
    """添加表头 + 数据行"""
    worksheet = ET.SubElement(report, 'Worksheet')
    ET.SubElement(worksheet, 'SheetName').text = '数据演示'
    cells = ET.SubElement(worksheet, 'Cells')
    for col, text in enumerate(headers):
        cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
        ET.SubElement(cell, 'Value').text = text
        ET.SubElement(cell, 'Expand', {'dir': '0'})
    for r, vals in enumerate(data_rows, start=1):
        for col, v in enumerate(vals):
            cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': str(r)})
            ET.SubElement(cell, 'Value').text = v
            ET.SubElement(cell, 'Expand', {'dir': '0'})

# ============ 1. 单元格扩展 ============
wb, tdm, pui = make_wb('单元格扩展')
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'ColumnNames').text = '地区,产品,销量,利润'
ET.SubElement(td, 'ColumnType').text = '0,0,0,0'
ET.SubElement(td, 'RowData').text = '华东,产品A,100,20\n华东,产品B,200,30\n华北,产品C,150,25'
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '单元格扩展演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '单元格扩展演示'
cells = ET.SubElement(worksheet, 'Cells')
# 标题不扩展
cell = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': '0'})
ET.SubElement(cell, 'Value').text = '销售数据(纵向扩展)'
ET.SubElement(cell, 'Expand', {'dir': '2'})  # 2=不扩展
# 表头
for col, text in enumerate(['地区', '产品', '销量', '利润']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '1'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '2'})
# 数据（纵向扩展 dir=0）
for col, f in enumerate(['地区', '产品', '销量', '利润']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '2'})
    ET.SubElement(cell, 'Value').text = f'=ds1.select({f})'
    ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_单元格扩展.cpt'), wb)

# ============ 2. 扩展后排序 ============
wb, tdm, pui = make_wb('扩展后排序')
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'ColumnNames').text = '产品,销量'
ET.SubElement(td, 'ColumnType').text = '0,0'
ET.SubElement(td, 'RowData').text = '产品A,300\n产品B,100\n产品C,200'
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '扩展后排序演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '扩展后排序演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in enumerate(['产品', '销量']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '2'})
# 最父格（销量, 扩展后升序排序 sortAfterExpand=1）
cell = ET.SubElement(cells, 'CellElement', {'col': '1', 'row': '1'})
ET.SubElement(cell, 'Value').text = '=ds1.select(销量)'
ET.SubElement(cell, 'Expand', {'dir': '0', 'sortAfterExpand': '1'})
ET.SubElement(cell, 'SortExpression').text = '=ds1.select(销量)'
# 产品列（跟随）
cell = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': '1'})
ET.SubElement(cell, 'Value').text = '=ds1.select(产品)'
ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_扩展后排序.cpt'), wb)

# ============ 3. 超链接 ============
wb, tdm, pui = make_wb('超链接', with_ds=False)
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '超链接演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '超链接演示'
cells = ET.SubElement(worksheet, 'Cells')
# 超链接单元格（JS 打开新窗口）
cell = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': '0'})
ET.SubElement(cell, 'Value').text = '点击打开百度'
ET.SubElement(cell, 'Expand', {'dir': '2'})
hg = ET.SubElement(cell, 'NameHyperlinkGroup')
link = ET.SubElement(hg, 'JavaScript')
link.text = "FR.remoteEvaluate('=len(ds_demo.select(名称))').then(function(v){ if(v>0){ window.location.href='http://www.baidu.com'; } else { FR.Msg.alert('提示','无数据'); } })"
# 普通单元格
cell2 = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': '1'})
ET.SubElement(cell2, 'Value').text = '普通单元格(无超链接)'
ET.SubElement(cell2, 'Expand', {'dir': '2'})
write_cpt(os.path.join(OUT, 'JavaAPI_超链接.cpt'), wb)

# ============ 4. 下拉树控件 ============
wb, tdm, pui = make_wb('下拉树控件')
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'ColumnNames').text = '地区,省份,城市'
ET.SubElement(td, 'ColumnType').text = '0,0,0'
ET.SubElement(td, 'RowData').text = '华东,江苏,南京\n华东,浙江,杭州\n华北,河北,石家庄'
# 参数 + 下拉树控件
params = ET.SubElement(wb, 'Parameters')
ET.SubElement(params, 'Parameter', {'name': 'tree', 'class': 'java.lang.String'}).text = ''
iw = ET.SubElement(pui, 'InnerWidget', {'class': 'com.fr.form.ui.TreeComboBoxEditor', 'widgetName': 'tree'})
ET.SubElement(pui, 'WidgetName', {'name': 'tree'})
ET.SubElement(iw, 'Attributes', {'multipleSelection': 'true', 'ajax': 'false', 'selectLeafOnly': 'true'})
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '下拉树演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '下拉树演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in enumerate(['地区', '省份', '城市']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '2'})
for col, f in enumerate(['地区', '省份', '城市']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '1'})
    ET.SubElement(cell, 'Value').text = f'=ds1.select({f})'
    ET.SubElement(cell, 'Expand', {'dir': '0'})
# 参数引用单元格
cell = ET.SubElement(cells, 'CellElement', {'col': '3', 'row': '0'})
ET.SubElement(cell, 'Value').text = '选中值'
ET.SubElement(cell, 'Expand', {'dir': '2'})
cell = ET.SubElement(cells, 'CellElement', {'col': '3', 'row': '1'})
ET.SubElement(cell, 'Value').text = '=$tree'
ET.SubElement(cell, 'Expand', {'dir': '2'})
write_cpt(os.path.join(OUT, 'JavaAPI_下拉树控件.cpt'), wb)

# ============ 5. 控件字典联动 ============
wb, tdm, pui = make_wb('控件字典联动')
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'ColumnNames').text = '地区'
ET.SubElement(td, 'ColumnType').text = '0'
ET.SubElement(td, 'RowData').text = '华东\n华北\n华南'
td2 = ET.SubElement(tdm, 'TableData', {'name': 'ds2', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td2, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td2, 'ColumnNames').text = '城市'
ET.SubElement(td2, 'ColumnType').text = '0'
ET.SubElement(td2, 'RowData').text = '南京\n杭州\n北京'
# 参数
params = ET.SubElement(wb, 'Parameters')
ET.SubElement(params, 'Parameter', {'name': 'area', 'class': 'java.lang.String'}).text = '华东'
# 参数面板: 下拉框控件 + 数据字典
iw = ET.SubElement(pui, 'InnerWidget', {'class': 'com.fr.form.ui.ComboBox', 'widgetName': 'area'})
ET.SubElement(pui, 'WidgetName', {'name': 'area'})
dict_el = ET.SubElement(iw, 'Dictionary', {'class': 'com.fr.data.impl.TableDataDictionary'})
ET.SubElement(dict_el, 'TableData', {'name': 'ds1'})
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '控件字典联动演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '控件字典联动演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in enumerate(['地区', '城市']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '2'})
for col, f in enumerate(['地区', '城市']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '1'})
    ET.SubElement(cell, 'Value').text = f'=ds1.select({f})'
    ET.SubElement(cell, 'Expand', {'dir': '0'})
# 参数引用单元格
cell = ET.SubElement(cells, 'CellElement', {'col': '2', 'row': '0'})
ET.SubElement(cell, 'Value').text = '选中地区'
ET.SubElement(cell, 'Expand', {'dir': '2'})
cell = ET.SubElement(cells, 'CellElement', {'col': '2', 'row': '1'})
ET.SubElement(cell, 'Value').text = '=$area'
ET.SubElement(cell, 'Expand', {'dir': '2'})
write_cpt(os.path.join(OUT, 'JavaAPI_控件字典联动.cpt'), wb)

# ============ 6. 填报冻结 ============
wb, tdm, pui = make_wb('填报冻结')
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'ColumnNames').text = '地区,产品,销量'
ET.SubElement(td, 'ColumnType').text = '0,0,0'
ET.SubElement(td, 'RowData').text = '华东,产品A,100\n华东,产品B,200\n华北,产品C,150'
# Web 属性: 冻结首 2 行 1 列
wattr = ET.SubElement(wb, 'ReportWebAttr')
ET.SubElement(wattr, 'freezeRow').text = '2'
ET.SubElement(wattr, 'freezeCol').text = '1'
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '填报冻结演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '填报冻结演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in enumerate(['地区', '产品', '销量']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '2'})
for r, vals in enumerate([['华东', '产品A', '100'], ['华东', '产品B', '200'], ['华北', '产品C', '150']], start=1):
    for col, v in enumerate(vals):
        cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': str(r)})
        ET.SubElement(cell, 'Value').text = v
        ET.SubElement(cell, 'Expand', {'dir': '2'})
write_cpt(os.path.join(OUT, 'JavaAPI_填报冻结.cpt'), wb)

# ============ 7. Excel导出属性 ============
wb, tdm, pui = make_wb('Excel导出属性', with_ds=False)
# 导出属性
ea = ET.SubElement(wb, 'ReportExportAttr')
ET.SubElement(ea, 'ExcelExportAttr', {'exportHidedRow': 'true', 'exportHidedColumn': 'true', 'password': '123456', 'protectedWord': '654321'})
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': 'Excel导出属性演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = 'Excel导出属性演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in enumerate(['地区', '销量']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '2'})
for r, vals in enumerate([['华东', '1000'], ['华北', '2000']], start=1):
    for col, v in enumerate(vals):
        cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': str(r)})
        ET.SubElement(cell, 'Value').text = v
        ET.SubElement(cell, 'Expand', {'dir': '2'})
# 隐藏行示例
cell = ET.SubElement(cells, 'CellElement', {'col': '2', 'row': '0'})
ET.SubElement(cell, 'Value').text = '隐藏列'
ET.SubElement(cell, 'Expand', {'dir': '2'})
ET.SubElement(cell, 'Hidden').text = 'true'
write_cpt(os.path.join(OUT, 'JavaAPI_Excel导出属性.cpt'), wb)

# ============ 8. 分页SQL ============
wb, tdm, pui = make_wb('分页SQL', ds_type='DBTableData')
td = tdm.find('TableData')
ET.SubElement(td, 'Database', {'name': 'FRDemo'})
ET.SubElement(td, 'Query').text = 'SELECT 地区, 产品, 销量 FROM 销量'
ET.SubElement(td, 'PageQuerySql').text = 'SELECT 地区, 产品, 销量 FROM 销量 LIMIT ${fr_pagenumber}, ${fr_pagesize}'
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '分页SQL演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '分页SQL演示'
cells = ET.SubElement(worksheet, 'Cells')
for col, text in enumerate(['地区', '产品', '销量']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '0'})
    ET.SubElement(cell, 'Value').text = text
    ET.SubElement(cell, 'Expand', {'dir': '2'})
for col, f in enumerate(['地区', '产品', '销量']):
    cell = ET.SubElement(cells, 'CellElement', {'col': str(col), 'row': '1'})
    ET.SubElement(cell, 'Value').text = f'=ds1.select({f})'
    ET.SubElement(cell, 'Expand', {'dir': '0'})
write_cpt(os.path.join(OUT, 'JavaAPI_分页SQL.cpt'), wb)

# ============ 9. 图表数据源 ============
wb, tdm, pui = make_wb('图表数据源')
td = ET.SubElement(tdm, 'TableData', {'name': 'ds1', 'class': 'com.fr.data.impl.EmbeddedTableData'})
ET.SubElement(td, 'Attributes', {'maxMemRowCount': '-1'})
ET.SubElement(td, 'ColumnNames').text = '地区,销量'
ET.SubElement(td, 'ColumnType').text = '0,0'
ET.SubElement(td, 'RowData').text = '华东,100\n华北,200\n华南,150'
# 柱形图单元格
report = ET.SubElement(wb, 'Report', {'class': 'com.fr.report.worksheet.WorkSheet', 'name': '图表数据源演示'})
worksheet = ET.SubElement(report, 'Worksheet')
ET.SubElement(worksheet, 'SheetName').text = '图表数据源演示'
cells = ET.SubElement(worksheet, 'Cells')
chart_cell = ET.SubElement(cells, 'CellElement', {'col': '0', 'row': '0'})
ET.SubElement(chart_cell, 'Value').text = '=ds1.select(地区)'
ET.SubElement(chart_cell, 'Expand', {'dir': '0'})
chart = ET.SubElement(chart_cell, 'Chart')
ET.SubElement(chart, 'ChartName').text = 'chart1'
ET.SubElement(chart, 'ChartType').text = '柱形图'
plot = ET.SubElement(chart, 'Plot')
data = ET.SubElement(plot, 'DataPane')
ET.SubElement(data, 'Category').text = '=ds1.select(地区)'
ET.SubElement(data, 'Series').text = '=ds1.select(销量)'
write_cpt(os.path.join(OUT, 'JavaAPI_图表数据源.cpt'), wb)

print('\n=== 9 个模板全部生成完成 ===')
