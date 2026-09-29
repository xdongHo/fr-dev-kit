<!--
KB_INDEX: {
  "title": "FR11 二次开发与 JS API 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["doc", "view", "新增", "API", "实测", "本文件"],
  "summary": "--- name: fr11-js-api description: 何时使用：FR11 报表二次开发与前端 JS API 问题——写 JS 事件、调用 _g()/FR/FS 接口、填报提交与插删行、单元格取值赋值、工具栏/参数面板/Tab"
}
-->

---
name: fr11-js-api
description: 何时使用：FR11 报表二次开发与前端 JS API 问题——写 JS 事件、调用 _g()/FR/FS 接口、填报提交与插删行、单元格取值赋值、工具栏/参数面板/Tab 控制、Web 集成 iframe、单点登录、插件扩展开发时使用。触发词：JS、JavaScript、JS API、二次开发、_g()、contentPane、FR对象、FS对象、填报、writeReport、setCellValue、单元格接口、表格接口、工具栏接口、跑马灯、FVS、duchamp、插件开发、Java引擎API。
keywords: [contentPane, 废弃, 表格对象, 三级表格对象, 单元格接口, 表格接口, 工具栏接口]
compatibility: FR11
---

# FR11 二次开发与 JS API 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/js-api二次开发/references/js_api_summary.md`；完整文档条目大表见本目录 `references\` 下对应原文。

## 主题速览
- 收录 436 篇文档（doc-view ID 113~5131，非连续），全部直接转录自 FR11 离线 HTML 正文，0 篇解析失败；其中 78 篇明确提及 FR11 子版本号（11.0.x）变更。
- 标题关键词频次：JS 173 / 插件 60 / 自定义 57 / 报表 41 / 数据 30 / 单元格 25 / FVS 19 / 填报 14 / 控件 13 / 提交 10 / API 9 / 导出 9。
- 内容四大块：前端 JS API（_g()/FR/FS 全局接口与表格/工具栏/控件/分页接口）、填报接口（提交/插删行/校验）、Java 引擎 API（导出、自定义函数/校验/调度）、Web 集成与插件生态。

## 核心结论

### 常见问法：想在前端用 js 拿到某个单元格的内容有什么接口？/ 单元格赋值 setCellValue 怎么写？/ 提交后回调事件怎么写（成功失败提示）？/ 填报提交按钮 JS 用哪个？/ contentPane 废弃了还能用吗？

| 口语问题 | 落点（本文件实读内容） |
|---|---|
| 前端取单元格内容/给单元格赋值 | _g().getCellValue(sheetIndex, address|row,col) / setCellValue(...)；10.0 下仅「填报预览」支持；11.0.10 起 getCellValue() 变更为单元格对象接口 getValue()，旧接口仍可用【实测·本文件】 |
| js 回调/提交后事件（自定义提交结果提示） | 自定义提交没有默认防重复提交与结果提示，需 setEnable(false) 配合回调 fr_submitinfo.failinfo 自行实现【实测·本文件】 |
| 填报提交按钮三件套 | _g().writeReport() 直接提交、verifyAndWriteReport() 校验并提交、verifyReport() 只校验【实测·本文件】 |
| contentPane 废弃怎么办 | 11.0 废弃的 contentPane 仍可用但不再随版本迭代、有兼容风险；新写法统一 _g()（doc-view-4285/4896）【实测·本文件】 |
- 11.0 提供全新 JS API 手册：`_g()` 获取报表对象，接口在普通报表/决策报表间统一规整并标注移动端支持；废弃的 contentPane 对象及方法在 11.0 仍可用但不再随版本迭代，存在兼容风险（doc-view-4285/4896）。
- 单元格取值赋值：`_g().getCellValue(sheetIndex, address|row,col)` / `setCellValue(...)`，10.0 下仅「填报预览」支持；11.0.10 起单元格值获取接口 getCellValue() 变更为单元格对象接口 getValue()，旧接口仍可用（doc-view-1200/4305）。
- 11.0.10 优化表格接口为「表格对象>表格行列>单元格对象」三级层级，历史接口保留但不再迭代优化；单元格圆角接口 setCellRadius 变更为 setRadius（旧接口可继续用）（doc-view-4355/4362/5024）。
- 填报提交三件套：`_g().writeReport()` 直接提交、`_g().verifyAndWriteReport()` 校验并提交、`_g().verifyReport()` 只校验；自定义提交没有默认的防重复提交与结果提示，需 setEnable(false) 配合回调 `fr_submitinfo.failinfo` 自行实现（doc-view-921/596/4376/4049/1219）。
- 插删行接口：`_g().appendReportRC(n)/deleteReportRC()`、`appendReportRow(location,reportIndex,num)`；每行都放按钮在数据量大时会拖慢模板加载，可用超链传参代替按钮实现删行（doc-view-595/4056/4236）。
- 分页接口 gotoFirstPage/gotoPreviousPage/gotoNextPage/gotoLastPage，11.0 新增 getCurrentPageIndex、getReportTotalPage（不支持 FVS）；报表块局部刷新翻页用 `getWidgetByName('report0').gotoPage(pn,para,noCache)`（doc-view-4197/1304）。
- 效果接口 addEffect（11.0 新增）：highlightRow/highlightCol/highlightCross/highlightCell、setCellFont/setRowFont、showTooltip，移动端 APP\H5 需 11.0.70 及以后；跑马灯 startMarquee/stopMarquee、隐藏滚动条 setH/VScrollBarVisible 为 10.0.19+ 接口（后者不支持 FVS）（doc-view-4301/4302/4306/4348/4299/4300）。
- 在 JS 中复用 FR 能力：`FR.remoteEvaluate('=公式')` 调用 FR 公式简化复杂 JS 计算；图表刷新 `FR.Chart.WebUtils.getChart("chartID").dataRefresh()` 不支持扩展图表；`chart.saveAsImage()` 为 11.0.2 新增官方导出图片接口（doc-view-1785/2317/4515）。
- Java 引擎侧：报表分「模板（未执行，含数据集）」与「结果（执行后，不再保存数据集）」两个基本面；输入输出类集中在 com.fr.report.io；自定义函数继承 com.fr.script.AbstractFunction 实现 run(Object[])；定时调度支持自定义附件处理类与自定义类执行条件（doc-view-632/668/735/1840/699/5014）。
- Web 集成坑点：iframe 跨域嵌入报「拒绝连接」需在管理系统>安全防护>Security Headers 高级设置放行；中文参数乱码用 encodeURI/encodeURIComponent 处理（中日韩文最易出问题）；FR.ajax 封装 jQuery.ajax，data 参数已做中日韩文编码处理（doc-view-2700/936/602）。
- 单点登录矩阵：前台接口（用户名密码拼 URL，要求与平台账号密码一致）、后台单点登录插件 ssoToken（11.0.4/插件 V1.1.1 之前新计算引擎请求无法适配 ssoToken）、CAS 集成后远程设计需自定义 RemoteFilter 放行 /remote/design（doc-view-884/4322/3288）。
- FVS 大屏：11.0.7 起配合「FVS大屏编辑模式」插件 V1.8.0+ 支持 duchamp 接口，并补充支持决策报表全部接口；分页切换 switchStory/nextStory/previousStory；轮播器 getShowIndex/showCardByIndex 为 11.0.9/V1.9.1 新增（doc-view-4251/4939/4220/5004）。

## 关键 API 与版本要点

### 常见问法：_g() 全局对象有哪些常用接口？/ 参数面板和工具栏怎么用 JS 控制？/ JS 里怎么调用 FR 公式或弹窗？/ 大数据集直接导出 Excel 的 JS 怎么写？

| 口语问题 | 落点（本文件实读内容） |
|---|---|
| _g() 取参数面板/所有控件/提交参数 | 11.0 新增 getParameterContainer（参数面板）、getAllWidgets（覆盖 10.0 的 name_widgets）；parameterCommit 在 11.0.6 之前的填报 Web 端需加 setTimeout 延时【实测·本文件】 |
| JS 复用 FR 能力（公式/弹窗/超链） | FR.remoteEvaluate('=公式') 调公式；FR.showDialog/closeDialog/destroyDialog；FR.doHyperlinkByGet/Post（11.0.10 起参数支持 json）【实测·本文件】 |
| 前端直接导大数据集为 Excel | _g().directExportToExcel("数据集名","文件名",paramStr,colNames,forMat,enCoding)，后台流式导出；11.0.10 新增 CSV 与编码参数【实测·本文件】 |
| 行高亮/跑马灯/隐藏滚动条等效果 | addEffect 系列（highlightRow/Col/Cross/Cell、setCellFont/setRowFont、showTooltip，11.0 新增）；startMarquee/stopMarquee、setH/VScrollBarVisible 为 10.0.19+【实测·本文件核心结论】 |
- `_g()` 全局对象：11.0 新增 getParameterContainer（参数面板）、getAllWidgets（覆盖 10.0 的 name_widgets）；parameterCommit 在 11.0.6 之前的填报 Web 端使用需加 setTimeout 延时（doc-view-4177/4251）。
- FR 对象：showDialog/closeDialog/destroyDialog、doHyperlinkByGet/Post；11.0.10 起 showDialog、doHyperlinkByGet 参数支持 json 格式；超链传 title 自定义标题 HTML5 端仅支持 V11.0.76+（doc-view-4316/1393）。
- 打印：FR.doURLPrint/doURLPDFPrint/doURLFlashPrint（JAR 2018-04-09 及以后请用新打印方式），打印功能不支持移动端（doc-view-1071/1090）。
- 表格新接口：getCell/getRow/getColumn/getRowCount/getColumnCount（后两个为 11.0.10 新增，计算扩展后的行/列数）、setRowHeight/setColWidth、setRadius、setStyle/showToolTip（doc-view-4864/4865/4866/5104）。
- 数据分析专有：11.0.1 新增 expandNodeLayer/collapseNodeLayer/expandAllNodeLayer/collapseAllNodeLayer 及 centerReport（居中显示）；折叠树接口要求新计算引擎，分页/数据分析预览可用（doc-view-4237/2369/4431）。
- 大数据集导出：FR11 新增 `_g().directExportToExcel("数据集名","文件名",paramStr,colNames,forMat,enCoding)`，后台流式导出、无需前台展示；11.0.10 新增 CSV 类型与 enCoding 编码参数（doc-view-2597）。
- 事件体系：事件响应方式共 7 种（JavaScript 脚本、提交入库、发送邮件、导出、移动端弹窗、提交事件、自定义提交）；自定义事件共四类（控件/组件事件、Web 页面事件等）（doc-view-1180/3888/1229）。
- 安全相关：11.0.12 新增 Referer 校验（按白名单控制访客）；Java 防盗链 Filter 方案需将 webroot 部署在外置 Tomcat（内置设计器 Tomcat 不再读 web.xml）（doc-view-2454/1429）。
- 11.0.3 新增 JavaScript 高级编辑器：可在编辑器内搜索、查看官方 JS 接口并按接口推荐帮助文档示例（doc-view-597）。
- 常用效果接口速记：loadSheetByName/loadSheetByIndex（指定 sheet）、setTabVisible/showCardByIndex/getShowIndex（Tab 块）、expandAllNodeLayer/collapseAllNodeLayer（折叠树一键展开收起）、refreshAllSheets（刷新报表，location.reload 为整页刷新）（doc-view-1740/1980/2083/2624/2369/1394）。

## 深入查询
遇到本主题具体问题（接口参数签名、完整场景 JS 示例、插件名与适配版本、Java 类包名），读取 `references\` 下 js_api_summary.md 原文，按 doc-view ID 查原始条目。
