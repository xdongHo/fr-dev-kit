# -*- coding: utf-8 -*-
"""ckzl/zsk/gczsk建库脚本：FR Java API 方法 -> SQLite（零件表 + BOM 表 + 工艺表）
用法: python build_kb.py [--rebuild]
"""
import sqlite3, os, sys

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_kb.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS parts (
  part_id     INTEGER PRIMARY KEY,
  part_no     TEXT UNIQUE NOT NULL,
  name        TEXT NOT NULL,          -- 方法/构造名
  class_name  TEXT NOT NULL,          -- 所属 Java 类
  signature   TEXT,                   -- 完整签名
  category    TEXT NOT NULL,          -- 类别: FORM_BUILD/CPT_BUILD/CHART/DATASET/PARAM/STYLE/CONTAINER/WIDGET/EVENT/IO/UTIL
  description TEXT,
  params      TEXT,
  returns     TEXT,
  pitfalls    TEXT,
  source      TEXT,                   -- 来源
  verified    INTEGER DEFAULT 0,      -- 1=实测, 0=文档推断
  embed_vec   BLOB,                    -- 语义检索向量 (float32, 1024/512 维)
  embed_dim   INTEGER DEFAULT 1024,
  embed_model TEXT,                    -- 生成向量的模型名
  cn_name     TEXT                     -- i18n 中文口语名（用户可见名称）
);
CREATE TABLE IF NOT EXISTS bom (
  bom_id         INTEGER PRIMARY KEY,
  parent_part_id INTEGER NOT NULL REFERENCES parts(part_id),
  child_part_id  INTEGER NOT NULL REFERENCES parts(part_id),
  qty            INTEGER DEFAULT 1,
  rel_type       TEXT NOT NULL,       -- CALL/COMPOSE/REQUIRE/PREPARE
  note           TEXT,
  UNIQUE(parent_part_id, child_part_id, rel_type)
);
CREATE TABLE IF NOT EXISTS routing (
  routing_id  INTEGER PRIMARY KEY,
  routing_no  TEXT NOT NULL,
  routing_name TEXT NOT NULL,         -- 工艺名（任务）
  step_no     INTEGER NOT NULL,
  work_center TEXT NOT NULL,          -- JAVA_API / PYTHON_ATTR / VALIDATE / DESIGNER
  part_id     INTEGER REFERENCES parts(part_id),
  op_desc     TEXT NOT NULL,
  output      TEXT,
  UNIQUE(routing_no, step_no)
);
CREATE INDEX IF NOT EXISTS idx_parts_class ON parts(class_name);
CREATE INDEX IF NOT EXISTS idx_parts_cat  ON parts(category);
CREATE INDEX IF NOT EXISTS idx_bom_parent ON bom(parent_part_id);
CREATE INDEX IF NOT EXISTS idx_routing_no ON routing(routing_no);
"""

from overnight_parts import EXTRA_PARTS as EXTRA_PARTS_OVER
from chart_parts import EXTRA_PARTS as EXTRA_PARTS_CHART
from api_reflect_parts import EXTRA_PARTS as EXTRA_PARTS_REFLECT
from api_classes_parts import EXTRA_PARTS as EXTRA_PARTS_CLASSES
from i18n_dict_parts import EXTRA_PARTS as EXTRA_PARTS_DICT

# ---------- 零件表（物料主数据）----------
PARTS = [
 # CPT 构建核心
 ("P-0001","WorkBook","com.fr.main.impl.WorkBook","new WorkBook()","CPT_BUILD","模板工作簿，承载报表/页面属性/参数","-","TemplateWorkBook","readTemplateWorkBook 对 FRM 无效","夜学+实测",1),
 ("P-0002","WorkSheet","com.fr.report.worksheet.WorkSheet","new WorkSheet()","CPT_BUILD","工作表，单元格容器","-","-","addReport(WorkSheet) 挂到 WorkBook","夜学+实测",1),
 ("P-0003","writeTemplateWorkBook","com.fr.io.TemplateWorkBookIO","writeTemplateWorkBook(WorkBook, String)","IO","写出 .cpt 到 reportlets 相对路径","(WorkBook, 路径)","-","FRM 用 form.export，不能用这个","夜学+实测",1),
 ("P-0004","DefaultTemplateCellElement","com.fr.report.cell.DefaultTemplateCellElement","new DefaultTemplateCellElement(int col, int row)","CPT_BUILD","单元格实现类","(列,行)","CellElement","setStyle/setWidget/setCellGUIAttr/setCellExpand 入口","夜学+实测",1),
 ("P-0005","setCellExpand","com.fr.report.cell.TemplateCellElement","setCellExpand(CellExpandAttr)","CPT_BUILD","设置单元格扩展属性","(CellExpandAttr)","-","漏掉扩展=不扩展，整列塌陷","夜学",0),
 ("P-0006","CellExpandAttr","com.fr.report.cell.CellExpandAttr","new CellExpandAttr()","CPT_BUILD","扩展属性（方向/排序/分组）","-","-","setExtendDirection(ExpandType)","夜学",0),
 ("P-0007","ExpandType","com.fr.report.stable.ExpandType","TOP_TO_BOTTOM / LEFT_TO_RIGHT / NONE","CPT_BUILD","扩展方向枚举","-","-","0=纵 1=横 2=不扩展","夜学",0),
 ("P-0008","setExtendDirection","com.fr.report.cell.CellExpandAttr","setExtendDirection(ExpandType)","CPT_BUILD","设扩展方向","(ExpandType)","-","-","夜学",0),
 ("P-0009","Style","com.fr.report.style.Style","new Style()","STYLE","单元格样式对象","-","-","setFormat/setFont/setForeground/setBorder/setBackground/setHorizontalAlignment 等","夜学+实测",1),
 ("P-0010","setFormat","com.fr.report.style.Style","setFormat(String)","STYLE","数字/日期显示格式","(\"0.00\"/\"yyyyMMdd\")","-","-","夜学",0),
 ("P-0011","setFont","com.fr.report.style.Style","setFont(java.awt.Font)","STYLE","字体","(Font)","-","-","夜学",0),
 ("P-0012","setForeground","com.fr.report.style.Style","setForeground(java.awt.Color)","STYLE","前景色/文字色","(Color)","-","-","夜学",0),
 ("P-0013","setBorder","com.fr.report.style.Style","setBorder(BorderAttr)","STYLE","边框","(BorderAttr)","-","-","夜学",0),
 ("P-0014","BorderAttr","com.fr.report.style.BorderAttr","new BorderAttr()","STYLE","边框属性","-","-","setTopBorder/setBottomBorder/setLeftBorder/setRightBorder","夜学",0),
 ("P-0015","BorderLine","com.fr.report.style.BorderLine","(int lineType, Color)","STYLE","边框线","(线型,颜色)","-","线型如 Constants.LINE_THIN","夜学",0),
 ("P-0016","setBackground","com.fr.report.style.Style","setBackground(com.fr.base.background.Background)","STYLE","背景","(Background)","-","ColorBackground/ImageBackground/TextureBackground","夜学+实测",1),
 ("P-0017","ColorBackground","com.fr.base.background.ColorBackground","getInstance(Color) / createBackground(Color)","STYLE","纯色背景","(Color)","Background","FRM 组件背景也用这个","夜学+实测",1),
 ("P-0018","setHorizontalAlignment","com.fr.report.style.Style","setHorizontalAlignment(int)","STYLE","水平对齐","(Constants.LEFT/CENTER/RIGHT)","-","XML: 0=居中 1=左 2=右（反直觉）","夜学+实测",1),
 ("P-0019","setVerticalAlignment","com.fr.report.style.Style","setVerticalAlignment(int)","STYLE","垂直对齐","(Constants.TOP/MIDDLE/BOTTOM)","-","-","夜学",0),
 ("P-0020","setWrapText","com.fr.report.style.Style","setWrapText(boolean)","STYLE","自动换行","(boolean)","-","-","夜学",0),
 ("P-0021","CellGUIAttr","com.fr.report.cell.CellGUIAttr","new CellGUIAttr()","STYLE","单元格展现/打印/导出 GUI 属性","-","-","FRM HTML 必须 setShowAsHTML(true)","夜学+实测",1),
 ("P-0022","setShowAsHTML","com.fr.report.cell.CellGUIAttr","setShowAsHTML(boolean)","STYLE","HTML 渲染开关","(true)","-","否则 HTML 显示纯文本","实测",1),
 ("P-0023","setPageShowContent","com.fr.report.cell.CellGUIAttr","setPageShowContent(boolean)","STYLE","预览显示单元格内容","(boolean)","-","-","夜学",0),
 ("P-0024","Parameter","com.fr.report.parameter.Parameter","new Parameter(name, value)","PARAM","模板参数对象","(name, defaultValue)","-","setName/setValue；WorkBook.addParameter","夜学",0),
 ("P-0025","addParameter","com.fr.main.impl.WorkBook","addParameter(Parameter)","PARAM","注册模板参数","(Parameter)","-","-","夜学",0),
 ("P-0026","ReportParameterUI","com.fr.form.ui.parameter.ReportParameterUI","new ReportParameterUI()","PARAM","参数面板容器","-","-","WorkBook.setParameterUI；addWidget(Widget)","夜学",0),
 ("P-0027","DBTableData","com.fr.data.impl.DBTableData","new DBTableData()","DATASET","SQL 数据集","-","TableData","setDatabaseName/setSql/setName；SQL 内 ${para} 即数据集参数","夜学+实测",1),
 ("P-0028","setSql","com.fr.data.impl.DBTableData","setSql(String)","DATASET","设置 SQL","(SQL 含 ${para})","-","-","夜学",0),
 ("P-0029","setDatabaseName","com.fr.data.impl.DBTableData","setDatabaseName(String)","DATASET","设置数据连接","(连接名)","-","-","夜学",0),
 ("P-0030","putTableData","com.fr.main.impl.WorkBook","putTableData(TableData) / putTableData(name, td)","DATASET","挂数据集到工作簿","(TableData)","-","FRM 用 form.putTableData","夜学+实测",1),
 ("P-0031","EmbeddedTableData","com.fr.data.impl.EmbeddedTableData","new EmbeddedTableData()","DATASET","内置数据集","-","TableData","addColumn(name,Class) 参数顺序！","实测",1),
 ("P-0032","addColumn","com.fr.data.impl.EmbeddedTableData","addColumn(name, Class)","DATASET","加列","(String, Class)","-","不是 (Class,name)！Nashorn 用 java.lang.String.class","实测",1),
 ("P-0033","addRow","com.fr.data.impl.EmbeddedTableData","addRow(List)","DATASET","加行","(ArrayList)","-","-","实测",1),
 ("P-0034","NameDatabaseConnection","com.fr.data.impl.NameDatabaseConnection","new NameDatabaseConnection(connName)","DATASET","按名取连接","(连接名)","Connection","DBTableData XML <Connection> 必须带 class 属性","实测",1),
 ("P-0035","TableDataDictionary","com.fr.data.impl.TableDataDictionary","new TableDataDictionary()","PARAM","数据集数据字典","-","Dictionary","setTableDataName(数据集名)；包名勘误20260912(B-A5 jar实测): 实际 com.fr.data.impl.TableDataDictionary","夜学",0),
 ("P-0036","FormulaDictionary","com.fr.data.impl.FormulaDictionary","new FormulaDictionary(valueFormula, showFormula)","PARAM","公式数据字典","(值公式, 显示公式)","Dictionary","包名勘误20260912(B-A5 jar实测): 实际 com.fr.data.impl.FormulaDictionary","夜学",0),
 ("P-0037","ReportPageAttr","com.fr.report.core.ReportPageAttr","-","CPT_BUILD","报表页面属性（重复标题/冻结）","-","-","XML <ReportPageAttr>/<ReportSettings>；精确 setter 版本不稳定","夜学",0),
 ("P-0038","FrozenColumnRow","-","<FrozenColumnRow columnrow=\"A2\"/>","CPT_BUILD","冻结表头（XML 节点）","-","-","A2=冻结1行表头；树形报表不加","实测",1),
 # FRM 构建核心
 ("P-0039","Form","com.fr.form.main.Form","new Form()","FORM_BUILD","表单（FRM 根对象）","-","IOFile","setContainer(WBorderLayout)；form.export 写盘；不实现 TemplateWorkBook","实测",1),
 ("P-0040","WBorderLayout","com.fr.form.ui.container.WBorderLayout","new WBorderLayout(\"form\")","CONTAINER","表单布局：North=参数区 Center=body","(name)","Layout","addNorth/addCenter/setNorthSize","实测",1),
 ("P-0041","WParameterLayout","com.fr.form.ui.container.WParameterLayout","new WParameterLayout()","CONTAINER","参数面板容器","-","Layout","setUseParamsTemplate(false)/setDelayDisplayContent(false)/setDesignWidth","实测",1),
 ("P-0042","WFitLayout","com.fr.form.ui.container.WFitLayout","new WFitLayout(\"body\")","CONTAINER","body 自适应容器","(name)","Layout","setContainerWidth/Height；子组件必须 BoundsWidget 包装","实测",1),
 ("P-0043","WAbsoluteBodyLayout","com.fr.form.ui.container.WAbsoluteBodyLayout","new WAbsoluteBodyLayout()","CONTAINER","绝对坐标 body（组件坐标生效的关键）","-","Layout","setDesigningResolution(Dimension)；缺中间层 y 坐标全吞成 0","实测",1),
 ("P-0044","BoundsWidget","com.fr.form.ui.BoundsWidget","new BoundsWidget(widget, Rectangle(x,y,w,h))","CONTAINER","组件坐标包装","(Widget, Rectangle)","-","所有组件入容器必须包装，裸 addWidget ClassCastException","实测",1),
 ("P-0045","WGridLayout","com.fr.form.ui.container.WGridLayout","new WGridLayout(rows, cols, hgap, vgap)","CONTAINER","栅格自动布局","(行,列,横距,纵距)","Layout","addWidget(widget,row,col)；无 setDesigningResolution","实测",1),
 ("P-0046","WTitleLayout","com.fr.form.ui.container.WTitleLayout","(String) 或 (String,int)","CONTAINER","图表卡片（标题+内容）","-","Layout","内部 Label+ChartEditor；外层 border 才是用户所见","实测",1),
 ("P-0047","WCardMainBorderLayout","com.fr.form.ui.container.cardlayout.WCardMainBorderLayout","new WCardMainBorderLayout()","CONTAINER","卡片/Tab 容器","-","Layout","North=标题栏 Center=标签","实测",1),
 # FRM 组件
 ("P-0048","Label","com.fr.form.ui.Label","new Label()","WIDGET","标签","-","Widget","setWidgetValue(new WidgetValue(\"文本\"))","实测",1),
 ("P-0049","WidgetValue","com.fr.form.ui.WidgetValue","new WidgetValue(Object)","WIDGET","控件值包装","(值)","-","-","实测",1),
 ("P-0050","TextEditor","com.fr.form.ui.TextEditor","new TextEditor()","WIDGET","文本框","-","Widget","setWidgetValue","实测",1),
 ("P-0051","NumberEditor","com.fr.form.ui.NumberEditor","new NumberEditor()","WIDGET","数字框","-","Widget","setWidgetValue","实测",1),
 ("P-0052","DateEditor","com.fr.form.ui.DateEditor","new DateEditor()","WIDGET","日期框","-","Widget","<DateAttr format=\"yyyy-MM\"/> + widgetValue =today()","实测",1),
 ("P-0053","ComboBox","com.fr.form.ui.ComboBox","new ComboBox()","WIDGET","单选下拉","-","Widget","setWidgetValue；setDictionary","实测",1),
 ("P-0054","ComboCheckBox","com.fr.form.ui.ComboCheckBox","new ComboCheckBox()","WIDGET","多选下拉","-","Widget","RAAttr delimiter/isArray=4 才有箭头；setWaterMark 有效","实测",1),
 ("P-0055","RadioGroup","com.fr.form.ui.RadioGroup","new RadioGroup()","WIDGET","单选按钮组","-","Widget","自定义字典 CustomDictionary","实测",1),
 ("P-0056","CheckBox","com.fr.form.ui.CheckBox","new CheckBox()","WIDGET","复选按钮","-","Widget","setWidgetValue(new WidgetValue(\"启用\"))","实测",1),
 ("P-0057","CheckBoxGroup","com.fr.form.ui.CheckBoxGroup","new CheckBoxGroup()","WIDGET","复选框组","-","Widget","少用","实测",1),
 ("P-0058","TreeComboBoxEditor","com.fr.form.ui.TreeComboBoxEditor","new TreeComboBoxEditor()","WIDGET","下拉树","-","Widget","setMultipleSelection/setReturnFullPath/setWatermark 等","夜学",0),
 ("P-0059","FreeButton","com.fr.form.ui.FreeButton","new FreeButton()","WIDGET","自定义按钮","-","Widget","只有 setText！没有 setWidgetValue","实测",1),
 ("P-0060","FormSubmitButton","com.fr.form.parameter.FormSubmitButton","new FormSubmitButton()","WIDGET","查询/提交按钮","-","Widget","setWidgetName(\"formSubmit0\") 即可","实测",1),
 ("P-0061","ElementCaseEditor","com.fr.form.ui.ElementCaseEditor","new ElementCaseEditor()","WIDGET","表格/报表块（HTML 混合展示）","-","Widget","setElementCase(FormElementCase)；KPI 卡/标题块","实测",1),
 ("P-0062","FormElementCase","com.fr.report.worksheet.FormElementCase","new FormElementCase()","WIDGET","ElementCase 内容","-","-","不是 com.fr.form.main.FormElementCase！addCellElement","实测",1),
 ("P-0063","ChartEditor","com.fr.form.ui.ChartEditor","srcChart.clone()","CHART","图表编辑器","-","Widget","new ChartEditor() 是空壳 NPE；必须 clone 已有图表","实测",1),
 ("P-0064","clone","com.fr.form.ui.ChartEditor","srcChart.clone()","CHART","克隆图表配置","(源)","ChartEditor","clone 不带数据集，需单独 putTableData","实测",1),
 ("P-0065","Formula","com.fr.base.Formula","new Formula(String)","UTIL","公式对象","(\"=...\")","-","KPI HTML 拼 VALUE() 公式；XML <O t=\"XMLable\">","实测",1),
 ("P-0066","FU","com.fr.stable.unit.FU","FU.valueOfPix(pixels, 96)","UTIL","像素转 FR 单位","(px, dpi)","FU","1px≈17561 FU；720000≈41px；ElementCase 行高列宽必须显式设","实测",1),
 ("P-0067","Listener","com.fr.form.event.Listener","new Listener()","EVENT","组件事件","-","-","setEventName(\"afterinit\")/setName/setAction；三参构造被拒；不是 com.fr.event.Listener","实测",1),
 ("P-0068","export","com.fr.form.main.Form","form.export(OutputStream)","IO","FRM 写盘（继承 IOFile）","(FileOutputStream/ByteArrayOutputStream)","-","Java API 异常会把文件清成 0 字节，先备份","实测",1),
 ("P-0069","readStream","com.fr.form.main.Form","Form.readStream(InputStream)","IO","读 FRM","(InputStream)","Form","readTemplateWorkBook 对 FRM 无效","实测",1),
 ("P-0070","setWidgetName","com.fr.form.ui.*","setWidgetName(String)","WIDGET","控件命名（参数控件必须 para_ 前缀）","(name)","-","FRM 里 WidgetName 必须唯一","实测",1),
]

# ---------- BOM 表（方法间关系）----------
def pid(no):
    for i, p in enumerate(PARTS):
        if p[0] == no:
            return i + 1
    raise KeyError(no)

BOM = [
 # CPT：WorkBook 装配
 ("P-0001","P-0002","COMPOSE","addReport(WorkSheet) 挂工作表",1),
 ("P-0001","P-0024","COMPOSE","addParameter 挂模板参数",1),
 ("P-0001","P-0027","COMPOSE","putTableData 挂数据集",1),
 ("P-0001","P-0003","PREPARE","writeTemplateWorkBook 写出",1),
 ("P-0002","P-0004","COMPOSE","addCellElement 挂单元格",1),
 ("P-0004","P-0009","COMPOSE","setStyle 挂样式",1),
 ("P-0004","P-0021","COMPOSE","setCellGUIAttr 挂展现属性",1),
 ("P-0004","P-0005","COMPOSE","setCellExpand 挂扩展属性",1),
 ("P-0009","P-0014","COMPOSE","setBorder 边框",1),
 ("P-0009","P-0017","COMPOSE","setBackground 背景",1),
 ("P-0026","P-0050","COMPOSE","addWidget 参数控件",1),
 ("P-0027","P-0028","COMPOSE","setSql 定义 SQL",1),
 ("P-0027","P-0029","COMPOSE","setDatabaseName 绑定连接",1),
 # FRM：Form 装配
 ("P-0039","P-0040","COMPOSE","setContainer(WBorderLayout)",1),
 ("P-0039","P-0031","COMPOSE","putTableData 数据集",1),
 ("P-0039","P-0068","PREPARE","export 写盘",1),
 ("P-0039","P-0069","REQUIRE","readStream 读取",1),
 ("P-0040","P-0041","COMPOSE","addNorth 参数区",1),
 ("P-0040","P-0042","COMPOSE","addCenter body",1),
 ("P-0042","P-0044","COMPOSE","BoundsWidget 包装",1),
 ("P-0044","P-0043","COMPOSE","absBody 绝对坐标层",1),
 ("P-0043","P-0044","COMPOSE","子组件 BoundsWidget",1),
 ("P-0044","P-0061","COMPOSE","ElementCaseEditor 挂载",1),
 ("P-0044","P-0063","COMPOSE","ChartEditor 挂载",1),
 ("P-0061","P-0062","COMPOSE","setElementCase(FormElementCase)",1),
 ("P-0062","P-0004","COMPOSE","addCellElement(DefaultTemplateCellElement)",1),
 ("P-0062","P-0066","REQUIRE","行高列宽 FU 显式设置",1),
 ("P-0063","P-0064","REQUIRE","图表必须 clone() 源图表",1),
 ("P-0063","P-0031","REQUIRE","克隆图表不带数据集，需 putTableData",1),
 ("P-0054","P-0004","PREPARE","RAAttr 属性需 Python 改 XML（setDelimiter 不写 XML）",1),
 ("P-0041","P-0067","PREPARE","init_css Listener 挂 afterinit",1),
 ("P-0039","P-0003","REQUIRE","writeTemplateWorkBook 对 FRM 无效，必须 export",1),
]

# ---------- 工艺表（工艺路线）----------
ROUTING = [
 ("R-001","构建 CPT 报表骨架",1,"JAVA_API","P-0001","new WorkBook() 创建工作簿","WorkBook 实例"),
 ("R-001","构建 CPT 报表骨架",2,"JAVA_API","P-0002","new WorkSheet() + wb.addReport(ws)","WorkSheet"),
 ("R-001","构建 CPT 报表骨架",3,"JAVA_API","P-0004","addCellElement(DefaultTemplateCellElement(col,row)) 建单元格","单元格"),
 ("R-001","构建 CPT 报表骨架",4,"JAVA_API","P-0009","单元格 setStyle(Style) 设样式","样式"),
 ("R-001","构建 CPT 报表骨架",5,"JAVA_API","P-0003","TemplateWorkBookIO.writeTemplateWorkBook(wb, reportlets相对路径) 写盘",".cpt 文件"),
 ("R-002","构建 FRM 骨架（三层层级）",1,"JAVA_API","P-0039","new Form() + setContainer(new WBorderLayout(\"form\"))","Form"),
 ("R-002","构建 FRM 骨架（三层层级）",2,"JAVA_API","P-0041","border.addNorth(new WParameterLayout()) 参数区 + setNorthSize(36)","参数区"),
 ("R-002","构建 FRM 骨架（三层层级）",3,"JAVA_API","P-0042","border.addCenter(new WFitLayout(\"body\")) + setContainerWidth/Height","body"),
 ("R-002","构建 FRM 骨架（三层层级）",4,"JAVA_API","P-0044","bodyFit.addWidget(new BoundsWidget(absBody, Rect(0,0,W,H)))","三层结构"),
 ("R-002","构建 FRM 骨架（三层层级）",5,"JAVA_API","P-0043","absBody.setDesigningResolution(Dimension) 设计分辨率","DesignResolution"),
 ("R-002","构建 FRM 骨架（三层层级）",6,"JAVA_API","P-0068","form.export(FileOutputStream(绝对路径)) 写盘",".frm 文件"),
 ("R-003","FRM 加 KPI 卡片（ElementCaseEditor）",1,"JAVA_API","P-0061","new ElementCaseEditor()","ECE"),
 ("R-003","FRM 加 KPI 卡片（ElementCaseEditor）",2,"JAVA_API","P-0062","new FormElementCase()（⚠ com.fr.report.worksheet 包）","FormElementCase"),
 ("R-003","FRM 加 KPI 卡片（ElementCaseEditor）",3,"JAVA_API","P-0062","fec.addCellElement(new DefaultTemplateCellElement(col,row,html或Formula)) 多格写","3×2 格子"),
 ("R-003","FRM 加 KPI 卡片（ElementCaseEditor）",4,"JAVA_API","P-0022","每格 new CellGUIAttr()+setShowAsHTML(true)+cell.setCellGUIAttr","HTML 渲染"),
 ("R-003","FRM 加 KPI 卡片（ElementCaseEditor）",5,"JAVA_API","P-0066","setRowHeight/setColumnWidth(FU.valueOfPix(px,96)) 显式尺寸","防滚动条"),
 ("R-003","FRM 加 KPI 卡片（ElementCaseEditor）",6,"JAVA_API","P-0044","absBody.addWidget(new BoundsWidget(ece, Rect(x,y,w,h)))","挂载"),
 ("R-004","FRM 加图表（必须 clone）",1,"JAVA_API","P-0069","Form.readStream(InputStream) 读含图表模板","源图表"),
 ("R-004","FRM 加图表（必须 clone）",2,"JAVA_API","P-0063","srcChart.clone() 克隆图表（new ChartEditor() 空壳 NPE）","克隆图表"),
 ("R-004","FRM 加图表（必须 clone）",3,"JAVA_API","P-0031","form.putTableData(数据集名, embeddedTableData) 补数据集","数据集"),
 ("R-004","FRM 加图表（必须 clone）",4,"PYTHON_ATTR",None,"Python 只改绑定属性值（NameTableData/CD 定义），禁全局 replace","绑定完成"),
 ("R-004","FRM 加图表（必须 clone）",5,"VALIDATE",None,"Form.readStream 回读 getContainer() 必须是 WBorderLayout + Designer 打开","验证"),
 ("R-005","参数面板按 CPT 规则",1,"JAVA_API","P-0041","paraLayout.setUseParamsTemplate(false) 取消常用参数组合","-"),
 ("R-005","参数面板按 CPT 规则",2,"JAVA_API","P-0041","setDelayDisplayContent(false) 取消点击查询前不显示","-"),
 ("R-005","参数面板按 CPT 规则",3,"JAVA_API","P-0054","ComboCheckBox + TableDataDictionary 数据字典（dict SQL）","下拉"),
 ("R-005","参数面板按 CPT 规则",4,"JAVA_API","P-0060","search 查询按钮 + 导出按钮","按钮"),
 ("R-005","参数面板按 CPT 规则",5,"JAVA_API","P-0067","init_css Listener（afterinit）注入按钮 CSS（查询蓝 #3676C5）","CSS"),
 ("R-005","参数面板按 CPT 规则",6,"PYTHON_ATTR",None,"RAAttr 空→Python 替换为 delimiter=\"','\" isArray=\"4\" 才有箭头","下拉箭头"),

 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",1,"JAVA_API",None,"前置: fr-agent 18999/19000 存活 + frm_blank_skeleton.xml + _test_chart.frm 源图表就位","环境确认"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",2,"JAVA_API","P-0069","Form.readStream(frm_blank_skeleton.xml) 读原生骨架（带 FormMobileAttr）","Form"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",3,"JAVA_API","P-0041","border.addNorth(new WParameterLayout()) 参数区 + setNorthSize(40)","参数区"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",4,"JAVA_API","P-0042","bodyFit.setContainerWidth/Height(1920,1080) 画布大小","Size"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",5,"JAVA_API","P-0043","absBody.setDesigningResolution(Dimension(1920,1080)) 设计分辨率","DesignResolution"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",6,"JAVA_API","P-0044","bodyFit.addWidget(new BoundsWidget(absBody, Rect(0,0,1920,1080))) 三层结构","absBody"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",7,"JAVA_API","P-0053","参数控件 ComboBox 年份/版本 + FormSubmitButton 查询按钮 addToPara（BoundsWidget 包装）","参数控件"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",8,"JAVA_API","P-0063","读 _test_chart.frm → srcChart.clone() × 4 → setWidgetName → 挂 absBody（new ChartEditor() 空壳 NPE）","4 图表"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",9,"JAVA_API","P-0034","addDB × 4: DBTableData + NameDatabaseConnection(demo_connection) + 参数宏 SQL → form.putTableData","4 数据集"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",10,"JAVA_API","P-0061","KPI 卡片 ElementCaseEditor × 4 + FormElementCase + CellGUIAttr.setShowAsHTML(true)","KPI 卡"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",11,"JAVA_API","P-0066","FU.valueOfPix 行高列宽显式设置（防 ElementCase 撑大滚动条）","尺寸"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",12,"JAVA_API","P-0068","form.export(FileOutputStream 绝对路径) 写盘（异常会截断0字节，先备份）",".frm"),
 ("R-006","示例驾驶舱骨架构建（Java API 端到端）",13,"VALIDATE","P-0069","Form.readStream 回读 getContainer()==WBorderLayout + absBody children + Designer 打开","验证"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",1,"PYTHON_ATTR",None,"Python 改图表绑定属性值: NameTableData 数据集名 / CategoryName / seriesName / valueName（禁全局 replace）","绑定"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",2,"PYTHON_ATTR",None,"图表标题 Formula 变体正则可改（纯 CDATA 正则静默失败）","标题"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",3,"VALIDATE",None,"JDBC 独立验证数据（fr_jdbc_probe.py）排除数据问题","数据在"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",4,"DESIGNER",None,"强制重开 Designer（JForm+addAndActivateJTemplate）+ 用户 F5 重新预览（旧缓存根因）","重开"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",5,"PYTHON_ATTR",None,"终极修复: OneValueCDDefinition 动态系列 → MoreNameCDDefinition 固定系列 + pivot SQL 宽表","柱高修复"),
 ("R-007","示例驾驶舱 图表绑定与柱高0修复",6,"VALIDATE",None,"ET.parse 校验 + fr-agent 回读 NameTableData 指向新数据集 + Designer 打开","验证"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",1,"DESIGNER",None,"原版备份 _backup_copa_v1 带时间戳 + Copy-Item 克隆 v2（原版不动）","v2 副本"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",2,"JAVA_API","P-0061","渐变标题栏 ElementCaseEditor 替换 Label（background linear-gradient + 琥珀竖条）","标题栏"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",3,"JAVA_API","P-0062","KPI 卡片独立 ElementCaseEditor × 4（3×2 多格 HTML，非整段 div）","KPI 4 卡"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",4,"JAVA_API","P-0044","布局按 demo 百分比重排（bw.setBounds 精确改位置，禁 Python 全局替换）","布局"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",5,"PYTHON_ATTR",None,"参数面板放标题 Label 实现标题+筛选同行（Python 改 XML，setBounds ClassCastException）","标题Label"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",6,"PYTHON_ATTR",None,"init_css 追加 CSS（查询琥珀 #f3b042 / widgetname 大写匹配）","CSS"),
 ("R-008","示例驾驶舱 v2 版本迭代（备份+demo重构）",7,"VALIDATE",None,"用户手动调整后禁止重置画布三处（Size/DesignResolution/BoundsAttr），以用户调整为基准","验证"),
 ("R-009","FRM 样式收尾（全局默认格式）",1,"PYTHON_ATTR",None,"画布背景 #f5f5f5 + Form 默认 1280×720 三处一致","画布"),
 ("R-009","FRM 样式收尾（全局默认格式）",2,"PYTHON_ATTR",None,"图表取消原生标题 + 主题白 + 透明度80% + 圆角5 + 边框细线","图表基"),
 ("R-009","FRM 样式收尾（全局默认格式）",3,"PYTHON_ATTR",None,"图例右侧9号微软雅黑 + 标签 #,##0.00 + 系列宽30间隔20%圆角5 + 无网格线 + tooltip 9号","图表样式"),
 ("R-009","FRM 样式收尾（全局默认格式）",4,"PYTHON_ATTR",None,"图表标题 ElementCaseEditor HTML 块（▎ + #2563eb 18px 微软雅黑 + 行高44px）替代原生标题","标题块"),
 ("R-009","FRM 样式收尾（全局默认格式）",5,"PYTHON_ATTR",None,"WTitleLayout 外层+内层 border 圆角都要设（用户看到的是外层）","圆角"),
 ("R-009","FRM 样式收尾（全局默认格式）",6,"VALIDATE",None,"Designer 打开 + 预览确认（样式基线以 FRM全局默认格式.md 为准）","验证"),
# 2026-08-12 复盘新增:通用工艺路线
 ("R-010","SQL 查询格式化与验证",1,"PYTHON_ATTR",None,"format_sql.py 一键格式化(美化/缩进)数据集 SQL","格式化 SQL"),
 ("R-010","SQL 查询格式化与验证",2,"VALIDATE",None,"verify_sql.py 验证闭环(FR 宏拼接语法 ${} 解析)","验证通过"),
 ("R-010","SQL 查询格式化与验证",3,"VALIDATE",None,"fr_check.py <cpt> 校验 XML + 级联 SQL 格式(ORDER BY 在 ${} 后)","模板通过"),
 ("R-011","API 用法调研(零件表/BOM)",1,"JAVA_API",None,"query_kb.py part <关键字> 查零件(含坑) / bom <P-xxx> 查装配关系","API 清单"),
 ("R-011","API 用法调研(零件表/BOM)",2,"JAVA_API",None,"fr-agent /exec 实测签名(未核验方法禁止写 Java 示例)","实测确认"),
 ("R-011","API 用法调研(零件表/BOM)",3,"VALIDATE",None,"method_bytecode_probe.py 实读 writeXML(命名坑)或 docs 探针","无坑确认"),
 ("R-012","错误排查标准流程",1,"VALIDATE",None,"提取错误关键词 → ckzl/zsk/tbcw/README 索引表","定位"),
 ("R-012","错误排查标准流程",2,"VALIDATE",None,"未命中 → search_files 搜全库 + query_kb.py semantic 语义检索","命中章节"),
# 2026-08-12 复盘固化:人机料法环复盘流程(法)
 ("R-013","人机料法环复盘流程(5M1E)",1,"VALIDATE",None,"盘点五维度现状: query_kb.py 5m1e 总览 + 各表计数,对照实际仓库资产","现状基线"),
 ("R-013","人机料法环复盘流程(5M1E)",2,"VALIDATE",None,"机: 扫描实际脚本资产(kfgj/fzpy/生产脚本/沉淀工具) vs machines 表,补登漏网/修正 MISS 路径","机表同步"),
 ("R-013","人机料法环复盘流程(5M1E)",3,"VALIDATE",None,"料: 物料表补登整目录物料,登记 usage 台账(项目×物料×次数×角色 PROJECT/WIP),聚合 usage_count/used_projects","料表+台账"),
 ("R-013","人机料法环复盘流程(5M1E)",4,"VALIDATE",None,"环: 核对环境表版本/路径/状态(换机必查硬编码路径,统一改 __file__ 动态解析)","环表修正"),
 ("R-013","人机料法环复盘流程(5M1E)",5,"VALIDATE",None,"法: 复盘流程本身固化为工艺路线;检查工艺机械化覆盖,可挂脚本工序补 MC 编号","工艺扩充"),
 ("R-013","人机料法环复盘流程(5M1E)",6,"VALIDATE",None,"重建验证: build_kb.py --rebuild → build_bom_methods.py → build_5m1e.py → query_kb 抽查 + git commit","可重建闭环"),
]

def build(rebuild=False):
    if rebuild and os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    PARTS_ALL = PARTS + EXTRA_PARTS_OVER + EXTRA_PARTS_CHART + EXTRA_PARTS_REFLECT + EXTRA_PARTS_CLASSES + EXTRA_PARTS_DICT
    cur.executemany("INSERT INTO parts(part_no,name,class_name,signature,category,description,params,returns,pitfalls,source,verified) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    [(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10]) for p in PARTS_ALL])
    cur.executemany("INSERT INTO bom(parent_part_id,child_part_id,rel_type,note,qty) VALUES(?,?,?,?,?)",
                    [(pid(b[0]),pid(b[1]),b[2],b[3],b[4]) for b in BOM])
    cur.executemany("INSERT INTO routing(routing_no,routing_name,step_no,work_center,part_id,op_desc,output) VALUES(?,?,?,?,?,?,?)",
                    [(r[0],r[1],r[2],r[3], pid(r[4]) if r[4] else None, r[5], r[6]) for r in ROUTING])
    conn.commit()
    for t in ("parts","bom","routing"):
        print(t, cur.execute(f"SELECT count(*) FROM {t}").fetchone()[0])
    conn.close()
    print("DB:", DB)
    # 自动生成 类->方法 METHOD_OF 关系（组件方法归属）
    import subprocess, sys
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_bom_methods.py")], check=False)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fill_cn_name.py")], check=False)

if __name__ == "__main__":
    build(rebuild="--rebuild" in sys.argv)
