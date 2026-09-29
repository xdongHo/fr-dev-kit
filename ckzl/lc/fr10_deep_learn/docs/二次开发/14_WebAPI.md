<!--
KB_INDEX: {
  "title": "二次开发 - Web API",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "二次开发",
    "Web API"
  ],
  "summary": "「二次开发」分页：Web API（约 2 篇条目）；FR10 帮助文档「二次开发」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 二次开发 · Web API

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §二次开发


## Web API（2篇）

### 103. 数据JSON服务API

- **doc-view ID**: 3894
- **路径**: 二次开发 > Web API > 数据JSON服务API
- **核心概念**: FR系统提供了强大的数据支持功能，支持多种数据库和类型，并提供了异构数据源模型，使得同一张报表的数据可以来源于同一数据库的多个不同表，或多个不同数据库。数据JSON服务API功能插件是将报表数据集、报表结果输出为JSON格式内容，并作为WEB接口服务开放，提供给报表系统前端或者其他系统使用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FR系统提供了强大的数据支持功能，支持多种数据库和类型，并提供了异构数据源模型，使得同一张报表的数据可以来源于同一数据库的多个不同表，或多个不同数据库。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: l sign：安全签名（用于签名认证，可选）；

**关键代码/公式/API：**
- 代码片段: `$.ajax({ ⏎  url: "http://localhost:8075/webroot/decision/url/api/data", ⏎  type: "POST", ⏎  contentType: "application/json;charset=utf-8", ⏎  dataType: "json", ⏎  data: JSON.stringify({ ⏎  "report_pat`
- URL: `http://ip`
- URL: `http://localhost`
- Java类/方法: `data.toString()`

### 104. Web API

- **doc-view ID**: 4500
- **路径**: 二次开发 > Web API > Web API
- **核心概念**: WebAPI 是网络应用程序接口，包含了广泛的功能。网络应用通过 API 接口，可以实现存储服务、消息服务、计算服务等能力，利用这些能力可以开发出强大功能的 Web 应用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: WebAPI 是网络应用程序接口，包含了广泛的功能。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: WebAPI 是网络应用程序接口，包含了广泛的功能。

---
