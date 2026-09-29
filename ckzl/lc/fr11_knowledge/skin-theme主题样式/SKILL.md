<!--
KB_INDEX: {
  "title": "FR11 主题与样式 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["doc", "view", "FVS", "FR11", "模板主题", "主题"],
  "summary": "--- name: fr11-skin-theme description: FR11 外观样式与主题问题时使用。触发词：主题、皮肤、样式、配色、外观、单元格样式、跟随主题、FVS 模板主题、菜单主题、style 属性、控件风格。 keyw"
}
-->

---
name: fr11-skin-theme
description: FR11 外观样式与主题问题时使用。触发词：主题、皮肤、样式、配色、外观、单元格样式、跟随主题、FVS 模板主题、菜单主题、style 属性、控件风格。
keywords: [主题切换, 跟随主题, 主题样式, 皮肤, 配色, 模板主题, 单元格样式]
compatibility: FR11
---

# FR11 主题与样式 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/skin-theme主题样式/references/skin_theme_summary.md`；完整文档条目大表（58 篇 doc-view ID + 标题 + 核心概念 + API）见本目录 `references\skin_theme_summary.md`。

## 主题速览
- 58 篇文档（doc-view ID 142~5109，非连续），标题高频词：样式 12 / 主题 9 / 单元格 7 / FVS 5 / 图表 4 / 插件 4
- 覆盖：单元格样式体系、主题/皮肤配置、FVS 模板主题与组件样式、JS 样式接口、主题相关插件
- 11 篇文档含 FR11 子版本（11.0.x）变更要点

## 核心结论
- 单元格属性含「扩展/样式/形态/其他」四方面；样式可「跟随主题」或「自定义」，控制文本、背景、边框、对齐（doc-view-142）
- JS 样式属性 style 符合 CSS 规范，用于 `setStyle(opts)` 设单元格样式、`showToolTip(opts)` 设提示框样式；11.0.70 起新增该样式属性（doc-view-4863）
- FVS：V1.5.0（11.0.6）新增「模板主题」功能，当前仅支持对模板内「控件组件」样式统一设置（doc-view 相关条目）；V1.5.1 起组件样式支持圆角、毛玻璃、倒影、阴影（doc-view-4217）
- FVS 三维：模型数据预警（条件满足突出显示，V1.4.0）、自定义模型「线框风格」（V1.7.0 风格预处理）（doc-view-4820/4828）
- 数据门户插件支持门户样式设置与一键切换看板样式，页面/组件样式可跟随主题（11.0.7/V1.0 起，doc-view-4842）
- 旧版控件风格回退：装「控件以 711 版本的外观展示」插件可恢复 7.1.1 控件风格（doc-view-5109）
- 「菜单主题」插件把左侧二级菜单移到顶部导航栏，获得更完整展现区域（doc-view-4884）

## 关键 API 与版本要点
- `_g().getWidgetByName('report0').getCell(1,1).setStyle({...})`、`showToolTip({style:...})`（11.0.70+）
- FVS 版本线：V1.4.0 模型数据预警（11.0.5）→ V1.5.0 模板主题（11.0.6）→ V1.5.1 圆角/毛玻璃/倒影/阴影 → V1.7.0 线框风格
- 11.0.6/V1.8.0 起 FVS 组件可见性改由组件图层控制（取消「预览时可见」设置项）

## 深入查询
遇到本主题具体问题，读取 `references\skin_theme_summary.md` 查 doc-view 原始条目与 ID。
