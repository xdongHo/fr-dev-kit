<!--
KB_INDEX: {
  "title": "FR11 离线文档 i18n 验证报告",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["doc", "view", "i18n", "FR11", "Java", "API"],
  "summary": "> 数据源：`D:fr11_docsdoc-view-{did}.html`（FR11 离线文档，共 2289 篇） > 生成时间：2026-08-26 > 验证方法：全量 2289 篇正文扫描关键词 i18n / 国际化 / 多语言 "
}
-->

# FR11 离线文档 i18n 验证报告

> 数据源：`D:\fr11_docs\doc-view-{did}.html`（FR11 离线文档，共 2289 篇）
> 生成时间：2026-08-26
> 验证方法：全量 2289 篇正文扫描关键词 i18n / 国际化 / 多语言 / 语言包 / locale，命中 41 篇；对命中文档逐篇精读，提取接口与约束。

---

## 1. 验证结论摘要

| 验证项 | 结果 |
|--------|------|
| 扫描文档数 | 2289 篇（全部成功解析，0 无法解析） |
| 命中 i18n 关键词文档 | 41 篇 |
| 文档级 i18n 接口（公式/JS/URL/配置/插件） | ✅ 已逐条核实（见下） |
| Java 类级 i18n API（LocaleFinder 等） | ❌ 未出现在离线 HTML 文档中，无法由此源验证 |
| FR10 专有 i18n 接口对比 | 本文仅报告 FR11 离线文档实际出现内容，FR10 推断不混入 |

## 2. 已核实（出现在离线文档原文，附 doc-view ID）

| 接口/机制 | 出处 | 核实状态 |
|--------|------|----------|
| `i18n("键")` 单元格公式 | doc-view-4591 | ✅ 含用法与局限 |
| `FR.i18nText("键")` 前端函数 | doc-view-4591 | ✅ 含 JS 示例 |
| `fr_locale` URL 参数（zh_CN/zh_TW/en_US/ja_JP/ko_KR） | doc-view-4591 | ✅ |
| `fr_locale` 模板参数+下拉框数据字典 | doc-view-4591 | ✅ 含局限说明 |
| 模板语言工具栏控件 | doc-view-4591 | ✅ |
| 管理系统>语言配置（键-值+批量导入导出） | doc-view-4591 | ✅ |
| 系统语言偏好设置（管理员） | doc-view-4591 | ✅ |
| 国际化切换接口插件（用户级） | doc-view-3209 | ✅ 含版本 V1.9.3 与排障方案 |
| ZHMONEY / ZHLUNAR / DATEFORMAT（locale 参数） | doc-view-4710 | ✅ 含签名与示例 |
| 文本控件校验国际化插件 | doc-view-4778 | ✅ 含区域/数据类型矩阵 |
| App 系统语言（手动/跟随系统） | doc-view-1362 | ✅ |
| 语言切换方法汇总 | doc-view-4748 | ✅ 概述页 |
| 单张报表内中英文切换 | doc-view-3164 | ✅ |
| 日期转化为英文格式 | doc-view-3720 | ✅ |
| itext7 导出及国际化换行插件 | doc-view-5031 | ✅ |
| Linux 中文语言包 | doc-view-2028 | ✅ 部署层 |

## 3. 未在离线文档中出现的 i18n 内容（不作为已确认结论）

1. Java 类级接口（LocaleFinder / AbstractLocaleFinder / InterProvider / InterProviderFactory / LanguageConfig 等）在 2289 篇离线 HTML 中**无任何命中**——离线文档不覆盖平台 Java API 层。
2. 前端 JS 全局对象（如 FR.i18n 相关全局对象）除 `FR.i18nText()` 外无其他出现。
3. FineDB 中 i18n 相关表（FINE_INTERNATIONAL 等）未在离线文档表结构文档中确认（doc-view-3151 FineDB 表结构正文未见该表名断言，需以实际数据库为准）。

## 4. 验证局限

- 离线 HTML 为产品帮助文档，非 API 参考手册；"未出现"不等于"不存在"，仅代表该来源无法佐证。
- 涉及真实 JAR 包的类名/方法签名验证，须用 javap / 反编译手段另行完成。