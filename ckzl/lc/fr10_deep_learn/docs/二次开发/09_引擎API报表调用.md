<!--
KB_INDEX: {
  "title": "二次开发 - 引擎API报表调用",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "二次开发",
    "报表调用",
    "引擎API"
  ],
  "summary": "「二次开发」分页：报表调用（约 12 篇条目）；FR10 帮助文档「二次开发」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 二次开发 · 引擎API报表调用

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §二次开发


## 引擎API > 报表调用（12篇）

### 24. 报表调用

- **doc-view ID**: 660
- **路径**: 二次开发 > 引擎API > 报表调用 > 报表调用
- **核心概念**: FineReport 设计器基本可以零编码地设计出报表，但设计器中的样式都是固定的，如果用户想要设计器不能实现的功能效果，就需要借助二次开发完成。用户可以将模板读取在Java编辑器中，对其进行修改，修改后发布在工程上。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FineReport 设计器基本可以零编码地设计出报表，但设计器中的样式都是固定的，如果用户想要设计器不能实现的功能效果，就需要借助二次开发完成。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FineReport 设计器基本可以零编码地设计出报表，但设计器中的样式都是固定的，如果用户想要设计器不能实现的功能效果，就需要借助二次开发完成。

### 25. 读取修改报表

- **doc-view ID**: 664
- **路径**: 二次开发 > 引擎API > 报表调用 > 读取修改报表
- **核心概念**: 可以通过 java 程序读取一个模板，读取后在程序中修改报表的属性，然后重新导出成模板文件。如下图所示，读取模板文件Parameter.cpt，在程序中修改 A1 单元格的字体为红色，然后导出成模板文件，导出后在设计器打开模板，A1 单元格字体变成红色。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 可以通过 java 程序读取一个模板，读取后在程序中修改报表的属性，然后重新导出成模板文件。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: // 定义报表运行环境,用于执行报表

**关键代码/公式/API：**
- 代码片段: `WorkBook workbook = (WorkBook) TemplateWorkBookIO ⏎ .readTemplateWorkBook( ⏎ "/doc/Primary/Parameter/Parameter.cpt");`
- 代码片段: `// 定义报表运行环境,用于执行报表 ⏎ String envpath = "C:\\FineReport_10.0\\webapps\\webroot\\WEB-INF";//工程路径 ⏎ SimpleWork.checkIn(envpath); ⏎ module.start();`
- 代码片段: `// 获得WorkBook中的WorkSheet，进而修改A1单元格的前景色为红色 ⏎ TemplateElementCase report = (TemplateElementCase) workbook ⏎ .getReport(0); ⏎ // getCellElement(int column, int row)，column和row都从0开始，因此A1单元格便是第0列第0行     ⏎ `
- 公式: `\webroot\\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/io/SimpleDemo.java`
- Java类/方法: `SimpleWork.checkIn(envpath)`
- Java类/方法: `module.start()`
- Java类/方法: `report.getCellElement(0, 0)`
- Java类/方法: `FRFont.getInstance()`

### 26. 报表参数界面API

- **doc-view ID**: 666
- **路径**: 二次开发 > 引擎API > 报表调用 > 报表参数界面API
- **核心概念**: 在设计器中可以通过对参数界面的设计来控制参数的显示形式，如参数界面的布局、背景、显示方式等。那如何在程序中控制参数的相关属性呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在设计器中可以通过对参数界面的设计来控制参数的显示形式，如参数界面的布局、背景、显示方式等。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在设计器中可以通过对参数界面的设计来控制参数的显示形式，如参数界面的布局、背景、显示方式等。

**关键代码/公式/API：**
- 代码片段: `WorkBook workbook = (WorkBook) TemplateWorkBookIO.readTemplateWorkBook("//doc//Primary//Parameter//Parameter.cpt");`
- 代码片段: `ReportParameterAttr paraAttr = workbook.getReportParameterAttr();`
- 代码片段: `/* 参数界面的布局  ⏎  * 0 : 靠左  ⏎  * 1 ：居中  ⏎  * 2 ： 靠右  ⏎  */   ⏎ paraAttr.setAlign(1);`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/io/SetParameterWindow.java`
- Java类/方法: `TemplateWorkBookIO.readTemplateWorkBook("//doc//Primary//Parameter//Parameter.cpt")`
- Java类/方法: `workbook.getReportParameterAttr()`
- Java类/方法: `paraAttr.setAlign(1)`
- Java类/方法: `ColorBackground.getInstance(new Color(0, 255, 255)`

### 27. 报表执行

- **doc-view ID**: 668
- **路径**: 二次开发 > 引擎API > 报表调用 > 报表执行
- **核心概念**: 由引擎 API 概述可以知道，报表分为两种情况： 模板和结果 - 没有执行过的工作薄或者报表都为模板，模板中包含数据集，数据列没有扩展且公式未计算； - 模板执行后就成了结果，结果中所有数据列都已经扩展，因此结果中不再保存数据集。如下图所示，给模板传递参数值后就可以执行生成结果，以下具体介绍该过程的实现步骤。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 由引擎 API 概述可以知道，报表分为两种情况： 模板和结果 - 没有执行过的工作薄或者报表都为模板，模板中包含数据集，数据列没有扩展且公式未计算； - 模板执行后就成了结果，结果中所有数据列都已经扩展，因此结果中不再保存数据集。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: * 生成参数map，注入参数与对应的值，用于执行报表 该模板中只有一个参数地区，给其赋值华北

**关键代码/公式/API：**
- 代码片段: `String envpath = "C:\\FineReport_10.0\\webapps\\webroot\\WEB-INF";//工程路径 ⏎ SimpleWork.checkIn(envpath); ⏎ module.start();`
- 代码片段: `TemplateWorkBook workbook = TemplateWorkBookIO.readTemplateWorkBook("\\doc\\Primary\\Parameter\\Parameter.cpt");`
- 代码片段: `/* ⏎ * 生成参数map，注入参数与对应的值，用于执行报表 该模板中只有一个参数地区，给其赋值华北 ⏎ * 若参数在发送请求时传过来，可以通过req.getParameter(name)获得 ⏎ * 获得的参数put进map中，paraMap.put(paraname,paravalue) ⏎ */ ⏎ java.util.Map paraMap = new java.util.HashMap`
- 公式: `\webroot\\`
- 公式: `\Primary\\Parameter\\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/io/ExcuteDemo.java`
- Java类/方法: `SimpleWork.checkIn(envpath)`
- Java类/方法: `module.start()`
- Java类/方法: `TemplateWorkBookIO.readTemplateWorkBook("\\doc\\Primary\\Parameter\\Parameter.cpt")`
- Java类/方法: `req.getParameter(name)`

### 28. 动态修改数据

- **doc-view ID**: 669
- **路径**: 二次开发 > 引擎API > 报表调用 > 动态修改数据
- **核心概念**: 同样的模板样式，同样的数据源样式，希望通过网络报表连接不同数据库，使用同一个模板样式，在同一个网络报表里面显示结果，但数据来源不同。通过使用程序网络报表所在类需要继承 com.fr.web.reportlet 这个抽象类，并且需要实现 createReport(ReportletRequest arg0) 这个方法，并返回报表对象。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 同样的模板样式，同样的数据源样式，希望通过网络报表连接不同数据库，使用同一个模板样式，在同一个网络报表里面显示结果，但数据来源不同。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 同样的模板样式，同样的数据源样式，希望通过网络报表连接不同数据库，使用同一个模板样式，在同一个网络报表里面显示结果，但数据来源不同。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/demo/NewDateDemo.java`
- URL: `http://localhost`

### 29. 程序网络报表中获取参数值

- **doc-view ID**: 672
- **路径**: 二次开发 > 引擎API > 报表调用 > 程序网络报表中获取参数值
- **核心概念**: 我们定义的程序网络报表也可以包含参数，当用 Web 浏览器访问网络报表时，如何给它传递默认参数值呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 我们定义的程序网络报表也可以包含参数，当用 Web 浏览器访问网络报表时，如何给它传递默认参数值呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 我们定义的程序网络报表也可以包含参数，当用 Web 浏览器访问网络报表时，如何给它传递默认参数值呢？

**关键代码/公式/API：**
- 代码片段: `String countryValue = reportletRequest.getParameter("地区").toString();`
- 代码片段: `Parameter[] ps = wbTpl.getParameters();     ⏎ ps[0].setValue(countryValue);`
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `http://localhost`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/demo/URLParameterDemo.java`
- Java类/方法: `reportletRequest.getParameter("地区")`
- Java类/方法: `wbTpl.getParameters()`

### 30. 遍历单元格

- **doc-view ID**: 675
- **路径**: 二次开发 > 引擎API > 报表调用 > 遍历单元格
- **核心概念**: 定义了单元格后，有时候我们需要对报表每个单元格进行处理，如何在程序中遍历单元格呢？FineReport 中通过 Report 的 cellIterator() 方法获取 Report 中所有的单元格，这些单元格放在 Iterator 中，可以像遍历普通的 Iterator 对象一样遍历 Iterator 中的单元格，从而对单元格进行处理或作其他操作。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 定义了单元格后，有时候我们需要对报表每个单元格进行处理，如何在程序中遍历单元格呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 定义了单元格后，有时候我们需要对报表每个单元格进行处理，如何在程序中遍历单元格呢？

**关键代码/公式/API：**
- 代码片段: `// 读取模板保存为WorkBook对象   ⏎ workbook = TemplateWorkBookIO.readTemplateWorkBook("/doc/Primary/GroupReport/Group.cpt");`
- 代码片段: `// 遍历单元格   ⏎ int col = 0, row = 0; ⏎ byte direction = 0; ⏎ java.util.Iterator it = report.cellIterator(); ⏎ while (it.hasNext()) { ⏎     TemplateCellElement cell = (TemplateCellElement) it.next(); ⏎  `
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/demo/ChangeRowAndCol.java`
- URL: `http://localhost`
- Java类/方法: `TemplateWorkBookIO.readTemplateWorkBook("/doc/Primary/GroupReport/Group.cpt")`
- Java类/方法: `report.cellIterator()`
- Java类/方法: `it.hasNext()`
- Java类/方法: `it.next()`

### 31. 单元格样式设置

- **doc-view ID**: 677
- **路径**: 二次开发 > 引擎API > 报表调用 > 单元格样式设置
- **核心概念**: 上一节中示例如何创建报表，新增单元格。单元格是组成报表的最小元素，增加后就要对其进行格式设置，如列宽、行高、字体、前景色、背景色、显示位置、边框样式、边框颜色等等。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 上一节中示例如何创建报表，新增单元格。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 上一节中示例如何创建报表，新增单元格。

**关键代码/公式/API：**
- 代码片段: `TemplateCellElement cellElement = new DefaultTemplateCellElement(1, 1, 2, 2, "FineReport");`
- 代码片段: `worksheet.setColumnWidth(1, new OLDPIX(300));   ⏎ worksheet.setRowHeight(1, new OLDPIX(30));`
- 代码片段: `Style style = cellElement.getStyle();   ⏎ if (style == null) {   ⏎     style = Style.getInstance();   ⏎ }`
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/demo/SetCellElementStyle.java`
- URL: `http://localhost`
- Java类/方法: `worksheet.setColumnWidth(1, new OLDPIX(300)`
- Java类/方法: `worksheet.setRowHeight(1, new OLDPIX(30)`
- Java类/方法: `cellElement.getStyle()`
- Java类/方法: `Style.getInstance()`

### 32. 创建程序报表

- **doc-view ID**: 680
- **路径**: 二次开发 > 引擎API > 报表调用 > 创建程序报表
- **核心概念**: 由上一小节我们可以了解到所谓的网络报表就是指实现了 Reportlet 接口的类，可以在 Web 浏览器端直接访问，展示出我们通过程序设计的报表。上一节中我们是直接读取 cpt 模板文件生成的网络报表，为了您更加理解网络报表的原理，该节介绍如何在程序中创建程序网络报表。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 由上一小节我们可以了解到所谓的网络报表就是指实现了 Reportlet 接口的类，可以在 Web 浏览器端直接访问，展示出我们通过程序设计的报表。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 由上一小节我们可以了解到所谓的网络报表就是指实现了 Reportlet 接口的类，可以在 Web 浏览器端直接访问，展示出我们通过程序设计的报表。

**关键代码/公式/API：**
- 代码片段: `//创建一个WorkBook工作薄，在工作薄中插入一个WorkSheet ⏎ WorkBook workbook = new WorkBook(); ⏎ WorkSheet sheet1 = new WorkSheet(); ⏎ workbook.addReport(sheet1); ⏎ return workbook;`
- 代码片段: `new DefaultCellElement(int column, int row, Object value)`
- 代码片段: `TemplateCellElement CellA1 = new DefaultTemplateCellElement(0, 0, "FineReport");   ⏎     Style style = Style.getInstance();`
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/demo/CreateReportletDemo.java`
- URL: `http://localhost`
- Java类/方法: `workbook.addReport(sheet1)`
- Java类/方法: `Style.getInstance()`
- Java类/方法: `FRFont.getInstance("Arial", 1, 20.0F, Color.red)`
- Java类/方法: `style.deriveFRFont(frfont)`

### 33. 程序网络报表

- **doc-view ID**: 685
- **路径**: 二次开发 > 引擎API > 报表调用 > 程序网络报表
- **核心概念**: 如果要修改模板，首先需要读取模板。本文介绍如何将读取的模板保存为程序网络报表，然后直接在 Web 端访问定义的程序网络报表。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 如果要修改模板，首先需要读取模板。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 如果要修改模板，首先需要读取模板。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `http://localhost`

### 34. 保存模板至数据库

- **doc-view ID**: 694
- **路径**: 二次开发 > 引擎API > 报表调用 > 数据库读取报表 > 保存模板至数据库
- **核心概念**: 一般制作的模板文件都放在硬盘中，如果硬盘损坏，就会导致文件丢失，后果会很严重。为了降低这个风险，我们可将模板文件全部保存在数据库中（二进制数据），这样若是硬盘损坏导致文件丢失，也可以将数据库中的备份文件取出，从而避免发生重大损失。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 一般制作的模板文件都放在硬盘中，如果硬盘损坏，就会导致文件丢失，后果会很严重。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 一般制作的模板文件都放在硬盘中，如果硬盘损坏，就会导致文件丢失，后果会很严重。

**关键代码/公式/API：**
- SQL: `insert into \"report\" values(?,?)`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/demo/SaveReportToDatabase.java`

### 35. 从数据库读取报表

- **doc-view ID**: 1460
- **路径**: 二次开发 > 引擎API > 报表调用 > 数据库读取报表 > 从数据库读取报表
- **核心概念**: 注：阅读本文时，请先阅读 保存模板至数据库 。保存模板至数据库 中，可以将 cpt 模板保存入库，例如示例中将 GettingStarted.cpt 存在数据库表 report 中，那保存在数据库中的模板要如何访问呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 注：阅读本文时，请先阅读 保存模板至数据库 。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 注：阅读本文时，请先阅读 保存模板至数据库 。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `http://localhost`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/demo/ReadFromDatabase.java`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/demo/ReadfrmFromDatabase.java`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/demo/NewReadFrmFromDatabase.java`

---
