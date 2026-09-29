<!--
KB_INDEX: {
  "title": "FR11 权限 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["doc", "view", "frontSeed", "FR11", "权限", "Oauth2"],
  "summary": "--- name: fr11-permission description: FR11 权限与认证问题时使用。触发词：权限、角色、用户管理、数据权限、认证、单点登录 SSO、Oauth2、LtpaToken、密码加密、数据脱敏、上报审核。 "
}
-->

---
name: fr11-permission
description: FR11 权限与认证问题时使用。触发词：权限、角色、用户管理、数据权限、认证、单点登录 SSO、Oauth2、LtpaToken、密码加密、数据脱敏、上报审核。
compatibility: FR11
---

# FR11 权限 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/permission权限/references/permission_summary.md`；完整文档条目大表（92 篇 doc-view ID + 标题 + 核心概念 + API）见本目录 `references\permission_summary.md`。

## 主题速览
- 92 篇文档（doc-view ID 70~5137，非连续），标题高频词：权限 41 / 数据 8 / 定时调度 5 / 插件 5
- 覆盖：权限管理体系（用户/角色/目录）、数据权限、单点登录与认证、密码安全传输、上报审核权限
- 15 篇文档含 FR11 子版本（11.0.x）变更要点

## 核心结论
- 权限管理入口在数据决策系统「管理系统」：用户管理、目录管理、权限管理、安全管理等模块；普通用户只能查看权限内报表（doc-view-70）
- 单点登录失败排查路径：① 前台单点直接访问请求看是否成功；② 后台单点看请求中有无 Set-Cookie（有则一般正常）（doc-view-5042）
- 前台单点登录密码安全传输两条官方路线：MD5 系加密（`md5(md5_3(form.p.value))`）或 AES 对称加密（`aesEncrypt(password, frontSeed)`），密钥 `frontSeed` 存于 FINE_CONF_ENTITY 表 id='SecurityConfig.frontSeed'（doc-view-5047/5052）
- 类 Oauth2 单点登录插件支持 Oauth2 认证与自定义认证两种模式，统一认证平台内跨域单点登录/登出；参数含 LtpaToken cookie 方式（doc-view-5037）
- 数据权限可细到列级：定时调度中用公式按用户部门动态控制可见列（`GETUSERDEPARTMENTS()`，doc-view-5029）
- 上报审核有专门的数据权限设置（doc-view-579）
- 2023-02 起新增「数据脱敏」功能，按脱敏规则变形敏感数据（doc-view-5137）
- 帆软服务平台（service.fanruan.com）需企业合作认证，原 QQ 服务渠道 2023-01-03 关停（doc-view-4950/5035，非技术条目）

## 关键 API 与版本要点
- 公式：`GETUSERDEPARTMENTS()` / `GETUSERJOBTITLES()`（取用户部门/职务做数据权限过滤）、`encodeURIComponent()`（单点 URL 编码）
- 加密：`md5_3(s)`、`core_md5(str2binl(s))`、`aesEncrypt(password, frontSeed)`、`BI.aesEncrypt()`
- 认证：LtpaToken（cookie 取值）、Oauth2 跨域 SSO；SQL 示例 `select value from FINE_CONF_ENTITY where id = 'SecurityConfig.frontSeed'`

## 深入查询
遇到本主题具体问题，读取 `references\permission_summary.md` 查 doc-view 原始条目与 ID。
