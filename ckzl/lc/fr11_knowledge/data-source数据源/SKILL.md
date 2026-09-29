<!--
KB_INDEX: {
  "title": "FR11 数据源 核心结论",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["SQL", "数据集", "data", "FR11", "FineDB", "连接"],
  "summary": "--- name: fr11-data-source description: FR11 数据源/data source 场景使用：定义数据连接（JDBC/JNDI/ODBC）、创建数据集（SQL/内置/文件/程序/树数据集）、驱动管理、F"
}
-->

---
name: fr11-data-source
description: FR11 数据源/data source 场景使用：定义数据连接（JDBC/JNDI/ODBC）、创建数据集（SQL/内置/文件/程序/树数据集）、驱动管理、FineDB 外接数据库、连接池与取数性能问题时查阅。
compatibility: FR11
---

# FR11 数据源 核心结论

> 降级自 `ckzl/lc/fr11_knowledge/data-source数据源/references/data_source_summary.md`；完整文档条目大表（doc-view ID + 标题 + 核心概念 + API）见本目录 `references\data_source_summary.md`。

## 主题速览
- 主题范围：数据连接/数据集/数据库/驱动管理/FineDB；共 179 篇文档（doc-view ID 覆盖 100~5130），其中 44 篇提及 FR11 子版本号（11.0.x），0 篇解析失败。
- 标题关键词频次：数据 147、数据集 50、数据库 27、报表 12、插件 7。
- 数据连接两种建立途径：数据决策系统（服务器>报表平台管理）建立平台数据连接，或设计器「服务器>定义数据连接」；连接方式含 JDBC、JNDI、ODBC 等。
- 数据集类型丰富：数据库查询（SQL）、内置数据集、存储过程、关联数据集、树数据集、文件数据集（TXT/Excel/XML/CSV）、SAP 数据集、多维数据库（XMLA/MDX）、程序数据集（Java）等。
- FineReport 报表天然支持多数据源报表：一张报表可定义多个数据集（ds1、ds2…），所取表甚至可来自不同数据库。

## 核心结论
- 数据集管理 11.0.4 优化：新增「搜索」「复制」「批量选择数据集」；11.0.7 数据表搜索框移至上方。
- 树数据集用于组织树/层级结构：按「原始标记字段+父标记字段」自动递归层级，配合下拉树/折叠树控件；树结构配置错误或不完整会导致同步失败，需做完整性检查。
- 连接池核心是连接复用；定义数据连接、预览数据集都会占用连接，多数据集执行可能耗尽连接池（如 Oracle 报 ORA-12519），可用 V$process / V$parameter 查询进程数与最大连接数排查。
- 数据集何时执行直接影响性能：大数据量展开慢、数据集多时执行会创建数据连接；大数据量报表可用行式引擎（仅单数据集明细报表，不支持移动端）或手写分页 SQL（ROW_NUMBER()/top/limit + 页码参数）提速。
- 排序三种类型：数据集中排序（SQL ORDER BY，性能最佳但 SQL 复杂难维护）、高级排序（扩展前排序，依赖数据列）、扩展后排序；11.0.3 及之后支持多列排序与动态排序（点击表头）。
- 数据集函数 select(colname,筛选条件)/sql() 可在单元格按条件取数；限制：参数面板不支持使用、不支持模拟计算。
- 动态切换数据库/模式/表：把数据连接中的配置改为参数（如 select * from ${tablename}），预览时用 url 拼接参数访问不同库。
- 内置 FineDB 是 HSQL 数据库，存储目录树、定时任务等平台配置；HSQL 不能多线程访问，集群/大数据量下不稳定，正式使用必须配置外接数据库；LogDB 日志库基于 Swift 引擎，无法直接迁移，可装插件定期同步到其他数据库。
- 常见坑：连接 MySQL8 优先用平台 MySQL 连接，连不上再装 MySQL8 数据连接插件；Oracle 连接建议取消「显示Oracle所有表」避免性能问题；SQL Server 报 TCP/IP 连接失败需排查网络与配置。
- 11.0.13 新增「数据脱敏」：支持数据源脱敏与单元格脱敏，规则支持平台配置/本地配置，可部分或全部替换字符。

## 关键 API 与版本要点
- 11.0.1：新增「驱动管理」，上传驱动包实现热加载；11.0.5 默认禁止通过驱动管理上传驱动，可用 SystemConfig.driverUpload 参数控制开关。
- 11.0.3：设计器 JDBC 数据连接新增 SSH 设置、MySQL 数据连接新增 SSL 设置，提升安全性。
- 11.0.10：平台数据连接管理新增「数据连接超时检测」功能。
- 11.0.5：选择 Postgre 系列数据库连接时，只能添加连接时所选模式下的数据表。
- 程序数据集：继承 com.fr.data.SimpleTableData，实现 initColumnNames()/loadData() 等方法；支持带参程序数据集、EJB/WebService 程序数据集。
- 内置 FineDB 驱动类 com.fr.third.org.hsqldb.jdbcDriver；LogDB 直连驱动 com.fr.swift.jdbc.Driver（有 SQL 写法限制）。
- 文件数据集：Excel 数据集上传不超过 20M；CSV 数据集、多 sheet Excel 数据集需安装插件。

## 深入查询
遇到本主题具体问题，读取 `references\data_source_summary.md` 查 doc-view 原始条目与 ID。
