<!--
KB_INDEX: {
  "title": "官方文档沉淀增补-验收与判级",
  "stage": "error-analysis",
  "tags": [
    "官方文档",
    "验收",
    "判级"
  ],
  "keywords": [
    "魔数校验",
    "导出校验",
    "插件清单",
    "plugin_manifest",
    "JS控件名校验",
    "getWidget",
    "验收断言",
    "无JavaAPI",
    "四步全0",
    "文档消化",
    "图缺口"
  ],
  "summary": "官方文档持续学习沉淀的验收断言与判级强化细则（原 AGENTS.md §1.2 2026-08 增补块，2026-08-20 v3 拆出）。创建/导出/插件交付任务验收前必读",
  "trigger": "何时用：官方文档沉淀条目的验收标准与知识判级",
  "when_not": "何时不用：非知识沉淀类任务（日常报表开发）"
}
-->

# 官方文档沉淀增补 — 验收与判级（2026-08）

> **本文从 AGENTS.md v2 §1.2 的「2026-08 增补」块拆出**（2026-08-20 v3 瘦身重构）。
> **何时读**：创建报表/导出/插件交付任务的 **STEP 5 验证之前必读**；判「无 Java API」或写验收断言时必读。

## 前置判定（生成前）

- 生成前先判定模板类型——根节点 `<Form>`=决策报表(.frm) / `<WorkBook>`=普通报表(.cpt)，并记录插件版本清单（doc-3045）。

## 收尾产物校验

- 导出类任务**必做产物魔数校验**——HTTP 200 / 文件非空 ≠ 成功，必须校验产物真实文件类型（doc-1120）；拼预览/导出 URL 时把 `op` 当作请求层开关（默认 `write`，doc-2194）。

## 插件交付物

- 凡模板依赖官方插件，交付包必须附**插件/版本清单**（插件名 + 四件套最低版本：报表服务器 / JAR / APP / HTML5 移动端展现插件，doc-3195 门槛 V10.4.55、doc-3045 为 V10.4.49）；`plugin_manifest.json` 建议字段 `{name, minPluginVersion, minJarDate, reason, source}`，并加 `filesystem_evidence`（如 `WEB-INF/lib/postgresql-*.jar`）——有留痕的插件可静态检出、无留痕的才退回运行时 `PluginManager.getContext(id).isRunning()` 预检（doc-3898）。

## JS 引用控件名生成期校验

- 参数面板控件事件装配固定走 `WParameterLayout.getWidget(name)` → 校验 `w != null` → 校验 `event ∈ w.supportedEvents()` → `addListener`；JS 载荷里引用的每个控件名都应在生成期证明存在（doc-1206/1828）。

## 交付检查（打 war / 平台挂载）

1. war 包压缩部署不支持插件安装/删除/更新，**打 war 前必须预装所有插件**；WebLogic 外接库必须配 JNDI 数据源，模板侧一律 `NameDatabaseConnection` 按名引用（doc-1934）。
2. 「写盘 + 直连 URL 可开」≠ 交付完成：还需在决策系统「目录管理」挂目录节点（落 FineDB `FINE_AUTHORITY_OBJECT`，不落 .cpt）+ 分配查看权限 + 功能列表注册「决策平台」功能点（doc-3322）。
3. 交付目标为第三方 iframe 嵌入时，确认工具栏策略（空数组 or `__showtoolbar__=false`）与安全头（X-Frame-Options/CSP）并交付集成 URL（doc-4624）。

## 产物命名

- 手机端专属模板必须显式写 `writeTemplateWorkBook(wb, ".../xxx_mobile.cpt")`——设计器勾「手机模板画布」会自动另存 `_mobile.cpt`，API `setMobileCanvasSize(true)` 只置布尔位不改文件名，会覆盖 PC 版（doc-575）。

## 运行环境体检

- 新增一类「校验运行环境而非模板」的检查——`FineDBProperties.getInstance().isUsingDefaultOption()` 判外接库是否真生效、WebSocket `isStartup()`/`getRunningPort()` 三元比对、JDK/tools.jar/AWT 探针（doc-3860/4130/3814）。

## 验收与判级强化（2026-08-09 追加）

### 判「无 Java API」必须四步全 0

中文名/直译 find → 底座机制名 find → 正文字面量全 jar 扫 → 「文档要求用户自己写/上传/编译的东西」单独探（doc-563/2205/576/3475）；**不按正文体裁预判**——纯运维文（`ps -ef|grep`+`kill -9`）一条 `find Redundant` 也命中 `ThreadRedundantDetect`（doc-3977），纯 GUI 截图文一探即命中整条 API 面（doc-1573/4510）。第三方插件/厂商文档 0 命中只读作「探针 jar 集未覆盖」，不是「FR 无此机制」（doc-3774）。

### 验收断言

1. 配置值是类全名/插件 id → 回读相等不算通过，必须反查注册表（doc-3050/1163）
2. 读取模板后断言对象**运行时类型**（`instanceof`），不只判 `!=null`/`getReportCount()>0`（doc-4115/190/2664）
3. 环境自检 `checkXxx()` 先确认非短路链、没吞异常（doc-1342）
4. `.cpt` 落盘断言改为 `getCurrent().getPath()` 比值 + `getWorkResource() instanceof SimpleWorkResource` + `File(...).isFile() && length()>0`（`writeTemplateWorkBook` 恒返回 true、`EmptyWorkResource.exist` 恒 true，两条都是假阳性，doc-2804/1698）

### 文档消化前置

先扫正文「如下图/下图所示/如图/见下图」计数——官方 .txt 是文档的**有损投影**（88% 含图引用，操作顺序/交互行为只存在于图内），凡结论写「文档未说明 X」必须先确认不落在任一图缺口附近（doc-2608）；官方文档是 wiki 式社区可编辑站点，`com.fr.*` 类名/默认值/生效条件一律字节码为准（doc-75/2365）。

---

*本文为 AGENTS.md v3 kernel 的卫星文件；最后更新 2026-08-20（v3 拆分）。*
