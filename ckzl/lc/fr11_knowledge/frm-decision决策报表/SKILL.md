<!--
KB_INDEX: {
  "title": "FR11 决策报表 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["frm", "Tab", "实测", "body", "决策报表", "报表块"],
  "summary": "--- name: fr11-frm-decision description: 何时使用：制作 FR11 决策报表（FRM）大屏/驾驶舱/移动端看板、处理 body 布局与 PC 端自适应、组件（报表块/图表块/Tab块）联动、JS 接口"
}
-->

---
name: fr11-frm-decision
description: 何时使用：制作 FR11 决策报表（FRM）大屏/驾驶舱/移动端看板、处理 body 布局与 PC 端自适应、组件（报表块/图表块/Tab块）联动、JS 接口或 FVS 大屏插件时使用。触发词：决策报表、frm、报表块、Tab块、绝对布局、自适应、组件接口、FVS。
keywords: [新自适应引擎, 决策报表布局, 布局方式, 自适应, 报表块, Tab块, 绝对布局]
compatibility: FR11
---

# FR11 决策报表 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/frm-decision决策报表/references/frm_decision_summary.md`；完整文档条目大表（doc-view ID + 标题 + 核心概念 + API）见本目录 `references\frm_decision_summary.md`。

## 主题速览
- 关键词频次：报表 49 篇、决策报表 35 篇、FVS 19 篇、JS 10 篇，组件设计与 JS 接口是两大重心。
- 全类共 123 篇文档，doc-view ID 覆盖 132~5121，其中 37 篇提及 11.0.x 子ckzl/bb，0 篇解析失败。
- 覆盖：决策报表设计（body/布局/自适应）、组件体系（报表块/图表块/Tab块/绝对画布块）、联动与 JS 接口、FVS 大屏插件、数据门户插件。

## 核心结论

### 常见问法：frm 决策报表跟 cpt 有什么区别、什么时候用 frm？/ frm 打开布局乱，新版自适应引擎怎么用？/ 决策报表 body 的 PC 端自适应在哪设置？/ 决策报表里报表块和图表块怎么联动？

| 口语问题 | 落点（本文件实读内容） |
|---|---|
| frm 和 cpt 的区别/选型 | 决策报表与普通报表、聚合报表并列；组件添加更自由，专为大屏和移动端而生；预览方式为 PC 端预览、开发者调试、移动端预览【实测·本文件核心结论】 |
| 布局乱/自适应引擎用法 | 布局方式分自适应布局（非固定/固定两种效果）与绝对布局；11.0 内置 10.0 新自适应插件优化效果，另有「旧版决策报表」模式兼容 10.0 模板【实测·本文件】 |
| PC 端自适应设置入口 | 11.0.3 起 body 自适应设置由右侧属性面板移至菜单「模板>PC端自适应属性」；开发者调试预览所见即所得，自适应缩放以模板初始效果为基准【实测·本文件】 |
| 报表块/图表块联动 | 「当前决策报表对象」超链（决策报表专有）实现报表块/图表块联动；body 控件无查询按钮需 JS 传参，数据集用 ${if(len(area)=0,""," and 地区='"+area+"'")} 处理空参数；数据变化后不自动刷新用 dataRefresh()+setTimeout【实测·本文件】 |
- 决策报表与普通报表、聚合报表并列；组件添加更自由，专为大屏和移动端而生；预览方式为 PC 端预览、开发者调试、移动端预览。
- 布局方式分自适应布局（含非固定/固定两种效果）与绝对布局；11.0.3 起 body 自适应设置由右侧属性面板移至菜单「模板>PC端自适应属性」。
- 11.0 内置 10.0 新自适应插件优化自适应效果，并新增「旧版决策报表」模式兼容 10.0 模板；11.0.2 统一新旧版设计界面展示逻辑。
- 11.0.5 新增「决策报表计算设置」可开启报表块并行计算提效；11.0.7 FRM 重构合并计算替代 10.0 懒加载逻辑，用了懒加载的报表升级后需手动开启并行计算。
- 联动核心：「当前决策报表对象」超链（决策报表专有）实现报表块/图表块联动；body 中控件无法直接用查询按钮，需 JS 传参自动查询，数据集用 ${if(len(area)=0,""," and 地区='"+area+"'")} 处理空参数。
- 组件接口套路：先 _g().getWidgetByName('组件名') 取组件，再调 setVisible/gotoPage/showCardByIndex/dataRefresh 等；决策报表接口仅 frm 可用，普通报表、聚合报表不能使用。
- 报表块数据变化后联动图表不自动刷新时，用 dataRefresh() + setTimeout 刷新；报表块刷新插件与跑马灯接口互斥，且不支持移动端。
- 11.0.9：图片控件插件合并入设计器（此前需装图片控件设计器插件）；新增模板级「全局查找与替换」；11.0.12 优化「重复与冻结」设置界面。
- FVS 为插件形态（FVS大屏编辑模式）：11.0.2-V1.2.0 起除表格组件外字体单位统一 px；11.0.5-V1.4.0 表格组件与极速版合并；11.0.6-V1.8.0 画布自适应新增「双向铺满」；监控视频组件仅支持 hls 协议。
- 坑点：跨 sheet/跨报表块公式含 {} 条件无效，改用 greparray；Chrome 默认最小字号 12 号，自适应缩字号会被钳制；组件叠加无图层顺序概念，用复制/剪切粘贴调整层叠顺序。

## 关键 API 与版本要点

### 常见问法：决策报表的报表块/Tab块/图表块用什么 JS 接口取和控制？/ Tab 块怎么取当前页索引、切换页签？/ frm 怎么用 URL 导出？/ 决策报表怎么定时刷新或轮播？

| 口语问题 | 落点（本文件实读内容） |
|---|---|
| 取组件再操作 | 先 _g().getWidgetByName('组件名')，再调 setVisible/gotoPage/showCardByIndex/dataRefresh 等；决策报表接口仅 frm 可用，普通报表、聚合报表不能使用【实测·本文件核心结论】 |
| Tab 块当前页/切页签 | getShowIndex() 取当前索引、showCardByIndex(i) 切换页签、setTabVisible/setTitleVisible 控制显示（10.0 已支持无变动）【实测·本文件】 |
| frm 的 URL 导出参数 | 11.0.1 起 &op=export&format=xxx（此前 &export_format=xxx），可加 &__filename__=文件名【实测·本文件】 |
| 定时刷新/轮播 | setInterval('location.reload();',10000) 整体刷新；Tab 轮播 showCardByIndex + setInterval；地图数据点提示轮播 openAutoTooltip([delay, initPoints])【实测·本文件】 |
- 组件通用接口（10.0 已支持，无变动）：getWidgetByName、setVisible/visible/invisible，适用于绝对画布块、报表块、Tab块、图表块、控件。
- Tab 组件接口：getShowIndex() 取当前索引、showCardByIndex(i) 切换页签、setTabVisible/setTitleVisible 控制显示。
- 11.0 新增报表块工具栏接口 getToolbar(index)；导出接口 11.0.1 起为 &op=export&format=xxx（此前 &export_format=xxx），可加 &__filename__=文件名。
- 定时刷新与轮播：setInterval('location.reload();',10000)；Tab 轮播用 showCardByIndex + setInterval；地图数据点提示轮播联动用 openAutoTooltip([delay, initPoints])。
- 开发者调试预览可所见即所得调布局：该预览下效果正常则 PC 端预览一定正常，自适应缩放以模板初始效果为基准。

## 深入查询
遇到本主题具体问题，读取 `references\frm_decision_summary.md` 查 doc-view 原始条目与 ID。
