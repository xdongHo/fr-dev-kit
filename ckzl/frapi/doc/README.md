<!--
KB_INDEX: {
    "title": "ckzl/frapi/doc",
    "stage": "api-reference",
    "tags": [
      "API",
      "Java",
      "包名速查"
    ],
    "keywords": [
      "包名速查",
      "TemplateWorkBookIO",
      "DBTableData",
      "ConfigurationActivator"
    ],
    "summary": "FR 10.0 Java API 文档索引：包名速查表、验证记录、参数面板格式化 API 清单、设计器建表 SQL 执行"
  }
-->

# ckzl/frapi/doc

> javap 验证过的 FR 10.0 Java API 方法签名与包名参考。

← [返回主路由](../../gf/FR_HEADLESS_GUIDE.md)

---

## 文件清单

| 文件 | 内容 |
|------|------|
| `frjars_manifest.txt` | FR 10.0 核心 jar 清单与类列表 |
| `API验证记录_2026-07-31.md` | javap 实测验证记录（方法签名、返回类型） |
| `参数面板格式化API清单.md` | 参数面板相关 API 参考 |
| `ChartPainter图表画笔_API条目.md` | 图表画笔 ChartPainter 实测条目（包名/签名/拼写陷阱，2026-09-12 javap） |

## 核心包名速查（验证过）

> ⚠️ 旧文档中的包名多处错误。以下为 javap 实测验证。

| 类 | 正确包名 | 所在 jar |
|----|---------|---------|
| WorkBook | `com.fr.main.impl.WorkBook` | fine-report-engine |
| WorkSheet | `com.fr.report.worksheet.WorkSheet` | fine-report-engine |
| FRFont | `com.fr.general.FRFont` | fine-core |
| Style | `com.fr.base.Style` | fine-core |
| Formula | `com.fr.base.Formula` | fine-core |
| ColorBackground | `com.fr.base.background.ColorBackground` | fine-core |
| DSColumn | `com.fr.report.cell.cellattr.core.group.DSColumn` | fine-report-engine |
| FunctionGrouper | `com.fr.report.cell.cellattr.core.group.FunctionGrouper` | fine-report-engine |
| SummaryGrouper | `com.fr.report.cell.cellattr.core.group.SummaryGrouper` | fine-report-engine（汇总分组，已实现） |
| FormulaGrouper | `com.fr.report.cell.cellattr.core.group.FormulaGrouper` | fine-report-engine（公式分组，携带公式字符串，`$$$`=当前值；⚠ 构造参数/setFormula(String) 待 javap 核验）。`week()`/`year()` 公式为 Excel 兼容语义：**周日为周首日、跨年第一周归入上一年**（doc-316） |
| FU | `com.fr.stable.unit.FU` | fine-core |
| AbstractFunction | `com.fr.script.AbstractFunction`（唯一 abstract = `public Object run(Object[])`，须 public 无参构造） | fine-core |
| FunctionConfig | `com.fr.file.FunctionConfig`（extends Configuration，注册必须包 `Configurations.update(new WorkerAdaptor(FunctionConfig.class){...})`） | fine-core |
| FunctionDef | `com.fr.stable.script.FunctionDef`（三参构造 `(name, description, className)`；⚠ 不是 `com.fr.script.FunctionDef`） | fine-core |
| FunctionManager | `com.fr.file.FunctionManager#addFunctionDef`（字节码仅两条指令，转发给 FunctionConfig） | fine-core |

完整列表 → 阅读 [API验证记录_2026-07-31.md](API验证记录_2026-07-31.md)

## 能力说明（2026-08-07 实测更新）

> **核心原则**：模板生成**优先使用 FR Java API**（通过 fr-agent `/exec` Nashorn 注入 Designer JVM 执行），格式标准、类型安全、Designer 可正常编辑。

> 权威事实表见 `ckzl/gf/FR_HEADLESS_GUIDE.md §K`，此处为速查。

| API | 状态 | 说明 |
|-----|------|------|
| `TemplateWorkBookIO.writeTemplateWorkBook(wb, path)` | ✅ **可用**（fr-agent /exec 注入后） | path 为 reportlets 相对路径 |
| `TemplateWorkBookIO.readTemplateWorkBook(path)` | ❌ 不可用 | 磁盘读依赖 web 会话环境 |
| `Form.export(OutputStream)` | ✅ **可用**（fr-agent /exec 注入后） | .frm 写盘，绝对路径 |
| `ConnectionConfig.getInstance()` | ✅ **可用**（fr-agent /exec 注入后，Designer JVM 内） | ⚠️ 独立 JVM 外不可用（触发 License 验证） |
| `javax.xml.transform.Transformer` | ❌ 禁用 | 破坏 FR XML 格式（属性重排/CDATA 损坏） |

## 相关指引

- Java API vs Python XML 能力对比 → [../ckzl/lc/03_报表构建.md](../ckzl/lc/03_报表构建.md) §13
- GUI 操作追踪 API 映射 → [../fr-agent/README.md](../fr-agent/README.md)
- Java API 示例代码 → [../ckzl/frapi/ex/README.md](../FR%20JAVA%20API%20示例/README.md)
- 类名精确签名/构造坑（如 com.fr.general.FRFont → P-9458: 无 public 无参构造, 用 getInstance）→ `python ckzl/zsk/gczsk/query_kb.py class <全限定类名>` 或 `part <关键字>`（api_kb 14588 零件行不在向量索引, jcxt/js查类名本体属结构盲区）
