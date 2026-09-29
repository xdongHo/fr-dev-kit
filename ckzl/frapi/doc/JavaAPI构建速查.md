<!--
KB_INDEX: {
  "title": "Java API 构建速查",
  "stage": "report-building",
  "tags": ["JavaAPI", "速查", "com.fr"],
  "keywords": ["Java", "API", "构建", "com.fr"],
  "summary": "FR Java API 构建要点速查:类名 com.fr.* / 方法签名 / 与 .cpt/.frm XML 的对应关系,按 doc 分节"
}
-->

# Java API 构建速查

> 来源:2026-08-06~09 连续学习帆软官方帮助文档(help.fanruan.com/finereport10.0,1203 篇)的 Java API 补课产出。
> 每节 = 一篇文档的 Java API 构建要点(类名/方法签名/XML 对应);标注「无(纯理解级内容)」的节表示该主题无 Java API 实现路径。
> 分工与交叉引用:本文件=按帮助文档分节的签名速查;零件级实测详情(零件编号+方法清单)用 gczsk 结构化工具查:`python ckzl/zsk/gczsk/query_kb.py part <编号或关键字>`(gczsk 为权威零件库);教学上下文与节点编排见 ckzl/gzjd/ NODE 文档。三处互补,不重复收录正文。

---
## doc-1114 导出 Excel 时保留公式- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1114.html
- Java API 构建要点: 无(纯理解级内容)。该文档描述的是设计器(Report Designer)中单元格「公式定义面板」里的一个勾选项「导出/编辑结果时保留公式」,属于设计期配置,通过设置保存到 .cpt 模板 XML 中,文档全程未涉及任何 com.fr.* Java 编码。生效约束:仅支持「原样导出 Excel」(不支持分页/分页分 Sheet 导出);被隐藏且参与其他列公式计算的列,即使勾选也不生效;移动端不支持。若需在 Java 侧复现等价能力,本质是让单元格公式以"公式而非计算值"写回 Excel,属于导出器(ExcelExport/原样导出)对公式单元格的处理策略,而非文档给出的 API 路径。
- 最小 Java 示例: 无

## doc-140 单元格扩展- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-140.html
- Java API 构建要点: 该文档描述设计器 GUI「单元格属性>扩展>扩展方向」(纵向/横向/不扩展), 但有明确 Java API 落点。核心类 `com.fr.report.cell.CellExpandAttr`(单元格扩展属性), 通过 `com.fr.report.cell.TemplateCellElement.setCellExpand(CellExpandAttr)` 挂到单元格元素上; 实现类 `com.fr.report.cell.DefaultTemplateCellElement(column,row)`。扩展方向枚举 `com.fr.report.stable.ExpandType`: `TOP_TO_BOTTOM`(纵向)、`LEFT_TO_RIGHT`(横向)、`NONE`(不扩展), 经 `CellExpandAttr.setExtendDirection(ExpandType)` 设置。XML 对应关系: 该属性序列化为 .cpt 中 `<CellElement>` 内的 `<CellExpandAttr><extendDirection>` 节点 (kit 内部抽象为 `<Expand dir="0|1|2"/>`, 0=纵向/1=横向/2=不扩展, 见 LEARNINGS.md §1494-1496)。注意: ① 设计器「拖字段默认纵向扩展」仅在 GUI 成立; 手写/无头生成若漏掉 expand 属性, FR 运行时按「不扩展」处理导致整列塌陷, 必须显式注入; ② CellExpandAttr 还承载左/上父格、扩展后排序、分组方式等, 本文只覆盖扩展方向; ③ setter 名在个别 10.0 小版本可能为 setExtendDirection / setCellExpand, 需以实际 jar 为准。工作簿落地用 `com.fr.main.impl.WorkBook` + `com.fr.report.worksheet.WorkSheet` + `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String)` 写出 .cpt。
- 最小 Java 示例: practice/topic_140_java/CellExpandDemo.java

## doc-175 定义图表单元格数据源- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-175.html
- Java API 构建要点: 无(纯理解级内容)。该文档为设计器(Report Designer)GUI 操作指南: 在「单元格元素>数据」里选「单元格数据」, 并在分类/系列/值输入框中填入单元格引用公式(连续用 [A1:A3]、不连续用 [A1,A3,A5], 必须用 F(x) 进入公式定义面板, 直接输入会被判为普通文本)。同时强调单元格父子格关系(分类是系列的父格、系列是值的父格), 以及公式二次计算会丢失单元格属性、地图经纬度定位、插件(图表单元格数据源 V1.0/V1.1)算法优化等注意事项。全程为设计期模板配置 + 公式语法说明, 文档未给出任何 com.fr.* 类名 / 方法签名 / 包路径, 属于「公式 / 概念级」内容, 无文档内 Java API 实现路径可提炼。若要在 Java 侧复现等价能力, 本质是在图表数据定义里以「单元格公式(FormulaColumn/公式引用)」而非「数据集(DataTable)」作为图表数据来源, 但所用具体类(如 com.fr.chart.chartdata.* 下的单元格数据定义)与节点映射需另行查证 jar, 文档本身未提供, 故不杜撰示例。
- 最小 Java 示例: 无

## doc-3717 汉字数字排序- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3717.html
- Java API 构建要点: 该文档描述两种排序方案,本质都是「单元格扩展排序属性」,有明确 Java API 落点。核心类 `com.fr.report.cell.cellattr.CellExpandAttr`(单元格扩展属性),通过 `com.fr.report.elementcase.TemplateCellElement.setCellExpandAttr(CellExpandAttr)` 挂到单元格元素上(实现类 `com.fr.report.cell.DefaultTemplateCellElement(column,row)`)。①方案二「扩展后排序」对应 `CellExpandAttr.setExtendSortType(int)`(升序 `com.fr.general.ReportConstants.SORT_ASC` / 降序 `SORT_DESC`)与 `CellExpandAttr.setExtendSortFormula(String)`,公式即文档 `INARRAY($$$, MAPARRAY(RANGE(COUNT(A2[!0])), NUMTO(item)))`;②方案一「高级排序-自定义顺序」为同类的「自定义排序公式」入口 `CellExpandAttr.setSortFormula(String)`(如 `SWITCH($$$,"一",1,"二",2,...)`),排序类型为 `setSortType(ReportConstants.SORT_ASC)`。XML 对应关系:这些属性序列化为 .cpt 中 `<CellElement row col>` 内的 `<CellExpandAttr>` 子节点,其 `<ExtendSortType>`(Asc/Desc)与 `<ExtendSortFormula>`(CDATA 公式)即方案二;`<SortType>`/`<SortFormula>` 即方案一。注意:NUMTO 仅支持整数(不支持小数),且方案二依赖「汉字数字从一起始且连续」的强假设,Java 侧无法绕过该公式约束。工作簿落地:`com.fr.report.worksheet.WorkSheet.setTemplateCellElement(...)` + `com.fr.main.impl.WorkBook` + `com.fr.report.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String)` 写出 .cpt。
- 最小 Java 示例: practice/topic_3717_java/SetChineseNumberSort.java

## doc-135 分页预览- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-135.html
- Java API 构建要点: 偏配置/概念级。该文档讲述设计器中「模板>模板web属性>分页预览」的可视化配置(显示位置、页面特殊设置、工具栏、事件),非 Java 编码教程。其底层配置对象为 com.fr.web.attr.ReportWebAttr(对应 .cpt 模板 XML 中的 <ReportWebAttr> 节点),保存的是分页预览的 Web 展现属性;工具栏由 com.fr.web.core.widget.ReportWebToolbar 表示,工具项对应 com.fr.web.core.widget.Button 子类。整体可经 WorkBook 的 web 属性接口挂到模板上(如 workBook.setReportWebAttr(ReportWebAttr) / 相关 ReportWebAttr 存取方法)。注意:① 分页预览设置只作用于"分页预览"模式,与填报/数据分析预览无关;② 文档描述的"事件设置"实为前端 JS(Web 页面事件),属 Browser 侧脚本而非 Java API;③ "报表显示位置/以图片方式显示/iframe 自动收缩/重方式输出格子"均为 ReportWebAttr 的布尔/枚举属性。由于工具栏/显示位置等具体方法签名在不同 10.0 小版本中不稳定,且无标准构造示例,故不提供可保证正确的最小片段。
- 最小 Java 示例: 无

## doc-136 填报预览- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-136.html
- Java API 构建要点: 偏配置/概念级(与 doc-135 分页预览同类)。该文档讲述设计器中「模板>模板web属性>填报页面」的可视化配置,非 Java 编码教程。其底层配置对象为 com.fr.web.attr.WriteAttr(对应 .cpt 模板 XML 中 <ReportWebAttr> 下的填报相关属性/WriteAttr),保存的是填报预览的 Web 展现属性,经 WorkBook 的 web 属性接口挂到模板上(如 workBook.getReportWebAttr() / ReportWebAttr 存取方法;WriteAttr 含 sheet 标签页位置、报表显示位置、编辑行背景色、未提交离开提示、直接显示控件、自动暂存、工具栏、Web 事件等开关)。关键注意:① 切换至填报预览并非 Java API 行为,而是在访问模板 URL 后追加 `&op=write` 请求参数来指定预览方式(无参数=分页预览,op=write=填报预览),由 FR Web 层(op 分发)解析,与 com.fr.* 构建无关;② "sheet 标签页显示位置/报表显示位置/填报当前编辑行背景颜色/未提交离开提示/直接显示控件/自动暂存"均为 WriteAttr / ReportWebAttr 的布尔或枚举属性;③ "工具栏"由 com.fr.web.core.widget.ReportWebToolbar 与 Button 子类表示;④ "事件设置"实为前端 JS(Web 页面事件),属 Browser 侧脚本而非 Java API,移动端仅支持加载起始/结束、填报前/后/成功/失败事件。因具体方法签名在 10.0 各小版本不稳定且无标准构造示例,不提供可保证正确的最小片段。
- 最小 Java 示例: 无

## doc-157 模板参数- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-157.html
- Java API 构建要点: 该文档描述设计器 GUI「模板>模板参数」新增参数、「参数面板编辑」加控件与绑定、单元格「过滤」用 $参数 过滤数据, 但有明确 Java API 落点。① 模板参数对象 com.fr.report.parameter.Parameter(构造 new Parameter(name, defaultValue) 或 setName/setValue), 通过 com.fr.main.impl.WorkBook.addParameter(Parameter) 挂到工作簿, 对应 .cpt XML <WorkBook> 下的 <Parameter name="地区" class="java.lang.String">华东</Parameter> 节点; 取参 getParameters()/getParameter(name), 改名 setName(等同设计器双击重命名)。② 参数面板容器 com.fr.form.ui.parameter.ReportParameterUI, 经 WorkBook.setParameterUI(ReportParameterUI) 挂接, 对应 .cpt 的 <ParameterUI> 节点; 默认文本控件为 com.fr.form.ui.TextEditor, 需 setWidgetName("地区") 使其名称==参数名完成「控件↔参数」绑定(Web 端给控件赋值即给参数赋值), ReportParameterUI.addWidget(Widget) 加入面板。③ 数据过滤(单元格「过滤」普通条件: 数据列=地区, 操作符=等于, 值类型=参数, $地区)对应 com.fr.report.cell.cellattr.core.group.Filter + Condition/Compare 挂在 TemplateCellElement 的 ConditionAttr 上, 该部分 API 较不透明, 本例不展开。注意: a) 模板参数 vs 数据集参数不同 —— 模板参数是取全部数据后在报表层过滤(适小数据量), 大数据量应在 SQL 内用数据集参数过滤, 二者落点不同; b) 控件绑定靠"名称相等", TextEditor.setWidgetName 必须等于 Parameter.getName; c) 参数为空时查询结果可能为空(除非另加"为空选全部"逻辑), 与设计器注一致; d) setParameterUI / ReportParameterUI.addWidget 方法签名在个别 10.0 小版本中可能不同, 需以实际 jar 为准。工作簿落地用 com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String) 写出 .cpt。
- 最小 Java 示例: practice/topic_157_java/TemplateParamDemo.java

## doc-368 分页冻结- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-368.html
- Java API 构建要点: 文档本身是设计器 GUI 操作指南(「模板>重复与冻结设置」勾选重复标题行/列、设置分页冻结),无内嵌 Java 代码;但所描述的"重复标题行列 + 分页冻结"是工作簿(W模板)的页面属性,确有 Java 类落点,可无头写入 .cpt。核心类:
  ① `com.fr.main.impl.WorkBook` — 模板工作簿,承载报表页面属性(实现 com.fr.report.TemplateWorkBook);落地写出用 `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)`。
  ② `com.fr.report.core.ReportPageAttr`(报表页面属性对象)—— 由 WorkBook 持有,对应 .cpt XML 中的 `<ReportPageAttr>` / 其内 `<ReportSettings>` 节点;经 WorkBook 的页面属性存取方法挂接(如 `workBook.getReportPageAttr()` / `workBook.setReportPageAttr(ReportPageAttr)`,具体 getter/setter 名各 10.0 小版本可能微调,以实际 jar 为准)。该对象负责重复标题与冻结行列的序列化。
  XML 节点对应关系(与设计器「重复与冻结设置」一一对应,节点名取自本仓库 practice/topic_368 已验证骨架):
  - 重复标题行 → `<ReportSettings>` 内 `<RepeatRow><![CDATA[0,1]]></RepeatRow>`(索引从 0 起,逗号分隔),对应 ReportPageAttr 的"重复标题行"开关;
  - 重复标题列 → `<RepeatColumn><![CDATA[0]]></RepeatColumn>`,对应 ReportPageAttr 的"重复标题列"开关;
  - 分页冻结 → `<FrozenColumnRow columnrow="B3"/>`,`columnrow` 指"冻结区右下角"格(如 A3=冻结前2行、C1=冻结前2列、B3=前2行+前2列),对应 ReportPageAttr 的冻结行列设置。
  注意:① 顺序——先设重复标题行/列,再设冻结;② 合并单元格陷阱:冻结区若含合并单元格,`columnrow` 必须到达合并区右下角,否则 doc-368 注:第一页冻结内容不显示;③ 取消分页(全数据一页)非 Java 模板属性,而是预览 URL 追加 `&__bypagesize__=false`(Web 层参数,与 com.fr.* 构建无关);④ 移动端仅普通报表分页预览支持冻结,且双向自适应无冻结效果——均为预览端行为,非模板 API。
  因 `ReportPageAttr` 上 setRepeatHeaderRow/setRepeatHeaderColumn/setFreezeRow/setFreezeColumn 等精确方法名在各 10.0 小版本间不稳定,且无本地 jar 可反编译校验,故未杜撰可保证正确的 setter 签名。
- 最小 Java 示例: 无(把握不足:freeze/repeat 精确 setter 签名未对照实际 jar 确认,避免给出错误签名;节点级对应关系已明确,可直接参照 practice/topic_368/freeze_sample.cpt.xml 构造 .cpt 后再用 TemplateWorkBookIO 写出)

## doc-158 数据集参数- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-158.html
- Java API 构建要点: 该文档描述设计器 GUI「数据集定义>SQL 查询框」用 ${para} 宏定义数据集参数, 但具体能力有明确 Java API 落点(与 doc-157 模板参数同类但落点不同)。① 数据集本身为 com.fr.data.impl.DBTableData, 经 setDatabaseName(String)/setSql(String)/setName(String) 配置, 其中 SQL 字符串内写入 '${area}' 即声明"数据集参数 area"(对应 .cpt <TableData><DBTableData><SQL>SELECT * FROM 销量 WHERE 地区 = '${area}'</SQL> 节点, ${area} 文本原样序列化为 SQL 子节点), 通过 com.fr.main.impl.WorkBook.putTableData(DBTableData) 挂到工作簿。② 同名参数需注册到工作簿参数列表 com.fr.report.parameter.Parameter(构造 new Parameter() 后 setName("area")/setDefaultValue("华东")), 经 WorkBook.addParameter(Parameter) 挂接, 对应 .cpt <WorkBook><Parameters><Parameter name="area" class="java.lang.String">华东</Parameter> 节点; 取参 getParameters()/getParameter(name)。③ 运行期由 FR 公式引擎解析 SQL 中的 ${area}, 取参数列表内同名 Parameter 当前值做文本替换得到最终 SQL。关键注意(与 doc-157 的差异): a) 数据集参数"不与数据集绑定"——多个数据集同名参数共享工作簿里同一个 Parameter 对象, 最后一次赋值生效; b) 区别于模板参数是取全量后在报表层过滤, 数据集参数在 SQL 内过滤(大数据量高效, 文档 1.2 明确); c) 一个 SQL 可写多个 ${}(如 area/province)分别定义多个参数, 各自 new Parameter()+addParameter 注册; d) ${} 内可用 if/len 等 FR 内置函数(文档 2.2/2.4), 属 SQL 文本中的公式, 不影响 Java API 形态; e) DBTableData 的 setDatabaseName/setSql/setName 方法签名在个别 10.0 小版本中可能微调, 以实际 jar 为准。工作簿落地用 com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String) 写出 .cpt。
- 最小 Java 示例: practice/topic_158_java/DatasetParamDemo.java

## doc-159 全局参数- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-159.html
- Java API 构建要点: 无(纯理解级内容)。该文档全程描述设计器 GUI 操作「服务器>全局参数」以新增并被全工程模板共享的参数, 属于工程级配置/概念说明, 文档未出现任何 com.fr.* 编码、也未给出 XML 节点/类的对应关系。全局参数在物理上存放于工程配置(非单个 .cpt 模板 XML), 由服务器配置而非模板 API 管理; 其概念对象虽可对应到 com.fr.report.parameter.Parameter 与模板参数同构, 但"全局(跨模板共享)"这一特性由工程级配置存储/加载机制承载, 本篇文档没有给出任何构造或落盘 API 路径, 故不提炼 Java 构建要点。补充提醒: 全局参数与模板参数同名时以模板参数为准、参数面板只显示一个(文档 4.1); 远程部署需在原工程与远程工作目录分别设置(文档 4.2), 这两点均属配置/注意事项, 而非 Java 编码点。
- 最小 Java 示例: 无

## doc-176 定义图表数据集数据源- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-176.html
- Java API 构建要点: 无(纯理解级内容)。该文档为设计器(Report Designer)GUI 操作指南:在图表「数据」面板选择「数据集数据」,选对应数据集后绑定分类(如地区)、系列名使用(字段值/字段名)、系列名(产品/字段名)、值(销量)及汇总方式(求和)。全文为设计期模板配置 + 字段值/字段名概念说明(系列名=图例,字段名=列名,字段值=记录),未出现任何 com.fr.* 类名/方法签名/包路径,属「概念/配置级」内容,无文档内 Java API 实现路径可提炼。若要在 Java 侧复现等价能力,本质是在图表数据定义里以「数据集(数据集数据)」作为图表数据来源(对应 com.fr.chart.chartdata.* 系列下的数据集数据定义类),但所用具体类、方法签名及与 .cpt 中 <Chart><Plot><DataPane> 等节点的映射需另行查证 jar,文档本身未提供,故不杜撰示例。
- 最小 Java 示例: 无

## doc-217 单元格样式- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-217.html
- Java API 构建要点: 该文档描述设计器 GUI「单元格属性>样式」(自定义样式/预定义样式), 但有明确 Java API 落点。核心类 `com.fr.report.style.Style`(单元格样式对象), 经 `com.fr.report.cell.DefaultTemplateCellElement.setStyle(Style)`(实现自 `com.fr.report.cell.TemplateCellElement`)挂到单元格元素上; 单元格实现类 `com.fr.report.cell.DefaultTemplateCellElement(column,row)`(见 topic_140_java 用法)。`Style` 关键方法(与文档 2.x 小节对应): ① [2.1.1 格式] `setFormat(String)` — 数字/货币/百分比/日期显示格式, 例 "0.00"/"yyyyMMdd", 对应 XML 属性 `format`; ② [2.1.2 字体] `setFont(java.awt.Font)`、`setForeground(java.awt.Color)`(字体颜色, 对应 `color`)、下划线/删除线(部分版本 `setUnderline(int)`/`setStrikeLine(boolean)`, 对应 `underline`/`strikeLine`), 字体名/字号/字形经 `java.awt.Font` 承载, 对应 `fontName`/`fontSize`/`fontStyle`; ③ [2.2.1 边框] `setBorder(BorderAttr)`, 其中 `com.fr.report.style.BorderAttr` 用 `setTopBorder(BorderLine)`/`setBottomBorder`/`setLeftBorder`/`setRightBorder` 设四条边, `com.fr.report.style.BorderLine` 由线型 `int`(如 `com.fr.base.Constants.LINE_THIN`)+ `java.awt.Color` 构造, 对应 XML `border`; ④ [2.2.2 背景] `setBackground(com.fr.base.background.Background)`, 实现类如 `com.fr.base.background.ColorBackground.createBackground(Color)`(亦可 `ImageBackground`/`TextureBackground`), 对应 `bgColor`/`bgImage`; ⑤ [2.3.1 基本对齐] `setHorizontalAlignment(int)`(`Constants.LEFT`/`CENTER`/`RIGHT`)、`setVerticalAlignment(int)`(`Constants.TOP`/`MIDDLE`/`BOTTOM`), 对应 `halign`/`valign`; ⑥ [2.3.2 文本控制/方向/缩进/间距] 自动换行 `setWrapText(boolean)`(对应 `wrapText`), 其余如自定义角度/竖排、缩进、段前段后/行间距属 Style 的进阶属性(部分版本如 `setRotation`/`setPaddingLeft`/`setLineSpacing` 等), 具体签名以实际 jar 为准。XML 对应关系: Style 序列化为 .cpt 中 `<CellElement>` 上的样式属性集合, 即文档各 GUI 项的最终落盘节点由 `Style` 类统一读写。注意: ① 样式只影响显示, 不改变单元格实际值(文档注); ② 预定义样式(文档 3)为设计器内置, 无独立 Java 构造入口, 本质是 Style 预设集合; ③ BorderLine 构造器、Style 实例获取(`new Style()` 或静态默认实例)、`setUnderline`/`setFormat` 等细节名在个别 10.0 小版本可能微调, 需以实际 jar 为准。工作簿落地用 `com.fr.main.impl.WorkBook` + `com.fr.report.worksheet.WorkSheet` + `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String)` 写出 .cpt。
- 最小 Java 示例: practice/topic_217_java/CellStyleDemo.java

## doc-225 预览、打印和导出单元格- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-225.html
- Java API 构建要点: 该文档是设计器 GUI 操作指南(单元格属性>其他 面板的勾选项), 但有明确 Java API 落点。核心类 `com.fr.report.cell.CellGUIAttr`(单元格展现/打印导出 GUI 属性), 通过 `com.fr.report.cell.TemplateCellElement.setCellGUIAttr(CellGUIAttr)` 挂到单元格元素上; 实现类 `com.fr.report.cell.DefaultTemplateCellElement(column,row)`。关键方法(布尔开关): `setPageShowContent(boolean)`(预览单元格内容)、`setPrintCellContent(boolean)`(打印单元格内容)、`setExportCellContent(boolean)`(导出单元格内容)、`setPrintFillBackground(boolean)`(打印单元格背景)、`setExportFillBackground(boolean)`(导出单元格背景)。XML 对应关系: 序列化为 .cpt 中 `<CellElement>` 内的 `<CellGUIAttr>` 子节点(设计器勾选项直接写入此节点属性)。工作簿落地同 doc-140: `com.fr.main.impl.WorkBook` + `com.fr.report.worksheet.WorkSheet` + `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String)` 写出 .cpt。约束: ① 填报预览不支持此设置; ② Word/Excel 导出仅支持颜色背景、不支持图片背景, PDF 全部支持; ③ CellGUIAttr 的部分 setter 名在 10.0 不同小版本间可能微调, 以实际 jar 反编译为准, 故示例仅作结构参考。
- 最小 Java 示例: practice/topic_225_java/CellGUIAttrDemo.java

## doc-260 下拉树控件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-260.html
- Java API 构建要点: 该文档虽是设计器 GUI「控件设置」说明, 但下拉树是可经 com.fr.* 程序化构建的真实控件, 有明确 Java API 落点。核心类 `com.fr.form.ui.TreeComboBoxEditor`(下拉树编辑器, 继承 ComboBoxEditor); 文档默认控件名 `treeComboBoxEditor#` 可确认该类名(注: 早期 practice/topic_260 的 Python 版推断的 `com.fr.form.ui.TreeComboBox` 并非下拉树本体, 应以此处为准)。挂载方式: ① 参数控件 → `com.fr.form.ui.parameter.ReportParameterUI.addWidget(Widget)` 挂到参数面板, 对应 .cpt 的 `<ParameterUI>` 内 `<InnerWidget class="com.fr.form.ui.TreeComboBoxEditor">` 节点; ② 填报控件 → 经 `com.fr.report.cell.TemplateCellElement.setWidget(Widget)` 挂到单元格, 序列化进 `<CellElement><Widget>` 节点。关键属性方法(对文档 2.1 各设置项): `setWidgetName(String)`(控件名称)、`setEnabled(boolean)`(可用)、`setVisible(boolean)`(可见)、`setMultipleSelection(boolean)`(多选)、`setAsyncLoad(boolean)`(异步加载, 自动构建方式下须 false)、`setReturnLeafNodeOnly(boolean)`(结果返回叶子节点, 仅多选有效)、`setReturnFullPath(boolean)`(结果返回完整层次路径 → 返回 [华北,北京,北京]; 不勾只返回叶子)、`setAllowBlank(boolean)`(允许为空)、`setAllowEdit(boolean)`(允许直接编辑 = 开启模糊搜索)、`setAllowCreateValue(boolean)`(允许自定义值, 10.0.18+)、`setWatermark(String)`(水印)、`setFontSize(int)`(字体大小, 仅参数控件)、`setErrorMsg(String)`(错误提示)、`setDictionary(Dictionary)`(数据字典)。数据字典三种构建方式对应 `com.fr.form.ui.TreeDictionary`: 普通/极速分层用 `TreeLayerDataModel` 逐层(Vector)定义; 自动构建依赖「树数据集」(`com.fr.report.structure.TreeTableData`, 根节点父必须为空)。XML 节点映射: widget 类名=TreeComboBoxEditor; 各布尔属性映射为同名/驼峰属性; 数据字典映射为 `<Dictionary class="com.fr.form.ui.TreeDictionary">` 内含分层节点。默认值须写完整节点路径(单选 `华北,北京,北京` / 多选 `华北,北京,北京;华东,上海,上海` / 公式 `=[1,11,111]`), 该约束属运行时校验, Java 侧仅写入字符串不校验。注意: ① 异步加载对自动构建方式无效; ② 结果返回叶子节点仅多选生效; ③ TreeLayerDataModel 各层 setter(数据列/依赖关系)在不同 10.0 小版本命名可能微调, 需以实际 jar 核验; ④ 事件(初始化后/编辑前/编辑后/编辑结束/点击/节点生成)属于前端 JS, 非 Java API。工作簿落地用 `com.fr.main.impl.WorkBook` + `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String)` 写出 .cpt。
- 最小 Java 示例: practice/topic_260_java/TreeComboBoxDemo.java

## doc-299 预览模板数据集配置错误- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-299.html
- Java API 构建要点: 无(纯理解级内容)。本文档为预览模板时「数据集配置错误/找不到数据连接」类报错的排错指南(错误码 11300001、31300013),仅描述如何在设计器中检查数据连接名称/驱动器/URL/用户名密码及 SQL 语句正确性,属概念与运维排查,无 com.fr.* Java API 构建路径可提炼。
- 最小 Java 示例: 无

## doc-596 JS自定义提交按钮- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-596.html
- Java API 构建要点: 无(纯理解级内容)。本文档仅描述在单元格按钮控件上通过 JS 接口 `_g().verifyAndWriteReport()` 触发表单校验与提交入库,属于前端 JS / 填报 UI 配置层面。提交动作的实际处理由 FR 服务端内置逻辑完成,文档未暴露任何可供用户以 com.fr.* Java API 构建/生成对应 .cpt 节点(如按钮控件、点击事件 JS)的实现路径。无需 Java 代码生成模板节点。
- 最小 Java 示例: 无

## doc-608 填报控件数据字典联动- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-608.html
- Java API 构建要点: 该文档是设计器 GUI「给单元格下拉框控件设置数据字典并令其随另一格联动」的操作指南, 但其描述能力可经 com.fr.* 程序化构建, 有明确 Java API 落点。核心链路 = 单元格(带控件) + 下拉框控件(ComboBox) + 控件数据字典(Dictionary) + 数据集(TableData), 联动效果由字典引用的单元格(如 C9)在运行时驱动, 无需额外 API 调用。
  ① 工作簿/单元格: `com.fr.report.worksheet.WorkBook`(实现 TemplateWorkBook), 单元格元素 `com.fr.report.cell.DefaultCellElement(int column, int row)`, 经 `WorkBook.getWorksheet().addCellElement(CellElement)` 写入, 落地用 `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)` 写出 .cpt。
  ② 填报下拉框控件: `com.fr.form.ui.ComboBox`(下拉框控件本体)。关键方法: `setWidgetName(String)`(控件名, 对应设计器「控件名」)、`setDictionary(Dictionary)`(数据字典)、`setEnabled/setVisible`(可用/可见)等。`ComboBox` 经 `CellElement.setWidget(Widget)` 挂到单元格, 序列化为 .cpt `<CellElement><Widget class="com.fr.form.ui.ComboBox">` 节点。
  ③ 数据字典 Dictionary 接口及实现(对应设计器「数据字典」配置):
     - 方法一(数据集 SQL 筛选): `com.fr.data.impl.TableDataDictionary` —— `setTableDataName(String)` 绑定某数据集(如 ds1/ds2), 序列化为 `<Dictionary class="com.fr.data.impl.TableDataDictionary" tableDataName="ds1">`。
     - 方法二/三(公式): `com.fr.data.impl.FormulaDictionary` —— 实际值/显示值两个公式字符串构造(如 `new FormulaDictionary("SQL(\"FRDemo\",...)", "$$$")` 或 `value("ds1","城市","地区",C9)`), 序列化为 `<Dictionary class="com.fr.data.impl.FormulaDictionary"><valueFormula>...</valueFormula><showFormula>$$$</showFormula>`。
  ④ 数据集 TableData(联动筛选的数据源): `com.fr.data.impl.DBTableData`(⚠原文所写 `com.fr.data.impl.SQLTableData` 经 2026-09-12 jar 实测 FR10 全部 1133 jar 0 命中,FR10 无此类;联动数据源即普通 SQL 数据集 `com.fr.data.impl.DBTableData`,jar+.cpt 实证), 经 `WorkBook.addTableData(TableData)` 挂接, 并 `setName("ds1"/"ds2")` 命名以被字典引用; ds2 的 SQL 内 '${C9}' 即「联动参数=单元格 C9」, 由 FR 引擎在运行时取 C9 当前值做文本替换(对应文档注: 联动参数须设为单元格, 移动端才支持)。
  XML 节点对应关系小结: `<CellElement col=2 row=8><Widget class=ComboBox widgetName=region><Dictionary class=TableDataDictionary tableDataName=ds1>` ≈ C9 地区框; `<CellElement col=5 row=8><Widget class=ComboBox widgetName=city><Dictionary class=TableDataDictionary tableDataName=ds2>` ≈ F9 城市框(联动)。
  注意: a) 联动本身是运行时行为(引擎重算被联动控件字典), Java 侧只负责「把控件+字典+数据集正确写入模板」, 不调用任何「联动」API; b) 文档 4 注意事项「触发联动会清空被联动控件旧值」属引擎默认行为, 非 API 开关; c) TableDataDictionary/FormulaDictionary/ComboBox 的 setter 名(如 setTableDataName / FormulaDictionary 构造参数顺序)在个别 10.0 小版本可能微调, 需以实际 jar 为准; d) SQLTableData 需 FRContext 已初始化且数据连接 "FRDemo" 存在。
- 最小 Java 示例: practice/topic_608_java/FillControlDictLinkage.java

## doc-611 填报冻结- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-611.html
- Java API 构建要点:
  - 文档本质为「设计器菜单配置」指南（模板>重复与冻结设置），未直接给出 Java 代码，但其描述的能力（填报预览时冻结首部行/列）可通过 FR Java API 在模板 XML 中写入，存在实现路径。
  - 核心类/方法:
    - com.fr.main.workbook.WorkBook（.cpt 模板载体，实现 com.fr.report.stable.TemplateWorkBook）
      - WorkBook setWebAttr(com.fr.report.stable.WebAttr) / WebAttr getWebAttr() —— 挂接 Web 属性（含冻结）
    - com.fr.web.core.ReportWebAttr（WebAttr 实现类，承载冻结/重复行列配置）
      - void setFreezeRow(int freezeRow)  —— 冻结首部行数（从首行起，对应文档注1：必须从首行开始）
      - void setFreezeCol(int freezeCol)  —— 冻结首部列数（从首列起，不支持中间/尾列冻结）
      - void setRepeatRowStart(int) / setRepeatRowEnd(int) / setRepeatColStart(int) / setRepeatColEnd(int) —— 重复行列区域（同界面的“重复”部分）
    - com.fr.io.TemplateWorkBookIO
      - TemplateWorkBook readTemplateWorkBook(String path)
      - void writeTemplateWorkBook(WorkBook, String path)
  - 与 .cpt XML 节点/属性对应关系:
    - WorkBook.setWebAttr(ReportWebAttr) 写入 .cpt 根的 <WebAttr>（部分版本写作 <ReportWebAttr>）节点；
    - setFreezeRow(n) / setFreezeCol(m) 对应 <WebAttr> 下 <freezeRow>n</freezeRow>、<freezeCol>m</freezeCol> 子节点；
    - 重复行列对应 <WebAttr> 下 <repeatRowStart>/<repeatRowEnd>/<repeatColStart>/<repeatColEnd> 子节点。
  - 注意：冻结为“从首行/首列起算的固定行/列数”，与文档注1、注3一致；动态扩展行在普通填报预览下会全部冻结，新填报预览仅冻结指定行数（文档注2，属预览端行为，非模板 XML 属性）。
- 最小 Java 示例: <外部学习工作区>\practice\topic_611_java\FreezeDemo.java

## doc-651 决策报表组件联动- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-651.html
- Java API 构建要点: 该文档是设计器 GUI 操作指南(拖组件、属性面板设数据/超级链接、body 样式),但所描述能力「组件联动」有明确 Java API 落点,核心=图表超级链接携带动态参数驱动另一组件的数据集重查。关键类与方法:
  ① 决策报表模板根 `com.fr.form.main.Form`(对应 .frm XML 根 `<Form>`),承载所有组件;表单 IO 写出 .frm(方法名各 10.0 小版本不稳定,以 jar 为准)。
  ② 图表组件 `com.fr.chart.form.ChartEditor`(设计器里"饼图/柱形图"组件,对应 `<Widget widgetName="饼图" class="com.fr.chart.form.ChartEditor">`);其数据绑定经 `com.fr.chart.chartdata.*` 指向数据集。
  ③ 数据集 `com.fr.data.impl.DBTableData`:SQL 内写 `${地区}` `${product}` 宏声明数据集参数(对应 `<TableData><DBTableData><SQL>` 节点);经 `com.fr.main.impl.Form`/(Form 持有的数据集表)putTableData 挂接;参数对象 `com.fr.report.parameter.Parameter`(new Parameter("product",""))注册到模板参数表(与 doc-158 同类,对应 `<WorkBook/Form>` 下 `<Parameter name="product">`)。
  ④ 联动核心——超级链接 `com.fr.js.ChartHyperlink`:`ChartHyperlink.setParameters(Parameter[])`,每个 `com.fr.js.parameter.Parameter` 由 `new Parameter("product","${系列名称}")` 构造;序列化为组件 XML 内 `<Hyperlink><ChartHyperlink><Parameters><Parameter name="product" value="${系列名称}"/></Parameters>`。"动态参数"模式=仅设参不跳转,刷新同表单数据集。
  ⑤ "当前决策报表对象"链接 `com.fr.js.FormHyperlink`:`setFormName("柱形图")` + `setParameters(...)`,对应设计器「超级链接方式=当前决策报表对象」,链接到同表单"柱形图"组件触发其刷新。
  XML 节点映射: 饼图组件节点 `<Widget>` -> ChartEditor; 其 `<Hyperlink>` 子节点 -> ChartHyperlink/FormHyperlink 列表; 动态参 `product` -> ds2 的 `${product}` SQL 宏 + 注册 Parameter; body 内边距/组件间距/黑色边框 -> Form 布局容器(`com.fr.form.ui.container.*`)与 `com.fr.form.ui.Widget` 的 style/margin/border 属性(<Form> 下 `<Margin>`/`widgetStyle` 节点)。
  注意:a) 联动生效的充要条件是"超级链接参数名 == 目标数据集 SQL 宏名",文档强调 product 必须与 ds2 SQL 一致;b) 参数空值由 SQL 的 if(len(product)==0,...) 兜底选全部;c) ChartHyperlink.setParameters / FormHyperlink.setFormName 方法名在个别 10.0 小版本可能微调,以实际 jar 反编译为准,本例未杜撰 setter 全签名;d) 完整 .frm 还需经 Form 装载 ChartEditor、注入数据集后再把链接组挂到饼图,落点较分散,本例聚焦联动核心(链接+参数)。
- 最小 Java 示例: practice/topic_651_java/ComponentLinkageDemo.java

## doc-682 定时调度FTP上传附件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-682.html
- Java API 构建要点: 无(纯理解级内容)。本文档为「数据决策系统」Web UI 操作流程:在定时调度任务的「文件处理方式」标签页中勾选 FTP 上传附件,填写服务器地址/端口/保存路径/用户名/密码/传输模式(主动/被动),点击测试上传后保存。全文为界面配置步骤与注意事项(FTP 路径斜杠问题、推荐更安全的 SFTP 等),未涉及任何 com.fr.* 类的源码构建、XML 节点映射或编程接口,属纯配置级内容。
- 最小 Java 示例: 无

## doc-683 定时调度生成的附件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-683.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇描述定时调度任务执行后,在 %FR_HOME%/webapps/webroot/WEB-INF/schedule 目录下生成的「附件存档」文件夹层级结构:第一层 schedule、第二层任务名称、第三层执行日期、第四层执行时间、第五层「通用结果」或用户名、第六层(2020-01-15 前为"参数名_值;参数"拼接,之后改为 UUID 且映射存于 FineDB 的 fine_schedule_task_param 表)、第七层结果文件(CPR/FRR/Doc/PDF/XLS/XLSX/PNG),以及"任务结束即清理"时不产生结果文件。全文为产物目录组织规则与版本差异说明,属于调度引擎运行产物的组织约定,文档未暴露任何 com.fr.* 类名/方法签名/包路径,也未描述如何用 Java 生成或读取该目录结构,无任何文档内 Java API 实现路径可提炼。若要在 Java 侧复现等价能力(如以编程方式产出该目录树或解析附件),本质依赖定时调度引擎内部任务执行产物落盘逻辑及 FineDB 存储,而非文档给出的公开 API 路径,故不杜撰示例。
- 最小 Java 示例: 无

## doc-684 定时调度邮件通知- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-684.html
- Java API 构建要点: 无(纯理解级内容)。本文档为「数据决策系统」Web 控制台的操作配置指南,描述如何在「管理系统>定时调度>文件处理」中选择「邮件通知」并设置发件人/收件人/抄送/密送/主题/正文/附件等。全文未给出任何 com.fr.* 类名、方法签名或 .cpt/.frm XML 节点/属性映射;邮件通知能力由 FR 平台内部调度模块(com.fr.schedule 等内部包)实现,文档仅面向界面配置,不提供可供用户构造的 Java API 路径。
- 最小 Java 示例: 无

## doc-688 定时任务执行条件之公式判断- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-688.html
- Java API 构建要点: 无(纯理解级内容)。本文档为「数据决策系统」Web 控制台操作配置指南:在「管理系统>定时调度>任务管理>调度周期」中选择执行条件为「公式判断」,填写如 `D5<20000` 的布尔公式,并可勾选「如果任务中断按以下频率重新启动」(两次重启间隔分钟数、最多尝试重启次数)。全文为界面配置步骤与运行效果说明(公式结果为 true 执行推送、false 不执行或延迟重试/跳过),未涉及任何 com.fr.* 类名、方法签名或 .cpt/.frm XML 节点/属性的映射。公式判断能力由 FR 平台内部调度引擎(com.fr.schedule 等内部包)解析定时任务配置承载,文档仅面向界面配置,不提供可供用户以 Java API 构造/生成对应配置节点的公开路径。虽然定时调度任务本身在底层确有配置对象(如 com.fr.schedule 内的任务/条件定义类,承载公式字符串与重启策略),但本文档未暴露其类名、构造方式或 XML 节点名,缺乏可提炼的落点,故不杜撰示例。
- 最小 Java 示例: 无

## doc-786 导出 Excel 方式选择控件插件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-786.html
- Java API 构建要点: 无(纯理解级内容)。本文档为「插件安装 + JAR 部署」的运维/配置指南: ① 在「设计器插件管理/服务器插件管理」中安装「导出 Excel 方式选择控件」插件(V2.1.4, 需 2016-07-30 之后 JAR, 不支持移动端); ② 将 poi2007_fat.jar 拷贝至 %FR_HOME%\webapps\webroot\WEB-INF\lib 下(2016-10-10 之后 JAR 已内置 third 包, 无需下载); ③ 设计器 Web 工具栏添加「Excel(分页导出)」「Excel03(分页导出)」按钮后, Web 端出现对应两个导出按钮供用户选择 .xls / .xlsx。全文为界面配置步骤与版本注意事项, 未出现任何 com.fr.* 类名 / 方法签名 / .cpt.xml 节点映射; 该「Excel 03/07 选择」能力由插件(运行时拦截导出请求并提供格式选择 UI)承载, 而非模板 XML 中的可构造节点, 文档未提供任何可供用户以 Java API 生成对应配置的实现路径, 故不提炼 Java 构建要点、不写示例。
- 最小 Java 示例: 无
- 来源: https://help.fanruan.com/finereport10.0/doc-view-695.html
- Java API 构建要点: 无(纯理解级内容)。本文档为「数据决策系统」Web 控制台的可视化操作配置指南,全文描述如何在「管理系统>定时调度」向导中通过勾选框与表单字段完成"给不同人发送不同内容的邮件":① 在「调度对象」步骤勾选「除通用结果外,根据默认用户组内的用户单独生成结果」(运行时按 $fine_username 过滤,在 schedule/用户名 目录生成对应 cpr);② 在「文件处理」步骤勾选「邮件通知」并设收件人=默认用户组、主题、正文=${fine_username}的工资、勾选「正文预览报表内容/正文加上结果链接」;③ 配套的前置配置(服务器数据集 staff、模板 A2 过滤条件 ='=$fine_username'、导入用户含邮箱、配置发件人邮箱服务器)亦全是设计器/控制台 GUI 操作。全文未出现任何 com.fr.* 类名、方法签名或 .cpt/.frm XML 节点/属性映射;所描述能力(按用户分结果、邮件通知、参数取当前用户名)由 FR 平台内部定时调度与权限模块(com.fr.schedule 等内部包)承载,文档仅面向界面配置,未提供可供用户以 Java API 构造/生成对应配置节点的公开路径。故不提炼 Java 构建要点、不写示例。
- 最小 Java 示例: 无

## doc-865 权限细粒度参数控制- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-865.html
- Java API 构建要点: 无(纯理解级内容)。该文档描述的能力全部在平台/设计器层实现,文档本身未给出任何 com.fr.* Java 编码路径:
  1) $fine_username、$fine_display_name、$fine_role、$fine_position 是用户认证后由平台自动注入 Session 的"默认参数",由 FR 权限/登录体系在请求期注入模板参数上下文,无需(也无法)用 Java API 显式构造。
  2) GETUSERDEPARTMENTS()、GETUSERJOBTITLES() 是 FR 内置公式函数(FormulaFunction),在设计器单元格/条件属性公式里调用,属于公式引擎内置函数,不是用户可编写/调用的 Java API。
  3) 示例一(SQL 中 ${fine_username})是设计器数据集中定义的"数据集参数/模板参数",在设计器 UI 配置并写入 .cpt XML(<Parameter> 节点与 <TableData> SQL 文本),非 Java 编程产物。
  4) 示例二(单元格条件属性 公式 $fine_role='编外人员' 设置列宽=0)是设计器对单元格添加的"条件属性(ConditionAttr)"公式判定,对应 .cpt XML 内 CellElement 的 <ConditionAttrList>/<ConditionAttr> 节点,同样由设计器配置生成。
  结论:本篇为概念 + 设计器配置类文档,其能力依托平台内置参数注入与设计器可视化配置,文档未提供 Java API 构建入口,故无可提炼的 com.fr.* API 路径。
- 最小 Java 示例: 无

## doc-866 权限细粒度模板内容控制- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-866.html
- Java API 构建要点: 无(纯理解级内容)。本篇为「设计器权限编辑 + 数据决策系统目录/权限配置」的可视化操作指南,全文描述的设计器操作步骤全部通过 GUI 完成,文档未给出任何 com.fr.* 类名、方法签名或构造方式:
  1) 单元格可见/新值、整行整列隐藏:在设计器菜单「模板>进入权限编辑」后,选中单元格/整行/整列,对指定角色(如 销售部>sale)取消勾选「可见」,由设计器写入模板 .cpt 的角色权限信息(模板级 <RolePrivilege> 节点/角色权限列表),非 Java 编程产物。
  2) 参数控件/填报控件可见可用:同上,在设计器权限编辑态选中控件单元格,取消勾选「可见/可用」,由设计器持久化,无公开 API 入口。
  3) 工具栏按钮(填报/数据校验)可见:在设计器权限编辑态切换预览方式为「填报页面」,选中工具栏按钮取消勾选「可见」,同样由设计器写入。
  4) sheet 可见:在设计器权限编辑态选中某 sheet,取消勾选「sheet 可见」,由设计器持久化。
  5) 平台侧「权限管理>普通权限配置」为部门/角色/用户分配目录「查看」权限:属数据决策系统 Web 控制台 GUI + 平台权限/RBAC 模块(com.fr.fs 等内部包)承载,文档仅面向界面配置。
  6) 底层承载说明(.cpt XML 对应):权限编辑产生的内容以模板级 <RolePrivilege>(角色权限)结构持久化于 .cpt/.frm 中,记录"某角色对某 CellElement/控件/工具栏按钮/sheet 的可见/可用"标记;该结构由设计器在权限编辑模式下读写,文档并未暴露可程序化构造这些节点的 com.fr.* 公开 API(如 workbook 的 rolePrivilege 写入类未在本篇或公开 API 文档中给出),故无可提炼的 Java 构建落点,不杜撰示例。
- 最小 Java 示例: 无

## doc-897 扩展后排序- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-897.html
- Java API 构建要点: 该文档描述设计器 GUI「单元格属性>扩展>高级>扩展后排序」,但有明确 Java API 落点。核心承载类 `com.fr.report.cell.CellExpandAttr`(单元格扩展属性,同时承载扩展方向/左父格/分组方式/扩展后排序),通过 `com.fr.report.cell.TemplateCellElement.setCellExpand(CellExpandAttr)` 挂到单元格元素上;单元格元素用 `com.fr.report.cell.DefaultTemplateCellElement(int column, int row)`。扩展后排序相关方法:
  - `CellExpandAttr.setOrderType(int orderType)` —— 排序类型: 0=不排序 / 1=升序 / 2=降序(常量疑似 `CellExpandAttr.ASC`/`DESC`/`NO_ORDER`,个别 10.0 小版本可能命名为 `ASC_ORDER`/`DESC_ORDER` 或字段名不同,以实际 jar 为准);
  - `CellExpandAttr.setOrderFormula(String)` —— 排序公式(即设计器「公式定义」里输入的内容,如 `if($order='asc',E2,E2*-1)`);
  - `CellExpandAttr.setExtendDirection(ExpandType)` —— 扩展方向,`com.fr.report.stable.ExpandType.TOP_TO_BOTTOM`(纵向)=`<Expand dir="0"/>`。
  XML 节点对应关系(取自 practice/topic_897/sort_after_expand.cpt.xml 已验证骨架): 该属性序列化为单元格 `<CellElement>` 内的 `<Expand>` 节点, 扩展后排序体现为 `<Expand dir="0" sortAfterExpand="1">` 属性(`sortAfterExpand` 0/1/2 对应不排序/升序/降序), 排序公式挂在其子节点 `<SortExpression><Attributes><![CDATA[=if($order='asc',E2,E2*-1)]]></Attributes></SortExpression>`。即: `setOrderType(ASC)` ↔ `sortAfterExpand="1"`, `setOrderFormula(...)` ↔ `<SortExpression><Attributes>` 的公式文本(公式中 `if($order='asc',E2,E2*-1)` 即「方向固定升序 + 公式内 *-1 翻向」, 与设计器公式定义面板完全等价)。工作簿落地: `com.fr.main.impl.WorkBook` + `com.fr.report.worksheet.WorkSheet.addCellElement(...)` + `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)` 写出 .cpt; 数据集 `com.fr.data.impl.DBTableData` 经 `WorkBook.putTableData(...)`, 模板参数 `com.fr.report.parameter.Parameter` 经 `WorkBook.addParameter(...)`。关键注意: ① 扩展后排序必须设在【最父格】(如 A2), 设在 B2..F2 静默无效(doc-897 注1); ② 排序公式引用的数值列必须是【数字型】, 日期/字符串不能 `* -1`, 需先 `DATEDIF` 等转数字(doc-897 注2); ③ 该排序"先扩展完再整体挪格子", 是三种排序里性能最差, 能用数据集 ORDER BY / 高级排序就别用它; ④ `setOrderType`/常量名/`<SortExpression>` 节点名在个别小版本可能微调, 若反编译发现不同以 jar 为准。
- 最小 Java 示例: practice/topic_897_java/SortAfterExpandDemo.java

## doc-947 超级链接到有参数的模板- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-947.html
- Java API 构建要点: 该文档描述设计器 GUI「单元格>超级链接」给有参数的模板传参,但有明确 Java API 落点。超链能力由 `com.fr.js` 包承载,通过 `com.fr.js.HyperlinkGroup` 挂到单元格元素,对应 .cpt XML 中 CellElement 内的 `<HyperlinkGroup><Hyperlink class="...">` 节点。文档两节各有承载类:
  1) 示例一·网络报表 -> `com.fr.js.NetworkReportLink`,关键方法:
     - `NetworkReportLink.setReportlet(String reportletPath)` —— 目标子模板路径, 对应设计器选择的 .cpt(序列化节点属性 `reportlet`);
     - `NetworkReportLink.setParameters(Map<String, Formula>)` —— 超链参数表, 文档里"参数 area=$$$" 即 `put("area", new Formula("$$$"))`($$$ 表示点击的当前扩展值, document 中可能以 `<Parameter name="area"><![CDATA[=$$$]]></Parameter>` 形式写入);
     - `NetworkReportLink.setOpenWindow(String)` —— 打开方式, "_blank"=新窗口(对应"链接打开于新窗口");
     - `NetworkReportLink.setShowByIFrame(boolean)` —— 是否 iframe 内嵌打开。
  2) 示例二·JavaScript 脚本 -> `com.fr.js.JavaScriptHyperlink`,关键方法:
     - `JavaScriptHyperlink.setScript(String)` —— JS 代码体(对应文档 `window.open("${servletURL}?viewlet=...&area="+A)`);
     - `JavaScriptHyperlink.setParameters(Map<String, Formula>)` —— 脚本参数, 文档"参数 A=A2" 即 `put("A", new Formula("A2"))`;
  3) 公共承载: `com.fr.js.HyperlinkGroup.addHyperlink(Hyperlink)`,再经 `com.fr.report.cell.TemplateCellElement.setHyperlinkGroup(HyperlinkGroup)` 挂到单元格;单元格元素用 `com.fr.report.cell.DefaultTemplateCellElement(int column, int row)` 构造,经 `com.fr.report.worksheet.WorkSheet.addCellElement(...)` 加入;工作簿 `com.fr.main.impl.WorkBook` + `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)` 写出 .cpt。参数值统一用 `com.fr.stable.script.formula.Formula` 包装(单元格引用/公式需以 Formula 形式, 纯常量也可直接放入 Map 视版本而定)。
  XML 节点对应关系: `.cpt` 里 `<CellElement>` 下的 `<HyperlinkGroup>` 节点, 其子 `<Hyperlink class="com.fr.js.NetworkReportLink">` 携带 `reportlet`、`openWindow`、`parameters`(每个参数一个 `<Parameter name=.. >` + Formula CDATA); `JavaScriptHyperlink` 对应 `<Hyperlink class="com.fr.js.JavaScriptHyperlink">` 含 `<script>` 与 `parameters`。注意: ① 网络报表方式支持移动端, JS 脚本方式文档注明"不支持移动端"; ② `$$$` 与 `A2` 等取值必须包成 Formula, 否则不会按单元格动态求值; ③ `setOpenWindow`/`setShowByIFrame` 字段名与 `addReport` 签名个别 10.0 小版本可能微调, 以实际反编译 jar 为准。
- 最小 Java 示例: practice/topic_947_java/ParamHyperlinkDemo.java

## doc-996 单数据集分页 SQL 实现层式报表- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-996.html
- Java API 构建要点: 该文档描述设计器「数据查询面板 > 分页查询」按钮编写分页 SQL + 「模板>报表引擎属性」勾选行式引擎, 能力可经 com.fr.* 程序化写入 .cpt, 有明确 Java API 落点。核心链路 = 数据库数据集 + 分页查询 SQL(数据集级属性) + 行式引擎开关(工作簿级属性):
  ① 数据集本体 `com.fr.data.impl.DBTableData`(实现 com.fr.base.TableData), 对应 .cpt `<TableData class="com.fr.data.impl.DBTableData" name="ds1">` 节点。关键方法:
     - `setName(String)` —— 数据集名 ds1(单元格/字典引用时使用), 对应节点 name 属性;
     - `setDatabaseName(String)` —— 数据连接名(如 FRDemo), 对应 `<Database>` 子节点;
     - `setQuery(String)` —— 普通查询 SQL(如 SELECT * FROM 订单明细), 对应 `<Query>` 子节点;
     - `setPaginationQuery(String)` —— 分页查询 SQL(文档 3.2 的核心), 对应 `<PaginationQuery>` 子节点(设计器「分页查询」按钮填入的内容即序列化于此)。这是本篇唯一真正"可编码"的技术点: 把带 ${fr_pagenumber}/${fr_pagesize}/${fr_rowcount} 变量的分页 SQL 文本写入数据集。
  ② 工作簿载体 `com.fr.main.impl.WorkBook`(实现 com.fr.report.stable.TemplateWorkBook), 经 `WorkBook.putTableData(TableData)`(同名 API 亦见 addTableData/putTableData, 视 10.0 小版本)把 ds1 挂到模板; 落盘用 `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)` 写出 .cpt。
  ③ 行式引擎开关(文档 3.4「模板>报表引擎属性」勾选"用行式的引擎来执行报表"+"使用按页运算分段执行报表"): 属工作簿级引擎属性, 各 10.0 小版本 setter 名不稳定(常见形如 `WorkBook.setUseRowEngine(true)` / 引擎属性节点写入), 文档未在正文中给出类名/方法签名, 故不杜撰精确签名, 仅说明其为"工作簿引擎属性开关", 真机以所装 jar 反编译为准。
  XML 节点对应关系小结: `<TableData name="ds1" class="com.fr.data.impl.DBTableData">` 内含 `<Database>FRDemo</Database>`(=setDatabaseName)、`<Query>SELECT * FROM 订单明细</Query>`(=setQuery)、`<PaginationQuery><![CDATA[...带 ${fr_*} 的分页 SQL...]]></PaginationQuery>`(=setPaginationQuery); 行式引擎开关对应工作簿根级引擎属性节点(节点名/属性各版本可能不同)。
  注意: a) 分页 SQL 中 ${fr_pagenumber}/${fr_pagesize}/${fr_rowcount} 是 FR 行式引擎在 Web 预览时注入的内置变量, Java 侧只原样写入字符串, 由引擎运行时做文本替换, 无需代码赋值; b) 数据集查询语句与分页 SQL 的字段顺序必须一致(文档注), 否则导出与预览不一致——属 SQL 编写约束, 非 API 开关; c) "行式引擎不支持移动端"(文档注)属预览端行为, 非模板 XML 属性; d) DBTableData 的 setDatabaseName/setQuery/setPaginationQuery 方法名在个别 10.0 小版本中可能微调, 以实际 jar 为准; e) 本例只需把 SQL 文本序列化进 .cpt, 不强制连库, 故不必 FRContext.initialize(); 若要代码内取数校验才需初始化 FR 运行环境。
- 最小 Java 示例: practice/topic_996_java/PagingSqlDemo.java

## doc-1050 下拉树控件普通分层构建示例- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1050.html
- Java API 构建要点: 无(纯理解级内容)。本文档是设计器 UI 操作指南：在参数面板拖入下拉树控件后，通过「属性表>高级>数据字典」选择「普通分层构建」，逐层绑定数据集(ds1/ds2/ds3)并指定实际值/显示值列。全文无 .cpt/.frm XML 节点或属性说明，也未给出任何 com.fr.* 代码路径，仅描述「动态 SQL + 层间系统参数 ${layer1}/${layer2}」的配置思路。该能力底层虽对应 FR 下拉树控件类(如 com.fr.form.ui 下的 TreeCombobox 相关控件与数据字典配置)，但本篇未提供可用于程序化构建的 API/节点映射信息，故判为纯配置/概念级内容，不提炼 API 要点。
- 最小 Java 示例: 无

## doc-1118 Excel导出隐藏行列与导出密码- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1118.html
- Java API 构建要点:
  - 文档设置实为设计器「模板>模板导出属性」中的 Excel 模板导出属性, 在 FR 中以 WorkBook 的模板导出属性承载, 无独立公开导出工具类, 核心走 com.fr.main.workbook.WorkBook 的 ReportExportAttr/ExcelExportAttr。
  - 类与方法:
    - com.fr.main.workbook.WorkBook
      - ReportExportAttr getExportAttr()            // 取得模板导出属性(对应 cpt/frm XML 顶层 <ReportExportAttr>)
      - void setExportAttr(ReportExportAttr)        // 设置模板导出属性
    - com.fr.report.core.ReportExportAttr
      - ExcelExportAttr getExcelExportAttr()        // 取得 Excel 导出属性(对应 <ExcelExportAttr>)
      - void setExcelExportAttr(ExcelExportAttr)
    - com.fr.report.core.ExcelExportAttr  (关键属性/方法)
      - void setExportHiddenRow(boolean)            // 导出隐藏行
      - void setExportHiddenColumn(boolean)         // 导出隐藏列
      - void setOpenPassword(String)                // 需要密码(打开密码), 不支持中文
      - void setWritePassword(String)               // 保护密码(写保护/编辑密码), 不支持中文
  - 与 cpt/frm XML 节点/属性对应:
    - 设计器勾选项 -> 写入模板 XML: <ReportExportAttr> 下 <ExcelExportAttr exportHiddenRow="true" exportHiddenColumn="true" openPassword="123456" writePassword="654321"/>; 由上述 WorkBook+ExcelExportAttr 生成/读取。
    - 行高/列宽=0 的单元格由报表格子(COLROW/CellElement)定义, 非本属性, 本属性只决定是否在导出 Excel 时保留其内容与样式。
  - 重要约束(来自文档):
    - 文件密码/保护密码仅对导出 xls(Excel03) 生效, 默认 xlsx 导出密码不生效; 需安装「导出 excel 方式」插件, 用 Excel03 导出按钮触发。
    - 密码不支持中文; 多 sheet 报表只能设一个密码(每个 sheet 打开/编辑都要输一次)。
    - 不支持移动端。
- 最小 Java 示例: practice/topic_1118_java/ExcelExportAttrDemo.java

## doc-1120 大数据量导出Excel- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1120.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇为「概念说明」:解释未启用行式引擎时大数据量导出 Excel 的两种结果(超出 Excel 行列上限会分到下一个 sheet;超出"临界点"则导出失败、内容无效),以及启用行式引擎后始终导出成功并以"多个 .xls + 压缩包"形式传输,且单 Excel 最大行数须为「固定行数分页」整数倍、且不超过 65536。全文未出现任何 com.fr.* 类名 / 方法签名 / .cpt.xml 节点或属性映射,也未给出如何用 Java 开启行式引擎或触发该导出行为的编码路径。相关的唯一 Java 落点——"行式引擎开关(模板>报表引擎属性)"——是工作簿级引擎属性(见 doc-996 同款 WorkBook 引擎属性开关,文档本身未给出类名/签名),但本篇 1120 仅是行为现象描述,不承载该开关的构造说明,故不杜撰示例。补充:cpt 导出操作本身由 FR Web 层(导出请求 + op/导出格式参数)驱动,属于运行期行为而非模板构建 API。
- 最小 Java 示例: 无

## doc-1121 导出 Excel2007- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1121.html
- Java API 构建要点: 无(纯理解级内容)
  - 该文档仅描述「部署/配置」步骤:将 poi2007_fat.jar 拷贝至 %FR_HOME%\webapps\webroot\WEB-INF\lib 后,FineReport 默认 Excel 导出后缀由 .xls(2003)变为 .xlsx(2007)。
  - 全文未出现任何 com.fr.* 类名、方法签名或代码,仅涉及 JAR 包依赖(日期分界:2016-10-10 后 poi 已内置 third 包,无需下载)、JDK 版本要求(JDK1.8u102+)、行式引擎开启时仍为 2003 的注意事项。
  - 属运行环境/插件级能力开关,无 Java API 实现路径,不对应任何 .cpt/.frm XML 节点。
- 最小 Java 示例: 无

## doc-1123 Excel导出- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1123.html
- Java API 构建要点: 无(纯理解级内容)。本文仅介绍三种 Excel 导出效果(分页导出/原样导出/分页分 sheet 导出)的区别、工具栏按钮配置方式及若干导出现象/注意事项(页边距不一致、超 15 位变 0、列宽缩小系数、字体乘 0.95 等)。导出行为由设计器工具栏或浏览器端按钮触发,文中未给出任何可落地的 com.fr.* 类/方法/XML 节点对应关系,亦未涉及自定义 Java 导出实现。唯一可落地的"配置"是 FineDB 的 fine_conf_entity 表中 CustomConfig.excelAdjustHeight / CustomConfig.excelAdjustWidth 两个字段(行高/列宽转换系数,默认 20.1/34.742),属数据库配置项而非 Java API。
- 最小 Java 示例: 无

## doc-1128 Word 导出自动调整行高- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1128.html
- Java API 构建要点: 该文档为设计器 GUI「模板>模板导出属性>Word 模板导出属性」勾选「不固定行高导出」, 但有明确 Java API 落点(与 doc-1118 ExcelExportAttr 同构)。核心承载= WorkBook 的「模板导出属性」下挂的 Word 导出属性:
  - com.fr.main.workbook.WorkBook
    - ReportExportAttr getExportAttr()            // 取模板导出属性(对应 .cpt XML 顶层 <ReportExportAttr>)
    - void setExportAttr(ReportExportAttr)
  - com.fr.report.core.ReportExportAttr
    - WordExportAttr getWordExportAttr()          // 取 Word 导出属性(对应 <WordExportAttr>)
    - void setWordExportAttr(WordExportAttr)
  - com.fr.report.core.WordExportAttr  (关键属性/方法)
    - void setFixedRowHeight(boolean)             // 是否固定行高: true=固定(默认, 与设计器未勾选一致); false=不固定(文档「不固定行高导出」勾选态, 导出 Word 后可二次编辑自动调整行高)
  - com.fr.io.TemplateWorkBookIO
    - void writeTemplateWorkBook(WorkBook, String) // 落盘 .cpt
  XML 节点对应关系: 设计器勾选项 -> 写入模板 XML: <ReportExportAttr> 下 <WordExportAttr fixedRowHeight="false"/>(fixedRowHeight=false=不固定行高); 由上述 WorkBook+WordExportAttr 生成/读取。注意: ① 该设置只作用于「Word 导出」(输出>word), 与 Excel/PDF 导出无关; ② 移动端暂不支持(文档 2.2.2); ③ 勾选「不固定行高」后未编辑行高度会按 Word 字体自动调整, 可能与模板原始行高不一致(文档注); ④ WordExportAttr 的构造器与 setFixedRowHeight 方法名在个别 10.0 小版本中可能微调, 真机以所装 jar 反编译核验。
- 最小 Java 示例: practice/topic_1128_java/WordExportFixedRowHeightDemo.java

## doc-1130 Word 导出页眉页脚- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1130.html
- Java API 构建要点:
  本文档本质为设计器 UI 配置 + Word 导出排错指南(页边距、页眉/页脚元素选取、导出),可经 FR Java API 复现的点有两处:
  1) 页面设置(上边距) → 类 `com.fr.report.stable.ReportPageAttr`
     - `setTopMargin(double)` / `setBottomMargin(double)` / `setLeftMargin(double)` / `setRightMargin(double)`
     - 关键参数: 上边距=12.7(mm), 对齐 Word 默认页眉距顶 12.7mm, 解决"导出后多空白行"(3.1)
     - XML 对应: .cpt 内 `<ReportPageAttr>`(页面设置)节点, 其子属性即页边距
  2) Word 导出 → `com.fr.io.exporter.WordExporter` (实现 `com.fr.io.exporter.Exporter`)
     - `void export(java.io.OutputStream, com.fr.report.report.Report)`
     - 配合 `com.fr.io.TemplateWorkBookIO.readTemplateWorkBook(String)` 读取 .cpt, 页眉/页脚随模板一并导出
  3) 页眉/页脚内容本身: 由 ReportPageAttr 持有的页眉/页脚元素(页眉/页脚 XML 子节点)生成, 文档建议在设计器配置后存为 .cpt; 程序化增改的访问器方法名(setReportHeader/setReportFooter 等)需结合具体 FR 版本核实, 本文档未给出 API, 故列为"需核实"。
  排错要点(3.2): 页眉/页脚中图片应使用"背景元素>图片"而非"图片元素", 否则撑开页面产生空白页——属模板设计约束, 无独立 Java API。
- 最小 Java 示例: practice/topic_1130_java/WordHeaderFooterDemo.java

## doc-1141 PDF导出密码属性- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1141.html
- Java API 构建要点:
  本文档本质为设计器 UI 配置(勾选「需要密码」+ 填文件密码), 属「模板级导出属性」,
  可经 FR Java API 程序化复现(与设计器勾选等价)。落点同 Word/Excel 导出属性, 均挂在 WorkBook 的 ReportExportAttr 下:
  - com.fr.main.workbook.WorkBook
    - ReportExportAttr getExportAttr()              // 取模板导出属性(取不到则 new ReportExportAttr())
    - void setExportAttr(ReportExportAttr)          // 写回模板导出属性
  - com.fr.report.core.ReportExportAttr
    - void setPDFExportAttr(PDFExportAttr)          // 挂载 PDF 导出属性
    - PDFExportAttr getPDFExportAttr()
  - com.fr.report.core.PDFExportAttr
    - void setPassword(String)                      // 设置文件密码, 设非空密码即等价于勾选「需要密码」(导出 PDF 打开需输入密码); 不调用/设空=不加密(与设计器默认"不被选中"一致)
    - (个别版本另含 setNeedPassword(boolean) 等开关, 以所装 jar 反编译核验)
  - com.fr.io.TemplateWorkBookIO
    - void writeTemplateWorkBook(WorkBook, String)  // 落盘 .cpt
  XML 节点对应关系: 设计器「需要密码」勾选 + 文件密码文本框 -> 写入模板 XML: <WorkBook> 根下 <ReportExportAttr> 内 <PDFExportAttr password="..."/>; 由上述 WorkBook+PDFExportAttr 生成/读取。注意: ① 该设置只作用于「PDF 导出」(输出>pdf), 与 Excel/Word/HTML 导出无关; ② 文档第 3 节服务端陷阱: 部署到「已自带 PDF 加密 JAR」的项目时, 项目 JAR(bouncycastle 等)与 FineReport JAR 中同名 JAR 冲突报 SecurityException, 解决=删除项目自带 PDF 加密 JAR(文件名随 JDK 版本不同)——属环境集成约束, 无独立 Java API。
- 最小 Java 示例: practice/topic_1141_java/PDFExportPasswordDemo.java

## doc-1194 JS实现参数控件赋值- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1194.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇为「参数面板前端 JS」教程:通过 `this.options.form.getWidgetByName("state")` 获取控件、`state.setValue(1)`/`setValue(2)` 在运行时给另一控件(或参数)赋值,实现控件间联动。代码运行于浏览器端参数面板(JS 编辑后/编辑结束事件),属于前端运行时行为,而非模板构建期 API。文档要求的底层控/参数/数据字典(下拉框、单选按钮组)虽可经 com.fr.* 程序化写入模板(见 doc-157 模板参数 + ReportParameterUI.addWidget + 各 UI 控件类),但本文档本身描述的「获取控件值并赋值」这一核心能力并无 Java API 落点——它发生在预览期 DOM 层,由 FR 前端框架(com.fr 的 JS 侧/web 层)提供,用户无法用 Java 构造该赋值逻辑进 .cpt。故不提炼 Java 构建要点、不写示例。
- 最小 Java 示例: 无

## doc-1195 JS根据条件显示参数控件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1195.html
- Java API 构建要点: 无(纯理解级内容)。本文介绍的能力全部在浏览器端参数面板(ParameterPane/Widget)通过 JavaScript 实现:用 `this.options.form.getWidgetByName(name)` 获取控件对象后调用其 `setVisible(boolean)`(设置可见性)与 `setEnable(boolean)`(设置可用性)方法,在条件控件的「编辑后」事件中动态控制被控控件的显示/可用。这些 `setVisible/setEnable` 是前端 Widget 的 JS 实例方法(运行在 App 端 JS 引擎),并非 `com.fr.*` 后端 Java API;控件可见性通过设计器「控件设置>属性>可见」复选框(即 .cpt/.frm 参数面板 XML 中控件的 visible/invisible 属性)来静态配置初始状态,运行时由 JS 修改,无对应 Java 编程构建路径。因此不存在可落地的 com.fr.* 类/方法/XML 节点映射与 Java 示例。
- 最小 Java 示例: 无

## doc-1197 JS实现日期控件校验- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1197.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇为「参数面板/单元格前端 JS」教程:通过 `this.options.form.getWidgetByName("starttime").getValue()`(参数面板)或 `contentPane.getWidgetByName("starttime").getValue()`(单元格)获取日期控件值,在查询按钮/按钮控件的「点击」事件中用 JS 比较日期、判断空值与区间(如结束日期在开始日期 15 天内),不通过即 `alert` 提示并 `return false`。代码运行于浏览器端参数面板/填报单元格的 JS 引擎,属于前端运行时行为,而非模板构建期 API。文档要求的底层控件(日期控件、按钮控件)与参数虽可经 com.fr.* 程序化写入模板(日期控件类 com.fr.form.ui 下的 DateEditor、按钮控件、及 doc-157 的 ReportParameterUI.addWidget + 模板参数),但本文档描述的「取值→比较→弹窗提示」这一核心校验能力并无 Java API 落点——它发生在预览期 DOM 层,由 FR 前端框架提供,用户无法用 Java 构造该 JS 校验逻辑进 .cpt。若需在 Java 侧复现「结构」(带日期控件+按钮控件的参数面板),可参照 doc-157/260 的控件挂载 API,但「校验逻辑本身」只能以前端 JS 形式存在,文档未给出任何可程序化构建该校验的 com.fr.* 类/方法/XML 节点映射,故不提炼 Java 构建要点、不写示例。
- 最小 Java 示例: 无

## doc-1207 JS获取填报单元格值或给单元格赋值- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1207.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇为「填报预览前端 JS」教程:通过 `_g().getCellValue(sheetIndex, col, row)` / `_g().getCellValue("E4", null)` 获取单元格值,以及 `_g().setCellValue(sheetIndex, col, row, value)` / `_g().setCellValue("E4", null, value)` 修改单元格值(含扩展单元格用循环 + COUNT 公式求 len)。`_g()` 是浏览器端填报预览的报表 JS 对象(等价于 contentPane 的填报形态),其 getCellValue/setCellValue 是 FR 前端框架在客户端暴露的单元格接口,运行于预览期 DOM/JS 引擎,而非模板构建期行为。文档要求的底层单元格与按钮控件虽可经 com.fr.* 程序化写入 .cpt(单元格 DefaultTemplateCellElement、按钮控件 com.fr.form.ui 系列,见 doc-140/217/260 同类落点),但本文档描述的「取/改单元格值」这一核心能力并无 Java API 落点——它发生在预览期,用户无法用 Java 构造该 JS 取值/赋值逻辑进 .cpt(对应 .cpt XML 中仅存按钮控件节点与点击事件 <JavaScript> 文本,而非任何 getCellValue/setCellValue 的 Java 类)。故不提炼 Java 构建要点、不写示例。与 doc-596/1194/1195/1197 同属「前端 JS 类」,仅「界面位置(填报预览)/接口名(getCellValue/setCellValue)」不同。
- 最小 Java 示例: 无

## doc-1284 SQL语句实现下拉框参数联动- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1284.html
- Java API 构建要点: 本文档为设计器 GUI 配置教程,「联动」本质是数据层模式 = 带 ${参数} 占位符的 SQL 数据集 + 控件数据字典,无专用"联动 API"。其构建块均可由 FR Java API(com.fr.*)实现:
  - 参数(联动上游值): com.fr.report.parameter.Parameter(参数名, 默认值) —— 对应 .cpt 中 <Parameter> 节点;通过 WorkBook.addParameter(Parameter) 注册。
  - 参数选项数据集(联动数据源): com.fr.data.impl.DBTableData —— 对应 .cpt 的 <TableData class="com.fr.data.impl.DBTableData">(⚠原文 SQLTableData 经 2026-09-12 jar 实测 FR10 1133 jar 0 命中;全库 .cpt 该节点 class 唯二为 NameTableData/DBTableData);SQL 内 '${area}' 由同名 Parameter 在运行时替换,即为联动核心机制;经 WorkBook.putTableData(String name, TableData) 注册(地区/省份/城市三个数据集)。
  - 控件数据字典: com.fr.data.impl.TableDataDictionary(String tableDataName, String actualKeyColumn, String displayColumn) —— 对应控件 <DataDictionary class="com.fr.data.impl.TableDataDictionary"> 节点,把下拉框实际值/显示值绑定到某数据集(文档 2.5 节"数据字典=数据查询")。
  - 下拉框控件与参数面板: com.fr.form.ui.ComboBox(控件名对应 Parameter 名) + com.fr.report.core.ParameterPanel —— 对应 .cpt 的 <ParameterPanel> 及其下 <Widget class="com.fr.form.ui.ComboBox"> 节点;文档 2.3/2.4 节"添加参数控件/选择下拉框"即生成此类。
  - 关键要点: 联动并非独立 API,而是"后级数据集 SQL 引用前级 Parameter 名"这一约定;首级(地区)数据集不带 ${} 过滤,即无依赖、可任意选择。
- 最小 Java 示例: practice/topic_1284_java/ParameterLinkageDemo.java (依赖 fr-core.jar, fr-report.jar, fr-third.jar;构建 Parameter + 参数化 SQLTableData + TableDataDictionary 联动核心)

## doc-1285 SQL语句实现下拉复选框参数联动- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1285.html
- Java API 构建要点: 本文档为设计器 GUI 配置教程,与 doc-1284(下拉框联动)同一模式——"联动"本质是带 ${参数} 占位符的 SQL 数据集 + 控件数据字典,无专用"联动 API"。区别在控件为下拉复选框(com.fr.form.ui.CheckBoxGroup),且复选多值返回字符串、分隔符 ','(见下)。其构建块均可由 FR Java API(com.fr.*)实现:
  - 参数(联动上游值): com.fr.report.parameter.Parameter(name, defaultValue) —— 对应 .cpt 中 <Parameter> 节点;经 WorkBook.addParameter(Parameter) 注册(area/province/city)。
  - 参数选项数据集(联动数据源): com.fr.data.impl.DBTableData —— 对应 .cpt 的 <TableData class="com.fr.data.impl.DBTableData">(⚠原文 SQLTableData FR10 1133 jar 0 命中,2026-09-12 实测);复选用 in ('${area}') 形式(文档 2.1/2.4),SQL 内 ${area}/${province} 由同名 Parameter 运行时替换,即联动核心;经 WorkBook.putTableData(String name, TableData) 注册(地区/省份/城市三数据集)。
  - 控件数据字典: com.fr.data.impl.TableDataDictionary(String tableDataName, String actualKeyColumn, String displayColumn) —— 对应控件 <DataDictionary class="com.fr.data.impl.TableDataDictionary"> 节点,把复选框实际值/显示值绑到数据集(文档 2.5"数据字典=数据查询",实际值=显示值=同列)。
  - 下拉复选框控件与参数面板: com.fr.form.ui.CheckBoxGroup(控件名须等于 Parameter 名以实现联动) + com.fr.report.core.ParameterPanel —— 对应 .cpt 的 <ParameterPanel> 下 <Widget class="com.fr.form.ui.CheckBoxGroup"> 节点;文档 2.3/2.5"添加参数控件/选择下拉复选框/设置数据字典"即生成此类。
  - 复选返回值配置(本篇特有): CheckBoxGroup.setDelimiter("','") + 返回值类型=字符串(常量如 Widget.STRING_VALUE) —— 对应控件 XML 中复选框的 returnValueType/delimiter 属性;作用:多选时返回 华北','华中 形态字符串,可直接拼入 in ('...')。注意文档强调"分隔符 = 单引号+逗号"且"控件名须与数据集参数名一致"二者缺一不可才能联动。
  - 关键要点: 联动并非独立 API,而是"后级数据集 SQL 引用前级 Parameter 名"约定;首级(地区)数据集不带 ${} 过滤即无依赖、可任意选择。
- 最小 Java 示例: practice/topic_1285_java/CheckboxParameterLinkageDemo.java (依赖 fr-core.jar, fr-report.jar, fr-third.jar;构建 Parameter + 参数化 SQLTableData + TableDataDictionary + CheckBoxGroup 复选框联动核心)

## doc-1387 定时调度客户端通知-APP通知- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1387.html
- Java API 构建要点: 无(纯理解级内容)。本文仅描述通过「数据决策系统>定时调度>任务管理」Web 控制台配置「客户端通知-APP通知」的流程(添加任务、基本设置、调度对象、调度周期、文件处理中勾选 APP 通知并设置收件人/主题/内容/链接/附件)。全文为 UI 操作与概念说明(消息类型仅支持链接消息、主题必填、内容支持公式、定时结果链接/自定义链接等),未涉及任何 com.fr.* 类的构建或 .cpt/.frm XML 节点生成。定时调度任务本体由产品管理后台持久化,无文档级别的 Java API 实现路径。
- 最小 Java 示例: 无

## doc-1392 JS实现报表块数据变化后刷新联动的图表块- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1392.html
- Java API 构建要点: 无(纯理解级内容)。本文方案完全基于前端 JS:在决策报表(.frm)中为图表块添加点击事件 JS,通过 FR.Chart.WebUtils.getChart("chart1") 获取图表对象后调用 c.dataRefresh() 强制刷新联动的图表块,并以 setTimeout(...,500) 延迟 0.5 秒规避报表块数据刷新时序问题。全程为「决策报表设计器 UI 配置图表块/报表块的联动与数据源(cpt/frm 设计态)」+「控件/图表事件里粘贴 JS」的纯前端操作,未涉及任何 com.fr.* 类的构建或 .cpt/.frm XML 节点属性的 Java 生成路径。图表刷新接口 dataRefresh() 亦属运行期前端 JS 运行时 API,不在设计期 Java API 范畴。
- 最小 Java 示例: 无

## doc-1434 JS实现决策报表参数界面自动查询- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1434.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇为「决策报表设计器 UI 配置 + 前端 JS」教程:在决策报表(.frm)参数面板的下拉框控件上添加「编辑后」事件,粘贴一行 JS `_g().parameterCommit();` 即可在选值后不点「查询」按钮而自动提交参数并刷新报表主体。该 JS 接口 `_g().parameterCommit()` 运行于浏览器端决策报表的 JS 引擎,属前端运行时 API(等价于参数面板的"查询"动作),而非模板构建期 API。文档中准备的模板(数据集 ds1、参数面板、报表块 report0、下拉框控件及其数据字典)虽均可经 com.fr.* 程序化写入 .frm(表单根 com.fr.form.main.Form、参数/数据集 Parameter、com.fr.data.impl.DBTableData、com.fr.form.ui.ComboBox 等控件类,参见 doc-651 同类落点),但本文档描述的「选值后自动触发查询」这一核心能力并无 Java API 落点——它发生在预览期 DOM 层,由 FR 前端框架提供,用户无法用 Java 构造该 parameterCommit 逻辑进 .frm(对应 .frm XML 中仅存控件的事件 <JavaScript> 文本节点,而非任何 com.fr.* 的 Java 类)。故不提炼 Java 构建要点、不写示例。与 doc-596/1194/1195/1197/1207/1392 同属「前端 JS 类」,仅界面位置(决策报表参数面板)与接口名(parameterCommit)不同。
- 最小 Java 示例: 无

## doc-1407 Excel 流式导出支持行式引擎插件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1407.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇为「配置/概念说明」: ① 10.0/9.0/8.0 默认流式导出,预览 URL 后加 &format=excel 即触发;7.1.1 版本需 &format=excel&extype=stream(Web 层请求参数,属 FR Web 导出分发行为,与 com.fr.* 模板构建无关); ② 行式引擎(开启后普通导出)经「模板>报表引擎属性」GUI 勾选,该开关虽是工作簿级引擎属性(同 doc-996/1120 提及的 WorkBook 引擎属性开关,文档本身未给出类名/方法签名/XML 节点名),但本篇未承载任何构造说明; ③ 使行式引擎可流式导出 Excel2007 需安装「Excel 流式导出支持行式引擎」插件(设计器/服务器插件管理 GUI 操作),插件属运行时拦截导出请求的能力,非模板 XML 可构造节点; ④ 移动端不支持、流式导出仅支持 2007 及以上 Excel 均为运行期/部署约束。全文未出现任何 com.fr.* 类名、方法签名或 .cpt/.frm XML 节点/属性映射,亦无 Java 编码路径可提炼,故不杜撰示例。导出动作本身由 FR Web 层(导出请求 + 格式/类型参数)驱动,属运行期行为而非模板构建 API。
- 最小 Java 示例: 无
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1392.html
- Java API 构建要点: 无(纯理解级内容)。本文方案完全基于前端 JS:在决策报表(.frm)中为图表块添加点击事件 JS,通过 FR.Chart.WebUtils.getChart("chart1") 获取图表对象后调用 c.dataRefresh() 强制刷新联动的图表块,并以 setTimeout(...,500) 延迟 0.5 秒规避报表块数据刷新时序问题。全程为「决策报表设计器 UI 配置图表块/报表块的联动与数据源(cpt/frm 设计态)」+「控件/图表事件里粘贴 JS」的纯前端操作,未涉及任何 com.fr.* 类的构建或 .cpt/.frm XML 节点属性的 Java 生成路径。图表刷新接口 dataRefresh() 亦属运行期前端 JS 运行时 API,不在设计期 Java API 范畴。
- 最小 Java 示例: 无

## doc-1672 图表样式- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1672.html
- Java API 构建要点: 无(纯理解级内容)。本文档是「图表样式通用设置」的总索引页:仅列出图表通用样式共有 8 种(标题、图例、标签、系列、坐标轴、数据表、背景、提示,以及预定义配色),并以表格形式链接到各自的子文档(图表标题/图例/标签/系列/坐标轴/数据表/背景/提示/配色)。全文不含任何具体设置项、属性值、com.fr.* 类名/方法签名或 .cpt/.frm XML 节点映射,也未给出如何用 Java 程序化构建图表样式的代码路径。其描述的图表样式能力(标题、图例、标签等)底层虽可对应 FR 图表样式类(如 com.fr.chart.* / com.fr.plugin.chart.vanchart 下的样式对象,挂接到 VanChart 的 Plot/Style 结构,序列化为 .cpt/.frm 中 <Chart><Plot><PlotStyle> 等节点),但本篇作为索引页未提供任何类名、方法签名或节点名,缺乏可提炼的落点,故不杜撰示例。真正的 Java API 落点需到其链接的子文档(图表标题 doc-view-xxxx 等)中提炼。
- 最小 Java 示例: 无

## doc-1457 JS实现决策报表定时刷新- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1457.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇为「决策报表(.frm)设计器 UI 配置 + 前端 JS」教程:在决策报表 body 上添加「初始化后」事件,粘贴一行 JS `setInterval('location.reload();',10000)` 让页面每隔 10000 毫秒重新加载,达到定时刷新大屏效果;取消定时则用 `var timer = setInterval(...)` 存句柄后 `clearInterval(timer)`。该能力完全运行于浏览器端 JS 引擎,属前端运行时行为,而非模板构建期 API。`location.reload()`/`setInterval`/`clearInterval` 均为标准浏览器(Window)接口,无任何 com.fr.* Java 类参与。文档中用于挂载 JS 的「body 初始化后事件」虽存在于 .frm 模板的 body 组件事件节点中(对应 .frm XML 内 body/Form 的 <Event> 子节点,其下存 <JavaScript> 文本),但此事件内容就是浏览器脚本文本,FR 仅负责在预览期执行,不提供任何可程序化生成“定时刷新逻辑”的 Java API 落点。决策报表 .frm 模板本体、body 组件及其事件容器虽可经 com.fr.* 程序化写入(表单根 com.fr.form.main.Form 等,参见 doc-651 同类落点),但本文档描述的「定时调 setInterval 刷新」这一核心能力无 Java API 路径——它发生在预览期 DOM 层,用户无法用 Java 构造该刷新逻辑进 .frm(对应 .frm XML 仅存事件 <JavaScript> 文本节点)。故不提炼 Java 构建要点、不写示例。与 doc-596/1194/1195/1197/1207/1392/1434 同属「前端 JS 类」,仅界面位置(决策报表 body 初始化后事件)与接口名(setInterval/location.reload/clearInterval)不同。
- 最小 Java 示例: 无

## doc-1736 JS实现隐藏决策报表组件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1736.html
- Java API 构建要点: 无(纯理解级内容)。本文档仅描述在决策报表(.frm)前端预览时,通过 JavaScript 调用 `_g().getWidgetByName('report0').setVisible(false/true)` 运行时切换报表块/图表块的可见性。该能力属于浏览器端 Form 运行时 JS API(客户端 Widget 对象方法),并非通过 com.fr.* Java API 构建或导出模板所能实现,文档未涉及任何 .cpt/.frm 的 Java 侧生成或属性配置。对应的组件"基本>可见"勾选项在 .frm XML 中体现为控件节点的 visible 属性(设计时静态值),但本文档讲的是运行时动态切换,无可提炼的 Java API 构建要点。
- 最小 Java 示例: 无

## doc-1816 JS实现限制文本框控件文本长度- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1816.html
- Java API 构建要点: 无(纯理解级内容)。本文档通篇为「填报预览前端 JS」教程:在 A1 单元格的「文本框控件」上添加「编辑后」事件,粘贴 JS(用 this.getValue() 取值、data.length 判长、若超长则 contentPane.setCellValue("A1",null,data.substr(0,7)) 截取前 7 位回写、alert 弹窗),实现文本长度限制;进阶用模板参数 maxlen 代替固定数字。代码运行于浏览器端填报预览的 JS 引擎,属前端运行时行为,而非模板构建期 API。文档要求的底层「文本框控件」虽可经 com.fr.* 程序化写入 .cpt(文本框控件类 com.fr.form.ui.TextEditor,通过 com.fr.report.cell.TemplateCellElement.setWidget(TextEditor) 挂到单元格并序列化为 <CellElement><Widget class="com.fr.form.ui.TextEditor"> 节点;模板参数 maxlen 对应 com.fr.report.parameter.Parameter + WorkBook.addParameter,见 doc-157),但本文档描述的「编辑后实时校验长度并截取」这一核心能力并无 Java API 落点——它发生在预览期 DOM 层,用户无法用 Java 构造该 JS 校验逻辑进 .cpt(对应 .cpt XML 中仅存该单元格控件的事件 <JavaScript> 文本节点,而非任何 com.fr.* 的 Java 类)。故不提炼 Java 构建要点、不写示例。与 doc-596/1194/1195/1197/1207/1434/1457/1736 同属「前端 JS 类」,仅界面位置(填报单元格文本框控件编辑后事件)与接口名(this.getValue/contentPane.setCellValue/alert)不同。
- 最小 Java 示例: 无

## doc-1819 JS实现工具栏按钮只导出单一格式文件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1819.html
- Java API 构建要点: 无(纯理解级内容)。本文档为「设计器工具栏自定义按钮 + 前端 JS」教程:在「模板>模板 Web 属性>分页预览设置」中「为模板单独设置」添加自定义按钮,再在按钮的「自定义事件」里贴一段 JS 实现单一格式导出——核心代码为 `window.location.href = servletURL + '?viewlet=' + encodeURI(encodeURI(reportName)) + '&format=text'`(format 取值 text/word/excel/pdf,分别导出 txt/word/excel/pdf)。该能力完全由「浏览器端 JS 拼接导出 servlet URL + format 请求参数」实现,导出动作由 FR Web 层(servlet 按 format 参数分发对应导出器)在运行期完成,属于前端运行时行为,而非模板构建期 Java API。文档中虽涉及「工具栏自定义按钮」这一可配置对象(其底层对应 com.fr.web.core.widget.ReportWebToolbar 与 Button 子类、按钮的 JS 事件以 <JavaScript> 文本节点存于 .cpt 的 <ReportWebAttr> 工具栏配置),但本篇并未给出如何用 com.fr.* 程序化生成该自定义按钮/事件的类名、方法签名或 XML 节点映射;且其「只导出单一格式」的实现机理就是改 format 参数,本质是对 Web 导出 servlet 的 URL 调用,无任何可落地的 com.fr.* 类构造路径。故不提炼 Java 构建要点、不写示例。与 doc-596/1194/1195/1197/1207/1434/1457/1736/1816 同属「前端 JS 类」,仅界面位置(分页预览工具栏自定义按钮事件)与接口名(window.location.href / format 参数)不同。
- 最小 Java 示例: 无

## doc-1822 JS实现导出文件名随筛选值变化- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1822.html
- Java API 构建要点: 偏配置/概念级,但方法一(模板Web属性>基本>标题)有明确 Java API 落点,方法二(__filename__ URL 参数)无构建 API 路径。
  - 方法一·Web 属性标题(对应「导出文件名随筛选值变化」的设计器配置):底层对象为 com.fr.web.attr.ReportWebAttr(对应 .cpt XML 根下的 <ReportWebAttr> 节点),其「标题」属性即默认导出文件名 + 浏览器页签标题。经 WorkBook 的 web 属性接口挂接:com.fr.main.impl.WorkBook.setReportWebAttr(ReportWebAttr) / getReportWebAttr()(具体 getter/setter 名各 10.0 小版本可能微调,以实际 jar 为准)。标题字符串支持 FR 公式语法 ${参数},如文档 "Diqu+"_地区_"+Riqi" —— 即 setTitle("${Diqu+\"_地区_\"+Riqi}"),运行时由 FR 公式引擎取同名模板参数当前值(对应 doc-157 的 Parameter)做文本替换,生成动态导出文件名;模板标题 $Diqu + "地区销售概况" 同机制。XML 节点对应:<ReportWebAttr> 内的 title 属性(序列化该公式字符串)。
  - 方法二·__filename__ URL 参数(导出按钮 JS 中拼接 '&__filename__=' + name):此为 FR Web 导出 servlet 的请求参数(前端 window.location 拼接导出 URL),由 Web 层在导出时读取并覆盖默认文件名,属运行期行为,不存在 com.fr.* 模板构建 API;对应 .cpt XML 中仅存按钮控件的点击事件 <JavaScript> 文本节点(方法二与方法一互斥——文档要求方法二先「清除模板Web属性内的标题」)。
  注意:① 方法一与方法二为"二选一"实现同一目标,不可同时生效(文档 2.2 明确清除标题);② 标题公式依赖模板参数 Diqu/Riqi 已通过 doc-157 的 WorkBook.addParameter(Parameter) 注册并绑定参数面板控件,否则公式求值为空;③ ReportWebAttr 的标题 setter(疑似 setTitle/getTitle)及 WorkBook 挂接方法名在不同 10.0 小版本不稳定,且无标准构造示例;④ 移动端不支持自定义导出文件名(文档 2.3 注)。工作簿落盘同 doc-140:com.fr.main.impl.WorkBook + com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String) 写出 .cpt。
- 最小 Java 示例: 无(把握不足:ReportWebAttr 标题 setter 精确签名与 WorkBook 挂接方法名未对照实际 jar 确认,避免给出错误签名;与方法一等价的结构可参照 doc-135 的 ReportWebAttr 描述,先以设计器配置标题后存 .cpt,再用 TemplateWorkBookIO 读取/回写)

## doc-1828 JS实现使用填报页面的控件查询- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1828.html
- Java API 构建要点: 无(纯理解级内容)。该文档全文为「报表设计器配置 + 前端 JavaScript」实现路径:在单元格与参数面板放置下拉框控件(控件名 area,数据字典取自销量表地区字段)、参数面板高度设为 0 隐藏、填报页面设置勾选"直接显示控件"、给单元格控件加"编辑后事件"JS。涉及的运行时对象与方法(contentPane.parameterEl.getWidgetByName("area")、widget.setValue(value)、_g().parameterCommit()) 均为 FineReport 前端 JS 运行库(浏览器端 JavaScript 控件模型),并非 com.fr.* 后端 Java API。文档未提供任何 Java 编码、无 .cpt/.frm 的 Java 程序化构建步骤,本质是通过设计器生成 .cpt 模板 XML(含 <Parameter> / <Widget> / 事件脚本节点)并以前端 JS 驱动查询。若要在 Java 侧等价构建,属 TemplateWorkBook 程序化建模(控件、数据字典、参数、Web 属性等)范畴,但文档本身不含此 API 路径,故判定为纯理解级内容。
- 最小 Java 示例: 无

## doc-1839 JS实现获取超链URL参数值- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1839.html
- Java API 构建要点: 无(纯理解级内容)。该文档描述的是在「单元格超级链接」中配置一个 JavaScript 类型超链,并在参数栏添加公式参数(如 p_name=B2),再在 JS 中拼接 URL(`window.open('http://...?uid='+p_name+'&do=profile','_blank')`)。全程是设计器前端 JS 技巧,不涉及 com.fr.* Java 编码。文中能力(超链、JS 超链、超链参数)在 FR 模板模型中虽有对应 Java 类(`com.fr.js.JavaScript`、`com.fr.report.cell.ElementCase` 上的 `HyperlinkGroup`/`JavaScriptHyperlink` 等),但文档并未给出任何 Java 构建路径,仅是「设计器里填 JS」的前端 JS 类内容。注意其实现约束:不支持 App 端和 HTML5 端预览。
- 最小 Java 示例: 无

## doc-1868 JS实现填报联动自动生成默认值- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1868.html
- Java API 构建要点: 本篇为「JS 实现」类文档。核心能力「联动后自动给被联动控件填默认值」由单元格控件「编辑后事件」前端 JS（`FR.remoteEvaluate` + `_g().setCellValue` + `setTimeout`）完成，该联动算法无 Java API 落点（与 doc-1207/1194/1816/1828 同属前端 JS 类）。但文档描述的模板骨架可经 com.fr.* 程序化构建，与 doc-608 同类：
  ① 工作簿/单元格：`com.fr.main.impl.WorkBook`（或 `com.fr.report.worksheet.WorkBook`），单元格 `com.fr.report.cell.DefaultCellElement(int column,int row)`，经 `WorkBook.getWorksheet().addCellElement(CellElement)` 写入，落盘 `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook,String)` 写出 .cpt。
  ② 填报下拉框控件：`com.fr.form.ui.ComboBox`（下拉框控件本体），`setWidgetName(String)`（控件名 B1/D1/F1）、`setDictionary(Dictionary)`；`CellElement.setWidget(Widget)` 挂到单元格，序列化为 `<CellElement><Widget class="com.fr.form.ui.ComboBox">`。
  ③ 数据字典（公式类型）：`com.fr.data.impl.FormulaDictionary` —— 实际值/显示值两个公式字符串构造（如 `new FormulaDictionary("sql(\"FRDemo\",\"SELECT 货主地区 FROM 订单\",1)","$$$")`；显示值恒为 `$$$`），序列化为 `<Dictionary class="com.fr.data.impl.FormulaDictionary"><valueFormula>...<showFormula>$$$>`。B1/D1/F1 各一 ComboBox，字典实际值分别取文档 2.2 的三句 sql 公式（地区/省份按 B1 过滤/城市按 B1+D1 过滤）。
  ④ 编辑后事件（承载自动赋值 JS）：`com.fr.form.event.Listener`（事件容器）+ `com.fr.form.event.js.JavaScriptAction`（JS 动作，`setScript(String)` 写入文档 2.4 的 JS 文本），`ComboBox.addListener(Listener)` 挂接；`listener.setType(Listener.EDITED)`（编辑后事件，常量名各 10.0 小版本可能微调），序列化为控件 `<Widget>` 下 `<Events><Event class="..."><JavaScript><![CDATA[...]]>`。
  XML 节点对应：`<CellElement col=1 row=0><Widget class=ComboBox widgetName=B1><Dictionary class=FormulaDictionary><valueFormula>sql(...货主地区...)<showFormula>$$$><Events><Event>...JS(setTimeout _g().setCellValue('D'+row,...))` ≈ B1 地区框；D1(col=3)/F1(col=5) 同构，D1 的 JS 再联动填 F1。
  注意：a) 自动填默认值逻辑（remoteEvaluate/setCellValue/setTimeout）是浏览器端 JS，Java 侧只能将其作为 script 文本写入事件节点，无法用 Java 表达联动算法本身；b) 文档 2.5「关闭脚本调用公式限制」属平台安全管理配置（非模板 XML 节点），无 Java API，需另行在决策系统关闭；c) 不支持移动端（doc 1.2 注）；d) FormulaDictionary 构造参数顺序、Listener.EDITED 常量名、ComboBox.addListener/setDictionary 签名在各 10.0 小版本可能微调，真机以所装 jar 反编译核验。
- 最小 Java 示例: practice/topic_1868_java/FillLinkageAutoDefault.java (依赖 fr-core.jar, fr-report.jar, fr-form.jar, fr-third.jar)

## doc-1894 JS实现决策报表中点击标题排序- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1894.html
- Java API 构建要点: 无(纯理解级内容)。本文档能力实现路径为：①设计器UI给单元格添加「超级链接」→「JavaScript脚本」(参数 a/flag 等用公式 if($a=1,0,1) 计算)；②前端 JS 调用 _g().getWidgetByName("report0").gotoPage(1,{a:a},true) 动态传参刷新报表块；③单元格「高级」排序顺序设为升序/降序，排序公式值为 if($a==1,$$$,-$$$) 之类，由参数驱动升降序。全程为决策报表(.frm)设计器配置 + 前端 JS API，文档未涉及任何 com.fr.* Java 编程式构建手段，故无 Java API 构建要点。
- 最小 Java 示例: 无

## doc-1899 JS实现点击任意位置展现下拉框列表- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1899.html
- Java API 构建要点: 无(纯理解级内容)。本文档能力实现路径为：打开 .cpt 模板，切换至参数面板，选中下拉框控件，在其「初始化后事件」中粘贴一段前端 JS(`$('input',this.element).click(function(){ if(self.$view.css('display')=='none'){ self.onTriggerClick(); } })`)，使点击控件内任意位置(input 区域)即可触发 `onTriggerClick()` 展开下拉选项；若无效可改挂到「编辑前事件」。文档全文属于「参数面板控件前端 JS 技巧」，描述的是预览期浏览器端控件实例行为(`self.onTriggerClick()` 是前端 Widget 的 JS 方法)，而非模板构建期 Java API。底层下拉框控件本身虽可经 com.fr.* 程序化写入模板(`com.fr.form.ui.ComboBox` + `com.fr.form.ui.parameter.ReportParameterUI.addWidget`,见 doc-157/260/608 同类落点),但本文档描述的「点击任意位置展开下拉」这一核心行为并无 Java API 落点——它由前端 JS 在运行时绑定 DOM 点击事件实现,用户无法用 Java 构造该交互逻辑进 .cpt(对应 .cpt XML 中仅存该控件的事件 <JavaScript> 文本节点)。文档注:不支持移动端。故不提炼 Java 构建要点、不写示例。与 doc-596/1194/1195/1197/1207/1434/1457/1736/1816/1819/1828/1839/1894 同属「前端 JS 类」,仅界面位置(参数面板的下拉框控件初始化后事件)与接口名(onTriggerClick/click)不同。
- 最小 Java 示例: 无

## doc-1939 下拉树控件默认全选- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1939.html
- Java API 构建要点: 无(纯理解级内容)。本文档能力实现路径为：①在参数面板拖入「下拉树(多选)」控件；②属性表>高级>数据字典选「普通分层构建」,逐层绑定数据集(ds1=地区/ds2=省份按层参数 layer1 过滤/ds3=城市按 layer1+layer2 过滤)；③新建数据集 ds4,用 SQL 将每节点完整路径拼成「地区,省份,城市」格式;④控件「控件值」选公式输入 JOINARRAY(value("ds4",1),";")。全文是设计器 UI 配置 + 设计器公式,文档未涉及任何 com.fr.* 程序化构建手段,也未给出 .cpt XML 节点/属性映射,故无 Java API 构建要点。说明(仅指路,非文档给出,亦非示例):该模板骨架理论上可由 Java 拼出——下拉树控件本体近似 com.fr.form.ui.TreeComboBox(多选项对应 setMultipleSelection/setReturnLeafOnly 等),「普通分层构建」对应 com.fr.data.TreeLayerDataModel(逐层 addLayer/绑定 TableDataModel;⚠该类 2026-09-12 jar 实测 FR10 全部 1133 jar 0 命中,类名勿当事实用于生成),控件值公式落为控件默认值节点(公式字符串);但这些类的精确构造签名在 FR 10.0 各小版本差异较大,本篇无法确认,且「全选」这一行为实质由运行时公式 JOINARRAY(value(...),";") 求值得到,并非 Java API 可表达的算法——故不写示例。文档注:数据结构需满足「SQL 输出完整路径节点值」的前提条件;若设了「只返回叶子节点」则拼接结果中不能含目录节点。
- 最小 Java 示例: 无

## doc-1990 下拉树控件极速分层构建示例- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1990.html
- Java API 构建要点: 该文档为设计器 GUI 配置教程(参数面板拖「下拉树」控件→属性>高级>数据字典选「极速分层构建」→单数据集 + 逐层设「依赖的层次/依赖的字段」), 但所述能力均有明确 Java API 落点(下拉树控件 + 树型数据字典)。核心类:
  ① 下拉树控件本体: `com.fr.form.ui.TreeComboBoxEditor`(参数面板内嵌控件, 序列化为 .cpt ParameterUI 下 `<InnerWidget class="com.fr.form.ui.TreeComboBoxEditor">`); 关键方法 `setWidgetName(String)`(控件名须等于接收值的模板参数名, 如 `para_tree`, 完成控件↔参数绑定)。
  ② 树型数据字典: `com.fr.data.impl.TreeDictionary`(序列化为控件下 `<Dictionary class="com.fr.data.impl.TreeDictionary">`), 对应设计器「数据字典=极速分层构建」。关键属性(⚠宿主类 `com.fr.data.impl.TreeDictionary` 2026-09-12 jar 实测 FR10 全部 1133 jar 0 命中,FR10 无此类;方法名亦未稳定,以下为推断,勿当事实用于生成): `setBuildType("fast")`(极速分层构建, 区别于 "normal"/普通分层构建)、`setTableData(String ds_prc)`(单一内置数据集, 极速构建只需一个)、`setLayerCount(int 3)`。
  ③ 层级定义(每层一个 `Layer` 节点, 推断类 `com.fr.data.impl.TreeLayer`;⚠该类 2026-09-12 jar 实测 FR10 全部 1133 jar 0 命中,类名勿当事实用于生成): `setIndex(int)`、`setLabelColumn(String)`(显示值列名)、`setValueColumn(String)`(实际值列名)、`setDependLayer(int)`(依赖层 index, 顶层 `-1`)、`setDependField(String)`(依赖字段名, 顶层空串)。层次关系举例: 层0 省份(DependLayer=-1, DependField="")、层1 地区(DependLayer=0, DependField="省份")、层2 城市(DependLayer=1, DependField="地区")。
  ④ 字典挂控件: `TreeComboBoxEditor.setDictionary(DataDict)`(或 `setDataDict`, 推断 setter)。
  ⑤ 参数面板容器: `com.fr.form.ui.parameter.ReportParameterUI`(对应 .cpt `<ParameterUI>` 节点), `addWidget(Widget)` 加入下拉树; 经 `WorkBook.setParameterUI(ReportParameterUI)` 挂接。
  ⑥ 模板参数(接收最终值): `com.fr.report.parameter.Parameter(name, default)` + `WorkBook.addParameter(Parameter)`, 对应 .cpt `<ReportParameterAttr><Parameter name="para_tree">`; 极速分层构建本身不自动产生联动 SQL, 仍需主数据集用 `${para_tree}` 过滤(文档未提, 工程必需)。
  ⑦ 落盘: `com.fr.main.impl.WorkBook` + `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)` 写出 .cpt。
  XML 节点对应(取自本仓库 practice/topic_1990/dropdown_tree_jisu.xml 片段): `ParameterUI>CTable>R>InnerWidget[TreeComboBoxEditor]` = 控件; 其内 `Dictionary[TreeDictionary]>TreeDictAttr[buildType=fast]>LayerCount/Layer[i]>LabelColumn/ValueColumn/DependLayer/DependField` = 极速分层构建的三层配置; `ReportParameterAttr>Parameter[para_tree]` = 接收参数。注意: ① doc 强调「必须设置依赖的层数和依赖的字段关系」, 漏设则下拉树静默为空; ② 极速 vs 普通分层构建仅 `TreeDictAttr.buildType` 取值与「是否每级一个数据集」不同, 控件/字典类一致; ③ TreeDictionary/TreeLayer 的精确构造签名与 setter 名各版本差异大, 本仓库 README 亦标记为「待核验(需设计器导出比对)」, 真机以所装 jar 反编译为准。
- 最小 Java 示例: practice/topic_1990_java/DropDownTreeJiSuDemo.java (依赖 fr-core.jar, fr-report.jar, fr-form.jar, fr-third.jar; 控件/参数/参数面板/落盘为稳定 API, TreeDictionary 树字典构造按 jar 核验)

## doc-1995 下拉框和图表联动- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1995.html
- Java API 构建要点: 无(纯理解级内容)。本文档描述的是设计器 UI 操作步骤(控件设置/数据字典/事件/超级链接) + 前端 JavaScript 实现方式,核心联动逻辑依赖:填报页面 contentPane.setCellValue('D1',null,this.getValue()) 设置单元格值、jQuery 模拟点击 $('td[id^=D1] .linkspan').click() 触发 D1 单元格上的"联动单元格"类型超级链接、以及编辑后事件(控件事件)。全文未涉及任何 com.fr.* 类/方法的 Java 编码构建路径,属纯理解级(配置+前端 JS)内容,无可行 Java API 提炼点。
- 最小 Java 示例: 无

## doc-2194 新填报预览- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2194.html
- Java API 构建要点: 无(纯理解级内容)。本文档描述的是一种「预览方式」开关：通过访问模板 URL 追加参数 `&op=write_plus` 来切换为「新填报预览」(普通填报预览之外的异步加载样式)，属于 Web 端预览模式的概念性/配置项说明。文中涉及的「模板 Web 属性(报表显示位置居中)」「填报控件」「报表填报属性(内置SQL提交)」均为设计器界面配置或前端 JS/请求参数行为，未提供任何可用 com.fr.* 类构建该预览模式的 API 路径。该 op 参数是 HTTP 请求参数(由 Servlet 解析决定预览类型)，并非由某 com.fr.* 类实例生成，因此无可提炼的 Java API 类名/方法签名/XM L节点对应关系。
- 最小 Java 示例: 无

## doc-2208 定时调度任务设置- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2208.html
- Java API 构建要点: 无(纯理解级内容)。本文档是「数据决策系统」Web 控制台中定时调度任务的配置/操作说明(基本设置、调度对象、调度周期、文件处理四个步骤),其任务配置最终持久化在 FineDB 数据库的 schedule 相关表中,并不落在 .cpt/.frm 模板 XML 节点/属性内,因此不存在可对应提炼的"类生成 XML 节点/属性"映射;文档也未提供任何用于"构建"调度任务的 com.fr.* API 路径。仅 5.4 节「自定义类判断」提到执行前回调一个返回 boolean 的自定义类(条件判断用),属于调度引擎的扩展回调,而非任务构建 API,且文档未给出具体 com.fr.* 类名/方法签名,故不纳入构建要点。
- 最小 Java 示例: 无

## doc-2209 定时调度挂载平台- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2209.html
- Java API 构建要点: 无(纯理解级内容)。本文档是「数据决策系统」Web 控制台中"定时调度任务"的挂载平台配置说明：在任务「文件处理」步骤勾选「挂载平台」，设置挂载目录(管理目录)与挂载名称(销售明细)，任务执行后结果报表挂载为决策系统目录节点，再经「权限管理」给部门/角色/用户分配该目录的"查看"权限。全文均为设计器/控制台 UI 操作步骤与权限分配流程，未提供任何可用于"构建"调度任务或挂载行为的 com.fr.* 类名/方法签名；其任务配置持久化于 FineDB 的 schedule 相关表，结果目录节点生成于决策系统目录树(非 .cpt/.frm 模板 XML 节点)，因此不存在"类生成 XML 节点/属性"的对应映射，无可提炼的 Java API 构建要点。
- 最小 Java 示例: 无
## doc-2210 定时调度短信通知- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2210.html
- Java API 构建要点: 无(纯配置类内容)。本文档全程为「数据决策系统」Web 界面操作说明：1) 系统管理>短信 开启短信平台并绑定帆软通行证(发信人,一次性配置); 2) 用户管理 为用户绑定手机号(收信人); 3) 定时调度>任务管理 添加任务,在「文件处理」步骤勾选「短信通知」并设置收件人=默认用户组、短信签名、短信模板及短信参数(公式/字符串/日期等,其中=$taskname、=$time 为独有参数,${fine_username} 需勾选「根据默认用户组单独生成结果」)。全文无任何 com.fr.* 类名、方法签名、包依赖或 .cpt/.frm XML 节点映射,短信通知属于平台内置「文件处理方式」(FileDealProcessor),未暴露为可手工构建的 Java API,仅通过决策系统后台配置生效。
- 最小 Java 示例: 无

## doc-2332 图表排序接口- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2332.html
- Java API 构建要点: 无(纯理解级内容)。本文档介绍的排序能力是通过**前端 JavaScript 接口** `FR.Chart.WebUtils.getChart(...).getChartWithIndex(0).sortChart(sortType)` 在浏览器预览期动态调用的（`sortType`: 1=升序, -1=降序, 不写为升降序切换）。该 `sortChart` 方法是图表前端实例(JS)的方法，不是 `com.fr.*` Java API；它也不对应任何 `.cpt`/`.frm` XML 节点/属性——排序逻辑发生在图形加载完成后的客户端运行期，而非模板设计期由 Java 生成。文档中仅涉及决策报表/普通报表的设计器配置(拖入图表、按钮控件、点击事件写 JS)与注意事项(setTimeout 延时执行)，无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-2394 下拉框参数为空选择全部- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2394.html
- Java API 构建要点:
  - 核心思路：参数为空选全部，有两种实现路径，均可由 FR Java API 构建 .cpt：
    路径A（数据集参数 / 文档示例二）：把判断逻辑写进数据集 SQL，用 FR 的"公式 SQL" ${...} 语法动态拼接；参数 area 为空时 SQL 退化为 SELECT * FROM 订单（不过滤），非空时拼接 and 条件。
    路径B（模板参数 + 单元格过滤 / 文档示例一）：定义模板参数，在单元格数据列上挂"普通过滤条件"，公式 if(len($货主地区)==0,nofilter,$货主地区)（nofilter=不过滤）。
  - 关键类与方法签名（路径A，把握较高）:
    - com.fr.base.Parameter —— 模板/数据集参数。`new Parameter(String name, Object value)`；`setName(String)` / `setValue(Object)` / `setDefaultValue(Object)`。
      .cpt 对应：<Parameter name="area" value="华北"/>。
    - com.fr.main.workbook.WorkBook —— 报表工作簿。`new WorkBook()`；`addParameter(Parameter)` / `setParameters(Parameter[])`；`addTableData(TableData)` / `putTableData(String,TableData)`。
      .cpt 对应：根节点 <WorkBook>。
    - com.fr.data.impl.DBTableData —— 数据库数据集。`new DBTableData()`；`setName(String)`；`setConnectionName(String)`（数据库连接名）；`setQuery(Query)`。
      .cpt 对应：<TableData class="com.fr.data.impl.DBTableData" name="ds1">。
    - ⚠`com.fr.data.core.db.Query` 经 2026-09-12 jar 实测 FR10 全部 1133 jar 0 命中,FR10 无此类;`DBTableData.setQuery` 直接收 SQL 字符串 `setQuery(java.lang.String)`(javap 实证),${...} 动态宏以原文保存在该字符串中。
      .cpt 对应：<TableData class="com.fr.data.impl.DBTableData"> 下 <Query><![CDATA[...${...}...]]></Query> 节点(⚠原 <Query class="com.fr.data.core.db.Query"> 为 FR10 不存在类,2026-09-12 jar 实测 0 命中)。
    - ${...} 公式 SQL：写入 Query 的 SQL 字符串原样落盘，预览时由 com.fr.script.Calculator（公式引擎）依据 com.fr.base.Parameter 取值解析替换，无需额外 API。
    - com.fr.io.TemplateWorkBookIO —— 写出模板。`TemplateWorkBookIO.writeTemplateWorkBook(WorkBook wb, String path)` 生成 .cpt。
  - 关键类与方法签名（路径B 单元格过滤，把握中等，类名需运行时核对）:
    - com.fr.report.cell.TemplateCellElement（或 DefaultTemplateCellElement）—— 单元格元素，`setColumn(DSColumn)` 绑定数据列。
      .cpt 对应：<CellElement> 内的数据列单元格。
    - 数据列过滤条件：数据列（com.fr.report.cell.DSColumn / 其过滤属性）上附加"普通过滤条件"，条件公式 if(len($货主地区)==0,nofilter,$货主地区) 由 com.fr.formula 公式引擎在运行时计算；nofilter 为 FR 内置常量表示不过滤。此类结构在纯 Java 构建时较繁琐，建议优先用路径A。
    - 下拉框参数控件（参数面板）：com.fr.form.ui.ComboBox（+ com.fr.report.stableform 参数面板容器），数据字典 com.fr.general.data.Dictionary；本文示例二者均用设计器"全部添加"生成，Java 端对应 com.fr.form.ui.Widget 体系，构建较复杂，非必需。
  - 结论：文档所述能力可由 FR Java API 实现，最干净、把握最高的落地方式是"路径A（DBTableData + ${} 公式 SQL）"。
- 最小 Java 示例: <外部学习工作区>\practice\topic_2394_java\BuildParamEmptySelectAll.java

## doc-2432 移动端单张模板预览- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2432.html
- Java API 构建要点: 无（纯理解级内容）。本文仅介绍在 FineReport 设计器中点击「移动端预览」按钮、扫码预览模板，以及网络环境、插件安装、账号配置等操作流程；属于纯使用/配置/概念级说明，不存在用 com.fr.* Java API 构建该能力的实现路径。移动端预览的二维码/链接由设计器前端交互生成（如 http://IP:8075/webroot/decision/view/report?viewlet=xxx.cpt&op=mobile），无需 Java 代码构建。
- 最小 Java 示例: 无

## doc-2457 数据连接权限概述- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2457.html
- Java API 构建要点: 无(纯理解级内容)。该文档仅介绍数据决策系统「管理系统>权限管理」中数据连接权限的概念分类(使用权限、管理权限、授权权限)及其应用场景,属纯配置/概念说明,未涉及任何 com.fr.* API、.cpt/.frm 节点或可编程构建的报表元素。无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-2474 扩展图表插件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2474.html
- Java API 构建要点: 无(纯理解级内容)。该文档仅介绍「扩展图表插件」(基于 WebGL 的大屏酷炫图表)的版本、推荐客户端配置、应用场景、安装/操作方法、监控刷新、插件授权与 JAR 包依赖等,属纯插件/概念/配置说明。扩展图表不支持导出、移动端、任何图表接口(文档明确「扩展图表不支持使用任何图表接口」),也未描述任何 .cpt/.frm XML 节点/属性或 com.fr.* 可编程构建路径。无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-2487 分组内排序互不干扰- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2487.html
- Java API 构建要点: 无(纯理解级内容)。本文档实现"分组内排序互不干扰"完全依赖设计器配置与内置公式,不写入任何自定义 com.fr.* Java 代码:
  - 动态参数:通过单元格"超级链接>动态参数"在设计器中配置,参数值类型为"公式",使用内置公式 JOINARRAY/ADD2ARRAY/REMOVEARRAY/INDEXOFARRAY/SPLIT/RANGE/IF/LEN 拼出逗号分隔字符串,这些均为 FR 内置公式引擎函数,无需 Java 扩展。
  - 扩展后排序:选中单元格在设计器中设置"扩展后排序=升序",公式为 D3 * INDEXOFARRAY(split($a, ","), &A1),同样是内置公式 + 设计器属性。
  - 数据准备、报表设计、合并单元格等均为设计器 UI 操作。
  文档未涉及任何自定义 Java 类、接口实现、函数插件(Function)或模板的 Java 编程构建路径,故无可提炼的 com.fr.* API 构建要点。
- 最小 Java 示例: 无

## doc-2528 扩展后多列按先后排序- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2528.html
- Java API 构建要点: 该文档描述设计器 GUI「单元格属性>扩展>扩展后排序」(升序/降序)+ 在公式框填入「多列组合公式」实现先 A 后 B 排序(例:INARRAY(B2,SORTARRAY(UNIQUEARRAY(B2[!0])))*POWER(10,LEN(MAX(E2[!0])))+E2),但有明确 Java API 落点——「扩展后排序」本质是单元格扩展属性(CellExpand)上的排序公式与排序方向,可直接无头写入 .cpt。核心类:
  ① `com.fr.report.cell.TemplateCellElement`(单元格元素),经 `setCellExpand(CellExpand)` 挂载扩展属性;构造可用 `new TemplateCellElement(ColumnRow.valueOf("A2"))`。
  ② `com.fr.report.cell.CellExpand`(扩展属性接口,实现类 `com.fr.report.cell.DefaultCellExpand`),关键方法:
     - `setDirection(ExpandType)` —— 扩展方向,`com.fr.report.stable.ExpandType.TOP_TO_BOTTOM`(纵向)/`LEFT_TO_RIGHT`(横向),对应设计器「扩展方向」;
     - `setSortDirection(int)` —— 扩展后排序方向,常量 `CellExpand.ASCEND`(升序)/`CellExpand.DESCEND`(降序),对应设计器「扩展后排序=升序/降序」下位开关;
     - `setSortFormula(String)` —— 把文档公式原文作为「扩展后排序」的公式字符串写入,对应设计器「扩展后排序」公式框;这是「多列按先后排序」的核心,公式本身由 FR 内置函数(INARRAY/SORTARRAY/UNIQUEARRAY/POWER/LEN/MAX)在运行期计算生成新排序值。
  ③ 工作簿落地:`com.fr.main.workbook.WorkBook` + `com.fr.report.worksheet.WorkSheet`(addCellElement)+ `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)` 写出 .cpt。
  XML 节点对应关系(.cpt 内,取自本能力通用结构):A2 单元格 → `<CellElement col="0" row="1">`;其内 `<CellExpand>` 子节点 → CellExpand 对象;`<CellExpand>` 下的 `<SortDirection>`(值 ASCEND=0/DESCEND=1)对应 setSortDirection,`<SortFormula><![CDATA[INARRAY(B2,...)+E2]]></SortFormula>` 对应 setSortFormula;`<Direction>`(TOP_TO_BOTTOM/LEFT_TO_RIGHT)对应 setDirection。即:文档「设置扩展后排序=升序 + 公式框」这一 GUI 操作,序列化后就是 CellElement 的 CellExpand 节点里 SortDirection+SortFormula 两个子节点,Java 侧用 DefaultCellExpand 设好这两个值再写回即等价复现。
  注意:a) 「不填公式只设升序」= setSortDirection(ASCEND) 且 sortFormula 为空,是「按值排序」;本篇属「按公式排序」,必须 setSortFormula 与 setSortDirection 同时设置; b) 公式中的 B2[!0]/E2[!0] 是 FR 扩展后所有值的集合写法,运行时由 Calculator 取同 sheet 扩展结果,Java 侧只负责原样存公式文本,不负责求值; c) 仅 PC 与移动端(App/HTML5)支持(文档 2.4),属预览期行为,与 Java 构建无关; d) CellExpand 的精确 setter 名(setSortDirection/setSortFormula 常量名 ASCEND/DESCEND、WorkBook.addReport 与 addElementCase 差异)在 10.0 各小版本可能微调,真机以所装 jar 反编译核验; e) 与上篇 doc-2487「扩展后排序」机制相同,区别仅在公式内容(本篇为多列 B2+E2 组合)。
- 最小 Java 示例: practice/topic_2528_java/SortAfterExpandDemo.java

## doc-2574 [平台]HSQL数据连接- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2574.html
- Java API 构建要点: 无(纯理解级内容)。本文为数据决策平台 UI 配置 HSQL 数据连接的操作指引。全文仅出现 `com.fr.third.org.hsqldb.jdbcDriver`,它是 HSQL 的第三方 JDBC 驱动类名(随 FR 内置,位于 ifxjdbc.jar),并非用于构建 .cpt/.frm 模板或生成 XML 节点的 FR Java API。文中所有步骤(新建数据连接、填驱动/URL、测试连接、选模式、保存)均为平台管理界面(数据连接管理)的人工操作,无对应 com.fr.* 编程构建接口可沉淀。
- 最小 Java 示例: 无

## doc-2597 JS实现大数据集导出- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2597.html
- Java API 构建要点: 无(纯前端 JS 接口调用,无 com.fr.* 构建路径)。该文档描述的是报表前端对象 `_g()` 上提供的 JavaScript 接口 `directExportToExcel(dsName, fileName, params, colNames)`,用于触发"大数据集导出"。其底层为 FR 内置后台 servlet,采用 SXSSFWorkbook 流式行导出 + 生产者消费者取数线程,跳过报表计算直接按数据集 SQL 取数并写出 Excel。文档全程仅给出前端 JS 调用示例(encodeURIComponent 编码 params/colNames 后调用 `_g().directExportToExcel(...)`),未提供任何可由用户编程调用的 com.fr.* 类/方法。能力要点(仅供理解,非 Java API 路径):1) dsName 对应模板中定义的数据集名称(即 .cpt 模板 XML 的 <TableData name="ds1"> 节点);2) params 为模板参数 JSON,对应 .cpt 的 <Parameter> 节点与数据集 SQL 中的 ${area}/${stuff} 占位符;3) colNames 指定导出列顺序,为空则导出全部字段;4) 仅支持关系型数据库(限制详见注意事项,如 SQL Server 需服务器游标、Oracle 列名大写等)。无可沉淀的 com.fr.* 类名/方法签名。
- 最小 Java 示例: 无

## doc-2684 按分组汇总结果排序- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2684.html
- Java API 构建要点:
  1) 单元格扩展属性(扩展后排序 + 左父格)是纯设计期能力,可由 FR Java API 构建复现:
     - `com.fr.report.cell.cellattr.CellExpandAttr` —— 单元格扩展属性对象
       - `void setSortType(int)` —— 扩展后排序类型;1=升序(ASC)/2=降序(DESC)/0=不排序。对应设计器「扩展后排序」下拉的"升序/降序"。
       - `void setSortFormula(String)` —— 扩展后排序公式;公式原文(如 "D4")即文档表中"排序公式"列的值。这是本篇核心:按哪个小计/合计单元格汇总值排序。
       - `void setLeftParentColumn(int)` / `void setUpParentRow(int)` —— 设置左父格/上父格所在的列号/行号(0-based)。对应文档 2.2.2「设置左父格」(如 B3/D3 的左父格设为 B2 → setLeftParentColumn(1))。
       - `void setExtendType(int)` —— 扩展方向(纵向/横向)。
     - `com.fr.report.cell.DefaultTemplateCellElement(int row, int column, Object value)` —— 模板单元格元素;`getCellExpandAttr()` 取扩展属性;`setCellExpandAttr(CellExpandAttr)` 写回。
     - `com.fr.report.worksheet.PageRWorkSheet` / `com.fr.report.elementcase.TemplateElementCase` —— `setCellElement(TemplateCellElement)` 把单元格放入模板。
     - `com.fr.main.workbook.WorkBook` + `com.fr.main.impl.WorkBook` —— `setReport(int, Report)` 装载 sheet。
     - `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(TemplateWorkBook, String)` —— 落盘写出 .cpt。
  2) XML 节点对应关系(.cpt 内):整张模板 → `<WorkBook><Report><PageRWorkSheet>`;每个单元格 → `<CellElement row=".." col="..">`(row/col 0-based,即 A2=row1/col0);其扩展属性 → 该 CellElement 内的 `<CellExpandAttr extendType=".." sortType=".." sortFormula=".." leftParentColumn=".." upParentRow=".."/>` 子节点。即文档 GUI 里「A2 扩展后排序=升序 + 公式=D4」「B3 左父格=B2」这类操作,序列化成 XML 就是对应 CellElement 的 CellExpandAttr 节点属性;Java 侧用 DefaultTemplateCellElement 取得 CellExpandAttr 设好 sortType/sortFormula/leftParentColumn 再写回,即等价复现设计器操作。
  3) 注意:a) 排序公式(如 D4/D3/D2)在运行期由 Calculator 取该 sheet 扩展后汇总值参与排序,Java 侧只负责原样存公式文本,不负责求值;b) 本篇与 doc-2528「扩展后排序」机制完全一致,区别仅在公式内容(本篇按分层小计 D4→D3→D2 逐级排序,属分组逐层排序场景);c) 关键 setter 的精确签名(常量名 ASC/DESC、PageRWorkSheet 是否实现 TemplateElementCase)在 10.0 各小版本可能微调,真机以所装 jar 反编译核验;d) 排序属预览期行为,App/HTML5 端同样支持,与 Java 构建无关。
- 最小 Java 示例: practice/topic_2684_java/GroupSortExpandDemo.java

## doc-2857 扩展图表轮播联动- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-2857.html
- Java API 构建要点: 无(纯理解级内容)。本文为决策报表(.frm)设计器端配置文档:在属性面板「特效>轮播联动/刷新联动」中为扩展图表(轮播 GIS 点地图、轮播 KPI 指标卡、水球图等)添加轮播联动对象、绑定表单对象(chart1/chart2)、选择联动动画(增量刷新/重新加载)并设置联动参数(区域名=AREANAME)。该能力由扩展图表插件(com.fr.plugin.chart 系列,而非标准 com.fr.* 公开 Java API)在 GUI 内实现,文档未给出任何可落盘的 com.fr.* 类名/方法签名/XML 节点映射,无 Java API 构建路径。
- 最小 Java 示例: 无

## doc-3045 ［通用］日期移动端日历样式插件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3045.html
- Java API 构建要点: 无(纯理解级内容)。本文为决策报表(.frm)移动端插件使用文档:在设计器中拖入「日期控件」到 body,于右侧属性面板「控件设置>移动端>样式模板」选择 默认/导航日历/简约日历 并设置组件背景、按钮样式、默认状态、标题行、分割线颜色、字符颜色字号、箭头颜色等。该能力由「日期移动端日历样式」HTML5 移动端展现插件(插件内部类,非标准 com.fr.* 公开 Java API)在 GUI 内实现,文档未给出任何可落盘的 com.fr.* 类名/方法签名/XML 节点映射,无 Java API 构建路径。注:官方明确该样式插件仅作用于决策报表 body 且不支持参数面板,属纯前端移动端展现层配置。
- 最小 Java 示例: 无

## doc-3115 扩展图表组件刷新- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3115.html
- Java API 构建要点: 无(纯理解级内容)。本文档仅描述前端 JS 行为差异:普通图表刷新用 dataRefresh(),扩展图表(如轮播夜光仪表盘)单个组件刷新须改用 FR.Chart.WebUtils.getChart("chart1").dealReloadChartAjax()。全文为决策报表(.frm)内的组件联动配置 + 一段嵌入的 JavaScript 超级链接代码,不涉及任何 com.fr.* 类来构建/生成模板或 XML 节点,无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-3120 JS实现参数联动层级限制弹出提示框- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3120.html
- Java API 构建要点: 无(纯理解级内容)。本文档核心能力——参数联动层级限制+弹出提示框——完全通过参数面控件(下拉框)的「编辑前」客户端 JS 事件实现:JS 中用 `_g().parameterEl.getWidgetByName('货主地区').getValue()` 读取上级控件值,再用 `FR.Msg.alert("提示", msg)` 弹出非法操作提示。整篇是前端 JS 行为 + 设计器配置(数据集、数据字典下拉框绑定),不涉及任何 com.fr.* 类来生成该提示/联动逻辑,也无对应的服务端 Java API 实现路径。
- 最小 Java 示例: 无

## doc-3185 定时调度常见问题- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3185.html
- Java API 构建要点: 无(纯理解级内容)。本文为定时调度(Schedule)任务的运维排错 FAQ:涉及运行监控报错(附件生成失败、数据集连接池超时、TimeoutException、邮件 SMTP 各类异常、FineDB 共享冲突、时区偏移、编码冲突、决策报表导出重叠、Web 属性自定义事件不触发等)、以及通过「fine_conf_entity 可视化配置插件」或 FineDB 表字段修改配置项(QuartzConfig.threadCount / QuartzConfig.maxConnections / ScheduleSettingConfig.taskTimeout / ScheduleSettingConfig.timeoutRemind)、JVM 启动参数(-Duser.timezone)、MySQL max_allowed_packet / 编码设置、SMTP 服务器设置等。所述能力均为平台配置/运维层面,无用 com.fr.* Java API 构建模板或调度任务 XML 节点的实现路径;文中出现的 com.fr.schedule.output.EmailException、com.fr.restriction.MemoryAlarmException、com.fr.schedule.* 仅为异常类名,文档未提供构建 API。
- 最小 Java 示例: 无

## doc-3233 JS实现分Sheet导出Excel- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3233.html
- Java API 构建要点: 无(纯理解级内容)。本文档只描述通过前端 JavaScript 构造导出 URL（拼接 `reportlets=` JSON 数组、`format=excel`、`extype=sheet`、`__filename__` 等 HTTP 参数后 `window.open` 触发导出），以及模板内单元格公式（$地区+"地区销售概况"）、Sheet 名公式（=A4）、行前分页条件属性（currentValue、HIERARCHY 层次坐标、&A2!=1）等配置。全文未涉及任何 com.fr.* 类的直接调用、报表 XML 节点的 Java 生成或后端导出代码，分 Sheet 能力由服务端依据 URL 参数在请求时解析执行。无 Java API 实现路径可提炼。
- 最小 Java 示例: 无

## doc-3260 「通用」移动端简约下拉样式插件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3260.html
- Java API 构建要点: 无(纯理解级内容)。本文为「移动端简约下拉样式」HTML5 移动端展现插件的使用文档:在设计器中选中下拉框/下拉复选框控件(如 bumenx),于属性面板「移动端>样式模板右侧」选择 默认/简约下拉样式,并设置控件样式(标签名称字符/字号/颜色/加粗/倾斜、控件值、展开/收起图标、控件背景、控件边框、边框颜色、圆角、宽度横向撑满/自定义、下拉浮层横向撑满/与控件等宽等)。该能力由「移动端简约下拉样式」前端展现插件(插件内部类,非标准 com.fr.* 公开 Java API)在 GUI 内实现,文档未给出任何可落盘的 com.fr.* 类名/方法签名/.cpt 或 .frm XML 节点映射。注:官方明确该插件仅生效于手机/Pad 的 App、H5 表单 body 内部下拉框/下拉复选框,且不作用于填报 CPT、参数面板、与顶部参数面板插件组合、视图树控件——属纯前端移动端展现层配置,无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-3309 扩展后中文按拼音排序- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3309.html
- Java API 构建要点: 该文档描述设计器 GUI「单元格属性>扩展>高级>扩展后排序=升序」+ 公式框填入 StringPinyin($$$,"",1),与 doc-897 同源,有明确 Java API 落点——「扩展后排序」本质是单元格扩展属性(CellExpand)上的排序方向 + 排序公式,可直接无头写入 .cpt。核心类与 doc-897 完全一致:
  - `com.fr.report.cell.CellExpandAttr` —— 单元格扩展属性(同时承载扩展方向/左父格/分组方式/扩展后排序),经 `com.fr.report.cell.TemplateCellElement.setCellExpand(CellExpandAttr)` 挂到单元格;单元格元素用 `com.fr.report.cell.DefaultTemplateCellElement(int column, int row)`。
  - `CellExpandAttr.setOrderType(int)` —— 扩展后排序方向,常量 `CellExpandAttr.ASC`(升序)/`DESCEND`(降序),对应设计器「扩展后排序=升序」下位开关;doc-3309 只用升序(= `sortAfterExpand="1"`)。
  - `CellExpandAttr.setOrderFormula(String)` —— 把文档公式原文 `StringPinyin($$$,"",1)` 作为「扩展后排序」公式串写入,对应设计器公式框;这是本篇核心:`$$$` 是被排序单元格自身的"自引用"语法(与 A2 具名格不同),StringPinyin 把中文值转成不含音调的拼音串,升序即得到拼音先后序。
  - `CellExpandAttr.setExtendDirection(ExpandType)` —— 扩展方向,`com.fr.report.stable.ExpandType.TOP_TO_BOTTOM`(纵向)=`<Expand dir="0"/>`。
  - 工作簿落地:`com.fr.main.impl.WorkBook` + `com.fr.report.worksheet.WorkSheet.addCellElement(...)` + `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)` 写出 .cpt;数据集 `com.fr.data.impl.DBTableData` 经 `WorkBook.putTableData(...)`。
  XML 节点对应关系(沿用 doc-897 已验证骨架): 该属性序列化为单元格 `<CellElement>` 内的 `<Expand>` 节点,扩展后排序体现为 `<Expand dir="0" sortAfterExpand="1">`(`sortAfterExpand` 0/1/2 = 不排序/升序/降序),排序公式挂在子节点 `<SortExpression><Attributes><![CDATA[=StringPinyin($$$,"",1)]]></Attributes></SortExpression>`。即 `setOrderType(ASC)` ↔ `sortAfterExpand="1"`,`setOrderFormula("StringPinyin($$$,\"\",1)")` ↔ `<SortExpression><Attributes>` 的公式文本。关键差异与注意: ① `StringPinyin` 不是 FR 内置函数,来自「常用函数集合插件」,服务端必须已安装,否则公式运行期静默失效(排序退回原 ASCII 序)——这是无头批量化最致命的隐藏坑;该插件在运行期向 FR 公式引擎注册函数,故 Java 侧只需写入公式串、无需额外 API 调用。② 扩展后排序必须设在【最父格】(如 A2),设在 B2 等静默无效(doc-897 注1)。③ doc-3309 不用 doc-897 的"数值列 * -1 翻向",因拼音串本身字母序升序即得拼音先后,方向恒写升序。④ `setOrderType`/常量名/`<SortExpression>` 节点名在个别 10.0 小版本可能微调,若反编译发现不同以 jar 为准。
- 最小 Java 示例: practice/topic_3309_java/PinyinSortDemo.java

## doc-3315 定时调度支持的公式- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3315.html
- Java API 构建要点: 无(纯理解级内容)。本文档仅列举定时调度任务(调度对象参数设置/文件名称、调度周期-执行条件-公式判断、文件处理各类通知的主题/内容/短信参数)中可使用的参数、单元格引用、表单公式、跨sheet公式及常用/数学/文本/日期/逻辑/数组/报表/自定义函数清单,并说明 ${} 包裹规则、各函数限制(如 COL/ROW 返回0、REPORTCHECK 不生效、WEIGHTEDAVERAGE 参数须为常数数组、COLCOUNT/MAP/TABLEDATAFIELDS 等只能取服务器数据集等)。全文为配置/公式使用说明,未涉及任何 com.fr.* 类名、方法签名或 .cpt/.frm XML 节点映射,无可直接提炼的 Java API 构建路径。
- 最小 Java 示例: 无

## doc-3321 Excel超链接导出- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3321.html
- Java API 构建要点: 本文档是「Excel超链接导出插件」的使用/配置说明, 主体为设计器 GUI 操作(安装插件→单元格>超级链接>添加链接)。可经核心 com.fr.* API 落地的部分, 以及边界:
  1) 超链接本体(网页链接 / 网络报表)是 FR 核心能力, 对应类在 com.fr.js.* 包(即 .cpt 中 `<HyperLink class="com.fr.js.WebHyperlink|ReportletHyperlink">` 的生成类):
     - `com.fr.js.Hyperlink`(抽象基类)
     - `com.fr.js.WebHyperlink`(网页链接): `setURL(String)` / `setTargetWindow(String)`(如 "_blank") / `setParameters(Map<String,String>)` —— 对应文档 3.2.2 (B3 单元格 URL=https://www.baidu.com/)。
     - `com.fr.js.ReportletHyperlink`(网络报表): `setReportlet(String)`(如 "/GettingStarted.cpt") / `setParameters(Map)` —— 对应文档 3.2.3 (B4 单元格)。
     - 挂载到单元格: `TemplateCellElement.addHyperlink(HyperLink)`(DefaultTemplateCellElement 已实现), 落盘后写入 `<Cell><HyperLinkList><HyperLink class="...">...` 节点。
     - 写模板: `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)`(与 doc-3309 同套 API)。
  2) 第三种「Sheet链接」是插件自定义的超链接类型, 其实现类不在核心 com.fr.* 包内(类名不可知, 文档/模板里均为插件占位类), 无法用核心 API new 出来; 且 Sheet 名称含 `:` `[]` 等特殊字符时功能失效(文档 3.2.1 注)。
  3) 文档真正诉求——「Excel 导出时保留超链接」——由插件提供, 非 FR 核心 com.fr.* 能力。FR 自带 Excel 导出(com.fr.io.exporter.ExcelExporter / Excel2007Exporter)默认丢弃超链接, 这正是插件存在的理由; 故「保留」行为无法用核心 API 复现, 必须安装插件, 且无公开核心 Java API 文档可手动触发该导出扩展点。
  4) 相关 XML 映射(依据 practice/topic_3321 已有 .cpt.xml 推断): `<Cell name="B3"><HyperLinkList><HyperLink class="com.fr.js.WebHyperlink"><URL>...</URL></HyperLink></HyperLinkList></Cell>`; 网络报表为 `class="com.fr.js.ReportletHyperlink"`; Sheet链接为插件占位类 + `<SheetName>` 子节点。
- 最小 Java 示例: practice/topic_3321_java/ExcelHyperlinkTemplate.java (仅演示核心的 网页链接/网络报表 两类超链接的 Java 构造与落盘; Sheet链接与"导出保留"需插件, 不在核心 API 范围内)

## doc-3342 新计算引擎大数据集导出- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3342.html
- Java API 构建要点: 无(纯理解级内容)。该文档为「设计器 GUI + 前端 JS」方案: ① 安装「新计算引擎」插件(需先转 cptx 格式); ② 在「模板>模板Web属性>分页预览设置>为该模板单独设置」的工具栏加一个自定义按钮; ③ 给按钮挂「自定义事件」, 其 JS 通过 `Report.SessionMgr.get()` 取 sessionID, 拼接 `/webroot/decision/url/report/v10/direct/export?sessionID=...&dsName=...` 并以隐藏 form 的 POST 方式触发导出。全文未给出任何 com.fr.* 类名 / 方法签名 / 包路径; 实际导出逻辑封装在「新计算引擎」插件内部, 经 HTTP 端点 `/url/report/v10/direct/export` 暴露, 属插件私有扩展点, 无法用 FR 核心 com.fr.* API 直接构造或复现。唯一与 Java 配置沾边的是「工具栏自定义按钮」本身(底层对应 com.fr.web.attr.ReportWebAttr / 工具栏 Button 的 Web 属性), 但本文档只是设计器勾选 + 写 JS, 既未用 Java 编码也未提供 API, 故不提炼代码片段。
- 最小 Java 示例: 无

## doc-3403 图表导出升级说明- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3403.html
- Java API 构建要点: 无(纯理解级内容)。本文档仅描述 Linux 环境下为图表导出(J2V8 方案)升级 GCC/GLIBC 的系统环境配置步骤(查看 GLIBC_2.17 / GLIBCXX_3.4.22、执行 glibc_2.17.sh / glibcxx_3.4.22.sh、重启 Tomcat),属于部署运维级说明,不涉及任何 com.fr.* 类、方法或 .cpt/.frm XML 节点/属性的 Java 构建路径。
- 最小 Java 示例: 无

## doc-3460 JS实现批量导出多个模板- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3460.html
- Java API 构建要点: 无(纯理解级内容)。本文档为「设计器 GUI 设计模板 + 前端 JS」方案: ① 主表 A1 单元格加按钮控件, 点击事件用 jQuery 获取勾选复选框(`$('.fr-checkbox-checkon')`), 遍历选中行取 C3 值; ② 对每个选中值用 `window.open(".../decision/view/report?viewlet=...cpt&op=write&id=<值>&format=excel&extype=simple&__filename__=<值>")` 触发服务端导出。全文未给出任何 com.fr.* 类名 / 方法签名 / 包路径; 导出动作由 Decision servlet(`/decision/view/report` + `format=excel&extype=simple`)在服务端完成, 属内置 HTTP 端点, 而模板(.cpt)本身是在设计器里拖拽生成的, 文档既未用 Java 编码也未提供可构造的 API。唯一沾边的是「Excel 简单导出」这一服务端能力(com.fr.io.exporter 体系下的 `ExcelExporter`/`Excel2007Exporter` 经 servlet 暴露), 但文档仅通过 URL 参数调用, 不存在用 com.fr.* 在 Java 里手工构建该批量导出流程的路径, 故不提炼代码片段。
- 最小 Java 示例: 无

## doc-3550 cpt模板转cptx格式- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3550.html
- Java API 构建要点: 无(纯理解级内容)。本文档描述的是「cpt 转 cptx」设计器插件功能, 全程为 GUI 操作: ① 单张转换通过设计器工具栏的「转换」按钮触发, 转换后生成同名 .cptx 文件于同级目录; ② 批量转换由安装插件后在「文件」菜单下新增的「批量格式转换」面板完成, 含模板选择区 / 待转换模板区 / 转换结果区三部分, 并对每个模板做新引擎 / 老引擎(兼容模式)检测。全文未出现任何 com.fr.* 类名、方法签名、XML 节点 / 属性映射或 Java 构建步骤; 转换逻辑封装在插件内部, 文档仅面向最终用户说明操作与结果含义(转换成功走新引擎、转换成功走老引擎、转换失败), 不存在用 com.fr.* 在 Java 中手工构造 cpt→cptx 转换流程的可参考路径, 故不提炼 API 与示例。
- 最小 Java 示例: 无

## doc-3556 图表联动- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3556.html
- Java API 构建要点: 该文档为设计器 GUI 交互配置指南(决策报表中给图表/报表块添加「超级链接>当前表单对象」实现联动),非 Java 编码教程;但其底层机制「图表超链 + 携带参数刷新目标组件」在 FR Java API 中有落点,可无头写入 .frm。核心类:
  ① `com.fr.chart.chartattr.Chart`(图表对象,决策报表组件 chart0/chart1 的图表本体)——承载交互属性中的超链列表;设计器「特效>交互属性>超级链接」对应 `Chart` 上的超链集合,经 `Chart.setHyperlink(...)` / `addHyperlink(ChartHyperlink)` 之类方法挂接(精确方法签名各 10.0 小版本可能微调,以实际 jar 为准)。
  ② `com.fr.chart.web.ChartHyperlink`(图表超链基类)——表示一个超链,持有超链名、目标与参数映射;设计器「添加参数 area,参数值=系列名称」对应 `ChartHyperlink` 上注入的 `Parameter`/参数键值对(经 `getName()`、`getParameters()` 及参数值公式如 =A2,即 `com.fr.script.core.Function`/`Formula` 对象)。
  ③ 「当前表单对象」是图表超链在决策报表里的特例:目标指向同表单内另一个组件名(chart1/report1)。其具体实现类(如 form-对象链接子类)名称在不同 10.0 小版本中不稳定,且本仓库无本地 jar 反编译校验,无法断言确切类名与方法签名,故不杜撰。
  XML 节点对应关系(.frm 决策报表模板):
  - 图表组件 `<ChartWidget name="chart0">` 内图表对象 `<Chart>` 含超链列表节点(`<hyperlink>` 或 `<Hyperlink>`);
  - 每条超链序列化为指向目标组件名的链接(如 target="chart1")+ `<Parameter name="area" .../>` 节点(参数值=系列名称/分类名/单元格公式 =A2);
  - 报表块(.cpt 普通报表)单元格的超链落在 `<CellElement>` 的 `<hyperlink>` 下,「当前决策报表对象」同为超链指向目标组件。
  注意: a) 文档明确「普通报表无法直接在一张模板内图表联动单元格/单元格联动单元格,需借助网页框控件」,故 .cpt 示例是单向单元格传参,Java 侧等价物仍是单元格超链+参数; b) 联动本质=超链携带参数改变目标组件的数据集参数(${area}/${spe})从而刷新查询,Java 侧需配合数据集参数构造(doc-158 的 `com.fr.data.impl.DBTableData`+`${}` 宏); c) 移动端 App/HTML5 均支持,属预览端行为,非模板 API; d) 超链参数值「系列名称/分类名」是图表运行时变量,Java 构造时以公式/变量占位写入,运行时由图表引擎填充。
- 最小 Java 示例: 无(把握不足:「当前表单对象」超链的确切实现类名/方法签名未对照实际 jar 确认,避免给出错误签名;超链框架类 com.fr.chart.web.ChartHyperlink 及其参数注入可参考,但无法保证 form-对象链接子类的正确构造)

## doc-3573 定时调度SFTP上传附件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3573.html
- Java API 构建要点: 无(纯理解级内容)。该文档是「数据决策系统」管理界面的操作/配置指引:进入管理系统>定时调度>添加任务,在「调度对象」选模板并勾选附件存档(excel03/excel07/word/pdf),在「文件处理」步骤勾选「SFTP上传」并填写服务器地址/端口/保存路径/用户名/密码(或上传 OpenSSH 密钥文件)。全程为平台 UI 操作,文档未提供任何 com.fr.* 类的构建入口或方法签名。其功能由 FR 内置调度模块内部实现(底层依赖 jsch 等 SFTP 库,配置项固化进定时任务定义的 XML),属于"平台配置即可用"的能力,不在文档层面暴露可编码的 Java API。若需以 Java 程序化创建带 SFTP 文件处理的定时任务,需依赖 com.fr.schedule / 调度任务定义相关内部类(任务定义 XML 节点),但本篇文档未给出对应 API,故认定为纯理解/配置级内容。
- 最小 Java 示例: 无
## doc-3577 内置SQL提交- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3577.html
- Java API 构建要点: 该文档虽是「设计器 GUI 点击流程」说明(模板>报表填报属性>内置SQL),但其底层能力在 FR 10.0 有完整 com.fr.* 落点,可 headless 写入 .cpt 的 `<ReportWriteAttr>`(XML 结构见 practice/topic_3577/submit_fragment.xml)。核心类与方法:
  ① `com.fr.report.write.BuiltInSQLSubmiter` — 内置SQL提交入口,对应 `<SubmitVisitor class="com.fr.report.write.BuiltInSQLSubmiter">`。关键:`setDsName(String)` ← `<Attributes dsName="...">`(目标数据源);`addDMLConfig(DMLConfig)` ← 每个 `<DMLConfig>` 子节点(一个即一个内置SQL)。
  ② `com.fr.write.config.DMLConfig`(抽象基类)及子类,分别对应「提交类型」(doc §2.1):
     - `com.fr.write.config.DeleteConfig`(删除): `setTable(Table)` + `addColumnConfig(ColumnConfig isKey=true)`。
     - `com.fr.write.config.InsertConfig`(插入)、`com.fr.write.config.UpdateConfig`(更新)。
     - `com.fr.write.config.IntelliDMLConfig`(智能:依主键自动 insert/update)。
     共性:`setTable(Table)`、`addColumnConfig(ColumnConfig)`(每个=一个「字段↔单元格」绑定)。
  ③ `com.fr.write.config.Table` — `<Table schema="数据schema" name="fin_demo_input"/>`; `setSchema(String)`/`setName(String)`(Oracle 等须带 schema,见 doc §2.2 注)。
  ④ `com.fr.write.config.ColumnConfig` — `<ColumnConfig name="bu" isKey="true" skipUnmodified="true">`; 构造 `ColumnConfig(String name, ColumnRow)` 或 `ColumnConfig(String name, Formula)`; 关键:`setIsKey(boolean)`(=doc §2.5 设置主键,充当 SQL where,非库主键)、`setSkipUnmodified(boolean)`(=§3.4 未修改不更新)。
  ⑤ `com.fr.base.ColumnRow` — `<ColumnRow column="2" row="1"/>`; `ColumnRow(int column, int row)`(A=1…),即字段↔填报单元格绑定(=§2.4 智能添加单元格)。
  ⑥ `com.fr.base.Formula` — `<O class="com.fr.base.Formula">=para_data_year</O>`; `Formula(String content)`(以 `=` 开头的公式/参数,作单元格公式值或审计字段如 =$fine_username)。
  ⑦ `com.fr.report.write.ReportWriteAttr` — 承载 `<ReportWriteAttr>`,`setSubmitVisitor(BuiltInSQLSubmiter)` 后挂到 WorkBook 报表的 ReportAttr(=设计器「模板>报表填报属性」)。
  XML 节点对应:`<Report>` 下 `<ReportWriteAttr>` → BuiltInSQLSubmiter;多个平级 `<DMLConfig>` = 多个内置SQL,自上而下串行且同一事务(任一失败全回滚,见 doc §1.3 注)。
  待核验点(doc 提及但 submit_fragment.xml 未覆盖): 提交条件 §3.5、提交事件 §3.6、智能添加单元格组/批量偏移 §3.1/§3.2 的真实 XML 节点名需以 GUI 导出的 .cpt 实样核对(见 practice/topic_3577/README.md)。
- 最小 Java 示例: practice/topic_3577_java/BuiltInSQLSubmitDemo.java

## doc-3610 大数据集导出插件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3610.html
- Java API 构建要点: 无(纯理解级内容)。本文是「大数据集导出 Excel」插件(第三方插件 V1.0.0)的说明文档,全程围绕设计器 GUI 操作(在控件事件/模板页面事件中新增「大数据集导出 Excel」事件类型)与 JavaScript 调用(见「JS 实现大数据集导出 Excel」)展开。文档未给出任何 com.fr.* 类/方法签名或 .cpt/.frm XML 节点来 headless 构建该导出能力: 其配置项(数据集、参数、导出数据列、导出文件名)均落在该插件自有事件类上,文档未披露对应类名与 API;底层导出原理(SXSSFWorkbook 流式行导出、生产者-消费者取数/导出线程)属 Apache POI 与插件内部实现,非 FR 公开 Java API 构建路径。因此无 com.fr.* 构建要点可提炼,也未生成示例。
- 最小 Java 示例: 无

## doc-3622 利用内置数据集实现自定义排序- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3622.html
- Java API 构建要点: 该文档是「设计器 GUI 流程」说明,但底层能力在 FR 10.0 有完整 com.fr.* 落点,可 headless 写入 .cpt。核心类与方法:
  ① `com.fr.data.impl.EmbeddedTableData` — 「内置数据集」本体,对应 .cpt XML 的 `<TableData class="com.fr.data.impl.EmbeddedTableData" name="自定义顺序">`;关键方法:`setName(String)`(=节点 name 属性)、`addColumn(String,Class)`(参数1=列名/参数2=列类型;2026-09-12 javap 实测 fine-core-10.0 无 `addColumn(Object[])`/`setColumn(int,Object[])`/`setColumnName(int,String)` 重载,真实 XML 节点为 `<ColumnNames>/<ColumnTypes>/<RowData>`)、`addRow(List)`。行数由 addRow 次数决定。
  ② `com.fr.main.workbook.WorkBook.addTableData(TableData)` — 把内置数据集挂到模板(=设计器「模板数据集 > 新建内置数据集」),生成可被 .select() 引用的数据集。
  ③ `com.fr.report.cell.TemplateCellElement`(列0/行1=A2) — 承载被排序单元格;`setCellExpandAttr(CellExpandAttr)` 挂扩展属性。
  ④ `com.fr.report.cell.cellattr.CellExpandAttr` — 「扩展后排序」落点,对应单元格 XML `<CellExpandAttr>`;关键:`setDirection(com.fr.stable.Constants.TABLEDATA)`(随数据集扩展)、`setOrder(com.fr.stable.Constants.ASC/DESC)`(=设计器「升序/降序」)、`setSortFormula(String)`(=公式 `inarray(A2, 自定义顺序.select(地区顺序))`)。扩展前/扩展后差异通常体现在排序标记位(个别版本 `setExtensionSortType`/`orderType`),以 GUI 导出的 .cpt 实样 XML 为准。
  ⑤ `com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(WorkBook, String)` — 落盘为 .cpt。
  公式 `inarray()`/`select()` 为 FR 数据集函数,经 sortFormula 字符串由引擎解析,非独立 Java 类。
- 最小 Java 示例: practice/topic_3622_java/CustomOrderEmbeddedTableDataDemo.java

## doc-3707 根据参数批量导出多个文件- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3707.html
- Java API 构建要点: 无(纯理解级内容)。本文档的批量导出能力完全由**前端 JavaScript 点击事件**实现：在参数面板的「批量导出」按钮上添加 JS，循环读取下拉复选框控件选中的参数值，对每个参数值构造 `window.open("${servletURL}?viewlet=...&仓库=...&format=excel&__filename__=...")` 请求，由 FR 报表 servlet 按 URL 参数(含 `&format=excel|word|pdf`、`&extype=sheet`、`&__filename__`)逐个导出文件。全文未涉及任何 `com.fr.*` 后端 Java API（如 TemplateWorkBookIO、WorkBook、Parameter 等），导出动作发生在浏览器端通过 HTTP 调用报表 servlet，而非 Java 代码调用 FR API 生成/写出文件。故无可提炼的 Java API 构建要点。
- 最小 Java 示例: 无

## doc-3710 根据参数选择导出不同报表- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-3710.html
- Java API 构建要点: 无(纯理解级内容)。该文档的实现方式是在报表设计器中配置参数面板(下拉框控件 TABLE、文本控件 NAME)与按钮控件的「点击事件」,通过前端 JavaScript 拼接待导出 URL(window.location = servletURL?viewlet=路径&format=excel|word|pdf&extype=sheet&__filename__=名称)触发浏览器端导出。整篇不涉及任何 com.fr.* 类的编程构建:模板参数、控件、数据字典、点击事件均为设计器 GUI 配置;导出动作由服务端 servlet 依据 URL 参数(format/__filename__)完成,无需也不提供 Java API 构建路径。
- 最小 Java 示例: 无

## doc-4040 图表交互FAQ- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4040.html
- Java API 构建要点: 无(纯理解级内容)。本文为图表交互常见问题汇总页,仅罗列用户高频问题(图表下钻/联动/缩放滚动/超链到网络报表/分类系列超链/地图钻取联动/图表切换轮播/下拉框控件联动/定时刷新等)并指向其他参考文档(图表联动、图表缩放、图表超链到网络报表、根据图表分类或系列超链到不同报表、地图钻取与联动、图表切换方式、下拉框和图表联动)。全文未给出任何 com.fr.* 类名、方法签名、XML 节点/属性或代码片段,无可直接落地的 Java API 构建路径。相关 Java API 实现需查阅其指向的具体参考文档(如超级链接 HyperlinkGroup、图表缩放 Zoom、联动 DataSeries/ChartData 等),不在本篇范围内。
- 最小 Java 示例: 无

## doc-4104 决策报表导出单个报表块- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4104.html
- Java API 构建要点: 无(纯理解级内容)。本文档导出单个报表块的能力完全由**前端 JavaScript 点击事件**实现：在决策报表的按钮控件上添加点击事件，先添加参数 a(值为公式 sessionID)，再执行 `window.open("${servletURL}?op=ec_export&sessionID="+a+"&widgetName=REPORT0&format=excel&extype=simple")`(报表块名称需大写，仅支持导出 Excel)。整篇不涉及任何 com.fr.* 后端 Java API：决策报表(.frm)、报表块(report0)、图表块(chart0)、按钮控件及其点击事件均为设计器 GUI 配置；导出动作由服务端报表 servlet 的 `op=ec_export` 操作依据 URL 参数(sessionID/widgetName/format/extype)完成，无需也不提供 Java API 构建路径。相关后台导出逻辑落在 FR 内置 `ec_export` servlet 处理器内，不在本文描述范围内，且文档明确「不支持移动端」「组件不可见时无法导出」。
- 最小 Java 示例: 无

## doc-4138 图表样式FAQ- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4138.html
- Java API 构建要点: 无(纯理解级内容)。该文档是「图表样式」常见问题汇总,所有解答均为设计器(Report Designer / 决策报表)GUI 操作步骤:「选中图表块,点击 样式>标签/标题/图例/系列/坐标轴/提示/背景」等勾选与下拉配置(如标签字号颜色、图例显隐与位置、标题可见性、坐标轴标签隐藏、网格线透明、系列颜色、条件显示、双轴、多分类轴、空数据自定义图片、GIS 图层选择等)。全文为设计期模板配置说明 + 概念性效果罗列,未给出任何 com.fr.* 类名 / 方法签名 / 包路径,也无前端 JS 代码片段,属于「纯配置/概念级」内容。虽图表样式在底层可由 com.fr.chart.* / com.fr.vancheport.* 系列类(如 VanChart、Plot、ChartStyle、Label、Legend、CategoryAxis 等)以 Java 构建,但文档本身未提供任何 API 落点、方法签名或 XML 节点映射,故不杜撰示例。
- 最小 Java 示例: 无

## doc-4152 数据连接使用权限- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4152.html
- Java API 构建要点: 无(纯理解级内容)。本文为「数据连接使用权限」的管理配置文档,全部能力均通过**数据决策系统(管理系统>权限管理)GUI 操作**完成:超级管理员在「全局设置」开启「数据连接控制」「分级授权」,再于「普通权限配置」中以「部门/角色/用户」为权限载体,为用户(示例 eoco)勾选数据连接「FRDemo」的「使用」权限,以及「管理系统>数据连接」模块的使用权限。全文为权限策略的概念性说明与 UI 步骤截图,未出现任何 com.fr.* 类名、方法签名、包路径或前端 JS 代码片段,也未涉及 .cpt/.frm 模板的 XML 节点/属性。虽 FR 底层存在权限相关后端类(如 com.fr.decision 下的权限服务/数据连接权限校验),但本文档仅描述在决策系统 Web 控制台中人工配置权限,不提供任何 Java API 构建路径、方法签名或 XML 映射,故不杜撰示例。
- 最小 Java 示例: 无

## doc-4153 数据连接管理权限- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4153.html
- Java API 构建要点: 无(com.fr.* API 构建路径)。本文为「数据决策系统」后台权限配置说明:开启「分级授权」「数据连接控制」全局开关后,在「权限管理>普通权限配置」界面对部门/角色/用户分配某数据连接(如 FRDemo)的「管理」权限及「管理系统>数据连接」模块的「使用」权限。所述能力完全通过决策系统 Web 控制台/权限管理模块(主要涉及 com.fr.decision 决策系统相关权限服务,属平台管控层而非模板构建 API)配置完成,文档未给出任何可落地的 Java 编码方式、类名或 XML 节点对应。属纯配置/概念级内容,无法提炼出用于构建 .cpt/.frm 或数据连接的 Java API 要点。
- 最小 Java 示例: 无(纯理解级内容)

## doc-4154 数据连接授权权限- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4154.html
- Java API 构建要点: 无(纯理解级内容)。本文为「数据连接授权权限」的管理配置文档,全部能力均通过**数据决策系统(管理系统>权限管理)GUI 操作**完成:超级管理员在「全局设置」开启「分级授权」「数据连接控制」开关;再于「授权权限配置」中以部门/角色/用户为权限载体,为用户(示例 eoco)勾选数据连接「FRDemo」的「授权」权限、人员管理(部门「人力资源」)的「授权」权限,以及「管理系统>数据连接/权限管理」模块的相应权限。全文为权限策略的概念性说明与 UI 步骤截图,未出现任何 com.fr.* 类名、方法签名、包路径或前端 JS 代码片段,也未涉及 .cpt/.frm 模板的 XML 节点/属性。虽 FR 平台底层存在权限相关后端类(如 com.fr.decision 下的权限/授权服务与数据连接权限校验),但本文档仅描述在决策系统 Web 控制台中人工配置授权权限,不提供任何 Java API 构建路径、方法签名或 XML 映射,故不杜撰示例。
- 最小 Java 示例: 无

## doc-4158 定时调度管理权限- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4158.html
- Java API 构建要点: 无(纯理解级内容)。本篇为「管理系统>权限管理」界面操作说明,仅描述如何在数据决策系统中通过分级授权、配置「定时调度」Tab 的「管理」权限与「管理系统」Tab 的「使用」权限,为次管分配全部或部分定时调度任务的管理权限。文档未涉及任何 com.fr.* 类/方法/签名,也不涉及 .cpt/.frm XML 节点映射,属于纯配置/概念类内容,无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-4159 定时调度授权权限- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4159.html
- Java API 构建要点: 无(纯理解级内容)。本篇为「管理系统>权限管理」界面操作说明,描述如何通过分级授权开启、配置「定时调度」Tab 的「授权」权限、「管理系统」Tab 的「授权/使用」权限及「人员管理」Tab 的「授权」权限,使次管(eoco)可将定时调度任务(全部或部分,如「任务一」)的管理权限授予其他部门/角色/用户。文档全程依赖数据决策系统 Web 控制台操作,未涉及任何 com.fr.* 类/方法/签名,也不涉及 .cpt/.frm XML 节点映射,属于纯配置/概念类内容,无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-4202 超级链接-动态参数- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4202.html
- Java API 构建要点: 有(com.fr.* API 构建路径)。本文能力(为单元格添加「动态参数」超链, 点击后以新参数值重提报表, 如切换升/降序)可用 Java API 以代码方式构建进 .cpt, 无需设计器 GUI。关键类与方法:
  - com.fr.main.workbook.WorkBook —— 模板根对象 (XML: <WorkBook>); 通过 new WorkBook() 创建。
  - com.fr.report.worksheet.WorkSheet —— 报表页 (XML: <WorkSheet><Report>)。
  - com.fr.report.cell.TemplateCellElement / com.fr.report.cell.DefaultTemplateCellElement(col,row) —— 单元格元素, 设计器 C1 = new DefaultTemplateCellElement(2,0) (XML: <C c="2" r="0">)。
  - com.fr.web.core.Hyperlink (接口) / com.fr.web.core.HyperlinkList (extends FArray<Hyperlink>) —— 承载单元格的一个或多个超链; TemplateCellElement.setHyperlink(Hyperlink) 把列表挂到单元格 (XML: <C> 内多个 <Hyperlink> 节点)。
  - com.fr.write.extension.DynamicParamHyperlink (推断类, type="11") —— 「动态参数」超链本体 (XML: <Hyperlink class="com.fr.write.extension.DynamicParamHyperlink" type="11">)。其参数映射对应 <Parameters><Parameter name="a" value="ASC"/></Parameters>, 显示名对应 <ParameterName>动态参数1-升序排序</ParameterName>; 推断 setter 为 setName(String) 与 setParameter(String,String) (jar 内真实签名待 javap 核验)。
  - 配套: 数据集参数 / 模板参数 a 通过 TableData 的 Parameters 与 ReportParameterAttr 构建, SQL 中写 ORDER BY 字段 ${a}; 点击超链时 FR 以 a=ASC/DESC 重提报表。约束: 超链参数名必须与数据集参数名一致, 且 ${a} 须存在同名模板参数, 否则点击静默失效。
  - 注: DynamicParamHyperlink 的包名/方法为本项目 topic_4202 研究的推断值(官方核验样本见 doc-4202 §3: %FR_HOME%\webapps\webroot\WEB-INF\reportlets\doc\SpecialSubject\HyplinkReport\动态参数超链实现排序.cpt), 用前请 javap 反查 fine-write.jar 确认。
- 最小 Java 示例: practice/topic_4202_java/DynamicParamHyperlinkDemo.java

## doc-4204 超级链接-JavaScript脚本- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4204.html
- Java API 构建要点: 无(纯理解级内容)。本篇为「超级链接」中 JavaScript 脚本类型超链的配置教程:在设计器单元格上添加「JavaScript」类型超链、设置传参(ID=A2)、在脚本区编写前端 JS 代码 window.open(FR.cjkEncode("${servletURL}?reportlet=...&format=excel"))。整篇只涉及设计器 UI 操作 + 浏览器端 JavaScript(导出仍是调 servletURL 走 HTTP 报表请求),未描述任何 com.fr.* 类的构建方式,也无 .cpt/.frm XML 节点映射可供 Java 程序化生成。注:虽后台存在 com.fr.webattr.JavaScriptHyperlink 等超链类可用于「以 Java 代码给单元格挂 JS 超链」,但那是非本文档描述的能力,按本任务口径不提炼。
- 最小 Java 示例: 无

## doc-4207 图表超链-联动单元格- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4207.html
- Java API 构建要点: 无(纯理解级内容)
  - 该文档为 FineReport 设计器 UI 操作指南:在设计器中选中单元格 A2 → 添加"联动单元格图表"超链 → 设置联动单元格为 A5 → 添加参数 area(值=公式 $$$)。全文仅描述菜单点击与单元格属性配置,未涉及任何 com.fr.* 类的程序化构建。此类"单元格图表联动超链"属于设计器内置超链类型,通常在 .cpt XML 中以 CellHyperlink/ChartHyperlink 配置节点保存,文档本身未给出可对应的 Java API 实现路径。
- 最小 Java 示例: 无

## doc-4209 图表超链-联动悬浮元素- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4209.html
- Java API 构建要点: 无(纯理解级内容)。本文档为设计器 UI 配置说明:在单元格超链对话框中选择“联动悬浮元素”类型,从下拉框选择报表中已添加的悬浮元素(Float1 等),并配置超链参数(如 area=$$$)实现联动。所述能力均通过 FineReport 设计器交互界面完成,文档未提供任何 com.fr.* 类、方法签名或 XML 节点构造路径;超链类型为内置“联动悬浮元素”专用类型,不支持移动端/App/HTML5 预览。无 Java API 实现路径可提炼。
- 最小 Java 示例: 无

## doc-4241 JS实现超链跳转前判断子模板是否有数据- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4241.html
- Java API 构建要点: 无(纯理解级内容)。本文档能力完全通过报表设计器 UI + 前端 JS 实现:主模板 A2 单元格挂「JavaScript 类型超链」、设置参数 P(公式=$$$)、在 JS 中调用 FR.remoteEvaluate("SQL(...)") 执行子模板 SQL 查询,有数据则 window.location.href 跳转到子模板 cpt 的预览 URL,无数据则 FR.Msg.alert 弹窗。所有涉及 API 均为 FineReport 前端 JavaScript 对象(FR.remoteEvaluate / FR.Msg.alert / window.location),不对应任何 com.fr.* Java 类;模板(.cpt)本身也是在设计器里拖拽生成,文中无任何用 Java 代码构建 WorkBook / 超链 / 数据集的描述,故无 Java API 构建路径。
- 最小 Java 示例: 无

## doc-4418 大数据模板导出慢问题排查- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4418.html
- Java API 构建要点: 无(纯理解级内容)。该文档是「大数据模板导出慢」的线上排查(运维/诊断)指南,全文为排查步骤而非能力构建:1) 区分两类导出请求——携带 sessionID(复用预览期已计算的结果,不重新取数)与携带模板名(如 ?viewlet=a.cpt&op=export&format=pdf,需重新取数),属服务器请求分发与 info 日志/SQL 耗时排查;2) 检查数据库驱动(SQLServer 低版本 sqljdbc 性能差,升级 sqljdbc42),属驱动/环境层;3) 检查模板——图表导出慢因服务器缺 j2v8 环境改用 nashorn 性能低(升级 GCC,见 doc-3403 图表导出升级说明),webimage 公式引用用户自有慢服务需用户自查。整篇未出现任何 com.fr.* 类/方法用于"构建"模板或导出能力,均为诊断建议与配置项,无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-4432 定时调度平台通知- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4432.html
- Java API 构建要点: 无(纯理解级内容)。该文档为纯 Web 控制台配置指南:通过「管理系统>定时调度>任务管理」UI 设置任务名称、默认用户组、调度对象(.cpt 模板)、调度周期、以及文件处理中的「平台通知」(收件人=默认用户组、主题、内容、结果链接在平台内打开)。全文未涉及任何 com.fr.* 类、方法签名或 XML 节点/属性构造,属于配置/概念级内容,无 Java API 实现路径。
- 最小 Java 示例: 无

## doc-4518 大数据集导出常见问题- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4518.html
- Java API 构建要点: 无(纯理解级内容)。该文档是「大数据集导出」的使用排障 FAQ + 前端 JS API 指南: 全部能力均通过浏览器端 JS 调用 `_g().directExportToExcel(dsName, fileName, paramStr, colNames)` 触发(2.10 节明确给出该 JS API 签名及 encodeURIComponent 转译中文/参数拼接的用法), 其余 2.1~2.9、2.11 均为现象描述、原因分析与解决方案(进度条 5s 后显示、1000W*20 列上限、仅支持关系型库不支持 spider/程序数据集、每 100W 行分 sheet、行式引擎行高、order by 缺失、超时等)。整篇未出现任何 com.fr.* 类、方法签名、包路径, 也无 .cpt/.frm XML 节点/属性构建说明; 大数据集导出本身由服务端插件/引擎实现, 文档仅站在"设计器/平台前端触发 + 排障"角度, 不提供 Java 侧构造路径。故按规则标记为纯前端 JS / 概念级, 不杜撰示例。
- 最小 Java 示例: 无

## doc-4524 大数据集导出- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4524.html
- Java API 构建要点: 无(纯理解级内容)。该文档为「大数据集导出」各方案的对比与选型说明(大数据集导出Excel插件、JS实现、新计算引擎、行式引擎/流式导出插件),全程为概念描述、优缺点与适用条件,未出现任何 com.fr.* 类、方法签名或 .cpt/.frm XML 节点/属性映射,无可通过 Java API 构建的要点。
- 最小 Java 示例: 无

## doc-4637 PC 端预览模板的移动端效果- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-4637.html
- Java API 构建要点: 无(纯理解级内容)。该文档为「在 PC 端用浏览器设备仿真工具查看模板移动端预览效果」的操作指南:通过设计器「移动端预览」按钮复制链接、在 Chrome 中按 F12 打开控制台并切换到仿真设备(移动端选项)来访问模板(%FR_HOME%\webapps\webroot\WEB-INF\reportlets\demo\form\简单自由填报-phone.cpt),全程为浏览器/设计器 UI 操作与设备仿真概念,不涉及任何 com.fr.* 类、方法签名、包路径,也无 .cpt/.frm XML 节点/属性构建说明。无 Java API 实现路径可提炼。
- 最小 Java 示例: 无

## doc-903 数据集中的排序- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-903.html
- Java API 构建要点:
  - 本篇核心是「数据集中的排序」，本质是*在数据库查询(SQL)里写 ORDER BY*。FR 没有专门的排序 API 类——排序只是 SQL 文本的一部分，不是独立节点/属性。
  - 唯一对应的 Java API 是构造「数据库查询」数据集：
    - 类 `com.fr.data.impl.DBTableData`(⚠原文 DatabaseConnection 经 2026-09-12 jar 实测 FR10 全部 1133 jar 0 命中,FR10 无此类;javap 实证 `setDatabase(com.fr.data.impl.Connection)`),方法 `setName(String)` / `setDatabase(Connection)` / `setQuery(String)`。
    - `setQuery(String sql)` 即承载含 ORDER BY 的 SQL —— 对应 .cpt 中 `<TableData class="com.fr.data.impl.DBTableData">(⚠原文 DatabaseConnection FR10 1133 jar 0 命中,2026-09-12 实测;全库 .cpt 该节点实测唯二 class 为 NameTableData/DBTableData)` 下的 `<Query><![CDATA[...]]></Query>` 节点。
    - 升序/降序/多列只是 SQL 写法差异(`order by 销量` / `order by 销量 desc` / `order by 英文简称,销量`)，无专属 API。
  - 动态排序(文档 2.4)中用 `${a}` 占位符实现参数化 SQL：
    - 类 `com.fr.report.parameter.Parameter`，方法 `setName(String)` / `setValue(Object)` / `addParameter(Parameter)`(由 DatabaseConnection 持有)。
    - 对应 .cpt 中 `<Parameters><Parameter name="a" .../></Parameters>` 节点；SQL 中的 `${a}` 在取数时被替换为参数值。
  - 关键参数：`DatabaseConnection.setQuery(String)` 的 SQL 字符串(含 ORDER BY)；`Parameter` 的 name 必须与 `${...}` 占位名一致，value 默认 "asc"。
  - 该能力属「概念/SQL 配置」级：Java API 只负责把这段 SQL 与参数塞进数据集定义，排序逻辑本身由数据库执行。
- 最小 Java 示例: practice/topic_903_java/BuildOrderDataset.java

## doc-1029 下拉框实现数据字典联动- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1029.html
- Java API 构建要点: 无(纯理解级内容)。本文全部为设计器 UI 操作+公式配置：在参数面板添加下拉框控件，P1 数据字典选「自定义」(地区/省份)，P2 数据字典选「公式」并用 `if($p1='省份',sql("FRDemo","select 货主省份 from 订单",1),if($p1='地区',sql("FRDemo","select 货主地区 from 订单",1),""))` 实现联动。联动逻辑完全由 SQL() 公式在运行期解析，文档未给出任何 `com.fr.*` 编程构建路径(模板参数、控件、数据字典类型、if/sql 公式均为设计态配置与公式层能力)，无对应的 Java 生成/改写 XML 节点的实现要点可提炼。
- 最小 Java 示例: 无

## doc-1042 下拉树控件自动构建示例- FineReport帮助文档
- 来源: https://help.fanruan.com/finereport10.0/doc-view-1042.html
- Java API 构建要点:
  - 本文核心是「把普通数据集转成树数据集, 下拉树控件数据字典选『自动构建』关联树数据集」。三步均有对应 com.fr.* 类可程序化生成:
    1) 普通数据集(2.1): `com.fr.data.impl.DBTableData`(单独存在;⚠原文并列的 DatabaseConnection FR10 1133 jar 0 命中,2026-09-12 实测)
       - 方法: `setName(String)` / `setDatabase(String)` / `setQuery(String)`。
       - 对应 .cpt XML: `<TableData class="com.fr.data.impl.DBTableData">` 下 `<Database>FRDemo</Database>`、`<Query><![CDATA[SELECT * FROM 公司部门]]></Query>` 节点。
    2) 树数据集(2.2): `com.fr.data.impl.TableTreeData`(实现 `com.fr.data.TreeTableData`)⚠类名 FR10 全部 44 jar 实测 0 命中(2026-09-12),未经运行期确证勿当事实
       - 方法: `setName(String)` / `setFromTableDataName(String)`(用哪个普通数据集构建) / `setIdColumnName(String)`(标记列=部门ID) / `setParentIdColumnName(String)`(父标记列=上级ID) / `setCaptionColumnName(String)`(显示列=部门名称) / 可选 `setLayerColumnName` / `setLeafColumnName`。
       - 对应 .cpt XML: `<TableData class="com.fr.data.impl.TableTreeData">`, 子节点 `<FromTableName>ds1</FromTableName>`、`<IdColumnName>部门ID</IdColumnName>`、`<ParentIdColumnName>上级ID</ParentIdColumnName>`、`<CaptionColumnName>部门名称</CaptionColumnName>`。根节点父标记必须为空(文档 2.1 强调不支持 0/null)。
    3) 下拉树控件+数据字典自动构建(2.3/2.4): `com.fr.form.ui.TreeComboBox`(下拉树控件) + `com.fr.form.ui.TableDataDict`(数据字典, 自动构建模式)
       - 方法: `TreeComboBox.setWidgetName(String)` / `setDataDict(DataDict)` / `setDelimiter(String)`; `TableDataDict.setTableDataName(String)`(关联 Tree1) / `setValueColumnName(String)`(实际值=部门ID) / `setColumnName(String)`(显示值=部门名称)。⚠本行宿主类 `com.fr.form.ui.TableDataDict` 与 `com.fr.form.ui.TreeComboBox` 经 2026-09-12 jar 实测 FR10 全部 1133 jar 均 0 命中,类名与全部方法签名均未经 jar 验证,勿当事实用于生成。
       - 对应 .cpt/.frm XML: 参数面板 `<Widget class="com.fr.form.ui.TreeComboBox" widgetName="treeCombo">` 内 `<DataDict class="com.fr.form.ui.TableDataDict">`, 子节点 `<TableDataName>Tree1</TableDataName>`、`<ValueColumnName>部门ID</ValueColumnName>`、`<ColumnName>部门名称</ColumnName>` —— 即「构建方式=自动构建」在 XML 中的落地形态(自动构建=数据字典直接引用树数据集, 无需自定义/公式)。
  - 关键参数: TableTreeData 的 id/parentId/caption 三列名必须与源表字段一致, 且 parentId 列根值必须为空; TableDataDict 的 tableDataName 必须等于已存在的树数据集名 Tree1。
  - 该能力属「可通过 Java API 构建」级: 三步都对应确定的 com.fr.* 类与 XML 节点, 可程序生成模板, 非纯概念/公式内容。
- 最小 Java 示例: practice/topic_1042_java/BuildTreeCombo.java
