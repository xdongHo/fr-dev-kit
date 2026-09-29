<!--
KB_INDEX: {
  "title": "fr11_knowledge 复核报告（i18n 记录问题 + FR11 探针落地）",
  "stage": "fr11-knowledge",
  "tags": ["FR11", "复核", "i18n", "fr-agent", "探针", "质量闸门"],
  "keywords": ["复核", "i18n", "臆造类名", "LocaleFinder", "inject_fr11", "fr-agent", "探针", "attach", "getLocText", "验证", "实践验证"],
  "summary": "2026-08-22 对其他机器生成的 fr11_knowledge（i18n 线）做本机双 FR 实证复核：键数基本属实，17 个新增类名全部臆造，LocaleFinder 论断被推翻；同时补齐 FR11 fr-agent 探针（inject_fr11.py）并完成注入+运行时 getLocText 实证。"
}
-->

# fr11_knowledge 复核报告 —— i18n 记录问题清单与 FR11 探针落地

> **复核时间**：2026-08-22
> **复核对象**：其他机器学习入库的 `ckzl/lc/fr11_knowledge/`（重点 i18n 线 2 份 + 实践验证 1 份）
> **复核方法**：本机双环境实证 —— FR10（`C:\Program Files\FineReport_10.0`，31 jar 静扫）+ FR11（`C:\FineReport_11.0`，255 jar 静扫 + fr-agent 注入后 JVM 运行时反射）
> **子报告**：`fr10_i18n_verification_report.md`（FR10 侧）/ `fr11_install_survey_report.md`（FR11 侧）

---

## 一、总体判定

| 被复核记录 | 判定 | 一句话结论 |
|-----------|------|-----------|
| `fr11_i18n_api_optimization.md` §1 键数表 | ✅ 基本属实 | 4 项中 3 项精确（core 324/chart 427/locale 97），dec 3748 对应 zh_TW（zh_CN 实为 3749，差 1 键） |
| `fr11_i18n_api_optimization.md` §2 "新增 Java API" | ❌ **全部臆造** | 17 个类名在本机 FR11 全 255 jar 扫描 0 命中；其中 7 个存在"名称近似但包路径错误"的真实类，10 个完全无对应 |
| `fr11_java_api_i18n.md` §10.4 "FR10 无 i18n Java API" | ❌ 不属实 | FR10 有 26 个 i18n 相关类（LocaleFinder/InterProvider/LocaleManager 等完整体系） |
| `fr11_java_api_i18n.md` 附录C "LocaleFinder 疑为内部接口" | ❌ 不属实 | 是 fine-core **公开插件扩展点**（`com.fr.stable.fun.LocaleFinder`，标准 fun 扩展点形态），FR10/FR11 双证存在 |
| `fr11_java_api_i18n.md` 附录D "plugin.xml i18n 标签未知" | ⚠ 仓库内早有答案 | `<plugin-xml-i18n>` 块是 FR11 插件标配（23_FR10到11插件迁移指南 + 多篇 v11 逆向笔记实证） |
| `fr11_java_api_i18n.md` 主体（公式/插件/表结构） | ➖ 未逐条复核 | 离线文档转录内容，源头为官方文档，风险较低；附录 B 文档索引可信 |
| practice_verification（FR11 注入验证;2026-08-21 学习批产物,2026-08-26 已随 mimo 线清理移除） | ✅ 本机复现成功 | 本机 attach FR11 自带 JRE 成功（见 §三），其"必须用 FR11 自带 JDK 注入"结论正确 |

**核心教训（已回写进优化文档 §4）**：i18n keys 差异只能推断**功能方向**，不能推断 **Java 类名**——i18n key 前缀（Func_Fvs/Time_Logger 等）是文案命名空间，与 Java 包结构无映射关系。从"功能存在"跳到"我编一个类名"是 LLM 生成知识的高危幻觉模式。

## 二、17 个臆造类速查（修正对照）

| 臆造类名（原文） | 真实状态 | 真实对应（本机实证） |
|-----------------|---------|---------------------|
| com.fr.decision.data.masking.DataMaskingRule/Service/MaskAlgorithm | 无任何近似类 | 决策平台付费功能，疑插件承载（本机未装） |
| com.fr.decision.disk.DiskManagement/AutoCleanConfig/DiskMonitor | 无任何近似类 | FR 自有 Disk* 全是缓存（com.fr.cache.DiskCacheMap 等） |
| com.fr.fvs.FvsReport / component.Fvs3DComponent/FvsUnityComponent | 无 com/fr/fvs 包 | FVS 走 wysiwyg.v11 插件 + FvsShowType（fine-decision-report） |
| com.fr.log.time.TimeLogger / TimeLoggerConfig | 包路径错 | **com.fr.general.log.TimeLogger** 族 + com.fr.log.TimeLoggerProperties |
| com.fr.template.TemplateOverflow / Config | 包路径错 | com.fr.web.core.TemplateOverflowException（仅异常类） |
| com.fr.chart.map.mapbox.MapboxLayer / MapboxConfig | 无 Java 类 | mapbox 仅前端资源（css/js） |
| com.fr.chart.data.ChartDataFunction / ChartDataProcessor | 包名错（chart→chartx） | **com.fr.chartx.data.result.ChartDataProcessor** |

（完整证据链见 `fr11_install_survey_report.md` §4-§6）

## 三、FR11 fr-agent 探针落地（本机新增能力）

### 3.1 缺口确认

复核前仓库现状：`fr-agent/` 全目录 grep `FR11|11.0|FineReport_11` **0 命中**——inject.py 硬编码 FR10 路径，README 无 FR11 章节。其他机器的 practice_verification（已移除的 0821 学习批文件）声称注入成功但**脚本未入库**，本机无从复现。

### 3.2 新增 `fr-agent/inject_fr11.py`（已实测 ✅）

与 FR10 inject.py 的三处关键差异：

| # | 差异点 | 原因 |
|---|--------|------|
| 1 | **Attacher 用 FR11 自带 JRE 跑**（`C:\FineReport_11.0\jre\bin\java.exe` + 自带 `jre\lib\tools.jar`） | FR11 JRE = OpenJDK 8u191-redhat 且自带 tools.jar；混用 Corretto/Oracle JDK 会 attach 失败（practice_verification 的 jvm.dll 结论） |
| 2 | PID 识别匹配 `FineReport_11.0` + `com.fr.start` | 与 FR10 的 `FineReport_10.0` 精确区分（双 FR 共存时防注错进程） |
| 3 | `--start` 模式拉起 `bin\designer.bat` | FR11 设计器主类 com.fr.start.Designer，纯 classpath 启动 |

### 3.3 本机实测记录（2026-08-22）

```
[1/4] 拉起 C:\FineReport_11.0\bin\designer.bat
[2/4] 定位 PID=13972（等 25s GUI 初始化）
[3/4] attach: C:\FineReport_11.0\jre\bin\java.exe -cp .;tools.jar Attacher 13972 fr-agent.jar
[4/4] ✅ 18999 /ping {"status":"ok","pid":13972}   ✅ 19000 /ping {"status":"ok"}
```

**运行时实证两连**（19000 /exec Nashorn 反射）：

1. `Class.forName` 7 类探测：LocaleFinder/AbstractLocaleFinder/InterProviderFactory/InterProvider/TimeLogger(chartx 修正后)/ChartDataProcessor/TemplateOverflowException **全部 EXISTS**（AppClassLoader 已加载）
2. **真实调用 i18n API**：`InterProviderFactory.getProvider()` → `com.fr.general.InterProviderImpl`；`getLocText('Fine-Core_License_Your_License_Is_Not_Support_Multiple_Connection')` → 返回 **"当前License不支持多数据连接"** ✅
   附带确认 `LocaleFinder` 接口方法签名：`find() + currentAPILevel()`（标准 fun 扩展点）

### 3.4 使用方式

```bash
python fr-agent/inject_fr11.py                          # 设计器已起 → 直接注入
python fr-agent/inject_fr11.py --start                  # 拉起设计器再注入
python fr-agent/inject_fr11.py --exec "<Nashorn 脚本>"   # 注入后跑一段反射/验证脚本
```

陷阱继承 fr-agent/README.md：一 JVM 只能注入一次；绝不用 -javaagent（License 校验失败）；重注入需重启设计器。

## 四、已执行的修正动作

| # | 动作 | 文件 |
|---|------|------|
| 1 | 17 个臆造类名全部标注 + 真实对应回填 + 教训沉淀 | `fr11_i18n_api_optimization.md`（重写 §2，含复核警示头） |
| 2 | §10.4 论断推翻重写（FR10 i18n API 体系表） | `fr11_java_api_i18n.md` |
| 3 | 附录C 补 LocaleFinder 实证（接口/抽象/插件样例/工厂四层表） | `fr11_java_api_i18n.md` |
| 4 | 附录D 补 plugin-xml-i18n 仓库内证据引用 | `fr11_java_api_i18n.md` |
| 5 | FR10/FR11 两侧验证报告入库（本文件为汇总） | `fr10_i18n_verification_report.md` / `fr11_install_survey_report.md` |
| 6 | FR11 注入探针入库 | `fr-agent/inject_fr11.py` |
| 7 | fr-agent README 补 FR11 章节 | `fr-agent/README.md` |
| 8 | G05 断链修复（版本区分速查表→23_迁移指南；dump_attach.py 引用声明） | 见 guard 重跑记录 |

## 五、遗留风险与建议

1. **dec 键数口径**：优化文档与验证报告的统计口径（单文件 vs 模块总计）不同——后续引用键数时注明文件路径，避免歧义。
2. **脱敏/磁盘管理**：本机 FR11 未装对应插件，无法定位其 API 面；如需深挖，先在装了 `数据脱敏` 插件的环境用 fr-agent /exec 或 jar 扫描复采。
3. **fr11_knowledge 其余 13 份 summary**：未逐条复核（源为离线文档转录，风险中低）；引用其中具体 API/类名前建议同样过一遍本机 jar 探针。
4. **其他机器同步**：本复核修正应随下次 git push 分发；若远端再学 FR11 内容，先读本文件"核心教训"避免同类臆造。
