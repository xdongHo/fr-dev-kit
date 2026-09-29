<!--
KB_INDEX: {
    "title": "PageRWorkSheet cannot be cast to AnalyReport 渲染报错分析",
    "stage": "error-analysis",
    "tags": [
      "错误案例",
      "🔥新沉淀",
      "渲染报错",
      "程序化生成"
    ],
    "keywords": [
      "PageRWorkSheet",
      "AnalyReport",
      "cannot be cast",
      "view_content",
      "CellPageAttr",
      "SHADOW-RUNTIME",
      "分页预览",
      "字节码定位",
      "enginex",
      "程序化生成cpt"
    ],
    "summary": "程序化生成 cpt 时非默认单元格分页属性组合（repeat/HR 退化/冻结盖扩展行）触发 view_content 数据分析管道对分页结果 PageRWorkSheet 做 (AnalyReport) 强转失败；含字节码证据链、已验证骨架与排查方法论（2026-09-04 示例明细表B实战）"
  }
-->

# PageRWorkSheet cannot be cast to AnalyReport 渲染报错分析

> 实战来源：2026-09-04 示例报表工程/明细报表/示例明细表B.cpt 程序化重建（build_vave_detail_20260904.py 首版）。
> 该错误在 `ckzl/zsk/tbcw/README.md` 索引与 `ckzl/lc/08 §16.2` 均无命中，属新增知识（首次收录）。

---

## 1. 现象

用户浏览器打开分页预览查询页点「查询」，服务端日志（Tomcat `严重:` 前缀）：

```
严重: ERROR [standard] com.fr.report.worksheet.PageRWorkSheet cannot be cast to com.fr.report.report.AnalyReport
[SHADOW-RUNTIME] dispatch 2 tasks for SCAfterReportCalculateTrigger
```

- 模板 XML 合法（ET.parse 通过）、fr_check 仅已知误报族、SQL 直连冒烟正常；
- 同目录旧版模板（骨架不同）同环境渲染正常；
- SHADOW-RUNTIME 行是**相邻日志（异步任务）**，不是因果行——enginex 影子任务本身不引用 AnalyReport（已反编译排除），勿被它带偏。

## 2. 根因

生成器把表头行从 r=1 提到 r=0 时，引入了**已验证骨架中不存在的非默认分页属性组合**：

| 首版引入的非默认构造 | bak 已验证骨架 |
|---|---|
| 19 个表头格 `<CellPageAttr repeat="true"/>` | 全部 `<CellPageAttr/>`（默认） |
| `<HR F="0" T="0"/>`（退化重复行区间） | `<HR F="0" T="1"/>`（原文保留） |
| `FrozenColumnRow columnrow="A3"` 冻结范围盖到数据扩展行 | A3 盖空行+表头（不含数据行） |

该组合使服务端把模板推入**数据分析内容管道**：浏览器端 `com/fr/view/web/js/view.js` 发送 `cmd=view_content`，stock 处理类对结果 sheet 做 `(AnalyReport)` 强转；而分页引擎（page actor）产出的结果 sheet 是 `com.fr.report.worksheet.PageRWorkSheet`（分页预览 Result Sheet 实现），不实现 AnalyReport 接口 → ClassCastException。

## 3. 字节码证据链（javap 实证，可复现）

1. **强转点全局唯一**：扫描 `WEB-INF/lib` + `WEB-INF/plugins` 全部 218 个 jar 的类常量池，对结果 sheet 直接 `checkcast com/fr/report/report/AnalyReport` 的只有两个混淆类：
   - `com.fr.web.core.bochavy.JxlxlgxiSvndkk`（javap 头还原源名 **AnalysisAction.java**）偏移 19：`(AnalyReport) session.getReport2Show(reportIndex)`，请求参数 `recal=true` 时调 `AnalyReport.recalculate(...)`；
   - 其子类 `EspiPccjvfmUxpfmm`（源名 **ViewContentAction.java**）`getCMD()` 返回 **`"view_content"`**；孙类 `EspiPccjvfmMlkyviXasipp`（ViewContentStreamAction）另 cast `AnalysisRWorkSheet`。
3. **分页结果类型**：`com.fr.stable.PageActor` 执行产出 `PageRWorkBook`，sheet 为 `PageRWorkSheet`（`NormalPageBreakWorkSheet` 是其子类）；`AnalysisRWorkSheet`（实现 AnalyReport）只由 `ViewActor.createResultECWorkSheet` 产出。
4. **非默认 CellPageAttr 是引擎特殊分支判据**：`PageActor.isNormalPageBreak` 逐格检查 `getHighlightGroup() != null || !CellPageAttr.DEFAULT_CELLPAGEATTR.equals(getCellPageAttr())`，命中任一即走非常规分页路径。`CellPageAttr` 的合法 XML 属性为 `pageAfterColumn/pageAfterRow/pageBeforeColumn/pageBeforeRow/repeat/breakOnPaginate`（readXML 实证）。
5. **SHADOW-RUNTIME 排除**：`[SHADOW-RUNTIME] dispatch 2 tasks for SCAfterReportCalculateTrigger` 来自 `plugin-com.fr.plugin.enginex`（新计算引擎）`com.fr.nx.shadow.*`；两个任务 SCDriverRecommendRuntimeTask（JDBC 驱动版本推荐）/ SCGroupToListRuntimeTask（分组转列表）均不引用 AnalyReport，是异步邻行日志非因果。
6. **影子快照佐证**：`WEB-INF/assets/shadow/`（enginex 影子/版本镜像）中首版模板快照里 `repeat="true"` 被引擎加载-归一化剥离、数据格被补写显式左父格 `left="A2"`——引擎确实对该模板的分页属性做了特殊处理，与正常模板路径不同。

## 4. 触发场景

- **程序化生成/批量改写 cpt** 时改动了表头行结构（上移/删空行），同时引入 `CellPageAttr` 非默认值（尤其 `repeat="true"`）、改动 `<HR F= T=>` 区间、或让 `ReportSettings/FrozenColumnRow` 冻结范围覆盖到含 `<Expand>` 的数据行；
- 人工设计器操作通常不会踩中：设计器对「重复标题行」的标准序列化是 `ReportPageAttr` 的 HR 区间 + 表头格默认 CellPageAttr（见 bak 及 Mtrl Report实际.cpt 的对照）。

### 4.1 冲突速查：CellPageAttr repeat × 冻结（FrozenColumnRow）互斥组合
> 问法别名：每页重复表头 冻结 报错 / repeat HR 生成 cpt 报错 / 分页重复与冻结冲突

- 冲突本体：程序化生成 cpt 同时引入 ①`<CellPageAttr repeat="true"/>`（每页重复表头）
  ②非默认 `<HR F= T=>` 区间 ③`ReportSettings/FrozenColumnRow` 冻结范围覆盖含 `<Expand>` 数据行
  ——三者叠加使 view_content 数据分析管道强转分页结果失败（根因见 §2）。
- 设计器人工操作通常不踩中：标准序列化 = ReportPageAttr HR 区间 + 表头格默认 CellPageAttr（见 §4 对照）。
- 取舍口诀：冻结区只盖静态表头行，不盖 repeat 格与扩展行；二者都想要 → 冻结上界止于表头最后一行。
- 索引行：ckzl/zsk/tbcw/README.md 错误索引 `PageRWorkSheet cannot be cast to AnalyReport` 行（已含本冲突别名）。

## 5. 修复方案（已验证骨架，直接沿用）

明细查询页主体骨架不要发明，逐项对齐已验证版本：

```xml
<ReportPageAttr>
<HR F="0" T="1"/>                <!-- 原样保留，勿改 F/T -->
<FR/><HC/><FC/>
<UPFCR COLUMN="false" ROW="true"/>
</ReportPageAttr>
...
<CellElementList>
<C c="0" r="0">                  <!-- 空 r0 行，仅 c0 一格 -->
<PrivilegeControl/>
<Expand/>
</C>
<C c="0" r="1" s="0">            <!-- 表头在 r=1，格属性一律默认 -->
<O><![CDATA[列名]]></O>
<PrivilegeControl/>
<CellPageAttr/>                  <!-- 不加 repeat="true" -->
<Expand leftParentDefault="false"/>
</C>
<C c="0" r="2" s="1">            <!-- 数据从 r=2 起 -->
...
<HighlightAction class="com.fr.report.cell.cellattr.highlight.PageHighlightAction">
<P i="1"/>                       <!-- 行后分页公式按数据起始行配：(row()-2)%100=0 -->
</HighlightAction>
```

- 冻结行区间（如 `FrozenColumnRow columnrow="A3"`）只盖空行+表头，**不得盖到数据扩展行**；
- 生成器侧加固：凡会写出 `repeat="true"` 或篡改 HR 的逻辑一律删除/断言拦截（参见 fr_dev_kit_v2.1 `_runs/build_vave_detail_20260904.py` 的修复版注释）。

## 6. 排查方法论（本案例沉淀的通用打法）

1. **反编译 lib 定位唯一强转点**：对 ClassCastException，先扫 jar 类常量池找 `checkcast <目标类>` 的全部类（Python zipfile 逐类读字节找 `b"com/fr/.../Xxx"`），再用 `javap -c -p` 看偏移与源名（javap 首行 `Compiled from "Xxx.java"` 能还原混淆类真名）。强转点唯一时，调用栈方向立刻清晰。
2. **找"谁发的请求"**：强转点属于哪个 cmd/op（`getCMD()` 字节码字符串），再全库（含插件、前端 js 资源）反查该 cmd 的发送方，确定渲染管道归属（分页/填报/数据分析/新引擎 page_plus 是平行栈）。
3. **邻行日志先做因果排除**：异步 dispatch/调度行与异常并发时，逐个反编译邻行日志的发起类，确认其是否引用目标类型，再决定是否纳入因果链。
4. **影子快照对照**：`WEB-INF/assets/shadow/` 是引擎加载-归一化后的模板镜像/版本仓；把快照与源文件 diff，能直接看到引擎"改了什么"（剥离哪些属性、补写哪些默认父格），是定位引擎特殊分支的免费探针。
5. **正常模板对照**：同目录找同预览方式（PreviewType/isPage 相同）且正常的模板，diff Report 段骨架属性，非默认构造一目了然。

## 7. 置信度与环境绑定

- 强转点/管道归属/属性触发分支为字节码实证（置信度高）；"非默认组合→路由进 view_content 管道"的最后一环未能本机无头闭环复现（需登录 Web 会话），按还原已验证骨架的最大公约数修复后待浏览器复验（置信度中高）。
- 类名/行为绑定本机 FR 10.0（fine-report-engine-10.0.jar，混淆包 com.fr.web.core.bochavy）+ enginex 1.9.14；升级 jar 后混淆名会变，按源名（AnalysisAction/ViewContentAction）与 cmd 字符串重新定位。
