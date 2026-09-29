<!--
KB_INDEX: {
  "title": "FR11 打印 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["打印", "PDF", "print", "FR11", "服务器端打印", "静默打印"],
  "summary": "--- name: fr11-print description: 何时使用：实现 FR11 报表打印（print）——零客户端/本地/服务器端打印、静默打印、套打、批量或传参打印、水印控制，以及排查打印偏移与打印失败时使用。触发词：打印、"
}
-->

---
name: fr11-print
description: 何时使用：实现 FR11 报表打印（print）——零客户端/本地/服务器端打印、静默打印、套打、批量或传参打印、水印控制，以及排查打印偏移与打印失败时使用。触发词：打印、doURLPrint、PDF 打印、套打、静默打印、纸张、水印。
compatibility: FR11
---

# FR11 打印 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/print打印/references/print_summary.md`；完整文档条目大表（doc-view ID + 标题 + 核心概念 + API）见本目录 `references\print_summary.md`。

## 主题速览
- 关键词频次：打印 12 篇占绝对主体，另有报表、样式、插件、导出各 1 篇。
- 全类共 18 篇文档，doc-view ID 覆盖 135~4992，仅 1 篇提及 11.0.x 子ckzl/bb，0 篇解析失败。
- 覆盖：页面设置与纸张背景、打印方式与统一入口、套打与偏移、JS 打印 API、打印常见问题排查。

## 核心结论
- 10.0 起打印功能整合为统一入口，简化选择；注意 11.0 设计器与部署包默认使用 openjdk，无法启动 flash 打印，需 Oracle/Sun JDK 才可。
- 支持「静默打印」（点击即打，不弹选项窗与打印机设置窗）的方式：零客户端打印、本地打印、服务器端打印。
- 套打：把票据背景扫描成图片设为报表背景，打印时只打印数据不打印背景；不同打印机导致的位置偏差通过页面边距设置校正。
- 水印本质是报表背景，可实现「屏幕不显示、打印时显示水印」或按次选择是否带水印（如首打加水印）。
- 页面设置按 sheet 生效（每个 sheet 可不同）；填报预览不支持页边距设置；Excel 导出不支持报表背景，Word 导出仅支持颜色背景。
- 分页预览是默认预览方式，但不支持多 sheet 标签；新引擎插件 V1.6.0 起支持 expandNodeLayer/collapseNodeLayer，并新增 expandAllNodeLayer/collapseAllNodeLayer。
- 动态/批量打印：勾选复选框取值传参到另一模板打印（JAR 2018-04-09 及以上须用新打印方式）；批量打印多模板时页码默认连续累加，可改为各模板页码独立从 1 计。
- 本地打印在 https 环境需到打印软件 conf/https 目录配置证书；Word 报告插件 11.0.6 及之后（插件 2.0.2+）新增零客户端打印，要求 WPS 2021+ 专业版/个人版、暂不支持 MAC。
- 排障：打印失败按「打印常见问题」排查思路核对 FR.doURLPrint / FR.doURLPDFPrint / contentPane.pdfPrint 调用；IE 打印 PDF 无预览可装 IE PDF 预览插件；打印字体太小可用打印样式设置插件做全局或单模板配置。

## 关键 API 与版本要点
- FR.doURLPrint(config)：统一打印入口，config 为 object（printUrl 模板地址、isPopUp 是否弹出设置窗等），使用 get 传参。
- FR.doURLPDFPrint(url)：以 PDF 方式打印指定报表地址，可结合 JS 超链实现传参打印其他报表、控制有无水印。
- contentPane.printReportServer / contentPane.pdfPrint：服务器端打印与 PDF 打印调用点。
- 分页预览专有接口：expandNodeLayer(layer)/collapseNodeLayer(layer)（10.0 已有，仅新引擎插件 V1.6.0+ 支持）；新增 expandAllNodeLayer/collapseAllNodeLayer。
- 11.0.6（Word 报告插件 2.0.2+）：新增零客户端打印；插件 2.0.3+：支持引用当前模板资源免挂载、WPS 原生表格形式导出后可编辑。

## 深入查询
遇到本主题具体问题，读取 `references\print_summary.md` 查 doc-view 原始条目与 ID。
