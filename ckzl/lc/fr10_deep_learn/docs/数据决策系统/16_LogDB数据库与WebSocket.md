<!--
KB_INDEX: {
  "title": "数据决策系统 - LogDB 数据库与WebSocket",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "数据决策系统",
    "LogDB 数据库",
    "WebSocket",
    "管理平台应用"
  ],
  "summary": "「数据决策系统」分页：LogDB 数据库、WebSocket（约 10 篇条目）；FR10 帮助文档「数据决策系统」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 数据决策系统 · LogDB 数据库与WebSocket

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §数据决策系统


## 管理平台应用 > LogDB 数据库（4篇）

### 193. 报表日志 LogDB 数据库

- **doc-view ID**: 891
- **路径**: 数据决策系统 > 管理平台应用 > LogDB 数据库 > 报表日志 LogDB 数据库
- **核心概念**: 为了加强对报表工程的管理，随时监控其运行状态，可以在平台中开启日志记录，如下图所示： 注：系统日志级别的设置仅影响系统日志的输出，不影响操作日志。两种日志的区别请参见：日志简介 。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 为了加强对报表工程的管理，随时监控其运行状态，可以在平台中开启日志记录，如下图所示： 注：系统日志级别的设置仅影响系统日志的输出，不影响操作日志。
- 人员岗位: 未在文中明确指定（面向系统管理员/平台运维人员）
- 功能应用场景: LogDB 数据库是 FineReport 日志监控开启之后，用于保存日志的内置数据库.

**关键代码/公式/API：**
- 公式: `sum(consume)`
- 公式: `COUNT(consume)`
- 公式: `min(consume)`
- 公式: `max(consume)`
- SQL: `select * from fine_record_execute`
- SQL: `select tname, displayName, consume from fine_record_execute`
- SQL: `select sum(consume) from fine_record_execute group by tname, displayName`
- SQL: `select consume from fine_record_execute group by tname, displayName`
- 驱动类: `com.fr.swift.jdbc.Driver`
- JDBC URL: `jdbc:swift:emb://default`

### 194. LogDB 数据库的定时抽取

- **doc-view ID**: 2944
- **路径**: 数据决策系统 > 管理平台应用 > LogDB 数据库 > LogDB 数据库的定时抽取
- **核心概念**: FineReport 10.0 采用了帆软全新开发的 Swift 引擎，以便更好的记录分析 LogDB 数据库的性能，但是目前 Swift 引擎未完善对其他数据库的支撑。所以面临这样的现状： - FineReport 10.0的 LogDB 数据库无法直接迁移 - 直连内置的 LogDB 数据库进行增强分析，有 SQL 语句的限制，有些 SQL 写法不支持。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: FineReport 10.0 采用了帆软全新开发的 Swift 引擎，以便更好的记录分析 LogDB 数据库的性能，但是目前 Swift 引擎未完善对其他数据库的支撑。
- 人员岗位: 未在文中明确指定（面向系统管理员/平台运维人员）
- 功能应用场景: FineReport 10.0 采用了帆软全新开发的 Swift 引擎，以便更好的记录分析 LogDB 数据库的性能，但是目前 Swift 引擎未完善对其他数据库的支撑。

**关键代码/公式/API：**
- 公式: `TODATE($$$)`
- 公式: `= NOW()`
- 驱动类: `com.fr.swift.jdbc.Driver`
- JDBC URL: `jdbc:swift:emb://default（Mac、Windows、Linux通用）`

### 195. 平台日志同步到其他数据库插件

- **doc-view ID**: 3609
- **路径**: 数据决策系统 > 管理平台应用 > LogDB 数据库 > 平台日志同步到其他数据库插件
- **核心概念**: - 目前 LogDB 数据库不支持迁移，用户如果想对日志数据进行一些复杂分析时较为麻烦，希望日志数据可以迁移到自己的数据库中进行管理和分析。- 用户希望把各个系统的日志都放在同一个地方运维管理。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: - 目前 LogDB 数据库不支持迁移，用户如果想对日志数据进行一些复杂分析时较为麻烦，希望日志数据可以迁移到自己的数据库中进行管理和分析。
- 人员岗位: 若勾选「同步失败时，通知管理员」按钮，同步失败时，管理员会收到平台消息。如下图所示：
- 功能应用场景: - 目前 LogDB 数据库不支持迁移，用户如果想对日志数据进行一些复杂分析时较为麻烦，希望日志数据可以迁移到自己的数据库中进行管理和分析。

**关键代码/公式/API：**
- SQL: `delete、alter、update、select、insert 权限。`
- SQL: `update returned unexpected row count from update [0]`

### 196. LogDB 表结构

- **doc-view ID**: 3742
- **路径**: 数据决策系统 > 管理平台应用 > LogDB 数据库 > LogDB 表结构
- **核心概念**: 本文将简单介绍 Logdb 数据库中各个数据表和表字段的含义。**报表(BI)执行表**：报表访问/导出/打印日志，即如果报表访问/导出/打印的时候，将会在该表中添加一条记录，并在相应字段中填写其对应的信息记录。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 本文将简单介绍 Logdb 数据库中各个数据表和表字段的含义。
- 人员岗位: 未在文中明确指定（面向系统管理员/平台运维人员）
- 功能应用场景: **登录表**：用户登录日志，用于记录用户的登录信息。

**关键代码/公式/API：**
- 公式: `gc()`
- 公式: `life(生命周期)`
- 公式: `limit(模板限制)`
- 公式: `release(智能释放)`

---

## 管理平台应用 > WebSocket（6篇）

### 235. Websocket简介

- **doc-view ID**: 2512
- **路径**: 数据决策系统 > 管理平台应用 > WebSocket > Websocket简介
- **核心概念**: WebSocket 转发端口支持设置多个值 本文将从以下几点为大家介绍websocket。1）为什么要设置websocket 2）不设置websocket会怎么样 3）怎么设置websocket 4）websocket设置不生效怎么排查 WebSocket可以让服务器端主动向客户端推送数据。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: WebSocket 转发端口支持设置多个值 本文将从以下几点为大家介绍websocket。
- 人员岗位: 未在文中明确指定（面向系统管理员/平台运维人员）
- 功能应用场景: WebSocket 主要用于刷新 token、用户被踢出、平台消息、内存和 CPU 显示、平台日志处当前系统在线人数、数据连接编辑状态的确定。

### 236. HTTPS配置WebSocket

- **doc-view ID**: 2662
- **路径**: 数据决策系统 > 管理平台应用 > WebSocket > HTTPS配置WebSocket
- **核心概念**: HTTP 是超文本传输协议，信息是明文传输的。HTTPS 协议是由 SSL+HTTP 协议构建的可进行加密传输、身份认证的网络协议，比 HTTP 协议安全。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: HTTP 是超文本传输协议，信息是明文传输的。
- 人员岗位: 未在文中明确指定（面向系统管理员/平台运维人员）
- 功能应用场景: CA证书用于给自己的证书签名。

**关键代码/公式/API：**
- 代码片段: `server { ⏎         listen       443 ssl; ⏎         server_name  192.168.5.232; ⏎       ⏎         ssl_certificate      /mnt/hgfs/share/keys/server.crt; #证书绝对路径 ⏎         ssl_certificate_key  /mnt/hgfs/`
- 代码片段: `server {  ⏎       listen       38889 ssl;             ⏎       server_name  192.168.5.232; ⏎   ⏎       ssl_certificate      /mnt/hgfs/share/keys/server.crt; ⏎       ssl_certificate_key  /mnt/hgfs/share`
- 代码片段: `rewrite ^(.*)$  https://$server_name$1 permanent;`
- URL: `http://FR.com`
- URL: `http://WBS.com`

### 237. 不额外给WebSocket对外开放端口

- **doc-view ID**: 2854
- **路径**: 数据决策系统 > 管理平台应用 > WebSocket > 不额外给WebSocket对外开放端口
- **核心概念**: 部分公司对于工程环境安全级别要求较高，对于开发端口限制较多。若只开放一个端口，websocket往往无法正常连接。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 部分公司对于工程环境安全级别要求较高，对于开发端口限制较多。
- 人员岗位: 管理员登录数据决策系统，点击「管理系统>系统管理>常规」，设置websocket 请求端口。如下图所示：
- 功能应用场景: 部分公司对于工程环境安全级别要求较高，对于开发端口限制较多。

**关键代码/公式/API：**
- 代码片段: `... ⏎ server { ⏎         listen 8888;#监听端口，这个要和上面的WebSocketConfig.requestPort一致 ⏎         server_name _; ⏎         underscores_in_headers on; ⏎         location / { ⏎             proxy_http_version 1.`
- URL: `http://FR.com`
- URL: `http://WBS.com`

### 238. WebSocket连接失败

- **doc-view ID**: 4102
- **路径**: 数据决策系统 > 管理平台应用 > WebSocket > WebSocket连接失败
- **核心概念**: 1）管理员登录数据决策系统，点击「管理系统>智能运维>内存管理」，「内存预警」Tab 下「内存利用率和「CPU 利用率」两张图显示空白。顶部弹出提示信息：Socket 未连接，实时内存显示等异常，相关端口可能未开放 2）管理员登录数据决策系统，点击「管理系统>智能运维>平台日志」，「访问统计」Tab 下「当前系统在线人数」无法正确显示。

**业务场景四要素：**
- 统计指标方案: 顶部弹出提示信息：Socket 未连接，系统访问用户统计等异常，请开启相关端口，相关端口可能未开放
- 业务场景: 适用场景：通过负载均衡访问工程，websocket连接失败
- 人员岗位: 超级管理员可通过填报的方式修改 WebSocket 端口/转发端口。重启服务器后设置生效。
- 功能应用场景: 1）管理员登录数据决策系统，点击「管理系统>智能运维>内存管理」，「内存预警」Tab 下「内存利用率和「CPU 利用率」两张图显示空白。

### 239. 单机配置WebSocket端口

- **doc-view ID**: 4130
- **路径**: 数据决策系统 > 管理平台应用 > WebSocket > 单机配置WebSocket端口
- **核心概念**: 本文将介绍在单机环境下，如何配置 WebSocket 端口。超级管理员可通过「fine_conf_entity可视化配置插件」修改 WebSocket 端口。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 本文将介绍在单机环境下，如何配置 WebSocket 端口。
- 人员岗位: 超级管理员可通过「fine_conf_entity可视化配置插件」修改 WebSocket 端口。重启服务器后设置生效。
- 功能应用场景: 本文将介绍在单机环境下，如何配置 WebSocket 端口。

### 240. 集群配置WebSocket端口

- **doc-view ID**: 4131
- **路径**: 数据决策系统 > 管理平台应用 > WebSocket > 集群配置WebSocket端口
- **核心概念**: 本文将介绍在集群环境下，如何配置 WebSocket 端口。超级管理员可通过「fine_conf_entity可视化配置插件」修改 WebSocket 端口。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为平台管理功能/操作说明，无具体统计指标）
- 业务场景: 本文将介绍在集群环境下，如何配置 WebSocket 端口。
- 人员岗位: 超级管理员可通过「fine_conf_entity可视化配置插件」修改 WebSocket 端口。重启服务器后设置生效。
- 功能应用场景: 本文将介绍在集群环境下，如何配置 WebSocket 端口。

**关键代码/公式/API：**
- 代码片段: `#用户或者用户组 默认为nobody ⏎ #user  root; ⏎ #允许进程数量，建议设置为cpu核心数或者auto自动检测，注意Windows服务器上虽然可以启动多个processes，但是实际只会用其中一个 ⏎ worker_processes  auto; ⏎ #自动根据CPU数目绑定CPU亲缘性，nginx1.9.10及以上版本才能用 ⏎ #worker_cpu_affinity  `
- 公式: `fall(fall_count)`
- 公式: `rise(rise_count)`
- URL: `http://FR.com`
- URL: `http://WBS.com`

---
