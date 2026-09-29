<!--
KB_INDEX: {
  "title": "FR11 部署与集群 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["Tomcat", "FR11", "references", "deploy", "cluster", "WebLogic"],
  "summary": "--- name: fr11-deploy-cluster description: 何时使用：需要在服务器上部署（deploy）FR11 报表工程、配置 Tomcat/WebLogic/Nginx/Redis 集群（cluster）、负载"
}
-->

---
name: fr11-deploy-cluster
description: 何时使用：需要在服务器上部署（deploy）FR11 报表工程、配置 Tomcat/WebLogic/Nginx/Redis 集群（cluster）、负载均衡、状态服务器、外接数据库、容器化部署、升级迁移或注册授权与日常运维排障时使用。触发词：部署、集群、Tomcat、Nginx、Redis、升级、lic、websocket。
compatibility: FR11
---

# FR11 部署与集群 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/deploy-cluster部署集群/references/deploy_cluster_summary.md`；完整文档条目大表（doc-view ID + 标题 + 核心概念 + API）见本目录 `references\deploy_cluster_summary.md`。

## 主题速览
- 关键词频次：部署 34 篇、集群 25 篇居前，插件 16、定时调度 6、FVS 6，覆盖安装注册到运维全链路。
- 全类共 315 篇文档，doc-view ID 覆盖 66~5133，其中 94 篇提及 11.0.x 子ckzl/bb，0 篇解析失败。
- 三条主线：容器部署（Tomcat/WebLogic/WebSphere/JBoss/Resin/TongWeb）、集群组件（负载均衡+状态服务器+文件服务器+外置库）、10→11 升级与智能运维。

## 核心结论
- 官网设计器内置 Tomcat 开箱即用；仅远程设计或部署到其他应用服务器时才需服务器部署，Linux 环境推荐用内置 JDK 的部署包（不支持 32 位系统）。
- 容器版本要求：Tomcat 推荐 8.5.57+，JDK 1.8 且小版本 8u102+；WebLogic12c+、WebSphere8.5 同样要求 JDK8u102+。
- 嵌入式部署需把 lib 下 fine 开头 JAR 拷至 WEB-INF/lib；11.0.8 及之前还要额外拷 netty-all-xxx.Final.jar，11.0.9 起内置 netty-all-4.1.78.Final.jar，升级后须删除旧 netty 包。
- 集群架构=负载均衡+状态服务器+文件服务器/节点间同步+外置数据库；状态服务器和外置数据库是开启集群的前置条件，11.0.7 起禁止在节点间同步模式下开集群。
- Nginx 在 Windows Server 上撑不住高并发：并发<300 可用（仅热备场景），>300 必须换 Linux 或其他负载均衡；Redis 集群主节点须为奇数且≥3 个，存活节点少于总数一半则集群不可服务。
- 注册：免费试用版限 2 个并发；服务器 MAC 变化需本地机器信息认证迁移，跨大版本升级需销毁旧 lic；虚拟机/docker 等无固定机器信息环境用本地容器认证。
- 10.0→11.0 属跨大版本升级，官方提供辅助升级程序（JAR/插件/配置/FineDB 兼容升级，免安装多语言）；11.0 内置一键升级；11.0→11.0.1 属小版本升级。
- 配置存储：大部分配置存于 FineDB 的 FINE_CONF_ENTITY 表；系统日志默认 %FR_HOME%\logs\fanruan.log，11.0.4 起支持操作日志实时备份与磁盘运维。
- 宕机与并发：宕机处理可自动生成 DUMP 并重启；address pool is full 报错=并发超注册额度，减并发人数或增购；负载管理（原内存管理）做内存/CPU 实时监控预警。
- 容器化部署工具 FineKey 一条命令部署单机/集群工程，支持非容器化工程迁移为容器化及指令/镜像升级。

## 关键 API 与版本要点
- WebSocket：11.0.2 起新增容器 WebSocket 方案，端口复用 http、免手动配置，推荐优先使用；HTTPS 下老方案需 SSL 证书与单独开放端口。
- 11.0.2：模板限制增强内置、下载日志内置；11.0.3：新增报表检测、外接库迁移提示细化；11.0.4：磁盘运维、操作日志实时备份、「内存管理/内存预警」更名「负载管理/负载监控」。
- 11.0.5：FineDB 新增宕机记录表、超限模板表；11.0.7：禁节点间同步开集群、更新升级弹窗优化；宕机处理功能可自动生成 DUMP 并重启，支持导出堆栈/histo/dump。
- 集群组件出错优化：11.0 起状态服务器/文件服务器故障不再自动降级为节点内存、节点间同步，改为主动提示，避免问题被掩盖。
- JNDI 数据连接：在 Tomcat/WebLogic 配好 JNDI 后设计器按名调用即可（JDBC 驱动放 %Tomcat_HOME%\lib）。

## 深入查询
遇到本主题具体问题，读取 `references\deploy_cluster_summary.md` 查 doc-view 原始条目与 ID。本主题 references 下另有 `fr11_install_survey_report.md`（FR11 安装调研）可查阅安装环境与选型信息。
