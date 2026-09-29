<!--
KB_INDEX: {
  "title": "Stage 3 · Java API 正确包名速查",
  "stage": "pipeline",
  "tags": [
    "单元格",
    "样式",
    "行高",
    "冻结"
  ],
  "keywords": [
    "Java API",
    "包名",
    "类名",
    "报表构建"
  ],
  "summary": "验证过的 Java API 正确包名速查表（报表构建选型第一步）"
}
-->

# Stage 3 · Java API 正确包名速查

> 本页为 [03_报表构建.md](03_报表构建.md) 拆分分篇 1/9（2026-09-29 断链治理，单篇 ≤400 行）；返回 [导航页](03_报表构建.md)。

---

## 2. Java API 正确包名速查

> ⚠️ Ver0.1 和旧文档中的包名多处错误。以下为实测验证的正确包名。

| 类 | 正确包名 | 所在 jar |
|----|---------|---------|
| **WorkBook** | `com.fr.main.impl.WorkBook` | fine-report-engine |
| **WorkSheet** | `com.fr.report.worksheet.WorkSheet` | fine-report-engine |
| **FRFont** | `com.fr.general.FRFont` | fine-core |
| **Style** | `com.fr.base.Style` | fine-core |
| **Formula** | `com.fr.base.Formula` | fine-core |
| **ColorBackground** | `com.fr.base.background.ColorBackground` | fine-core |
| **CoreDecimalFormat** | `com.fr.base.CoreDecimalFormat` | fine-core |
| **CellBorderStyle** | `com.fr.base.CellBorderStyle` | fine-core |
| **DSColumn** | `com.fr.report.cell.cellattr.core.group.DSColumn` | fine-report-engine |
| **FunctionGrouper** | `com.fr.report.cell.cellattr.core.group.FunctionGrouper` | fine-report-engine |
| **SummaryGrouper** | `com.fr.report.cell.cellattr.core.group.SummaryGrouper` | fine-report-engine |
| **CellExpandAttr** | `com.fr.report.cell.cellattr.CellExpandAttr` | fine-report-engine |
| **DefaultTemplateCellElement** | `com.fr.report.cell.DefaultTemplateCellElement` | fine-report-engine |
| **EmbeddedTableData** | `com.fr.data.impl.EmbeddedTableData` | fine-core |
| **CommonCondition** | `com.fr.data.condition.CommonCondition` | fine-core |
| **ReportletHyperlink** | `com.fr.js.ReportletHyperlink` | fine-report-engine |
| **WBorderLayout** | `com.fr.form.ui.container.WBorderLayout` | fine-report-engine |
| **FU** | `com.fr.stable.unit.FU` | fine-core |
| **YearControl** | `com.fr.plugin.widget.year.YearControl` | 插件 |
| **DateEditor** | `com.fr.form.ui.DateEditor` | fine-report-engine |
| **ComboCheckBox** | `com.fr.form.ui.ComboCheckBox` | fine-report-engine |
| **FormSubmitButton** | `com.fr.form.parameter.FormSubmitButton` | fine-report-engine |
| **FreeButton** | `com.fr.form.ui.FreeButton` | fine-report-engine |
| **HSQL 驱动** | `com.fr.third.org.hsqldb.jdbcDriver` | 内置（FR 重打包） |

> 💡 **`com.fr.third.*` 重打包规律**（来源: 帆软官方帮助 doc-2574）：FR 会把第三方库重打包进 `com.fr.third.*` 命名空间（HSQL 官网的 `org.hsqldb.jdbcDriver` → FR 里是 `com.fr.third.org.hsqldb.jdbcDriver`）。凡内置驱动/工具类都先试 `com.fr.third.` 前缀，不要照抄上游官网的原生包名——这是排查 `ClassNotFound / 驱动加载失败` 的通用线索。HSQL 连接 URL 模板 `jdbc:hsqldb:file:[PATH_TO_DB_FILES]`，且 HSQL 表名**不得以数字开头**（连接/取数报错），生成器拼 SQL 可在本地直接拦。

> ➕ 包名速查补充（来源: 帆软官方帮助 doc-215 / doc-2498）：参数面板**单选下拉** = `com.fr.form.ui.ComboBox`（fine-report-engine），与 `ComboCheckBox`（下拉勾选多选）是**两个不同类**——无头构建「单选下拉」误用 ComboCheckBox 是高频错；单元格内控件场景见 §3.23。

### 2.1 ❌ 旧文档错误包名
| 错误 | 正确 |
|------|------|
| `com.fr.report.worksheet.WorkBook` | `com.fr.main.impl.WorkBook` |
| `com.fr.base.FRFont` | `com.fr.general.FRFont` |
| `com.fr.web.ReportletHyperlink` | `com.fr.js.ReportletHyperlink` |

### 2.2 系统性误记源补充（doc-958 + doc-3860）

> 来源: 帆软官方帮助 doc-958（条件属性）/ doc-3860（数据连接配置）

**修正一处系统性误记（doc-958）**：主体/组件背景的类型是接口 `com.fr.general.Background`（fine-core），而非 `com.fr.base.background.Background`（全 jar 零命中、不存在）；实现类才在 `com.fr.base.background.*`，且 `ColorBackground` **构造为 private，只能 `ColorBackground.getInstance(Color)`**；`GradientBackground(Color, Color[, int])` / `ImageFileBackground(String)` 为公开构造。

**.frm body 一组已核签名（doc-958）**：`WFitLayout` / `WAbsoluteBodyLayout` / `WBodyLayoutType` / `PaddingMargin(int,int,int,int)` + `XML_TAG='Margin'` / `AbstractGapWidget#setCompInterval` / `AbstractBorderStyleWidget#setBackground+setMargin+setBorderStyleNoBackground` / `WatermarkAttr(WatermarkData)` + `IOFile#addAttrMark`（水印需 fine-decision-10.0.jar）。

**「同名不同包」实例（doc-3860）**：MySQL8 的 hibernate 方言是 `com.fr.third.org.hibernate.dialect.MySQL8Dialect`，而 `com.fr.data.core.db.dialect.MySQL8Dialect` 是 FR 自己的取数方言——两者用途完全不同、都真实存在，`find MySQL8Dialect` 会同时命中；探针挑错包**不报错**（类真实存在、能编译），只在运行期表现为方言不匹配。

**「getter/setter 不对称」实例（doc-3860）**：`JDBCDatabaseConnection` 对外是 `setUser()/getUser()`，但 `writeXML` 里取的是 `getUsername()`（user/password 实际被包进 `com.fr.data.auth.Authentication`）——按 setter 名反推 XML 属性名会翻车。

### 2.3 公式单元格构建（doc-3741）

> 来源: 帆软官方帮助 doc-3741（公式）

公式单元格也可用纯 Java 精确构建（与 Python/XML 路线并列），标准链：

```java
DefaultTemplateCellElement cell = new DefaultTemplateCellElement(col, row, new com.fr.base.Formula("=SUM(A1:A3)")); // 值槽公式
sheet.addCellElement(cell);
...
com.fr.io.TemplateWorkBookIO.writeTemplateWorkBook(wb, path);
```

- 公式对象 = `com.fr.base.Formula(String)`（fine-core）；`new Formula("=...")` 与 `new Formula("...")` 等价（`BaseFormula` 内部归一化前导 `=`，practice/topic_1493 实读）；XML 落点 `<O t="Formula">`（单元格 `<C>` 内）。
- 与 §3.11 前导 `=` 铁律互补：单元格值公式一律以公式对象写入、建议统一带前导 `=` 书写，勿拼字符串。
- 参考 `practice/topic_1493_java/FormulaCellBuilder.java`（doc-1493：公式落 .cpt 单元格 + 内置函数替代插件）。

### 2.4 通用判据：同一 FR 类的双持久化形态（doc-615）

> 来源: 帆软官方帮助 doc-615（模板Web属性）

⚠ 同一 FR 类可能存在**双持久化形态**，两条链必须分开落地（模板类 vs 平台类判据的交叉特例）：

- 实例态 → 写进 .cpt 的对应 XML 节点（模板类产物）；
- 单例态（`com.fr.config.Configuration`）→ 写 FineDB `fine_conf_entity`（namespace = 类名）。

典型实例 `ReportWebAttr`：既是模板属性对象（→ `.cpt` 的 `<ReportWebAttr>` 节点），又是 Configuration 单例（namespace=`"ReportWebAttr"`，`getInstance()`，写必须包 `Configurations.update(new WorkerAdaptor(ReportWebAttr.class){...})`）。凡文档出现「模板>模板 Web 属性 X」与「服务器>服务器配置 X」成对入口，一律按两条链分别落地；**禁止把服务器级配置当作能写进 .cpt 的节点**（反之亦然）。

> ➕ 平台链运维备注（来源: 帆软官方帮助 doc-3861）：`Configuration` 单例持久化于 FineDB `fine_conf_entity` 表（namespace = 类名），该表随平台外接数据库**整体迁移**。外接库迁移时若排序规则选 `CI_AS`，报 `fine_conf_entity 违反 PRIMARY KEY` ⇒ 工程有脏数据，检查 SQL：`select lower(ID),COUNT(1) FROM FINE_CONF_ENTITY GROUP BY LOWER(ID) HAVING COUNT(1)>1`（ID 即平台配置类名，重复 ⇒ 脏数据）；建库建议 `COLLATE Chinese_PRC_CS_AS`（大小写敏感）。

---

### 2.5 公式字符串构建铁律：拼接 + XML 转义（doc-1897 + doc-249）

> 来源: 帆软官方帮助 doc-1897（字符串拼接函数）/ doc-249（计算操作符说明）

**① 字符串拼接生成铁律（doc-1897）**：

- 无头生成「拼接数字字符串」的输出单元格时，默认产出 `CONCATENATE(a, b, ...)` 而非 `&` 或公式 `+`——公式 `+` 会把 `"001"+"1201110"` 数字化相加成 `1201111`（`MathExpression#objectBinaryOperation` 先 `objectToNumber`，两边都非 null 才整体换成 Number，全有或全无）；
- 显式区分两条链路：往单元格写公式必须用 `new com.fr.base.Formula("=...")`（对象，运行时进公式引擎）；普通 `String` 用 Java `+` 是编译期拼好的字面量、与 FR 无关——混用会「本地跑对、报表里不对」；
- 生成期自检：扫描即将写入的 `"字面量"+"字面量"` 形态，若两边 `GeneralUtils.objectToNumber(x,true)` 均非 null 即告警改用 CONCATENATE（示例见 `practice/topic_1897_java/StringConcatFormula.java` §4）。

**② 公式字符串 XML 转义纪律（doc-249）**：

- 公式存入 `<Cell formula="...">` 时必须做实体转义：`>` → `&gt;`、`<` → `&lt;`、`&` → `&amp;`（`&&` → `&amp;&amp;`）、`"` → `&quot;`——比较/逻辑操作符（> < &&）在公式中高频，headless 直接拼接会出现非法 XML/解析失败或属性值漂移；转义后语义不变；
- 公式写入 Java setter 待核（候选 `TemplateCellElement` 公式 setter，公式类疑 `com.fr.formula.Formula`）——当前以 XML 写 `formula` 属性最稳；参考 `practice/topic_249_hermes/formula_cell.xml`（最小示例）。

### 2.6 常用报表函数速查（doc-813）

> 来源: 帆软官方帮助 doc-813（报表函数概述）

16 个函数全是「单元格公式字符串」，统一走 §2.3 的 Formula 构建链（`new Formula("=...")`，函数名大小写不敏感），**无需实例化函数类**：

| 分组 | 函数 | 要点 |
|------|------|------|
| 单元格定位 | `COL()` / `ROW()` | 无参，返回当前格列/行号（1 起；A5 中 =col()=1、=ROW()=5），常用于行号列/条件属性 |
| 数据集元数据 | `COLCOUNT(td)` / `ROWCOUNT(td)` / `COLNAME(td,列号)` / `TABLEDATAFIELDS(td)` / `TABLEDATAS()` | 首参为数据集名字符串，按「报表(私有)→服务器(公有)」查找、同名私有优先；`TABLEDATAS(0)`=仅服务器、`TABLEDATAS(1)`=仅报表 |
| 取数 | `VALUE(td,列,行)` / `MAP(td,匹配列,匹配值,取数列)` / `SQL(连接名,SQL语句,列,行)` | VALUE 4 种多态（列号/列名、行号/省略）；SQL 省略行号=返回整列（赋给单元格得到数组） |
| 连接元数据 | `FIELDS(连接名)` / `RECORDS(连接名)` / `TABLES(连接名)` | — |
| 编解码 | `ENCODE(...)` / `DECODE(...)` | — |
| 国际化 | `I18N('File')` | 字符串参数用英文双引号、I18N 用单引号 |

- **MySQL 纯数字表名须反引号包裹**（否则解析歧义）；数据集函数首参拼错/漏建在运行期**静默返回空或错误**。

### 2.7 常用聚合/序列函数速查（doc-831）

> 来源: 帆软官方帮助 doc-831（常用函数概述）

| 函数 | 语义边界（静默坑） |
|------|------|
| `SUM(...)` | 数值/逻辑值/文本表达式都算（TRUE=1、`"70"`=70），数组/引用只取数值 |
| `COUNT(...)` | 只计数字；可解析文本/逻辑值/零参与，不可解析文本忽略 |
| `AVERAGE(...)` | 第二参 `countString=false` 时文字/逻辑值不参与计数；**空单元格恒不参与**（默认文字按 0 参与） |
| `CHAR(n)` | 数字转字符 1~65535（CHAR(88)=X、CHAR(45)=-） |
| `DATE(y,m,d)` | month/day 溢出自动进位、≤0 往回减；**year≤0 取绝对值+1**；返回 `yyyy-MM-dd` 字符串（与 doc-876 的 date() 合并为函数全貌） |
| `MAX/MIN` | **无数字返回 0**；MIN 遇错误值返回错误 |
| `TIME(h,m,s)` | 当天日期+指定时间，越界按时分秒进位 |
| `RANGE(from,to,step)` | 等差序列；**方向不对返回空**（doc-3493 隔行变色 `range(2,100,2)` 同源） |

- 全部为公式字符串：Java 侧 `new Formula(整串)` 注入单元格即可；内置函数实现类（`com.fr.function.SUM` 等）由引擎注册、无需 new（参考 `practice/topic_831_hermes/CommonFunctionsFormulaBuilder.java`）。

### 2.8 插件函数引用与免插件等价（doc-1493）

> 来源: 帆软官方帮助 doc-1493（常用函数集合插件）

- ① **插件函数在模板中的落点** = 普通公式文本引用（`com.fr.base.Formula` + `TemplateCellElement#setFormula`，落 `<C><O t="Formula">`），与普通函数写法完全一致；函数分组：JS 脚本 ScriptEval / 字符串 / 加密 / 统计 / JSON / HTML / 图片；
- ② **免插件等价实现映射**（无头构建可在 Java 侧算好落值，减少模板运行期插件依赖）：加密族 = `java.security.MessageDigest`（SHA-1/SHA-256/MD5 小写 hex）+ DES/ECB/PKCS5Padding（JDK）；JSONPathFinder = `com.jayway.jsonpath.JsonPath.read`（仅 GET，URL 自做 HTTP）；统计族 = `org.apache.commons.math3.stat.descriptive.DescriptiveStatistics`；拼音族 = pinyin4j；任意函数 = 继承 `com.fr.script.AbstractFunction` 重写 `run(Object[])`，按包结构放 `WEB-INF/classes` 重启注册；
- ③ **易错点**：固定字符串加密必须带英文双引号（数字可不加）、StringFind 索引从 0 起、ScriptEval 总参数须为奇数个、JSONPathFinder 仅 GET；
- ④ **前提**：模板引用插件函数 = 运行期依赖服务器已装「常用函数集合」插件——**缺插件预览只显示 #NAME? 等错误值（零报错）**。

---


---
