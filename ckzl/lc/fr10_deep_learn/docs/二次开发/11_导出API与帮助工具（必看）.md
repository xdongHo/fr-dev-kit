<!--
KB_INDEX: {
  "title": "二次开发 - 导出API与帮助工具（必看）",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "二次开发",
    "导出API",
    "帮助工具（必看）",
    "引擎API"
  ],
  "summary": "「二次开发」分页：导出API、帮助工具（必看）（约 9 篇条目）；FR10 帮助文档「二次开发」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 二次开发 · 导出API与帮助工具（必看）

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §二次开发


## 引擎API > 导出API（6篇）

### 48. 导出API

- **doc-view ID**: 735
- **路径**: 二次开发 > 引擎API > 导出API > 导出API
- **核心概念**: FineReport 支持预览报表时将报表导出成各种通用的文件格式，如 PDF 、Excel 、Word 等；FineReport 设计器中也支持将模板导出成通用的文件格式或者内置数据模板。如下图所示： 如果用户不想通过预览报表或操作设计器导出文件，想直接后台导出，该如何实现呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FineReport 支持预览报表时将报表导出成各种通用的文件格式，如 PDF 、Excel 、Word 等；FineReport 设计器中也支持将模板导出成通用的文件格式或者内置数据模板。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FineReport 支持预览报表时将报表导出成各种通用的文件格式，如 PDF 、Excel 、Word 等；FineReport 设计器中也支持将模板导出成通用的文件格式或者内置数据模板。

**关键代码/公式/API：**
- 代码片段: `// 将未执行模板工作薄导出为内置数据集模板   ⏎  outputStream = new FileOutputStream(new File("C:\\test\\EmbExport.cpt")); ⏎  EmbeddedTableDataExporter templateExporter = new EmbeddedTableDataExporter(); ⏎  templateExport`
- 代码片段: `// 将未执行模板工作薄导出为内置数据集模板   ⏎   outputStream = new FileOutputStream(new File("C:\\test\\EmbExport.cpt")); ⏎    EmbeddedTableDataExporter templateExporter = new EmbeddedTableDataExporter(); ⏎   templateEx`
- 代码片段: `// 将模板工作薄导出模板文件，在导出前您可以编辑导入的模板工作薄，可参考报表调用章节   ⏎   outputStream = new FileOutputStream(new File("C:\\test\\TmpExport.cpt")); ⏎   ((WorkBook) workbook).export(outputStream)`
- 公式: `webroot\WEB-INF\lib目录下 fine 开头的 12 个 JAR 包。

- %FR_HOME%\`
- 公式: `webroot\WEB-INF\lib目录下的 sqlite-jdbc.jar

- %Tomcat_HOME%\`
- 公式: `webroot\WEB-INF\embed\`
- URL: `https://code.fanruan.com/demo/example/src/branch/persist/10.0/src/main/java/com/fr/io/ExportApi.java`
- URL: `https://code.fanruan.com/demo/example/src/branch/persist/10.0/src/main/java/com/fr/io/ExportApi_frm.java`
- URL: `http://localhost`
- Java类/方法: `templateExporter.export(outputStream, workbook)`
- Java类/方法: `templateExporter.export(outputStream, workbook,  parameterMap)`
- Java类/方法: `ExcelExport.setVersion(true)`
- Java类/方法: `ExcelExport.export(outputStream, workbook.execute(parameterMap, new WriteActor()`

### 49. 多个报表导出一个Excel

- **doc-view ID**: 736
- **路径**: 二次开发 > 引擎API > 导出API > 多个报表导出一个Excel
- **核心概念**: 在报表统计分析中，常常希望将某类报表或者不同参数的同一报表汇总导出到一个 Excel 中，每张报表对应一个 sheet。如下图所示，地区销售量统计报表，导出后，将每个地区的数据单独作为一个 sheet 汇总于一个 Excel 中。

**业务场景四要素：**
- 统计指标方案: 2）以第一个执行后的结果工作薄 workbook 作为容器，添加其他地区的统计报表，因此先将 workbook 中的第一个 sheet 重命名为华东，表示华东地区的数据。
- 业务场景: 在报表统计分析中，常常希望将某类报表或者不同参数的同一报表汇总导出到一个 Excel 中，每张报表对应一个 sheet。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在报表统计分析中，常常希望将某类报表或者不同参数的同一报表汇总导出到一个 Excel 中，每张报表对应一个 sheet。

**关键代码/公式/API：**
- 代码片段: `// 未执行模板工作薄 ⏎ TemplateWorkBook workbook = TemplateWorkBookIO.readTemplateWorkBook( ⏎ "Gettingstarted.cpt");`
- 代码片段: `// 参数值为China计算结果，将结果保存至rworkbook ⏎ Parameter[] parameters = workbook.getParameters(); ⏎ java.util.Map parameterMap = new java.util.HashMap(); ⏎ for (int i = 0; i < parameters.length; i++) { ⏎ paramete`
- 代码片段: `rworkbook.setReportName(0, "华东"); ⏎ 改变参数值为华北，执行获得结果报表 PageReport，加入结果工作薄 ⏎ // 清空parametermap，将参数值改为华北,计算后获得ResultReport ⏎ parameterMap.clear(); ⏎ for (int i = 0; i < parameters.length; i++) { ⏎ parame`
- 公式: `webroot\WEB-INF\lib目录下 fine 开头的 12 个 JAR 包。

- %FR_HOME%\`
- 公式: `webroot\WEB-INF\lib目录下的 sqlite-jdbc.jar

- %Tomcat_HOME%\`
- Java类/方法: `TemplateWorkBookIO.readTemplateWorkBook(
"Gettingstarted.cpt")`
- Java类/方法: `workbook.getParameters()`
- Java类/方法: `parameterMap.put(parameters[i].getName()`
- Java类/方法: `workbook.execute(parameterMap,new PageActor()`

### 50. Excel直接转成模板cpt

- **doc-view ID**: 737
- **路径**: 二次开发 > 引擎API > 导出API > Excel直接转成模板cpt
- **核心概念**: 存在很多 Excel 文件，要将它们转成 cpt 模板，不想通过设计器手动一张张导入，希望用程序在后台批量转换。通过程序读取 Excel 文件转为模板 TemplateWorkBook，然后把scwj/mb为 cpt 文件。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 存在很多 Excel 文件，要将它们转成 cpt 模板，不想通过设计器手动一张张导入，希望用程序在后台批量转换。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 存在很多 Excel 文件，要将它们转成 cpt 模板，不想通过设计器手动一张张导入，希望用程序在后台批量转换。

**关键代码/公式/API：**
- 代码片段: `File excelFile = new File("D:\\aa.xlsx"); // 获取EXCEL文件 ⏎ FileInputStream a = new FileInputStream(excelFile);`
- 代码片段: `TemplateWorkBook tpl = new ExcelReportImporter().generateWorkBookByStream(a); ⏎ OutputStream outputStream = new FileOutputStream(new File("D:\\abc.cpt")); // 转换成cpt模板 ⏎ ((WorkBook) tpl).export(outputS`
- 代码片段: `TemplateWorkBook tpl = new Excel2007ReportImporter().generateWorkBookByStream(a); ⏎ OutputStream outputStream = new FileOutputStream(new File("D:\\abc.cpt")); // 转换成cpt模板 ⏎ ((WorkBook) tpl).export(out`
- 公式: `webroot\WEB-INF\lib目录下 fine 开头的 12 个 JAR 包。

- %FR_HOME%\`
- 公式: `webroot\WEB-INF\lib目录下的 sqlite-jdbc.jar

- %Tomcat_HOME%\`

### 51. 后台批量导出Excel

- **doc-view ID**: 738
- **路径**: 二次开发 > 引擎API > 导出API > 后台批量导出Excel
- **核心概念**: 一张报表可以根据不同的条件统计出不同的数据结果，若您希望将每一种条件下的结果都保存下来如导出成 Excel 文件至磁盘，您可以在后台调用 FineReport 的导出接口 ExcelExporter 将每种情况下的结果批量保存起来。

**业务场景四要素：**
- 统计指标方案: 一张报表可以根据不同的条件统计出不同的数据结果，若您希望将每一种条件下的结果都保存下来如导出成 Excel 文件至磁盘，您可以在后台调用 FineReport 的导出接口 ExcelExporter 将每种情况下的结果批量保存起来。
- 业务场景: 一张报表可以根据不同的条件统计出不同的数据结果，若您希望将每一种条件下的结果都保存下来如导出成 Excel 文件至磁盘，您可以在后台调用 FineReport 的导出接口 ExcelExporter 将每种情况下的结果批量保存起来。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 一张报表可以根据不同的条件统计出不同的数据结果，若您希望将每一种条件下的结果都保存下来如导出成 Excel 文件至磁盘，您可以在后台调用 FineReport 的导出接口 ExcelExporter 将每种情况下的结果批量保存起来。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\reportlets\doc\Primary\Parameter\`
- 公式: `webroot\WEB-INF\`
- 公式: `webroot\WEB-INF\lib目录下 fine 开头的 12 个 JAR 包。

- %FR_HOME%\`
- 公式: `webroot\WEB-INF\lib目录下的 sqlite-jdbc.jar

- %Tomcat_HOME%\`

### 52. Excel 导出的多种方式

- **doc-view ID**: 739
- **路径**: 二次开发 > 引擎API > 导出API > Excel 导出的多种方式
- **核心概念**: 在导出章节中我们介绍了 Excel 导出方式 ExcelExporter，此为原样导出。在 FineReport 中，导出 Excel 还有分页导出、分页分 sheet 导出、大数据量导出三种导出方式，那通过程序导出时，这三种该如何实现呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在导出章节中我们介绍了 Excel 导出方式 ExcelExporter，此为原样导出。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在导出章节中我们介绍了 Excel 导出方式 ExcelExporter，此为原样导出。

**关键代码/公式/API：**
- 代码片段: `//原样导出excel2003 ⏎             outputStream = new FileOutputStream(new File("C:\\test\\ExcelExport.xls"));   ⏎             ExcelExporter excel = new ExcelExporter();   ⏎             excel.setVersion(tr`
- 代码片段: `//原样导出excel2007 ⏎            outputStream = new FileOutputStream(new File("C:\\test\\ExcelExport.xlsx"));   ⏎            StreamExcel2007Exporter excel1 = new StreamExcel2007Exporter(); ⏎            ex`
- 代码片段: `//分页导出excel2003 ⏎             outputStream = new FileOutputStream(new File("C:\\test\\PageExcelExport.xls")); ⏎             PageExcelExporter page = new PageExcelExporter(ReportUtils.getPaperSettingLi`
- 公式: `webroot\WEB-INF\lib目录下 fine 开头的 12 个 JAR 包。

- %FR_HOME%\`
- 公式: `webroot\WEB-INF\lib目录下的 sqlite-jdbc.jar

- %Tomcat_HOME%\`
- Java类/方法: `excel.setVersion(true)`
- Java类/方法: `excel.export(outputStream, workbook.execute(parameterMap,new WriteActor()`
- Java类/方法: `ReportUtils.getPaperSettingListFromWorkBook(workbook.execute(parameterMap,new WriteActor()`
- Java类/方法: `page.setVersion(true)`

### 53. 通过代码创建模板

- **doc-view ID**: 2431
- **路径**: 二次开发 > 引擎API > 导出API > 通过代码创建模板
- **核心概念**: 有时候需要批量生成 cpt 模板，手动操作比较繁琐；可以借助 FineReport 的 API 接口通过 Java 代码批量生成 cpt 模板。创建一个 WorkBook 后设置模板内容后将其导出成 cpt 模板。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 有时候需要批量生成 cpt 模板，手动操作比较繁琐；可以借助 FineReport 的 API 接口通过 Java 代码批量生成 cpt 模板。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 有时候需要批量生成 cpt 模板，手动操作比较繁琐；可以借助 FineReport 的 API 接口通过 Java 代码批量生成 cpt 模板。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\lib目录下 fine 开头的 12 个 JAR 包。

- %FR_HOME%\`
- 公式: `webroot\WEB-INF\lib目录下的 sqlite-jdbc.jar

- %Tomcat_HOME%\`

---

## 引擎API > 帮助工具（必看）（3篇）

### 54. 编译Java程序

- **doc-view ID**: 744
- **路径**: 二次开发 > 引擎API > 帮助工具（必看） > 编译Java程序
- **核心概念**: 用户通过 Java 类代码进行Finereport 二次开发，实现某些功能时，通常需要编译 Java文件，生成 Class 类，如在程序数据源、程序报表、自定义函数、自定义后台导出、自定义打印的应用中都需要 Class 类。那在进行二次开发时，如何编译 Java文件，需要哪些准备工作呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 用户通过 Java 类代码进行Finereport 二次开发，实现某些功能时，通常需要编译 Java文件，生成 Class 类，如在程序数据源、程序报表、自定义函数、自定义后台导出、自定义打印的应用中都需要 Class 类。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 用户通过 Java 类代码进行Finereport 二次开发，实现某些功能时，通常需要编译 Java文件，生成 Class 类，如在程序数据源、程序报表、自定义函数、自定义后台导出、自定义打印的应用中都需要 Class 类。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\`

### 55. Eclipse中启动设计器

- **doc-view ID**: 745
- **路径**: 二次开发 > 引擎API > 帮助工具（必看） > Eclipse中启动设计器
- **核心概念**: 利用 FineReport 进行二次开发时，可以在 Java 编辑器，如 Eclipse、Idea 中通过调用 FineReport 启动类来启动设计器，以便于开发过程中的调试和为二次开发做准备。从 Java 编辑器中启动 FineReport 设计器，设计器中的运行日志会显示在编辑器的 console 中，有源码的代码可以设置断点，进行调试。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 利用 FineReport 进行二次开发时，可以在 Java 编辑器，如 Eclipse、Idea 中通过调用 FineReport 启动类来启动设计器，以便于开发过程中的调试和为二次开发做准备。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 利用 FineReport 进行二次开发时，可以在 Java 编辑器，如 Eclipse、Idea 中通过调用 FineReport 启动类来启动设计器，以便于开发过程中的调试和为二次开发做准备。

**关键代码/公式/API：**
- 代码片段: `package com.fr; ⏎  ⏎ import com.fr.start.MainDesigner; ⏎  ⏎ public class StartFRDesigner { ⏎     public StartFRDesigner() { ⏎     } ⏎  ⏎     public static void main(String[] args) { ⏎      MainDesigne`
- 公式: `webroot\WEB-INF\`
- 公式: `system32\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/StartFRDesigner.java`
- Java类/方法: `MainDesigner.main(args)`

### 56. 后台输出Log信息

- **doc-view ID**: 746
- **路径**: 二次开发 > 引擎API > 帮助工具（必看） > 后台输出Log信息
- **核心概念**: 注：了解 FineReport 日志存储位置可查看 日志简介 在编写程序时，为了便于调试，往往需要向后台输出一些信息来判断程序是否运行正确，或者当用户执行某个操作时，希望服务器记录下来，将信息输出至后台，比如运行某个报表时希望将执行的 SQL 语句打印出来或者将报表执行每个阶段所用的时间输出便于性能分析等等。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 注：了解 FineReport 日志存储位置可查看 日志简介 在编写程序时，为了便于调试，往往需要向后台输出一些信息来判断程序是否运行正确，或者当用户执行某个操作时，希望服务器记录下来，将信息输出至后台，比如运行某个报表时希望将执行的 SQL 语句打印出来或者将报表执行每个阶段所用的时间输出便于性能
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 注：了解 FineReport 日志存储位置可查看 日志简介 在编写程序时，为了便于调试，往往需要向后台输出一些信息来判断程序是否运行正确，或者当用户执行某个操作时，希望服务器记录下来，将信息输出至后台，比如运行某个报表时希望将执行的 SQL 语句打印出来或者将报表执行每个阶段所用的时间输出便于性能

**关键代码/公式/API：**
- Java类/方法: `FineLoggerFactory.getLogger()`

---
