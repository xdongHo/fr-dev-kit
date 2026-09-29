<!--
KB_INDEX: {
  "title": "FR11 移动端 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["doc", "view", "App", "mobile_summary", "FR11", "移动端"],
  "summary": "--- name: fr11-mobile description: FR11 移动端开发/预览问题时使用。触发词：移动端、App、HTML5/H5、微信、钉钉、企业微信、小程序、OEM/Custom App 打包、NFC 读卡、移动端填报"
}
-->

---
name: fr11-mobile
description: FR11 移动端开发/预览问题时使用。触发词：移动端、App、HTML5/H5、微信、钉钉、企业微信、小程序、OEM/Custom App 打包、NFC 读卡、移动端填报、移动端导出。
compatibility: FR11
---

# FR11 移动端 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/mobile移动端/references/mobile_summary.md`；完整文档条目大表（192 篇 doc-view ID + 标题 + 核心概念 + API）见本目录 `references\mobile_summary.md`。

### 常见问法：移动端填报怎么清空/重置已填内容？

- ⚠待补登记（作战A6，2026-09-12）：App 与 HTML5 两通道清空/重置行为差异、移动端专属重置接口——mobile_summary 192 篇无此条目（grep 实测 0），待查官方文档后补 `references/mobile_summary.md` 并回填本 SKILL。

## 主题速览
- 192 篇文档（doc-view ID 147~5078，非连续），标题高频词：App 43 / 移动端 33 / 报表 18 / 单元格 8 / JS 6 / 插件 6
- 覆盖：数据分析 App 配置与打包、HTML5 端预览、微信/钉钉/企业微信集成、移动端填报与展示特性、OEM 定制
- 25 篇文档含 FR11 子版本（11.0.x）变更要点

## 核心结论
- 移动端双通道：FineMobile 数据分析 App 与 HTML5 端（部分功能仅其一支持，如 H5 悬浮工具栏插件仅 H5 端、横屏显示仅 App）
- 移动端模板需先设置「移动端属性」（普通报表/决策报表两套），与 PC 端展现差异需专门适配（doc-view-4275）
- 移动端支持 JS 导出接口：`_g().exportReportToExcel('sheet')` / `exportReportToPDF()` / `exportReportToWord()` / `exportReportToImage()`，仅支持普通报表（11.0.37 起，doc-view-3781）
- App 分享支持导出长图（Android 仅 6.0+，doc-view-4041）；移动端填报支持 NFC 读卡输入（11.0.54 起）与连续读卡 `nfcCode()`（11.0.64 起）
- FR 对象移动端专有方法：`FR.location()` 获取经纬度（https/企业微信/钉钉可用，doc-view-4332）
- 微信/钉钉集成前提是网络线路畅通（服务器须能访问微信/钉钉服务器，doc-view-4097）；推送/单点失败用调试页 `/url/weixin/start/debugger` 排查（doc-view-4004）
- 钉钉定时推送支持链接/图文/文件消息，V11.0.74 起支持图片消息（doc-view-3858）
- iOS App 打包需证书：企业开发者账号或 Custom App 模式（配合分发插件生成兑换码链接，doc-view-4252/4345）；打包错误码可自查（doc-view-3536）
- 企业微信旧 IP 停服与自建应用安全升级影响微信集成插件（仅新创建的自建应用受影响，doc-view-4681/4780）
- 移动端安全加固：关闭 DELETE 请求转 POST 等设置见「移动端安全加固手册」（doc-view-5043）
- 常见坑：数据分析 App 不显示参数面板（正常现象，可装顶部参数面板插件，doc-view-4960）

## 关键 API 与版本要点
- `_g().exportReportToExcel/PDF/Word/Image`（11.0.37+）；`nfcCode()` 连续读卡（11.0.64+）；`FR.location(function(status,message){...})`
- 定时调度钉钉图片消息（11.0.74+）；移动端插件 11.0.65+ 支持可见范围为部门
- 平板展示手机效果、折叠展开树、工具栏等依赖插件：fine_conf_entity 可视化配置、移动端折叠展开树（11.0.64+）等

## 深入查询
遇到本主题具体问题，读取 `references\mobile_summary.md` 查 doc-view 原始条目与 ID。
