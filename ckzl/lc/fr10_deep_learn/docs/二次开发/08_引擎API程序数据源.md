<!--
KB_INDEX: {
  "title": "二次开发 - 引擎API程序数据源",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "二次开发",
    "程序数据源",
    "引擎API"
  ],
  "summary": "「二次开发」分页：程序数据源（约 10 篇条目）；FR10 帮助文档「二次开发」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 二次开发 · 引擎API程序数据源

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §二次开发


## 引擎API > 程序数据源（10篇）

### 14. 程序数据源

- **doc-view ID**: 637
- **路径**: 二次开发 > 引擎API > 程序数据源 > 程序数据源
- **核心概念**: FineReport 报表的数据来源可以是数据库数据、文本数据，并且还可以是其它类型的数据。FineReport 主要通过 AbstractTableData 抽象类来读取数据源，上述所有的数据来源都继承 AbstractTableData 类实现抽象方法，因此用户只要实现了 AbstractTableData 抽象类，FineReport 报表引擎就能够读取用户自定义的数据源。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 获取 AbstractTableData 中第 columnIndex 列，第 rowIndex 行的数据，在某些应用场景中，需要在程序中对数据进行处理后再作为报表的数据源使用。**
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FineReport 报表的数据来源可以是数据库数据、文本数据，并且还可以是其它类型的数据。

**关键代码/公式/API：**
- 代码片段: `public int getColumnCount();`
- 代码片段: `public String getColumnName(int columnIndex);`
- 代码片段: `public int getRowCount();`

### 15. EJB程序数据源

- **doc-view ID**: 640
- **路径**: 二次开发 > 引擎API > 程序数据源 > EJB程序数据源
- **核心概念**: 应用场景：数据连接不需要直接访问数据库，而是使用 EJB 做为数据源。功能介绍：FR 通过定义程序数据集使用 EJB 的相关类获取到 EJB 数据源，然后转为我们里面的二维表作为报表数据源使用，进行展示。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 应用场景：数据连接不需要直接访问数据库，而是使用 EJB 做为数据源。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 功能介绍：FR 通过定义程序数据集使用 EJB 的相关类获取到 EJB 数据源，然后转为我们里面的二维表作为报表数据源使用，进行展示。如下获取到 EJB 数据所做的模板。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\`
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/data/DataModelDemo.java`

### 16. 带参程序数据集

- **doc-view ID**: 642
- **路径**: 二次开发 > 引擎API > 程序数据源 > 带参程序数据集
- **核心概念**: 在实际应用中，可能需要根据表名动态地改变数据源，比如在程序数据集中，通过传进的表名参数，到数据库取出对应的表作为数据源。FineReport 是通过 AbstractTableData 抽象类来读取数据源的，所有的数据来源都继承实现其抽象方法。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在实际应用中，可能需要根据表名动态地改变数据源，比如在程序数据集中，通过传进的表名参数，到数据库取出对应的表作为数据源。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在实际应用中，可能需要根据表名动态地改变数据源，比如在程序数据集中，通过传进的表名参数，到数据库取出对应的表作为数据源。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\`
- 公式: `webroot\WEB-INF\classes\com\fr\`

### 17. 简单程序数据集

- **doc-view ID**: 650
- **路径**: 二次开发 > 引擎API > 程序数据源 > 简单程序数据集
- **核心概念**: 实际应用中，用户可能需要通过程序来获取数据。FineReport 支持程序数据集，用户自定义程序数据源后，可在数据集处添加「程序」数据集使用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 实际应用中，用户可能需要通过程序来获取数据。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 实际应用中，用户可能需要通过程序来获取数据。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\`
- 公式: `\webroot\WEB-INF\classes\com\fr\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/data/ArrayTableDataDemo.java`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/data/SimpleArrayTableDataDemo.java`

### 18. SAP的RFC接口调用

- **doc-view ID**: 1235
- **路径**: 二次开发 > 引擎API > 程序数据源 > SAP的RFC接口调用
- **核心概念**: SAP 作为独立的系统，与其它系统进行交互的时候，主要是两种方式： - 底层数据库直接交互 - 通过 SAP 专门的 RFC 接口进行数据调用 所以 FineReport 设计报表时要使用 SAP 系统的数据，也就对应两种实现方式，直连数据库或使用 RFC 接口。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: SAP 作为独立的系统，与其它系统进行交互的时候，主要是两种方式： - 底层数据库直接交互 - 通过 SAP 专门的 RFC 接口进行数据调用 所以 FineReport 设计报表时要使用 SAP 系统的数据，也就对应两种实现方式，直连数据库或使用 RFC 接口。
- 人员岗位: SAP 现在主要的数据库有 Oracle 和 DB2 两种关系型数据库，FineReport 可以通过 JDBC 的方式直连 SAP 数据库实现取数，但此取数方式需要报表开发人员充分了解 SAP 数据库，并且 SAP 数据库要允许其他系统访
- 功能应用场景: SAP 作为独立的系统，与其它系统进行交互的时候，主要是两种方式： - 底层数据库直接交互 - 通过 SAP 专门的 RFC 接口进行数据调用 所以 FineReport 设计报表时要使用 SAP 系统的数据，也就对应两种实现方式，直连数据库或使用 RFC 接口。

**关键代码/公式/API：**
- 公式: `bin路径下
libsapjco3.so 放在usr\lib文件夹下，若 Linux 为 64 位，放到usr\`
- 公式: `bin路径下
libsapjco3.so 放在usr\`
- 公式: `System32路径下
sapjcorfc.dll 放在C:\Windows\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/function/ConnectSAPServer.java`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/data/ParamSAPDataTest.java`

### 19. WebService程序数据集

- **doc-view ID**: 1236
- **路径**: 二次开发 > 引擎API > 程序数据源 > WebService程序数据集 > WebService程序数据集
- **核心概念**: 在使用 WebService 作为您项目的数据源时，希望报表中也是直接调用这个 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？在程序中访问 WebService 应用服务，将 WebService 返回的数据转为程序数据集，然后在设计器中调用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在使用 WebService 作为您项目的数据源时，希望报表中也是直接调用这个 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在使用 WebService 作为您项目的数据源时，希望报表中也是直接调用这个 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？

### 20. 解析数据库内xml文件

- **doc-view ID**: 1238
- **路径**: 二次开发 > 引擎API > 程序数据源 > xml制作程序数据源 > 解析数据库内xml文件
- **核心概念**: 如果数据库表中某个字段所存的数据为 XML 格式。如下图所示： 那么如何将存于 XML 字段中的值读取出来作为报表数据源使用呢。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 如果数据库表中某个字段所存的数据为 XML 格式。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 如果数据库表中某个字段所存的数据为 XML 格式。

**关键代码/公式/API：**
- 代码片段: `<Field><Name>MemoryFreeSize</Name><Type>int</Type><Value>1962</Value></Field> <Field><Name>MemoryTotalSize</Name><Type>int</Type><Value>2047</Value></Field> <Field><Name>MemoryUsage</Name><Type>int</T`
- 代码片段: `<Field><Name>MemoryFreeSize</Name><Type>Int</Type><Value>1999</Value></Field> <Field><Name>MemoryTotalSize</Name><Type>Int</Type><Value>2048</Value></Field> <Field><Name>MemoryUsage</Name><Type>Int</T`
- 代码片段: `<Field><Name>MemoryFreeSize</Name><Type>Int</Type><Value>2000</Value></Field> <Field><Name>MemoryTotalSize</Name><Type>Int</Type><Value>2050</Value></Field> <Field><Name>MemoryUsage</Name><Type>Int</T`
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/data/GetXmlDate.java`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/data/XMLRead.java`

### 21. 解析某个目录下 XML 文件

- **doc-view ID**: 1239
- **路径**: 二次开发 > 引擎API > 程序数据源 > xml制作程序数据源 > 解析某个目录下 XML 文件
- **核心概念**: 电脑某个目录下保存了几个 XML 文件，希望把 XML 文件转换为报表数据源。如下图所示，将 Northwind.xml 中的数据转换为报表数据源。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 电脑某个目录下保存了几个 XML 文件，希望把 XML 文件转换为报表数据源。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 电脑某个目录下保存了几个 XML 文件，希望把 XML 文件转换为报表数据源。

**关键代码/公式/API：**
- 代码片段: `<?xml version="1.0" encoding="UTF-8"?> ⏎ <Northwind> ⏎     <Customers> ⏎     <CustomerID>ALFKI</CustomerID> ⏎ <CompanyName>ALfreds Futterkiste</CompanyName> ⏎ <ContactName>Maria Anders</ContactName> ⏎`
- 公式: `webroot\WEB-INF\classes\com\fr\`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/data/XMLColumnNameType4Demo.java`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/data/XMLParseDemoDataModel.java`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/data/XMLDemoTableData.java`

### 22. WebService程序数据集之jws方式

- **doc-view ID**: 1240
- **路径**: 二次开发 > 引擎API > 程序数据源 > WebService程序数据集 > WebService程序数据集之jws方式
- **核心概念**: 在使用 WebService 作为项目的数据源时，希望报表中可以直接调用 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？在程序中访问 WebService 应用服务，将 WebService 返回的数据转为程序数据集，然后在设计器中调用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在使用 WebService 作为项目的数据源时，希望报表中可以直接调用 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在使用 WebService 作为项目的数据源时，希望报表中可以直接调用 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？

**关键代码/公式/API：**
- 代码片段: `public class TestWS2TDClient { ⏎ public String[][] getTD() { ⏎ String[][] a = { { "城市", "销售员", "销售额" }, { "江苏", "Anna", "230" }, { "江苏", "Alex", "190" }, ⏎ { "江苏", "Jack", "320" }, { "江苏", "Apple", "2`
- 代码片段: `try { ⏎ String endpoint = "http://localhost:8080/axis/TestWS2TDClient.jws"; ⏎ Service service = new Service(); //创建一个服务(service)调用(call) ⏎ Call call = (Call) service.createCall(); // 通过service创建call对象`
- 公式: `axis\`
- URL: `http://localhost`
- URL: `https://code.fanruan.com/demo/example/src/release/10.0/src/main/java/com/fr/data/WebServiceTableData.java`
- Java类/方法: `service.createCall()`
- Java类/方法: `call.setTargetEndpointAddress(new java.net.URL(endpoint)`
- Java类/方法: `call.setOperationName(new QName("http://localhost:8080/axis/TestWS2TDClient.jws","getTD")`
- Java类/方法: `call.invoke(new Object[] {})`

### 23. WebService 程序数据集通过 JDBC 连接取数

- **doc-view ID**: 3129
- **路径**: 二次开发 > 引擎API > 程序数据源 > WebService程序数据集 > WebService 程序数据集通过 JDBC 连接取数
- **核心概念**: 在使用 WebService 作为项目的数据源时，希望报表中可以直接调用 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？在程序中访问 WebService 应用服务，将 WebService 返回的数据转为程序数据集，然后在设计器中调用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在使用 WebService 作为项目的数据源时，希望报表中可以直接调用 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在使用 WebService 作为项目的数据源时，希望报表中可以直接调用 WebService 数据源，而不是定义数据连接调用对应的数据库表，这样要怎么实现呢？

**关键代码/公式/API：**
- 代码片段: `package service; //需定义包名为service，对应之后的文件夹名 ⏎ import java.sql.*; ⏎ import java.util.ArrayList; ⏎ import java.util.List; ⏎ public class MyService { ⏎ // 定义数据库连接参数 ⏎ private static final String DRIVER_CL`
- 代码片段: `<service name="MyService">     <!--service名字可以自己定义--> ⏎     <description> ⏎         Web Service ⏎     </description> ⏎     <parameter name="ServiceClass"> ⏎         service.MyService      <!--对应包名和类名-`
- 代码片段: `jar cvf ws.aar .`
- 公式: `axis2\`
- 公式: `axis2\WEB-INF\`
- SQL: `select id,name from test"`
- URL: `http://www.w3.org/2004/08/wsdl/in-out`
- URL: `http://localhost`
- URL: `http://service`
- URL: `http://service/get`
- 驱动类: `com.mysql.jdbc.Driver`
- JDBC URL: `jdbc:mysql://localhost:3306/z`
- Java类/方法: `Class.forName(DRIVER_CLASS_NAME)`
- Java类/方法: `e.printStackTrace()`
- Java类/方法: `DriverManager.getConnection(URL, USERNAME, PASSWORD)`
- Java类/方法: `conn.close()`

---
