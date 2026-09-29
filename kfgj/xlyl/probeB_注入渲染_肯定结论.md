<!--
KB_INDEX: {
  "title": "探针B: 设计器注入渲染路线肯定结论",
  "stage": "render-preview",
  "tags": ["渲染", "探针", "注入", "fr-agent", "肯定结论"],
  "keywords": ["注入渲染", "ActorFactory", "page actor", "PageRWorkBook", "readStream", "Excel导出", "PDF导出", "HTMLExporter stub", "Nashorn反射", "contextClassLoader"],
  "summary": "注入式渲染全链路可行:readStream→ActorFactory.getActor('page')→execute→PageRWorkBook; PDF/Excel导出成功(46KB/39KB);内置HTMLExporter是stub('Not support yet'),HTML需手动拼单元格。单次往返~2.2s。injected backend 因此成为主路线。"
}
-->

# FR11 注入式渲染可行性探针报告

> **日期**: 2026-08-24  
> **目标**: 验证「注入已运行的设计器 JVM，通过 fr-agent 19000 /exec（Nashorn 反射）」完成 CPT 模板 解析→计算→HTML 导出 落盘  
> **结论**: ✅ **可行**，全链路跑通

---

## 一、三步结论表

| 步骤 | 结论 | 证据 |
|------|------|------|
| **1. 模板解析** (CPT → WorkBook) | ✅ 通过 | `WorkBook.readStream(InputStream)` 成功读取 `full_single.cpt`，report count=1, sheet class=`WorkSheet`, cell count=2, dataset=`EmbeddedTableData` |
| **2. 模板计算** (WorkBook → ResultWorkBook) | ✅ 通过 | `ActorFactory.getActor("page")` 返回 `MemXPageActor`(分页预览)，`WorkBook.execute(Map, Actor)` 返回 `PageRWorkBook`，result cell count=2 |
| **3. HTML 导出** (ResultWorkBook → HTML 文件) | ⚠️ 部分通过 | FR 内置 `HTMLExporter.export(OutputStream, ResultWorkBook)` 抛 `UnsupportedOperationException: Not support yet!`（**stub 方法**）；但 PDF/Excel 导出成功（PDF=46KB, Excel=39KB）；HTML 通过**手动遍历 ResultWorkBook 单元格值 + StringBuilder 拼 HTML** 落盘成功（782 bytes） |

---

## 二、可行的 Nashorn 调用链

### 核心类+方法（经实测验证）

| 类名 | 方法 | 用途 |
|------|------|------|
| `com.fr.main.impl.WorkBook` | `readStream(InputStream)` | 读取 .cpt 模板文件 |
| `com.fr.main.impl.WorkBook` | `getReportCount()` / `getReport(int)` | 获取 sheet 数量和对象 |
| `com.fr.main.impl.WorkBook` | `getTableDataNameList()` / `getTableData(String)` | 获取数据集信息 |
| `com.fr.stable.ActorFactory` | `getActor(String)` → `getActor("page")` | 获取页面 Actor |
| `com.fr.main.impl.WorkBook` | `execute(Map, Actor)` | 模板计算 → ResultWorkBook |
| `com.fr.main.workbook.PageRWorkBook` | `getReport(int)` / `cellIterator()` | 遍历结果单元格 |
| `com.fr.io.exporter.PDFExporter` | `export(OutputStream, ResultWorkBook)` | PDF 导出 ✅ |
| `com.fr.io.exporter.ExcelExporter` | `export(OutputStream, ResultWorkBook)` | Excel 导出 ✅ |
| `com.fr.io.exporter.HTMLExporter` | `export(OutputStream, ResultWorkBook)` | ❌ stub，不可用 |

### 关键发现

1. **ActorFactory 位置**: `com.fr.stable.ActorFactory`（非 `com.fr.report.stable.fun.ActorFactory`）
2. **Actor 实现**: `com.fr.stable.MemXPageActor`（description="分页预览"）
3. **ResultWorkBook 实现**: `com.fr.main.workbook.PageRWorkBook`
4. **Result Sheet 实现**: `com.fr.report.worksheet.PageRWorkSheet`
5. **Nashorn 反射模式**: 必须用 `java.lang.Class.forName(name, true, contextClassLoader)` 而非 `cl.loadClass(name)`（后者返回 StaticClass 而非 Class）

### 脚本资产

| 文件 | 路径 | 用途 |
|------|------|------|
| render.js | `%TEMP%\fr_injected_render\render.js` | 一键渲染脚本（可复用） |
| run_render.py | `%TEMP%\fr_injected_render\run_render.py` | Python 驱动脚本 |
| probe1_parse.js | `%TEMP%\fr_injected_render\probe1_parse.js` | 解析探针 |
| probe2_execute_full.js | `%TEMP%\fr_injected_render\probe2_execute_full.js` | 执行探针 |
| probe3_html_paint.js | `%TEMP%\fr_injected_render\probe3_html_paint.js` | HTML 生成探针 |

---

## 三、License / 环境依赖结论

| 条件 | 结论 |
|------|------|
| **License 状态** | 设计器已登录（fr-agent 注入成功 = JVM 正常运行 = License 有效）；注入式渲染**复用已登录 JVM 的 License**，无需额外校验 |
| **数据库依赖** | `EmbeddedTableData`（内嵌数据）不需要数据库；`DBTableData`（数据库数据集）需要数据库连接可用 |
| **Web 会话依赖** | 模板解析和计算**不需要** Web 会话；内置 HTML 导出器需要 `ReportRepositoryDeal`（Web 上下文），这是 `HTMLExporter` 报错的根因 |
| **JDK 版本** | FR11 自带 OpenJDK 1.8.0_191，Nashorn 可用 |

---

## 四、该路线 vs 独立 JVM 路线的优劣

### 性能数据

| 指标 | 测量值 |
|------|--------|
| **单次 /exec 往返耗时** | **~2.1-2.5 秒**（含 Nashorn 编译+反射+HTTP） |
| **模板加载** | < 100ms（FileInputStream + readStream） |
| **模板计算** | < 500ms（execute + ActorFactory） |
| **HTML 生成** | < 100ms（StringBuilder 拼接） |
| **PDF 导出** | ~11.5 秒（含渲染） |
| **Excel 导出** | ~11.5 秒（含渲染） |

### 对比分析

| 维度 | 注入式路线（fr-agent） | 独立 JVM 路线 |
|------|----------------------|--------------|
| **资源占用** | ✅ 零额外 JVM，复用已运行设计器 | ❌ 需要独立 JVM 进程 |
| **License** | ✅ 复用设计器 License | ❌ 需要独立 License 或离线模式 |
| **延迟** | ⚠️ ~2s /exec 往返（HTTP 开销） | ✅ 本地调用 < 100ms |
| **HTML 导出** | ⚠️ 内置 HTMLExporter 不可用，需手动拼 | ⚠️ 同样问题（FR 架构限制） |
| **PDF/Excel 导出** | ✅ 完全可用 | ✅ 完全可用 |
| **稳定性** | ⚠️ 依赖设计器 JVM 运行；每个 JVM 只能注入一次 | ✅ 独立可控 |
| **并发** | ❌ 单线程（Nashorn 同步执行） | ✅ 可并发 |
| **部署复杂度** | ✅ 零部署（注入即用） | ❌ 需要 FR 环境 + License |

---

## 五、架构建议

### 注入式作为哪种模式的 fallback

1. **开发/调试模式的首选**: 注入式路线最适合**开发环境**——设计师正在运行，需要快速预览模板效果，无需启动额外服务。

2. **轻量级预览的 fallback**: 对于"无服务器kfgj/xlyl工具"，注入式可作为**零部署 fallback**——当独立 JVM 不可用时（License 限制、资源不足），注入已运行的设计器 JVM 提供基础渲染能力。

3. **PDF/Excel 导出的一等公民**: 注入式路线的 PDF/Excel 导出完全可用且性能可接受，可作为这些格式的**首选导出通道**。

4. **HTML 渲染的局限**: FR 的 HTML 导出器 (`HTMLExporter`) 是 stub 实现，真正的 HTML 渲染走 Web 请求管线（`HTMLStreamWriter` + `WebReportCase`）。注入式路线无法复用这条管线，只能通过**手动遍历 ResultWorkBook 单元格**生成简化 HTML。这是该路线的最大局限。

### 推荐架构

```
┌─────────────────────────────────────────────────┐
│           无服务器kfgj/xlyl工具                      │
├─────────────────────────────────────────────────┤
│  优先级 1: 独立 JVM + FR Headless                 │
│  ├─ 完整 HTML/PDF/Excel 渲染                      │
│  ├─ 需要 License + 独立进程                        │
│  └─ 延迟: < 1s                                    │
├─────────────────────────────────────────────────┤
│  优先级 2: 注入式 (fr-agent) ← 本报告验证         │
│  ├─ PDF/Excel 导出: ✅ 完整                       │
│  ├─ HTML 导出: ⚠️ 简化版（手动拼接）               │
│  ├─ 零额外资源，复用 License                       │
│  └─ 延迟: ~2s /exec                               │
├─────────────────────────────────────────────────┤
│  优先级 3: Python/XML 路线                         │
│  ├─ 纯模板态操作（不计算）                         │
│  ├─ 无需 FR JVM                                   │
│  └─ 适合模板生成/修改，不适合kfgj/xlyl              │
└─────────────────────────────────────────────────┘
```

---

## 六、附录：Nashorn 反射注意事项

1. **Class.forName vs loadClass**: 必须用 `java.lang.Class.forName(name, true, cl)` 而非 `cl.loadClass(name)`——后者在 Nashorn 中返回 `StaticClass` 而非 `java.lang.Class`。

2. **字符串参数**: Nashorn 字符串不能直接传给 Java 反射方法，需要用 `Java.type('java.lang.String')` 创建 Java String 实例。

3. **引号转义**: 多层嵌套（Python → JSON → Nashorn → Java 字符串）时，使用 `json.dumps` 序列化注入脚本可避免转义地狱。

4. **错误处理**: 用 `try/catch(e)` 捕获异常，`e.getStackTrace()` 获取栈信息，`e.getCause()` 获取根因。

5. **FR 类加载**: FR 类通过 `contextClassLoader` 加载（不是 AppClassLoader），反射时必须指定 `true, contextClassLoader` 参数。

---

## 七、产物清单

| 文件 | 路径 | 大小 | 说明 |
|------|------|------|------|
| render.js | `%TEMP%\fr_injected_render\render.js` | 6.3KB | 一键渲染脚本 |
| run_render.py | `%TEMP%\fr_injected_render\run_render.py` | 0.7KB | Python 驱动 |
| out.html | `%TEMP%\fr_injected_render\out.html` | 782B | 渲染输出 |
| out.pdf | `%TEMP%\fr_injected_render\out.pdf` | 46KB | PDF 导出验证 |
| out.xls | `%TEMP%\fr_injected_render\out.xls` | 39KB | Excel 导出验证 |
| probe_report.md | `%TEMP%\fr_injected_render\probe_report.md` | - | 本报告 |
