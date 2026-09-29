<!--
KB_INDEX: {
  "title": "数据准备 - JNDI数据连接与其他数据库",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "数据准备",
    "JNDI数据连接",
    "其他数据库",
    "数据连接"
  ],
  "summary": "「数据准备」分页：JNDI数据连接、其他数据库（约 13 篇条目）；FR10 帮助文档「数据准备」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 数据准备 · JNDI数据连接与其他数据库

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §数据准备


## 数据连接 > JNDI数据连接（3篇）

### 58. [设计器]JNDI连接数据库

- **doc-view ID**: 102
- **路径**: 数据准备 > 数据连接 > JNDI数据连接 > [设计器]JNDI连接数据库
- **核心概念**: 通过 JNDI 方式定义数据连接，首先在应用服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，选择连接数据库所需要的驱动程序等操作，即可成功使用 JNDI 连接。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 通过 JNDI 方式定义数据连接，首先在应用服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，选择连接数据库所需要的驱动程序等操作，即可成功使用 JNDI 连接。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 通过 JNDI 方式定义数据连接，首先在应用服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，选择连接数据库所需要的驱动程序等操作，即可成功使用 JNDI 连接。

### 59. [设计器] WebLogic 配置 JNDI 连接

- **doc-view ID**: 295
- **路径**: 数据准备 > 数据连接 > JNDI数据连接 > [设计器] WebLogic 配置 JNDI 连接
- **核心概念**: 通过 JNDI 方式定义数据连接，首先在 Weblogic 服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，即可成功使用JNDI连接，连接步骤如下： 使用版本及环境 下面以 Windows Server 2008，Weblogic 12c，jdk 1.8，连接 Oracle 11c 数据库进行 JNDI 连接说明，其他版本数据库步骤基本相同。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 通过 JNDI 方式定义数据连接，首先在 Weblogic 服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，即可成功使用JNDI连接，连接步骤如下： 使用版本及环境 下面以 Windows Server 2008，Weblogic 12c，jdk 1.8，连接 Oracle 11c
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 通过 JNDI 方式定义数据连接，首先在 Weblogic 服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，即可成功使用JNDI连接，连接步骤如下： 使用版本及环境 下面以 Windows Server 2008，Weblogic 12c，jdk 1.8，连接 Oracle 11c

**关键代码/公式/API：**
- 代码片段: `<resource-ref> ⏎       <description>DB Connection</description> ⏎       <res-ref-name>jdbc/TestDB</res-ref-name> ⏎       <res-type>javax.sql.DataSource</res-type> ⏎       <res-auth>Container</res-auth`

### 60. [设计器]Tomcat配置JNDI连接

- **doc-view ID**: 297
- **路径**: 数据准备 > 数据连接 > JNDI数据连接 > [设计器]Tomcat配置JNDI连接
- **核心概念**: 通过 JNDI 方式定义数据连接，首先在 Tomcat 服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，即可成功使用 JNDI 连接，连接步骤如下： 使用版本及环境 下面以 Windows10 系统，Tomcat 8.5.5，jdk 1.8，连接 mysql 5.1.73 数据库进行 JNDI 连接说明，其他版本数据库步骤基本相同。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 通过 JNDI 方式定义数据连接，首先在 Tomcat 服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，即可成功使用 JNDI 连接，连接步骤如下： 使用版本及环境 下面以 Windows10 系统，Tomcat 8.5.5，jdk 1.8，连接 mysql 5.1.73 数据库进
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 通过 JNDI 方式定义数据连接，首先在 Tomcat 服务器配置好 JNDI，然后在设计器中直接调用 JNDI 的名字，即可成功使用 JNDI 连接，连接步骤如下： 使用版本及环境 下面以 Windows10 系统，Tomcat 8.5.5，jdk 1.8，连接 mysql 5.1.73 数据库进

**关键代码/公式/API：**
- 代码片段: `<Resource name="jdbc/TestDB" auth="Container" type="javax.sql.DataSource" ⏎                maxActive="100" maxIdle="30" maxWait="10000" ⏎                username="yourusername" password="yourpassword"`
- 代码片段: `<resource-ref> ⏎       <description>DB Connection</description> ⏎       <res-ref-name>jdbc/TestDB</res-ref-name> ⏎       <res-type>javax.sql.DataSource</res-type> ⏎       <res-auth>Container</res-auth`
- 驱动类: `com.mysql.jdbc.Driver`
- JDBC URL: `jdbc:mysql://112.124.109.239:3306/test`

---

## 数据连接 > 其他数据库（10篇）

### 61. SAP 数据集插件

- **doc-view ID**: 103
- **路径**: 数据准备 > 数据连接 > 其他数据库 > SAP数据连接 > SAP 数据集插件
- **核心概念**: 启用「SAP数据集插件」后，可连接 SAP 系统，并在数据集中添加 SAP 数据集类型。安装插件 SAP 数据集，安装方法参考以下文档： 设计器插件安装方法参照 设计器插件管理 服务器安装插件方法参照 服务器插件管理 与 SAP 系统进行连接，需要导入 SAP 接口包和本地库，并确保运行的 JVM 能够找到接口包和本地库。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 启用「SAP数据集插件」后，可连接 SAP 系统，并在数据集中添加 SAP 数据集类型。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: SAP系统名：SAP 系统中设置的属性，用于交互的端口号，一般来说是 00，具体根据 SAP 系统来定。

### 62. 多维数据集插件

- **doc-view ID**: 104
- **路径**: 数据准备 > 数据连接 > 其他数据库 > 多维数据集插件
- **核心概念**: 多维数据库（Multi Dimensional Database，MDD），就是指将数据存储在多个维度中。简单来说，就是将数据存放在一个 n 维数组中，而不是像关系数据库那样以记录的形式存放。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 多维数据库（Multi Dimensional Database，MDD），就是指将数据存储在多个维度中。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 多维数据库（Multi Dimensional Database，MDD），就是指将数据存储在多个维度中。

**关键代码/公式/API：**
- 代码片段: `<ConfigurationSettings> ⏎     <ServerName>localhost</ServerName> ⏎     <SessionTimeout>3600</SessionTimeout> ⏎     <ConnectionPoolSize>100</ConnectionPoolSize> ⏎     <MinThreadPoolSize>0</MinThreadPoo`
- 代码片段: `<ConfigurationSettings> ⏎     <ServerName>localhost</ServerName> ⏎     <SessionTimeout>3600</SessionTimeout> ⏎     <ConnectionPoolSize>100</ConnectionPoolSize> ⏎     <MinThreadPoolSize>200</MinThreadP`

### 63. MongoDB 数据库插件

- **doc-view ID**: 1413
- **路径**: 数据准备 > 数据连接 > 其他数据库 > MongoDB 数据库插件
- **核心概念**: MongoDB 作为一款非常流行的 NoSQL 数据库，越来越被广泛地使用，但是帆软报表中 JDBC 和 JNDI 都无法连接 MongoDB 进行取数，安装该插件可以连接 MongoDB 数据库。有关 MongoDB 的介绍和使用方法可以参阅MongoDB官方帮助文档的说明。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: MongoDB 作为一款非常流行的 NoSQL 数据库，越来越被广泛地使用，但是帆软报表中 JDBC 和 JNDI 都无法连接 MongoDB 进行取数，安装该插件可以连接 MongoDB 数据库。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: MongoDB 作为一款非常流行的 NoSQL 数据库，越来越被广泛地使用，但是帆软报表中 JDBC 和 JNDI 都无法连接 MongoDB 进行取数，安装该插件可以连接 MongoDB 数据库。

**关键代码/公式/API：**
- 公式: `ISODate("2019-08-31T12:50:11.000Z")`
- 公式: `ISODate()`
- 公式: `ISODate('2019-01-01T00:00:00.000Z')`
- 公式: `Date()`

### 64. 新SAPBW数据集插件

- **doc-view ID**: 1466
- **路径**: 数据准备 > 数据连接 > 其他数据库 > SAP数据连接 > 新SAPBW数据集插件
- **核心概念**: 注：2. 新 SAP BW 多维数据集用于连接 BW Cube 和 BW Query，从以前的多维数据集中分离出来单独做成了插件。注：3. 暂不支持 服务器部署包 下使用新 SAP BW 数据集插件。

**业务场景四要素：**
- 统计指标方案: 4）切换成行/列的设置界面，分别拖动左侧目录中的关键指标进入列面板，维度进入行面板，点击保存查询，如下图所示：
- 业务场景: 注：2. 新 SAP BW 多维数据集用于连接 BW Cube 和 BW Query，从以前的多维数据集中分离出来单独做成了插件。
- 人员岗位: 2）XMLA 的 URL 的获取方法：IP 请询问 SAP 管理员，端口号有两种获取方法。
- 功能应用场景: 注：2. 新 SAP BW 多维数据集用于连接 BW Cube 和 BW Query，从以前的多维数据集中分离出来单独做成了插件。

**关键代码/公式/API：**
- URL: `http://ip地址`
- JDBC URL: `jdbc:xmla:Server=http://[ip]:[port]/sap/bw/xml/soap/xmla?sap-client=***`

### 65. JSON 数据集插件

- **doc-view ID**: 1985
- **路径**: 数据准备 > 数据连接 > 其他数据库 > JSON 数据集插件
- **核心概念**: 点击下载插件：JSON数据集 设计器插件安装方法参照 设计器插件管理 服务器安装插件方法参照 服务器插件管理 随着 JavaScript 的流行，JSON 格式的数据也被越来越广泛的使用，但是由于 JSON 格式的灵活性，把这类数据结构和其他数据一起分析的时候，就会面临结构不统一导致无法分析的问题，在 FineReport 报表中是没有办法直接使用的。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 点击下载插件：JSON数据集 设计器插件安装方法参照 设计器插件管理 服务器安装插件方法参照 服务器插件管理 随着 JavaScript 的流行，JSON 格式的数据也被越来越广泛的使用，但是由于 JSON 格式的灵活性，把这类数据结构和其他数据一起分析的时候，就会面临结构不统一导致无法分析的问题，
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: - 预读列名：先遍历所有的数据，把列名获取出来，可用于 JSON 结构不整齐的情况，会稍微的降低效率。默认即为不开启。

**关键代码/公式/API：**
- 代码片段: `var books = $.store.book; ⏎ var rowCount = books.length; ⏎ console.log("行数为:" + rowCount); ⏎ var table = []; ⏎ var column = []; ⏎ books.forEach(function(value, index) { ⏎     var row = []; ⏎     for (`
- 代码片段: `var books = $.store.book; ⏎ var rowCount = books.length; ⏎ var table = []; ⏎ var column = []; ⏎ books.forEach(function(value, index) { ⏎     var row = []; ⏎     if (value.price < 10) { ⏎       for (va`
- 代码片段: `var books = $.store.book; ⏎ var rowCount = books.length; ⏎ var table = []; ⏎ var column = ["author"]; ⏎ books.forEach(function(value, index) { ⏎     var row = []; ⏎     row.push(value.author); ⏎     t`
- 公式: `log("行数为:" + rowCount)`
- 公式: `forEach(function(value, index)`
- 公式: `push(value[key])`
- 公式: `push(key)`
- URL: `http://fine-doc.oss-cn-shanghai.aliyuncs.com/book.json`

### 66. Spider 数据集插件

- **doc-view ID**: 2594
- **路径**: 数据准备 > 数据连接 > 其他数据库 > Spider 数据集插件
- **核心概念**: 使用 Spider 数据集插件需要 FineBI 与 FineReport 版本适配。详细请参见：适配详细信息 - 数据需要通过复杂报表展示的需求，FineBI5.1 无法直接实现的时候，可以通过使用 Finereport 设计器获取 FineBI 业务包中的数据实现复杂报表制作的功能。

**业务场景四要素：**
- 统计指标方案: 下面列出各种字段类型的汇总方式：
- 业务场景: 使用 Spider 数据集插件需要 FineBI 与 FineReport 版本适配。
- 人员岗位: 1）管理员先连接 FineBI 工程，详细请参见本文 2.2.1 节。
- 功能应用场景: 即用户登录 FineBI ，选择管理系统>目录管理，将模板挂载在任一目录下便可实现预览。如下图所示：

### 67. 新SSAS插件

- **doc-view ID**: 3406
- **路径**: 数据准备 > 数据连接 > 其他数据库 > 新SSAS插件
- **核心概念**: 用户工程有时需要使用 SSAS 数据库来解决效率问题，同时前端使用中国式复杂报表展现，因此需要解决两者的连接问题。用户可下载SSAS插件与 SSAS 数据库进行连接，可轻松获取到多维数据库中的数据，将其转换为二维表用以进行模板制作和数据分析。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 用户工程有时需要使用 SSAS 数据库来解决效率问题，同时前端使用中国式复杂报表展现，因此需要解决两者的连接问题。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 用户工程有时需要使用 SSAS 数据库来解决效率问题，同时前端使用中国式复杂报表展现，因此需要解决两者的连接问题。

**关键代码/公式/API：**
- URL: `http://localhost`

### 68. InfluxDB数据集

- **doc-view ID**: 3544
- **路径**: 数据准备 > 数据连接 > 其他数据库 > InfluxDB数据集
- **核心概念**: InfluxDB是一个开源分布式时序、事件和指标数据库。在最新的DB-ENGINES给出的时间序列数据库的排名中，InfluxDB高居第一位，可以预见，InfluxDB会越来越得到广泛的使用。

**业务场景四要素：**
- 统计指标方案: InfluxDB是一个开源分布式时序、事件和指标数据库。
- 业务场景: InfluxDB是一个开源分布式时序、事件和指标数据库。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: InfluxDB是一个开源分布式时序、事件和指标数据库。

**关键代码/公式/API：**
- SQL: `SELECT,SHOW`

### 69. Elasticsearch数据集-悦享版

- **doc-view ID**: 3629
- **路径**: 数据准备 > 数据连接 > 其他数据库 > Elasticsearch数据集-悦享版
- **核心概念**: Elasticsearch简称ES，是一个基于Lucene的实时分布式的搜索与分析引擎，是当前主流的企业级搜索引擎。它提供了一个分布式服务，可以使您快速的近乎于准实时的存储、查询和分析超大数据集，通常被用来当做构建复杂查询特性和需求强大应用的基础引擎或技术。

**业务场景四要素：**
- 统计指标方案: - 操作种类：查询，显示数据明细内容作为数据集；聚合，显示数据聚合分析的统计信息作为数据集。对应红框4；
- 业务场景: Elasticsearch简称ES，是一个基于Lucene的实时分布式的搜索与分析引擎，是当前主流的企业级搜索引擎。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: Elasticsearch简称ES，是一个基于Lucene的实时分布式的搜索与分析引擎，是当前主流的企业级搜索引擎。

**关键代码/公式/API：**
- URL: `http://192.168.3.102`
- URL: `https://192.168.3.102`

### 70. [平台]MySQL8数据连接插件

- **doc-view ID**: 3751
- **路径**: 数据准备 > 数据连接 > 其他数据库 > [平台]MySQL8数据连接插件
- **核心概念**: 安装此插件后用户可以连接 MySQL8 数据库。本文仅适用于 10.0.11 之后的报表服务器，10.0.11 之前的报表服务器若要连接 MySQL8 数据库请参见：[平台]MySQL数据连接 注：不支持在设计器连接。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 本文仅适用于 10.0.11 之后的报表服务器，10.0.11 之前的报表服务器若要连接 MySQL8 数据库请参见：[平台]MySQL数据连接
- 人员岗位: 注：如果非管理员用户想要配置数据连接，需要管理员给其分配管理系统下数据连接节点的权限，具体操作请查看 数据连接控制
- 功能应用场景: 本文仅适用于 10.0.11 之后的报表服务器，10.0.11 之前的报表服务器若要连接 MySQL8 数据库请参见：[平台]MySQL数据连接

**关键代码/公式/API：**
- 驱动类: `com.mysql.cj.jdbc.Driver`
- JDBC URL: `jdbc:mysql://ip:port/<数据库名>?useSSL=false&serverTimezone=UTC`
- JDBC URL: `jdbc:mysql://localhost:端口号/<数据库名>?generateSimpleParameterMetadata=true&useUnicode=true&characterEncoding=utf8&useSSL=fal`

---
