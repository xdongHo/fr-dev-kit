<!--
KB_INDEX: {
  "title": "FR11 · 数据源 · FineDB / LogDB / 专项数据库插件",
  "stage": "fr11-knowledge",
  "tags": [
    "FR11",
    "数据源",
    "数据连接"
  ],
  "keywords": [
    "FineDB",
    "LogDB",
    "MongoDB",
    "SAP",
    "多维数据库",
    "身份验证"
  ],
  "summary": "FineDB 外接、LogDB、MongoDB/SAP/多维等专项数据库插件与身份验证条目（5 条 doc-view 条目，ID 120~2944）；data_source_summary.md 拆分页 4/5，条目原样保留。"
}
-->

# FR11 知识库 · 数据源 · FineDB / LogDB / 专项数据库插件

> 数据源：`D:\fr11_docs\doc-view-{did}.html`（FR11 离线文档，gb2312）。
> 本页为 [data_source_summary.md](data_source_summary.md) 2026-09-29 主题拆分页 **4/5**；条目内容原样搬移、未做改写；归类方法：按条目标题关键词启发式（延续建库打分思路），页内保持原 doc-view ID 升序。
> 本页收录 **5 条**（ID 120~2944，非连续）。

## 文档条目

### doc-view-120｜多维数据库
- **doc-view ID**：120
- **核心概念**：利用 多维数据库插件 连接后就可以新增 XMLA 数据集 1）在模板数据集面板中点击添加按钮，新建一个「多维数据库」，如下图： 2）进入多维数据库 XMLA 数据集配置界面，XMLA 数据集查询取数方式包括「简单通用查询」和「自定义 MDX 查询」两种：
### doc-view-1413｜MongoDB 数据库插件
- **doc-view ID**：1413
- **核心概念**：MongoDB 作为一款非常流行的 NoSQL 数据库，越来越被广泛地使用，但是帆软报表中 JDBC 和 JNDI 都无法连接 MongoDB 进行取数，安装该插件可以连接 MongoDB 数据库。 有关 MongoDB 的介绍和使用方法可以参阅MongoDB官方帮助文档的说明。 设计器菜单栏服务器>定义数据连接处会新增MongoDB类型的数据连接方式。
- **关键API/代码**：公式: ISODate("2019-08-31T12:50:11.000Z")；公式: ISODate()；公式: ISODate('2019-01-01T00:00:00.000Z')；公式: Date()
### doc-view-1432｜实现基于数据库的身份验证
- **doc-view ID**：1432
- **核心概念**：进行基于数据库的身份验证，允许不同用户都能够实现登录。 本文以 MySQL 数据库为例进行操作。 注：如果使用 mysql 8.0 版本，需要下载 mysql-connector-java-5.1.46.jar(Feb. 2018版本)。
- **关键API/代码**：SQL: select userpass from userinfo where username=?" />；公式: jar(Feb. 2018版本)
### doc-view-1573｜FineDB 数据库简介
- **doc-view ID**：1573
- **核心概念**：数据决策系统中除平台属性配置以外的所有信息，包括目录树设置、模板定时任务信息等，均存储于一个数据库中，我们 FineDB 数据库。 FineReport 支持使用内置 FineDB 数据库或启用外接 FineDB 数据库。 FineReport 报表工程内置了一个 HSQL 数据库，作为 FineDB 数据库。
- **关键API/代码**：Java: com.fr.third.org.hsqldb.jdbcDriver
### doc-view-2944｜LogDB 数据库的定时抽取
- **doc-view ID**：2944
- **核心概念**：FineReport 11.0 采用了帆软全新开发的 Swift 引擎，以便更好的记录分析 LogDB 数据库的性能，但是目前 Swift 引擎未完善对其他数据库的支撑。所以面临这样的现状： FineReport 11.0的 LogDB 数据库无法直接迁移 直连内置的 LogDB 数据库进行增强分析，有 SQL 语句的限制，有些 SQL 写法不支持。
- **关键API/代码**：Java: com.fr.swift.jdbc.Driver；公式: TODATE($$$)；公式: NOW()

> 本页收录 doc-view ID（5 条）：120、1413、1432、1573、2944
