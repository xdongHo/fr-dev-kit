<!--
KB_INDEX: {
  "title": "部署集成 - 自定义按钮与Web 页面集成问题",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "部署集成",
    "自定义按钮",
    "Web 页面集成问题",
    "Web 页面集成"
  ],
  "summary": "「部署集成」分页：自定义按钮、Web 页面集成问题（约 13 篇条目）；FR10 帮助文档「部署集成」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 部署集成 · 自定义按钮与Web 页面集成问题

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §部署集成


## Web 页面集成 > 自定义按钮（8篇）

### 64. 自定义按钮

- **doc-view ID**: 910
- **路径**: 部署集成 > Web 页面集成 > 自定义按钮 > 自定义按钮
- **核心概念**: FineReport 中内置的工具栏形式相对固定，不能够灵活地变更样式和位置。用户希望可以自定义一套工具栏，通过 iframe 嵌入报表内容，将自定义按钮放置在报表页面之外。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 注：下面文档适用于普通报表。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 注：下面文档适用于普通报表。

**关键代码/公式/API：**
- 公式: `getElementById('reportFrame')`
- 公式: `gotoFirstPage()`
- 公式: `gotoLastPage()`
- 公式: `gotoPreviousPage()`
- JS API: `contentPane`
- URL: `http://localhost`

### 65. 自定义提交按钮

- **doc-view ID**: 921
- **路径**: 部署集成 > Web 页面集成 > 自定义按钮 > 自定义提交按钮
- **核心概念**: 在我们使用填报表时，不希望使用 FineReport 内置的工具栏的按钮，希望能够自定义提交按钮，将数据入库。自定义按钮既可以是 FineReport 模板中添加的按钮控件，也可以是 Web 集成页面中，HTML 的按钮标签。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 在我们使用填报表时，不希望使用 FineReport 内置的工具栏的按钮，希望能够自定义提交按钮，将数据入库。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 在我们使用填报表时，不希望使用 FineReport 内置的工具栏的按钮，希望能够自定义提交按钮，将数据入库。

**关键代码/公式/API：**
- 代码片段: `<html>      ⏎ <head>      ⏎ <title>自定义提交按钮</title>    ⏎ <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />  ⏎ </head>      ⏎ <body>      ⏎ <div id="toolbar">      ⏎ <button type="bu`
- 公式: `writeReport()`
- 公式: `getElementById('报表所在iframe的id')`
- 公式: `getElementById('reportFrame')`
- 公式: `afterload()`
- JS API: `contentPane`
- URL: `http://localhost`

### 66. 自定义缩放按钮

- **doc-view ID**: 923
- **路径**: 部署集成 > Web 页面集成 > 自定义按钮 > 自定义缩放按钮
- **核心概念**: 一般情况下我们将网页中的一部分嵌入了一张 FR 做的报表，图表数据比较密集，我们希望能够进行缩放，从而更加清楚地查看报表，就需要定义报表的缩放。缩放可放大和缩小报表页面，Web 页面调用，效果如下图所示： 注：也可以直接在模板工具栏中添加缩放按钮。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 一般情况下我们将网页中的一部分嵌入了一张 FR 做的报表，图表数据比较密集，我们希望能够进行缩放，从而更加清楚地查看报表，就需要定义报表的缩放。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 一般情况下我们将网页中的一部分嵌入了一张 FR 做的报表，图表数据比较密集，我们希望能够进行缩放，从而更加清楚地查看报表，就需要定义报表的缩放。

**关键代码/公式/API：**
- 代码片段: `<html>   ⏎  <head>   ⏎   <title>自定义缩放按钮</title>   ⏎   <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />   ⏎  </head>  ⏎ <script type="text/javascript">       ⏎    function afterloa`
- 公式: `scale('+')`
- 公式: `scale('-')`
- 公式: `afterload()`
- 公式: `getElementById('reportFrame')`
- JS API: `contentPane`
- URL: `http://localhost`

### 67. 自定义批量导出按钮

- **doc-view ID**: 924
- **路径**: 部署集成 > Web 页面集成 > 自定义按钮 > 自定义批量导出按钮
- **核心概念**: 用户有以下需求时： - 所有的表都放在一个 Excel 里面，然后分不同的 sheet 。- 多个普通报表，通过一个 url ，导出包含多个报表的 Excel 。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 注：本文方法适用于普通报表。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 注：本文方法适用于普通报表。

**关键代码/公式/API：**
- 代码片段: `http://localhost:8075/webroot/decision/view/report?reportlets= ⏎ [{reportlet:"/doc/Primary/Parameter/Parameter.cpt",地区:"华北"}, ⏎ {reportlet:"/doc/Primary/CrossReport/Cross.cpt"}] ⏎ &format=excel&__file`
- 代码片段: `http://localhost:8075/webroot/decision/view/report?reportlets=%5B%7Breportlet%3A%22%2Fdoc%2FPrimary%2FParameter%2FParameter.cpt ⏎ %22%2C%E5%9C%B0%E5%8C%BA%3A%22%E5%8D%8E%E5%8C%97%22%7D%2C%7Breportlet `
- 代码片段: `var reportlets = "[{reportlet: '/doc/Primary/Parameter/Parameter.cpt',地区: '华北'}, {reportlet: '/doc/Primary/CrossReport/Cross.cpt'}]" ⏎ function clickEvent() { ⏎      window.open(encodeURI('/webroot/de`
- 公式: `clickEvent()`
- JS API: `window.open`
- URL: `http://localhost`

### 68. 工具栏显示数据总量

- **doc-view ID**: 926
- **路径**: 部署集成 > Web 页面集成 > 自定义按钮 > 工具栏显示数据总量
- **核心概念**: 在自定义工具栏中，可以显示总页数，那么有什么方法能实现在工具栏中显示数据的总条数呢，如下图所示 通过在某个单元格中使用 count 函数计算总的数据条数，然后在分页预览的加载结束事件中获取对应单元格的值并赋值给主页面中的文本框或其他控件中。注：使用 count 函数的单元格必须在扩展数据的上方单元格。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 在自定义工具栏中，可以显示总页数，那么有什么方法能实现在工具栏中显示数据的总条数呢，如下图所示 通过在某个单元格中使用 count 函数计算总的数据条数，然后在分页预览的加载结束事件中获取对应单元格的值并赋值给主页面中的文本框或其他控件中。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 在自定义工具栏中，可以显示总页数，那么有什么方法能实现在工具栏中显示数据的总条数呢，如下图所示 通过在某个单元格中使用 count 函数计算总的数据条数，然后在分页预览的加载结束事件中获取对应单元格的值并赋值给主页面中的文本框或其他控件中。

**关键代码/公式/API：**
- 代码片段: `var totalnumber=$("tr[tridx=0]","div.content-container").children().eq(0).text();//获取A1单元格的值   ⏎ parent.document.getElementById("e").value="共"+totalnumber+"条数据";//给页面上id为e的文本框赋值`
- 代码片段: `<html>      ⏎   <head>      ⏎   <title>工具栏显示数据总个数</title>   ⏎   <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />      ⏎   <script type="text/javascript">      ⏎     function after`
- 公式: `=count(A3)`
- 公式: `children()`
- 公式: `eq(0)`
- 公式: `text()`
- JS API: `children().eq`
- JS API: `contentPane`
- JS API: `_g()`
- JS API: `_g().gotoFirstPage`
- URL: `http://localhost`

### 69. 自定义翻页按钮

- **doc-view ID**: 928
- **路径**: 部署集成 > Web 页面集成 > 自定义按钮 > 自定义翻页按钮
- **核心概念**: 用户将网页中的一部分嵌入了一张报表模板，有时希望能够自己定义翻页按钮，不使用报表已有的按钮，如下图所示： 由 自定义按钮 章节可知，如上图中的首页、上一页、下一页、末页按钮，直接调用 FR 内置方法即可 - 首页按钮调用方法：gotoFirstPage() - 上一页按钮调用方法：gotoPreviousPage() - 下一页按钮调用方法：gotoNextPage() - 末页按钮按钮调用方法：

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 用户将网页中的一部分嵌入了一张报表模板，有时希望能够自己定义翻页按钮，不使用报表已有的按钮，如下图所示： 由 自定义按钮 章节可知，如上图中的首页、上一页、下一页、末页按钮，直接调用 FR 内置方法即可 - 首页按钮调用方法：gotoFirstPage() - 上一页按钮调用方法：gotoPrevi
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 用户将网页中的一部分嵌入了一张报表模板，有时希望能够自己定义翻页按钮，不使用报表已有的按钮，如下图所示： 由 自定义按钮 章节可知，如上图中的首页、上一页、下一页、末页按钮，直接调用 FR 内置方法即可 - 首页按钮调用方法：gotoFirstPage() - 上一页按钮调用方法：gotoPrevi

**关键代码/公式/API：**
- 代码片段: `function afterload() {     //iframe加载后触发 ⏎       var contentPane = document.getElementById("reportFrame").contentWindow.contentPane;  //获取报表 contentPane    ⏎       var cPageIndex = contentPane.current`
- 代码片段: `function gotoPage() {      ⏎     var contentpane= document.getElementById('reportFrame').contentWindow.contentPane;      ⏎     var page = document.getElementById("index").value;      ⏎     if(page >= `
- 代码片段: `<html>      ⏎   <head>      ⏎   <title>自定义翻页按钮</title>   ⏎   <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />      ⏎   <script type="text/javascript">      ⏎     function afterloa`
- 公式: `gotoFirstPage()`
- 公式: `gotoPreviousPage()`
- 公式: `gotoNextPage()`
- 公式: `gotoLastPage()`
- JS API: `contentPane`
- URL: `http://localhost`

### 70. 自定义导出按钮

- **doc-view ID**: 1145
- **路径**: 部署集成 > Web 页面集成 > 自定义按钮 > 自定义导出按钮
- **核心概念**: 虽然 FineReport 支持多种不同的导出方式，但是在 Web 页面集成 中，用户往往只想将报表内容嵌入到 iframe 中，而工具栏以及工具栏上的按钮都会隐藏掉。用户可以通过 Web 页面自定义按钮实现导出。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 虽然 FineReport 支持多种不同的导出方式，但是在 Web 页面集成 中，用户往往只想将报表内容嵌入到 iframe 中，而工具栏以及工具栏上的按钮都会隐藏掉。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 虽然 FineReport 支持多种不同的导出方式，但是在 Web 页面集成 中，用户往往只想将报表内容嵌入到 iframe 中，而工具栏以及工具栏上的按钮都会隐藏掉。

**关键代码/公式/API：**
- 代码片段: `onclick="document.getElementById('reportFrame').contentWindow.contentPane.exportReportToPDF()"`
- 代码片段: `<html> ⏎   <head>   ⏎   <title>FineReport自定义导出</title>   ⏎   <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />   ⏎   </head>   ⏎   <body> ⏎   ⏎     <fieldset> ⏎     <div id="toolba`
- 代码片段: `<html> ⏎   <head>   ⏎   <title>FineReport自定义导出</title>   ⏎   <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />   ⏎   <script type="text/javascript" src="/webroot/decision/view/repo`
- 公式: `exportReportToPDF()`
- 公式: `exportReportToExcel('page')`
- 公式: `exportReportToExcel('simple')`
- 公式: `exportReportToExcel('sheet')`
- JS API: `contentPane`
- JS API: `window.open`
- URL: `http://localhost`

### 71. 自定义打印按钮

- **doc-view ID**: 4604
- **路径**: 部署集成 > Web 页面集成 > 自定义按钮 > 自定义打印按钮
- **核心概念**: 用户在遇到 FineReport 报表嵌入 iframe 中的场景时，如果需要打印报表内容，可以自定义打印按钮并将其放置在报表外部。如果报表嵌入在 ID 为 reportFrame 的 iframe 中，直接通过 JS 代码调用 FineReport 内置工具栏中的方法即可。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 用户在遇到 FineReport 报表嵌入 iframe 中的场景时，如果需要打印报表内容，可以自定义打印按钮并将其放置在报表外部。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 用户在遇到 FineReport 报表嵌入 iframe 中的场景时，如果需要打印报表内容，可以自定义打印按钮并将其放置在报表外部。

**关键代码/公式/API：**
- 代码片段: `<!DOCTYPE html> ⏎ <html> ⏎ <head> ⏎ <title>自定义打印</title>   ⏎ <meta http-equiv="Content-Type" content="text/html; " charset="UTF-8"> ⏎ </head> ⏎ <body> ⏎ <div> ⏎  <button type="button" onClick="documen`
- 公式: `getElementById('reportFrame')`
- 公式: `pdfPrint()`
- JS API: `contentPane`
- URL: `http://localhost`

---

## Web 页面集成 > Web 页面集成问题（5篇）

### 72. Web 传递中文参数

- **doc-view ID**: 916
- **路径**: 部署集成 > Web 页面集成 > Web 页面集成问题 > Web 传递中文参数
- **核心概念**: 给 iframe 设置 src 嵌入某个报表时，往往会给报表传递初始的参数值，例如： ``` <iframe id="reportFrame" width="900" height="400" src="/webroot/decision/view/report?viewlet=/report.cpt&参数1=参数值&参数2=参数值..."></iframe> ``` 若参数名称、参数值甚至报表名

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 给 iframe 设置 src 嵌入某个报表时，往往会给报表传递初始的参数值，例如： ``` <iframe id="reportFrame" width="900" height="400" src="/webroot/decision/view/report?viewlet=/report.cp
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 给 iframe 设置 src 嵌入某个报表时，往往会给报表传递初始的参数值，例如： ``` <iframe id="reportFrame" width="900" height="400" src="/webroot/decision/view/report?viewlet=/report.cp

**关键代码/公式/API：**
- 代码片段: `<iframe id="reportFrame" width="900" height="400" src="/webroot/decision/view/report?viewlet=/report.cpt&参数1=参数值&参数2=参数值..."></iframe>`
- 代码片段: `<html>   ⏎   <head>   ⏎   <title>FineReport Demo</title>   ⏎   <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />   ⏎   <script language="javascript"> ⏎     function autoLoad(){ ⏎  `
- 公式: `autoLoad()`
- 公式: `encodeURIComponent("地区")`
- 公式: `encodeURIComponent("华东")`
- 公式: `getElementById("reportFrame")`
- JS API: `window.onload`
- URL: `http://localhost`

### 73. IE8或9下Web集成页面显示异常

- **doc-view ID**: 930
- **路径**: 部署集成 > Web 页面集成 > Web 页面集成问题 > IE8或9下Web集成页面显示异常
- **核心概念**: 本文汇总了一些 Web 集成后在 IE8 或 IE9 浏览器下出现的问题及解决方案。

**业务场景四要素：**
- 统计指标方案: 本文汇总了一些 Web 集成后在 IE8 或 IE9 浏览器下出现的问题及解决方案。
- 业务场景: 本文汇总了一些 Web 集成后在 IE8 或 IE9 浏览器下出现的问题及解决方案。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 本文汇总了一些 Web 集成后在 IE8 或 IE9 浏览器下出现的问题及解决方案。

**关键代码/公式/API：**
- 代码片段: `<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"> ⏎ <html> ⏎   <body> ⏎ <iframe id="total" width="800px" height="800px" src="/webroot/decision/view/report?viewlet=/doc/Primary/Chart/Char`
- 代码片段: `<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> ⏎ 完整代码如下： ⏎ <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "ht`
- 代码片段: `<meta http-equiv="X-UA-Compatible" content="IE=9"> ⏎ 完整代码如下： ⏎ <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"> ⏎ <meta http-equiv="X-UA-Compatible" content="IE=9"> ⏎ <html> ⏎   <body> `
- URL: `http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd`
- URL: `http://ip`

### 74. 集成后参数值显示乱码

- **doc-view ID**: 936
- **路径**: 部署集成 > Web 页面集成 > Web 页面集成问题 > 集成后参数值显示乱码
- **核心概念**: 报表已集成到 Web 页面中，通过在页面传递参数至报表中时，会发现有时某些参数值，传递到报表中是显示为问号（？？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 报表已集成到 Web 页面中，通过在页面传递参数至报表中时，会发现有时某些参数值，传递到报表中是显示为问号（？
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 报表已集成到 Web 页面中，通过在页面传递参数至报表中时，会发现有时某些参数值，传递到报表中是显示为问号（？

**关键代码/公式/API：**
- 代码片段: `<html> ⏎  ⏎ <head> ⏎  ⏎ <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"> ⏎  ⏎ <script Language="JavaScript">              ⏎  ⏎ function frOpen() {    ⏎  ⏎ window.location=encodeURI(`
- 代码片段: `window.location="http://localhost:8075/webroot/decision/view/report?viewlet="+encodeURIComponent("中文.cpt")`
- 代码片段: `<html> ⏎ <head> ⏎ <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/> ⏎ <script> ⏎ function autoSubmit() { ⏎  var Region1 = document.getElementById('Region');     //获取到参数 Region 所在文本框`
- 公式: `encodeURIComponent("中文.cpt")`
- 公式: `frOpen()`
- 公式: `autoSubmit()`
- 公式: `getElementById('Region')`
- JS API: `window.location`
- URL: `http://localhost`

### 75. Web页面集成FAQ

- **doc-view ID**: 4066
- **路径**: 部署集成 > Web 页面集成 > Web 页面集成问题 > Web页面集成FAQ
- **核心概念**: 可参见文档：Web 页面集成简单示例 可自定义一个批量导出按钮，详情请参见：自定义批量导出按钮 可参见文档：自定义导出按钮 可以的，详情请参见：自定义提交按钮 可自定义一个提交按钮，详情请参见：自定义提交按钮 可以的，详情请参见：URL 参数传递给 iframe 中的报表 可参见文档：iframe 嵌入报表滚动条问题 解决。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 可参见文档：Web 页面集成简单示例 可自定义一个批量导出按钮，详情请参见：自定义批量导出按钮 可参见文档：自定义导出按钮 可以的，详情请参见：自定义提交按钮 可自定义一个提交按钮，详情请参见：自定义提交按钮 可以的，详情请参见：URL 参数传递给 iframe 中的报表 可参见文档：iframe 
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 可参见文档：Web 页面集成简单示例 可自定义一个批量导出按钮，详情请参见：自定义批量导出按钮 可参见文档：自定义导出按钮 可以的，详情请参见：自定义提交按钮 可自定义一个提交按钮，详情请参见：自定义提交按钮 可以的，详情请参见：URL 参数传递给 iframe 中的报表 可参见文档：iframe 

### 76. Web页面集成常见问题

- **doc-view ID**: 4624
- **路径**: 部署集成 > Web 页面集成 > Web 页面集成问题 > Web页面集成常见问题
- **核心概念**: 本文主要汇总了 Web 页面集成过程中经常出现的问题以及解决方案。**问题描述：** 用户以非管理员身份进入数据决策系统后，访问：http://IP:Port/webroot/decision/接口调用 ，出现如下报错： **解决方案：** 需要获得该页面的权限，请参考 分级权限分配 **问题描述：** 在 Web 页面集成时，将报表嵌入到用户页面，会自动显示 FineReport 内置工具栏。

**业务场景四要素：**
- 统计指标方案: 本文主要汇总了 Web 页面集成过程中经常出现的问题以及解决方案。
- 业务场景: 本文主要汇总了 Web 页面集成过程中经常出现的问题以及解决方案。
- 人员岗位: 管理员进入平台，点击「管理系统>安全管理」，关闭点击挟持攻击防护按钮。如下图所示：
- 功能应用场景: 本文主要汇总了 Web 页面集成过程中经常出现的问题以及解决方案。

**关键代码/公式/API：**
- 公式: `postMessage()`
- 公式: `doURLPDFPring()`
- URL: `http://IP`
- URL: `http://localhost`

---
