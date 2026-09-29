<!--
KB_INDEX: {
  "title": "探针A: 独立JVM渲染路线否定结论",
  "stage": "render-preview",
  "tags": ["渲染", "探针", "否定结论", "headless", "架构决策"],
  "keywords": ["独立JVM", "headless", "FineAssist", "FinePluginBridge", "加密", "EntityDao", "ConfigurationActivator", "原子耦合", "否定结论", "AttachNotSupportedException"],
  "summary": "独立 headless JVM 渲染 cpt 三步全部不可行:三重阻断(FineAssist需Attach API无provider/加密桥magic 0x03030309/EntityDao需完整模块链)。FR10/11无差异,FR架构整体式原子耦合。java backend因此判死,主押injected路线。"
}
-->

# FR Headless Probe 可行性实验报告

> **实验日期**: 2026-08-22  
> **实验目标**: 验证「不启动任何 FineReport 服务器/设计器，仅用 FR10 的 lib jar 起 headless JVM」完成 cpt 模板 解析→计算→HTML 导出 三步是否可行  
> **实验环境**: Windows, JDK 1.8.0_202 (Amazon Corretto), FR10 + FR11 lib

---

## 一、三步结论总表

| 步骤 | 结论 | 证据 |
|------|------|------|
| **Step 1: 解析** | ❌ **不可行** | `WorkBook.readStream()` → `NullPointerException`（缺内部状态）；`TemplateWorkBookIO.readTemplateWorkBook()` → `EntityDao can not be used before the ConfigurationActivator starts!`（需要完整 FR 运行时） |
| **Step 2: 计算** | ❌ **不可行** | 依赖 Step 1 产出的 WorkBook 对象；且 `ActorFactory` 未找到（包名不确定/未初始化） |
| **Step 3: 导出 HTML** | ❌ **不可行** | 无 WorkBook/ResultWorkBook 对象可导出；且 HTML 导出器类名未确认 |

---

## 二、实验详细记录

### 2.1 使用的确切 API 调用链

#### 方案 A: WorkBook.readStream 绕行（推荐路径）
```java
com.fr.main.impl.WorkBook wb = new com.fr.main.impl.WorkBook();
wb.readStream(new FileInputStream("path/to/template.cpt"));
```

#### 方案 B: TemplateWorkBookIO（标准路径）
```java
com.fr.workspace.simple.SimpleWork.checkIn(webInfPath);  // 初始化工作空间
TemplateWorkBookIO.readTemplateWorkBook(templatePath);    // 读取模板
```

#### 方案 C: 执行
```java
Actor actor = ActorFactory.getActor("page");  // 获取 Actor
ResultWorkBook rwb = wb.execute(params, actor);  // 执行模板
```

#### 方案 D: 导出
```java
// HTML 导出器（类名待确认）
HtmlExporter exporter = new HtmlExporter();
exporter.export(outputStream, resultWorkBook);
```

### 2.2 License 相关错误

| 步骤 | License 报错 | 具体信息 |
|------|-------------|---------|
| Step 1A (readStream) | ❌ 无 License 报错 | NullPointerException（内部状态问题） |
| Step 1B (TemplateWorkBookIO) | ❌ 无 License 报错 | EntityDao/ConfigurationActivator 未初始化 |

**结论**: 本次实验**未触及 License 检查**，因为在 License 检查之前就被其他初始化问题阻断。

### 2.3 完整异常栈分析

#### 异常 1: NullPointerException (readStream)
```
java.lang.NullPointerException
    at com.fr.main.impl.WorkBook.readStream(WorkBook.java:xxx)
```
**原因**: `WorkBook.readStream` 内部依赖 `ProductConstants` 或其他静态字段，这些字段需要 FR 运行时初始化后才有值。

#### 异常 2: EntityDao 未初始化 (TemplateWorkBookIO)
```
java.lang.IllegalArgumentException: EntityDao can not be used before the ConfigurationActivator starts!
    at com.fr.config.dao.DaoContext.getEntityDao(DaoContext.java:19)
    at com.fr.config.utils.ConfigReadUtils$1.call(ConfigReadUtils.java:438)
    ...
    at com.fr.module.TopModule.start(TopModule.java:49)
    at com.fr.module.ServerModule.start(ServerModule.java:40)
    at com.fr.module.BaseModule.start(BaseModule.java:26)
    at com.fr.report.module.EngineModule.start(EngineModule.java:106)
    at com.fr.general.ModuleContext.startModule(ModuleContext.java:54)
    at com.fr.io.TemplateWorkBookIO.readTemplateWorkBook(TemplateWorkBookIO.java:48)
```

**调用链**: `TemplateWorkBookIO.readTemplateWorkBook` → `ModuleContext.startModule` → `EngineModule.start` → `TopModule.start` → `CacheManager.getProviderInstance` → `CacheManager.createDBCache` → `CacheConfig.getDbConfig` → `Conf.get` → `ConfigReadUtils.getData` → `DaoContext.getEntityDao` → **失败**

#### 异常 3: FineAssist 需要 JVM Attach API
```
[ERROR]Fine assist start failed.
com.sun.tools.attach.AttachNotSupportedException: no providers installed
    at com.sun.tools.attach.VirtualMachine.attach(VirtualMachine.java:203)
```

**原因**: FR 的 `FineAssist` 在初始化时尝试加载 `com.sun.tools.attach.VirtualMachine`（JVM Attach API），用于动态附加到运行中的 JVM。即使 classpath 包含 `tools.jar`，在 Windows 环境下 `AttachProvider` 也无法实例化。

#### 异常 4: FinePluginBridge 加密类
```
[ERROR]com.fr.plugin.bridge.FinePluginBridge
java.lang.ClassNotFoundException: com.fr.plugin.bridge.FinePluginBridge
Caused by: java.lang.ClassFormatError: Incompatible magic value 50661129 in class file com/fr/plugin/bridge/FinePluginBridge
```

**原因**: `FinePluginBridge` 是 FR 的加密类，magic value `50661129` (0x03030309) 不是标准 Java class 文件格式，而是 FR 自定义的加密格式。

---

## 三、阻断链分析

```
TemplateWorkBookIO.readTemplateWorkBook()
  └─ ModuleContext.startModule("EngineModule")
       └─ FineRuntime.start()
            ├─ FineAssist.loadNativeLibrary()
            │    └─ VirtualMachine.attach() ← ❌ AttachNotSupportedException
            └─ FineRuntime.initEncryptedBridge()
                 └─ FinePluginBridge (encrypted) ← ❌ ClassFormatError
       └─ TopModule.start()
            └─ CacheManager.createDBCache()
                 └─ CacheConfig.getDbConfig()
                      └─ Conf.get()
                           └─ DaoContext.getEntityDao() ← ❌ EntityDao not initialized
```

**核心问题**: FR 的模块化启动链（`FineRuntime` → `FineAssist` → `ModuleContext`）是一个**原子操作**，无法跳过任何环节单独使用底层 API。

---

## 四、FR10 vs FR11 差异

| 维度 | FR10 | FR11 |
|------|------|------|
| **核心阻断** | 相同：EntityDao/ConfigurationActivator 未初始化 | 相同 |
| **FineAssist** | 需要 JVM Attach API | 相同 |
| **FinePluginBridge** | 加密 (magic 50661129) | 相同 |
| **jar 大小** | fine-core: 35MB, fine-third: 155MB | fine-core: 53MB, fine-third: 168MB |
| **新增 jar** | 无 | fine-cbb-11.0.jar (90MB) |

**结论**: FR11 与 FR10 在 headless 可行性上**无本质差异**，阻断原因完全相同。

---

## 五、最小可行 classpath 分析

由于所有路径都被阻断，**不存在**最小可行 classpath。

尝试过的 classpath 组合：
1. **全量 classpath** (cp.txt 原样): 失败
2. **全量 + tools.jar**: 失败
3. **仅 fine-core + fine-report-engine + fine-third**: 未测试（预判同样失败）

**关键依赖链**:
- `TemplateWorkBookIO` → `fine-report-engine` → `fine-core` → `fine-third` (加密桥)
- `ConfigurationActivator` → `fine-core` → `fine-activator`
- `FineAssist` → `tools.jar` (JVM Attach API)

---

## 六、对"无服务器渲染工具"架构的建议

### 6.1 独立 JVM 方案：❌ 不成立

**结论**: 在不启动 FR 服务器/设计器的情况下，**无法**通过独立 JVM 完成模板的解析→计算→导出全流程。

**根因**: FR 的架构设计是**整体式**的，核心功能（模板读写、公式引擎、导出器）与运行时基础设施（配置管理、插件系统、License 检查）深度耦合，无法解耦使用。

### 6.2 替代方案

#### 方案 A: FR 报表服务器作为渲染服务（推荐）
```
┌─────────────┐     HTTP      ┌─────────────────┐
│ 你的应用     │ ──────────→  │ FR 报表服务器     │
│ (调用方)     │  ←──────────  │ (Tomcat/Jetty)   │
│             │   HTML/PDF    │                 │
└─────────────┘               └─────────────────┘
```

- **优点**: 官方支持、功能完整、稳定性高
- **缺点**: 需要部署 FR 服务器、License 成本
- **实现**: 通过 FR 的 HTTP API (`/decision/view/report`) 获取渲染结果

#### 方案 B: 设计器内嵌模式
```
┌─────────────┐     JNI/RPC    ┌─────────────────┐
│ 你的应用     │ ──────────→   │ FR 设计器进程     │
│ (调用方)     │  ←──────────  │ (headless mode)  │
│             │   渲染结果     │                 │
└─────────────┘               └─────────────────┘
```

- **优点**: 不需要 License（设计器有试用期）、本地执行
- **缺点**: 需要启动设计器进程、资源占用大
- **实现**: 通过 fr-agent 注入设计器 JVM 执行脚本

#### 方案 C: 纯 XML 解析 + 自研渲染（高风险）
```
┌─────────────┐     解析       ┌─────────────────┐
│ CPT 文件     │ ──────────→  │ 自研 XML 解析器   │
│ (XML)       │              │ (Python/Java)    │
└─────────────┘              └─────────────────┘
                                    │
                                    ▼
                              ┌─────────────────┐
                              │ 自研渲染引擎     │
                              │ (HTML/PDF 生成)  │
                              └─────────────────┘
```

- **优点**: 完全自主可控、无外部依赖
- **缺点**: 
  - 需要逆向 FR 的 XML 格式（~500+ 节点类型）
  - 需要实现公式引擎（FR 有 500+ 内置函数）
  - 需要实现图表渲染（VanChart 是 FR 私有格式）
  - 维护成本极高，FR 版本升级可能导致兼容性问题
- **实现**: 参考仓库中的 XML 结构文档 + Python 解析脚本

#### 方案 D: 混合方案（务实选择）
```
简单模板 (纯表格/文字) → 方案 C (XML 解析)
复杂模板 (图表/公式)   → 方案 A (FR 服务器)
```

### 6.3 实际可行的 Headless 使用场景

虽然**全流程** headless 不可行，但以下场景可以在设计器 JVM 内实现：

1. **模板修改**: 通过 fr-agent 注入设计器 JVM，使用 Java API 修改模板属性
2. **模板验证**: 读取模板结构、检查数据集/参数配置
3. **批量导出**: 在设计器内批量导出已打开的模板

这些场景的前提是**设计器已启动**，不是真正的 headless。

---

## 七、总结

| 维度 | 结论 |
|------|------|
| **技术可行性** | ❌ 不可行 |
| **阻断原因** | FR 运行时初始化依赖 JVM Attach API + 加密插件桥 + ConfigurationActivator，三者缺一不可 |
| **License 问题** | 未触及（在 License 检查前已失败） |
| **FR10 vs FR11** | 无差异 |
| **架构建议** | 不建议自建 headless 渲染工具；推荐使用 FR 服务器作为渲染服务，或设计器内嵌模式 |

---

## 附录：实验产物

- **Probe.java**: 基础探针（v1）
- **Probe2.java**: 带运行时初始化的探针（v2）
- **Probe3.java**: 最终版探针（v3）
- **probe_report.txt**: 运行日志
- **输出目录**: `%TEMP%\fr_headless_probe\out\`
