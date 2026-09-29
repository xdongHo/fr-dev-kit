<!--
KB_INDEX: {
  "title": "数据准备 - 数据连接JDBC数据连接_上",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "数据准备",
    "JDBC数据连接",
    "数据连接"
  ],
  "summary": "「数据准备」分页：JDBC数据连接（约 55 篇条目）；FR10 帮助文档「数据准备」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 数据准备 · 数据连接JDBC数据连接_上

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §数据准备


## 数据连接 > JDBC数据连接（55篇）
### 3. [设计器]JDBC连接数据库

- **doc-view ID**: 101
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [设计器]JDBC连接数据库
- **核心概念**: FineReport 提供了两种数据连接方式： 方式一：在数据决策系统中进行连接，可参考 配置数据连接 方式二：在设计器中进行连接 ，本文主要介绍该种方法。注：FineReport 设计器中 JNDI 数据连接步骤请参考 [设计器]JNDI连接数据库 本章以 MySQL 数据库为例介绍 JDBC 数据连接的步骤。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: FineReport 提供了两种数据连接方式： 方式一：在数据决策系统中进行连接，可参考 配置数据连接 方式二：在设计器中进行连接 ，本文主要介绍该种方法。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: FineReport 提供了两种数据连接方式： 方式一：在数据决策系统中进行连接，可参考 配置数据连接 方式二：在设计器中进行连接 ，本文主要介绍该种方法。

**关键代码/公式/API：**
- 代码片段: `jdbc:oracle:thin:@(description=(address_list= (address=(host=192.168.10.1) (protocol=tcp)(port=1521))(address=(host=192.168.10.2)(protocol=tcp) (port=1521))(load_balance=yes)(failover=yes))(connect_da`
- JDBC URL: `jdbc:oracle:thin:@(description=(address_list=`

### 4. [设计器] ODBC 数据连接

- **doc-view ID**: 289
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 其他类型JDBC应用 > [设计器] ODBC 数据连接
- **核心概念**: FineReport10.0 内置了 JDK1.8 或 JDK 11 ，这两个版本的JDK 不支持直接连接 ODBC 数据源的。如果直接在平台连接 ODBC 数据源，会有如下报错信息： 那么 10.0 设计器如何连接 ODBC 呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: FineReport10.0 内置了 JDK1.8 或 JDK 11 ，这两个版本的JDK 不支持直接连接 ODBC 数据源的。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: FineReport10.0 内置了 JDK1.8 或 JDK 11 ，这两个版本的JDK 不支持直接连接 ODBC 数据源的。

**关键代码/公式/API：**
- 驱动类: `sun.jdbc.odbc.JdbcOdbcDriver`
- JDBC URL: `jdbc:odbc:数据源名称`

### 5. [设计器]dBASE数据连接

- **doc-view ID**: 290
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 其他类型JDBC应用 > [设计器]dBASE数据连接
- **核心概念**: 使用 FineReport 连接 dBASE 数据库，在数据库选择的下拉选项中没有 dBASE 这种数据库，此时，该如何连接 dBASE 数据库呢？手动将连接 dBASE 数据库需要使用到的 JAR 放置到%FR_HOME%\webroot\WEB-INF\lib下面，然后重启设计器，新建 JDBC 数据连接，其数据库下拉选项中选择 Others，接着手动输入其驱动 URL 以及用户名密码即可。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 使用 FineReport 连接 dBASE 数据库，在数据库选择的下拉选项中没有 dBASE 这种数据库，此时，该如何连接 dBASE 数据库呢？
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 使用 FineReport 连接 dBASE 数据库，在数据库选择的下拉选项中没有 dBASE 这种数据库，此时，该如何连接 dBASE 数据库呢？

**关键代码/公式/API：**
- JDBC URL: `jdbc:jstels:dbf:C:/FineReport/webapps/webroot/.该路径是`

### 6. 连接池满问题

- **doc-view ID**: 291
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 连接池属性 > 连接池满问题
- **核心概念**: 若日志报 ORA-12519 TNS:no appropriate service handler found，是数据库连接失败的错误，12519 错误是监听不能提供服务。原因是我们定义数据连接后，点击连接时，此时会用掉一个连接池中的一个连接。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 若日志报 ORA-12519 TNS:no appropriate service handler found，是数据库连接失败的错误，12519 错误是监听不能提供服务。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 若日志报 ORA-12519 TNS:no appropriate service handler found，是数据库连接失败的错误，12519 错误是监听不能提供服务。

**关键代码/公式/API：**
- 代码片段: `select count(*) from V$process;`
- 代码片段: `select value from V$parameter where name='processes';`
- 代码片段: `alter system set processes=1000 scope=spfile`
- 公式: `count(*)`
- SQL: `select count(*) from V$process`
- SQL: `select value from V$parameter where name='processes'`

### 7. 数据连接高级设置

- **doc-view ID**: 292
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 连接池属性 > 数据连接高级设置
- **核心概念**: - 「连接池设置」按钮改名为「高级设置」 - 设计器部分数据连接支持设置 fetchsize 本文将介绍高级设置设置方法及其属性中各参数的意义。- 连接池 - fetchsize 在 FineReport 设计器中点击「服务器>定义数据连接」，选择某个数据连接，点击「高级设置」，可设置连接池属性，部分数据连接还可设置 fetchsize 。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: - 「连接池设置」按钮改名为「高级设置」 - 设计器部分数据连接支持设置 fetchsize 本文将介绍高级设置设置方法及其属性中各参数的意义。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: - 「连接池设置」按钮改名为「高级设置」 - 设计器部分数据连接支持设置 fetchsize 本文将介绍高级设置设置方法及其属性中各参数的意义。

**关键代码/公式/API：**
- 代码片段: `警告:Cannot get a connection, pool error Timeout waiting for idle object ⏎ at com.fr.third.org.apache.commons.dbcp.PoolingDataSource.getConnection(PoolingDataSource.java:114) ⏎ at com.fr.third.org.apach`
- 公式: `getConnection(PoolingDataSource.java:114)`
- 公式: `getConnection(BasicDataSource.java:1044)`
- 公式: `create(Unknown Source)`
- 公式: `createConnection(Unknown Source)`
- SQL: `SELECT 并且必须返回至少一行记录`

### 8. 连接池原理

- **doc-view ID**: 293
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 连接池属性 > 连接池原理
- **核心概念**: 连接池技术的核心思想是：连接复用，通过建立一个 数据库连接池 以及一套连接使用、分配、管理策略，使得该 连接池 中的连接可以得到高效、安全的复用，避免了数据库连接频繁建立、关闭的开销。

**业务场景四要素：**
- 统计指标方案: 本文实现的 数据库连接池 包括一个管理类DBConnectionManager，负责提供与多个连接池对象(DBConnectionPool类)之间的接口。每一个连接池对象管理一组封装过的JDBC连接对象Conn，封装过的 JDBC 连接对象Conn可以被任意数量的Model层的组件共享。
- 业务场景: 连接池技术的核心思想是：连接复用，通过建立一个 数据库连接池 以及一套连接使用、分配、管理策略，使得该 连接池 中的连接可以得到高效、安全的复用，避免了数据库连接频繁建立、关闭的开销。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 前面讨论的是关于使用数据库连接进行普通的数据库访问。对于 事务处理，情况就变得比较复杂。因为事务本身要求原子性的保证，此时就要求对于数据库的操作符合"All-or-Nothing"原则，即要么全部完成，要么什么都不做。如果简单的采用上述的连接复用的策略，就会发生问题，因为没有办法控制属于同一个事务的

**关键代码/公式/API：**
- 代码片段: `public class ConnectionParam implements Serializable{ ⏎   //各初始化参数的定义 ⏎ }`
- 代码片段: `public class ConnectionFactory{ ⏎   static Hashtable connectionPools = //用来保存数据源名和连接池对象的关系 ⏎   public static DataSource lookup(String dataSourceName) throws NameNotFoundException{ ⏎     //查找名字为dataSou`
- 代码片段: `Class Conn { ⏎ Private java. sgl .Connection con; //数据库连接对象 ⏎ Public Boolean inUse ; //是否被使用 ⏎ Public long lastAccess; //最近一次释放该连接的时间 ⏎ Public int useCount; // 被使用次数 ⏎ } ⏎ 下面是实现连接池的主要代码： ⏎ // 初始化数据库连接`
- 公式: `getActiveSize()`
- 公式: `getOpenSize()`
- 公式: `lookup(String dataSourceName)`
- 公式: `bind(Stringname, ConnectionParam param)`

### 9. [平台]IBM DB2数据连接

- **doc-view ID**: 298
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [平台]IBM DB2数据连接
- **核心概念**: DB2 主要应用于大型应用系统，具有较好的可伸缩性，可支持从大型机到单用户环境，应用于所有常见的服务器操作系统平台下。DB2 具有很好的网络支持能力，对大型分布式应用系统尤为适用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: DB2 主要应用于大型应用系统，具有较好的可伸缩性，可支持从大型机到单用户环境，应用于所有常见的服务器操作系统平台下。 DB2 具有很好的网络支持能力，对大型分布式应用系统尤为适用。
- 人员岗位: 注：如果非管理员用户想要配置数据连接，需要管理员给其分配管理系统下数据连接节点的权限，具体操作请查看 数据连接控制 。
- 功能应用场景: DB2 主要应用于大型应用系统，具有较好的可伸缩性，可支持从大型机到单用户环境，应用于所有常见的服务器操作系统平台下。 DB2 具有很好的网络支持能力，对大型分布式应用系统尤为适用。

**关键代码/公式/API：**
- 驱动类: `com.ibm.db2.jcc.DB2Driver`
- JDBC URL: `jdbc:db2://ip:port/dbname`

### 10. [设计器]通过oci方式连接Oracle

- **doc-view ID**: 301
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 其他类型JDBC应用 > [设计器]通过oci方式连接Oracle
- **核心概念**: 前面以 Oracle为例介绍了 JDBC 数据连接的过程，其中 Oracle 是通过 thin 的方式连接的。大家都知道 Oracle 除了 thin 方式可以连接之外，oci 方式也可以，本文介绍怎么通过 oci 的方式来连接 Oracle。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 前面以 Oracle为例介绍了 JDBC 数据连接的过程，其中 Oracle 是通过 thin 的方式连接的。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 前面以 Oracle为例介绍了 JDBC 数据连接的过程，其中 Oracle 是通过 thin 的方式连接的。

**关键代码/公式/API：**
- JDBC URL: `jdbc:oracle:oci:@axing,`

### 11. JDBC数据连接索引

- **doc-view ID**: 1344
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC数据连接索引
- **核心概念**: 索引:

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 索引:
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 索引:

### 12. [设计器]瀚高数据连接

- **doc-view ID**: 1548
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [设计器]瀚高数据连接
- **核心概念**: 瀚高数据库是一款对象 - 关系型数据库，拥有非常丰富的数据库基本功能，涵盖了所有主流数据库的核心特性，能够满足企业级应用的基本需求。瀚高数据库引进了国际上最先进的开源数据库 PostgreSQL 内核技术，在此 PostgreSQL 社区版之上做了一系列的研发和优化。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 瀚高数据库是一款对象 - 关系型数据库，拥有非常丰富的数据库基本功能，涵盖了所有主流数据库的核心特性，能够满足企业级应用的基本需求。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 瀚高数据库是一款对象 - 关系型数据库，拥有非常丰富的数据库基本功能，涵盖了所有主流数据库的核心特性，能够满足企业级应用的基本需求。

**关键代码/公式/API：**
- 驱动类: `org.Postgresql.Driver`
- JDBC URL: `jdbc:postgresql://localhost:port/databaseName`

### 13. [设计器]Firebird数据连接

- **doc-view ID**: 2076
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 其他类型JDBC应用 > [设计器]Firebird数据连接
- **核心概念**: Firebird 一款开源免费、全功能、强大高效、轻量级且免维护的数据库工具，目前能够运行在 Windows 、Linux 和各种 Unix 操作系统上，提供了大部分 SQL-99 标准的功能。它既能作为多用户环境下的数据库服务器运行，也提供嵌入式数据库的实现。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: Firebird 一款开源免费、全功能、强大高效、轻量级且免维护的数据库工具，目前能够运行在 Windows 、Linux 和各种 Unix 操作系统上，提供了大部分 SQL-99 标准的功能。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: Firebird 一款开源免费、全功能、强大高效、轻量级且免维护的数据库工具，目前能够运行在 Windows 、Linux 和各种 Unix 操作系统上，提供了大部分 SQL-99 标准的功能。

**关键代码/公式/API：**
- 驱动类: `org.firebirdsql.jdbc.FBDriver`
- JDBC URL: `jdbc:firebirdsql://数据库所在服务器IP:端口号/数据库所在具体路径`
- JDBC URL: `jdbc:firebirdsql://192.168.5.5/E:\fbdata\test.fdb`
- JDBC URL: `jdbc:firebirdsql://192.168.5.63/C:\data\sola.IB`

### 14. [设计器] Access 数据连接

- **doc-view ID**: 2121
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 其他类型JDBC应用 > [设计器] Access 数据连接
- **核心概念**: Microsoft Office Access 是微软把数据库引擎的图形用户界面和软件开发工具结合在一起的一个数据库管理系统。那么在 FineReport 中如何连接 Access 数据库呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 注：此方法仅适用于10.0（64位）设计器。
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: 注：此方法仅适用于10.0（64位）设计器。

**关键代码/公式/API：**
- 驱动类: `net.ucanaccess.jdbc.UcanaccessDriver`
- JDBC URL: `jdbc:ucanaccess://access数据库所在的路径`

### 15. [设计器]阿里云MaxCompute数据连接

- **doc-view ID**: 2424
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > 其他类型JDBC应用 > [设计器]阿里云MaxCompute数据连接
- **核心概念**: MaxCompute（之前称为 ODPS），是阿里巴巴通用计算平台提供的一种快速、完全托管的 GB/TB/PB 级数据仓库解决方案，现在已更名为MaxCompute，MaxCompute 向用户提供了完善的数据导入方案以及多种经典的分布式计算模型，能够更快速的解决用户海量数据计算问题，有效降低企业成本，并保障数据安全。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: MaxCompute（之前称为 ODPS），是阿里巴巴通用计算平台提供的一种快速、完全托管的 GB/TB/PB 级数据仓库解决方案，现在已更名为MaxCompute，MaxCompute 向用户提供了完善的数据导入方案以及多种经典的分布式计算模型，能够更快速的解决用户海量数据计算问题，有效降低企业成
- 人员岗位: 未在文中明确指定（面向报表设计人员/数据连接配置人员）
- 功能应用场景: MaxCompute（之前称为 ODPS），是阿里巴巴通用计算平台提供的一种快速、完全托管的 GB/TB/PB 级数据仓库解决方案，现在已更名为MaxCompute，MaxCompute 向用户提供了完善的数据导入方案以及多种经典的分布式计算模型，能够更快速的解决用户海量数据计算问题，有效降低企业成

**关键代码/公式/API：**
- URL: `http://service.cn-hangzhou.maxcompute.aliyun.com/api`
- URL: `http://service.odps.aliyun.com/api`
- 驱动类: `com.aliyun.odps.jdbc.OdpsDriver`
- JDBC URL: `jdbc:odps:<maxcompute_endpoint>?project=<maxcompute_project_name>`
- JDBC URL: `jdbc:odps:http://service.odps.aliyun.com/api?project=工程名&charset=UTF-8`

### 16. [平台]APACHE KYLIN数据连接

- **doc-view ID**: 2542
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [平台]APACHE KYLIN数据连接
- **核心概念**: Apache Kylin 是一个开源的分布式分析引擎，提供 Hadoop 之上的 SQL 查询接口及多维分析（OLAP）能力以支持超大规模数据，能够处理 TB 乃至 PB 级别的分析任务，能够在亚秒级查询巨大的 Hive 表，并支持高并发。FineReport 提供了两种数据连接方式： 方式一：在设计器中进行连接 ，具体方法请参见： [设计器]JDBC连接数据库 。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: Apache Kylin 是一个开源的分布式分析引擎，提供 Hadoop 之上的 SQL 查询接口及多维分析（OLAP）能力以支持超大规模数据，能够处理 TB 乃至 PB 级别的分析任务，能够在亚秒级查询巨大的 Hive 表，并支持高并发。
- 人员岗位: 注：如果非管理员用户想要配置数据连接，需要管理员给其分配管理系统下数据连接节点的权限，具体操作请查看 数据连接控制 。
- 功能应用场景: Apache Kylin 是一个开源的分布式分析引擎，提供 Hadoop 之上的 SQL 查询接口及多维分析（OLAP）能力以支持超大规模数据，能够处理 TB 乃至 PB 级别的分析任务，能够在亚秒级查询巨大的 Hive 表，并支持高并发。

**关键代码/公式/API：**
- 驱动类: `org.apache.kylin.jdbc.Driver`
- JDBC URL: `jdbc:kylin://<hostname>:<port>/<kylin_project_name>`

### 17. [平台]DERBY数据连接

- **doc-view ID**: 2543
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [平台]DERBY数据连接
- **核心概念**: Apache Derby 是一个100% Java 编写的内存数据库，是一个容易管理的关系数据库管理系统，可以和一些商业产品的特性进行交付。Derby 数据库体积小、安装非常简单。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: Apache Derby 是一个100% Java 编写的内存数据库，是一个容易管理的关系数据库管理系统，可以和一些商业产品的特性进行交付。
- 人员岗位: 注：如果非管理员用户想要配置数据连接，需要管理员给其分配管理系统下数据连接节点的权限，具体操作请查看 数据连接控制 。
- 功能应用场景: Apache Derby 是一个100% Java 编写的内存数据库，是一个容易管理的关系数据库管理系统，可以和一些商业产品的特性进行交付。

**关键代码/公式/API：**
- 代码片段: `NetworkServerControl start -h 192.168.5.143 -p 1527`
- 驱动类: `org.apache.derby.jdbc.ClientDriver`
- JDBC URL: `jdbc:derby://hostname:port/database`

### 18. [平台]HP Vertica数据连接

- **doc-view ID**: 2544
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [平台]HP Vertica数据连接
- **核心概念**: HP Vertica 是一款基于列存储的 MPP（massively parallel processing）架构的数据库。它可以支持存放多至 PB（Petabyte）级别的结构化数据。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: HP Vertica 是一款基于列存储的 MPP（massively parallel processing）架构的数据库。
- 人员岗位: 注：如果非管理员用户想要配置数据连接，需要管理员给其分配管理系统下数据连接节点的权限，具体操作请查看 数据连接控制 。
- 功能应用场景: HP Vertica 是一款基于列存储的 MPP（massively parallel processing）架构的数据库。

**关键代码/公式/API：**
- 驱动类: `com.vertica.jdbc.Driver`
- JDBC URL: `jdbc:vertica://ip:port/databaseName`

### 19. [平台]数据连接Kerberos认证

- **doc-view ID**: 2556
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [平台]数据连接Kerberos认证
- **核心概念**: 1）Kerberos 认证是 Hadoop 生态的一种通用的认证方式。2）配置 Kerberos 认证的方式有两种： - 直接使用数据连接配置界面中的 Kerberos 认证：主要用于 Hive、HBase 等驱动的认证连接。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 1）Kerberos 认证是 Hadoop 生态的一种通用的认证方式。
- 人员岗位: 1）若连接失败，可与平台数据库管理员确认相关服务的安全认证配置是否正确，并联系帆软技术支持并提供相关报错日志（提添加 JVM 安全调试参数，如下所示），数据平台数据库版本、对应驱动 JAR 包、相关连接信息、Java 认证连接测试代码或者能
- 功能应用场景: - 直接使用数据连接配置界面中的 Kerberos 认证：主要用于 Hive、HBase 等驱动的认证连接。

**关键代码/公式/API：**
- 代码片段: `Client { ⏎     com.sun.security.auth.module.Krb5LoginModule required doNotPrompt = true  ⏎     useKeyTab = true  ⏎     keyTab = "%FR_HOME%\webapps\webroot\WEB-INF\resources\XXX.keytab" ⏎     principal`
- 代码片段: `-Djava.security.krb5.conf=%FR_HOME%\webapps\webroot\WEB-INF\resources\krb5.conf ⏎ -Djava.security.auth.login.config=%FR_HOME%\webapps\webroot\WEB-INF\resources\krb5.ini`
- 代码片段: `-Djava.security.debug=gssloginconfig,configfile,configparser,logincontext ⏎ -Djava.security.krb5.debug=true`
- JDBC URL: `jdbc:hive2://192.168.5.127:10000/default;principal=hive/quickstart.cloudera@QUICKSTART.CLOUDERA`
- JDBC URL: `jdbc:impala://192.168.5.127:21050/default;AuthMech=1;KrbHostFQDN=quickstart.cloudera;KrbServiceName=impala`

### 20. [平台]Hadoop Hive数据连接

- **doc-view ID**: 2557
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [平台]Hadoop Hive数据连接
- **核心概念**: Hadoop 是个很流行的分布式计算解决方案，Hive是建立在 Hadoop 上的数据仓库基础构架。它提供了一系列的工具，可以用来进行数据提取转化加载（ETL），这是一种可以存储、查询和分析存储在 Hadoop 中的大规模数据的机制。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: Hadoop 是个很流行的分布式计算解决方案，Hive是建立在 Hadoop 上的数据仓库基础构架。
- 人员岗位: 注：如果非管理员用户想要配置数据连接，需要管理员给其分配管理系统下数据连接节点的权限，具体操作请查看 数据连接控制 。
- 功能应用场景: Hadoop 是个很流行的分布式计算解决方案，Hive是建立在 Hadoop 上的数据仓库基础构架。

**关键代码/公式/API：**
- 驱动类: `org.apache.hive.jdbc.HiveDriver`
- JDBC URL: `jdbc:hive2://hostname:port/databasename`

### 21. [平台]INFORMIX数据连接

- **doc-view ID**: 2558
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [平台]INFORMIX数据连接
- **核心概念**: Informix 是 IBM 公司出品的关系数据库管理系统（RDBMS）家族。作为一个集成解决方案，它被定位为作为 IBM 在线事务处理（OLTP）旗舰级数据服务系统。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: Informix 是 IBM 公司出品的关系数据库管理系统（RDBMS）家族。
- 人员岗位: 注：如果非管理员用户想要配置数据连接，需要管理员给其分配管理系统下数据连接节点的权限，具体操作请查看 数据连接控制 。
- 功能应用场景: Informix 是 IBM 公司出品的关系数据库管理系统（RDBMS）家族。

**关键代码/公式/API：**
- 驱动类: `com.informix.jdbc.IfxDriver`
- JDBC URL: `jdbc:informix-sqli://{host}:{port}/{database}:INFORMIXSERVER={server}`

### 22. [平台]Microsoft SQL Server数据连接

- **doc-view ID**: 2559
- **路径**: 数据准备 > 数据连接 > JDBC数据连接 > JDBC典型应用 > [平台]Microsoft SQL Server数据连接
- **核心概念**: 注：升级无法更新内置驱动 Microsoft SQL Server 是关系型数据库管理系统，具有使用方便、可伸缩性好、与相关软件集成程度高等优点。本文介绍 Microsoft SQL Server 数据连接的步骤。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为数据连接/数据集配置说明，无具体统计指标）
- 业务场景: 注：升级无法更新内置驱动 Microsoft SQL Server 是关系型数据库管理系统，具有使用方便、可伸缩性好、与相关软件集成程度高等优点。
- 人员岗位: 1）以管理员身份登录数据决策系统，点击管理系统>数据连接>数据连接管理，点击新建数据连接，如下图所示：
- 功能应用场景: 注：升级无法更新内置驱动 Microsoft SQL Server 是关系型数据库管理系统，具有使用方便、可伸缩性好、与相关软件集成程度高等优点。

**关键代码/公式/API：**
- SQL: `SELECT * FROM [dbo].[asdfg]`
- 驱动类: `jdbc.SQLServerDriver`
- JDBC URL: `jdbc:sqlserver://ip:port;databaseName=xxx`
- JDBC URL: `jdbc:sqlserver://ip;instanceName=实例名;databaseName=数据库名`
- JDBC URL: `jdbc:sqlserver://ip\实例名;databaseName=数据库名`
