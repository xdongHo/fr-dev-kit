<!--
KB_INDEX: {
  "title": "Stage 6: Web 呈现层（导航）",
  "stage": "pipeline",
  "tags": [
    "CSS",
    "Web",
    "工具栏",
    "注入"
  ],
  "keywords": [
    "CSSImport",
    "afterinit",
    "WebWriteContent",
    "ReportWebAttr"
  ],
  "summary": "导航页：原单文件已按既有章节边界拆分为 4 个分篇（单篇 ≤400 行，2026-09-29 断链治理）；原路径保留导航，按分篇表进入。"
}
-->

# Stage 6: Web 呈现层

> 来源: `ckzl/gf/FR_HEADLESS_GUIDE.md` 流水线拆分

---

> **导航页（2026-09-29 拆分治理）**：原单文件 751 行已按既有章节边界拆为 4 个分篇（单篇 ≤400 行）。原路径保留为导航页，AGENTS.md / 铁律 / 节点文档对本文件的引用不断链（G05）。

| 分篇 | 覆盖章节 | 内容 |
|---|---|---|
| [01_Web属性](01_Web属性.md) | §11 Web 属性 | Web 属性配置（ReportWebAttr）：分页预览/填报页面/数据分析三态设置、工具栏按钮、页面框架 |
| [02_参数面板CSS注入](02_参数面板CSS注入.md) | §22 参数面板 CSS 注入 | CSSImport 注入位置、afterinit 事件、参数面板样式覆盖 |
| [03_导出下载与定时刷新](03_导出下载与定时刷新.md) | §23-§24 导出下载/定时刷新 | 导出/下载（URL/分Sheet/大数据集/sessionID 复用）、ShortCut 按钮对照、决策报表定时刷新（表单级事件） |
| [04_移动端H5_集成与前端JS](04_移动端H5_集成与前端JS.md) | §25-§30 移动端/集成/URL字典/超链/图表JS/FR.ajax | 移动端与 H5 预览、嵌入与被嵌入（集成）、集成 URL 参数字典、超链接装配补充、图表 JS 接口速查、FR.ajax 前端请求 |
