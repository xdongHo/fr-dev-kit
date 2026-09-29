<!--
KB_INDEX: {
  "title": "FR11 参数与控件 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["doc", "view", "FVS", "SQL", "FR11", "控件"],
  "summary": "--- name: fr11-param-control description: FR11 参数查询与控件问题时使用。触发词：参数、参数面板、控件、下拉框、下拉复选框、日期控件、查询按钮、参数联动、参数为空、控件接口、FVS 控件。 co"
}
-->

---
name: fr11-param-control
description: FR11 参数查询与控件问题时使用。触发词：参数、参数面板、控件、下拉框、下拉复选框、日期控件、查询按钮、参数联动、参数为空、控件接口、FVS 控件。
compatibility: FR11
---

# FR11 参数与控件 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/param-control参数控件/references/param_control_summary.md`；完整文档条目大表（287 篇 doc-view ID + 标题 + 核心概念 + API）见本目录 `references\param_control_summary.md`。

## 主题速览
- 287 篇文档（doc-view ID 72~5115，非连续），标题高频词：控件 99 / 参数 72 / JS 37 / 报表 24 / FVS 9 / 填报 8
- 覆盖：参数面板与查询控件、下拉框系列控件、参数联动（SQL/公式两条路线）、控件 JS 接口、FVS 控件组件
- 44 篇文档含 FR11 子版本（11.0.x）变更要点

## 核心结论
- 控件接口统一入口：先 `getWidgetByName()` 获取控件再设属性（赋值/隐藏/禁用），可用于 Web 页面事件、控件事件、组件事件；接口分获取接口 + 通用/专有属性接口（doc-view-5100）
- 「查询按钮」= 内置查询功能的按钮控件，仅用于参数查询场景，定义参数后参数面板自动生成，也可拖入添加（doc-view-5088）
- 参数联动三路线：① SQL() 函数数据字典引用前序参数过滤（doc-view-1284/1285）；② 公式/数据集函数（文件数据集、内置数据集无法用 SQL 时，且大数据量时内置数据集联动更快，doc-view-3634/4181）；③ JS 事件控制（可见性 `setEnable`、编辑前/后事件做层级校验，doc-view-3120 等）
- 「参数为空查询全部」在大数据量下伤性能，可用公式让参数为空时改查特定时间段（doc-view-5115/4455）
- 下拉框显示值可用 value 公式合并多列（如学号+姓名）；默认选第 1 个值通过给控件赋值结合 SQL 函数实现
- 日期控件坑：不支持 integer 类型参数（11.0.12 起已适配）；单独显示年需 11.0.5+（doc-view 相关版本表）
- 非标准日期字符串（20200101、2020/05）需先 replace/left 公式转换再与日期控件匹配（doc-view-5107）
- FVS 六种控件组件（文本框/日期时间/下拉框/下拉复选框/单选按钮组/复选按钮组）11.0.6/V1.5.0 新增，均支持参数联动其他组件；轮播器接口 `getShowIndex()`/`showCardByIndex()` 11.0.9/V1.9.1 起支持
- 11.0.11 起 V8Painter 插件合并进主产品（防 V8 远程代码执行漏洞），旧插件升级后自动禁用（doc-view-5041）
- 中文拼音搜索浪费性能可用「只支持中文搜索的下拉框控件」插件规避（doc-view-3366）

## 关键 API 与版本要点
- `getWidgetByName("name")` / `getValue()` / `setValue()` / `setEnable(boolean)` / `setVisible()`
- SQL() 内置公式做下拉（复选）框联动数据字典；`ds1.select()`/`ds1.group()` 做公式联动；`TABLEDATAFIELDS()` 取列名
- FVS：`getShowIndex()`、`showCardByIndex()`（11.0.9/V1.9.1）、`setTabVisible`（V1.10.1）；FVS 下拉框 11.0.6/V1.8.0 取消「预览时可见」改组件图层控制

## 深入查询
遇到本主题具体问题，读取 `references\param_control_summary.md` 查 doc-view 原始条目与 ID。
