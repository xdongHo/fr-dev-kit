<!--
KB_INDEX: {
    "title": "设计器内执行 SQL（含建表）的 UI 路径与 Java API",
    "stage": "api-reference",
    "tags": [
      "建表",
      "SQL执行",
      "DBTableData",
      "extra session"
    ],
    "keywords": [
      "SQLEditPane",
      "PreviewPerformedSqlPane",
      "DBTableData",
      "NameDatabaseConnection",
      "extra session"
    ],
    "summary": "数据连接→SQL 编辑器→预览执行建表的 GUI 路径与对应 Java API 链路，以及 extra session 自动化的硬限制"
  }
-->

# 设计器内执行 SQL（含建表）的 UI 路径与 Java API

> 2026-08-05 通过 fr-agent 追踪用户 GUI 操作 + 反射实测整理。
> 场景：用 FR Designer「数据连接 → SQL 编辑器 → 预览」执行 DDL（如 CREATE TABLE），
> 用于建表/清表，绕开本地无 JDBC 凭据的限制。

## 一、UI 操作路径（用户实测可行）

```
设计器 数据连接面板
  → 打开连接 数据连接1 的 SQL 编辑器（粘贴 SQL）
  → 点击「预览」→ 执行完成
  → 再次执行同一条 SQL → 报「表已存在」→ 确认建表成功
```

- **注意**：Designer 为远程设计模式（连 内部远程设计服务器（示例））时，SQL 在**远程服务器**上执行——这是 UI 能执行而本地拿不到连接的原因。
- 该路径下 AWT 事件流**不捕获** SQL 编辑器窗口（组件在独立窗口/走远程通道），fr-agent `/events` 只能看到主窗口事件。

## 二、对应 Java API（反射实测，Designer JVM 内类）

| 环节 | 类 | 说明 |
|------|-----|------|
| SQL 编辑器 | `com.fr.design.data.datapane.sqlpane.SQLEditPane` | 数据连接面板的 SQL 编辑窗格 |
| 预览执行 | `com.fr.design.data.datapane.preview.sql.PreviewPerformedSqlPane` | `previewPerformedSql(DBTableData)` 执行入口；`getTableDataProviders()` 取结果 |
| 数据连接树 | `com.fr.design.data.datapane.connect.*` | `ConnectionManagerPane`/`ConnectionListPane`/`DatabaseConnectionPane` 等 |
| **执行核心** | `com.fr.data.impl.DBTableData` | `setQuery(String)` 设 SQL、`setDatabase(Connection)` 设连接、`createDataModel(Calculator)` 执行 |
| 连接名引用 | `com.fr.data.impl.NameDatabaseConnection` | `new NameDatabaseConnection("数据连接1")` 持有连接名 |
| 计算器 | `com.fr.script.Calculator` | `Calculator.createCalculator()`（静态工厂，无 public 构造） |

**自动化执行代码（fr-agent /exec Nashorn）**：
```javascript
var D = Java.type("com.fr.data.impl.DBTableData");
var NCC = Java.type("com.fr.data.impl.NameDatabaseConnection");
var Calc = Java.type("com.fr.script.Calculator");
var td = new D();
td.setQuery("CREATE TABLE ...");              // 任意 SQL（DDL/DML/SELECT）
td.setDatabase(new NCC("数据连接1"));
var dm = td.createDataModel(Calc.createCalculator());   // 执行
```

## 三、⚠ 硬限制：extra session（2026-08-05 实测）

上述代码在 fr-agent `/exec`（Nashorn，Designer JVM）里执行报：

```
java.lang.RuntimeException: cannot find extra session
```

**原因**：`createDataModel` 走 FR 配置系统（`com.fr.config` / `com.fr.transaction.HibernateUtils`）读取连接定义，
需要 **FR 平台 Hibernate 会话**（`SessionHolder`/`DBSession`，由平台启动时在 UI 线程创建）。
`/exec` 的独立线程没有该会话；`EventQueue.invokeAndWait`（EDT）也不行——远程设计模式下
会话绑定在 Designer 的远程工作区上下文（`RemoteDesignerWorkspaceInfo`）上。

已尝试无效的初始化：`ConfigurationActivator.start()`、`FineRuntime.start()`、
`ConfigManager.getInstance()`、`SessionHolder.begin()`（无无参构造）、`TransactorFactory.getTransactor()`
（返回 HibernateTransactor，仍需 ConnectionHolder）。

**可行的执行通道**（按优先级）：
1. **GUI 流程**（已跑通）：数据连接 → SQL 编辑器 → 预览（用户手动粘贴 SQL 执行）。
2. **服务器 web 环境**：在持有连接配置的 FR 报表服务器 web 上下文里执行（`DBTableData` 同样适用）。
3. **fr-agent 扩展**（待实现）：捕获 Designer UI 线程的远程会话上下文后再执行，或通过
   `RemoteDesignerWorkspaceInfo` 直接调用远程设计接口。

## 四、结论

- 「设计器内建表」= 数据连接 SQL 编辑器 + 预览，底层 = `DBTableData.createDataModel`。
- 自动化（fr-agent /exec）被 extra session 卡住；**当前最实用 = 生成 SQL 由用户在编辑器粘贴预览执行**。
- 后续若打通 extra session（方案 3），即可实现「AI 生成 SQL → 自动建表」闭环。
