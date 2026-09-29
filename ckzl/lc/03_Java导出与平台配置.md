<!--
KB_INDEX: {
  "title": "Stage 8 · Java API 导出与平台类配置",
  "stage": "pipeline",
  "tags": [
    "调试",
    "选型",
    "diff"
  ],
  "keywords": [
    "Java导出",
    "无头",
    "运行前提",
    "Configuration",
    "平台配置"
  ],
  "summary": "Java API 导出（无头产物落盘）、Java API 运行前提、平台类配置的 Java 写法（Configuration 类）"
}
-->

# Stage 8 · Java API 导出与平台类配置

> 本页为 [08_技术选型与调试.md](08_技术选型与调试.md) 拆分分篇 3/3（2026-09-29 断链治理，单篇 ≤400 行）；返回 [导航页](08_技术选型与调试.md)。

---

## 17. Java API 导出（无头产物落盘）

三层级模型（doc-1108/3814）——不能只记三段式链，有两条完全不经过 `execute()` 的导出路径：

1. **模板级** `((com.fr.main.impl.WorkBook) wb).export(OutputStream)`（返回 boolean，不查库）；
2. **数据固化级** `new com.fr.io.exporter.EmbeddedTableDataExporter().export(OutputStream, com.fr.base.io.IOFile[, Map])`（查库但不算版面；**文件数据集必须用三参重载**；它 implements `Exporter` 而非 `AppExporter`）——「报表连数据发给外部但不给库权限」这一常见需求的唯一答案；
3. **结果级** `TemplateWorkBook.execute(Map, com.fr.report.stable.fun.Actor)` + `AppExporter.export(OutputStream, ResultWorkBook)`。

注意 `TemplateWorkBook` 接口不是 IOFile，须转 `WorkBook`。

**format → (exporter, actor) 映射表**：

| format | exporter | actor |
|--------|----------|-------|
| 原样 Excel | `ExcelExporter()` | `WriteActor` |
| 分页 Excel | `PageExcelExporter(List)` | `PageActor` |
| 分 Sheet Excel | `PageToSheetExcelExporter(List)` | `PageActor` |
| xlsx | `Excel2007Exporter()` | — |
| 大数据 | `LargeDataPageExcelExporter(List,boolean)` | — |
| PDF/Word/图片/CSV/文本 | `PDFExporter()` / `WordExporter()` / `ImageExporter(String,int)` / `CSVExporter()` / `TextExporter()` | — |

三个 List 参数均取自 `ReportUtils.getPaperSettingListFromWorkBook(FineBook)`。

**CSV 编码边界（doc-773）**：CSV 编码无法在单次导出调用指定，只能靠 CSV 导出编码插件改 `csvcharset` 并重启；该设定是**服务器级**而非模板/任务级——「改了但没用」的典型静默失效族。

> 来源:帆软官方帮助 doc-1108/3814/773

---

## 18. Java API 运行前提（对所有 FR Java API 路线通用）

1. **env 启动**：`WorkContext.switchTo(WorkContext.getFactory().build(webInfPath))` + `com.fr.general.ModuleContext.startModule(com.fr.store.StateServiceActivator.class.getName())`；
2. **收尾**：`com.fr.general.ModuleContext.stopModules()`，不调 JVM 不退出；
3. **编译期 jar 清单**（`WEB-INF/lib` 下 fine 开头 12 个 + sqlite-jdbc + servlet-api + tools.jar + slf4j-simple + 数据源驱动/插件）；
4. ⚠️ `com.fr.module.ModuleContext` 与 `com.fr.general.ModuleContext` 同名不同类，**只有后者有 stopModules**。

> ③④ 属于「没写全就根本跑不起来」的门槛。

> 来源:帆软官方帮助 doc-3814

---

## 19. 平台类配置的 Java 写法（Configuration 类）

FR10 配置层通用范式（对邮件/短信/外观/数据连接等所有 XxxConfig 通用，doc-2512/3474/2662）：

1. 所有平台配置都是 `com.fr.config.DefaultConfiguration` 子类的单例 `XxxConfig.getInstance()`；
2. **写入必须包在 `com.fr.transaction.Configurations.update(new com.fr.transaction.WorkerAdaptor(XxxConfig.class){ public void run(){ ... } })` 里，直接调 setter 不落库且不报错**（三段式 idiom：`update(new Worker(){ void run(){...} Class[] targets(){return new Class[]{XxxConfig.class};} })`）；
3. Config 的 getter 多为 `field.get()` 返回持有对象本身且无 setter，须「取出来原地 mutate」；
4. 字段类型是 `com.fr.config.holder.Conf` / `ColConf`（集合型），getter 已解包成 `String`/`Integer[]`；
5. 这类配置存 FineDB、**与 .cpt 模板 XML 无对应节点**，fr_check.py 校验不到，改完需重启工程；**无 XML 可 diff，唯一校验手段是写完 `getInstance().getXxx()` 回读断言**。范例：`com.fr.decision.config.mobile.MobileConfig`（getWidgetIconConfig / setWidgetDefaultHeight）。

**fine_conf_entity 通用排查动作（doc-2662）**：`<ConfigClass>.<id>` 的 id **不可按名反推字段**——`com.fr.web.WebSocketConfig` 同时存在 `keyStorePassword`（明文 legacy 槽，只有 `getOldKeyStorePassword()` 读它、**无 setter**）与 `keyStorePasswordEncrypted`（现役槽，`setKeyStorePassword(p)` 字节码 = `keyStorePasswordEncrypted.set(StorageEncryptors.getInstance().encrypt(p))`）；老文档教的 id 在新版里只是一次性迁移源（`WebSocketActivator#encryptPassword()` 只搬一次），改了不报错、不生效、无日志。**写任何 `<ConfigClass>.<id>` 之前，先 dump setter 看它 `.set` 到哪个 `Conf` 字段**。

> 来源:帆软官方帮助 doc-2512/3474/2662

### 19.1 decision 层 setXxxBean(Bean) 写入铁律（read-modify-write）

`Service.getInstance().setXxxBean(bean)` 型 API（decision 层）**默认按 read-modify-write 调用**：`bean = svc.getXxxBean()` → mutate → `svc.setXxxBean(bean)`，**禁止 `new Bean()` 只填部分字段**。判据：`branch_bytecode_probe <jar> '<Service>$1' run` 看有无 ifnull 跳过字段，**无守卫即全量覆盖**（已三连命中：doc-3474 MobileOtherSettingsService / doc-879 SecurityService（12 字段）/ doc-2948 部分 Service）。覆盖语义形态家族：

- **无条件覆盖**：doc-3474（MobileOtherSettingsService）；
- **逐字段 ifnull**：doc-3050；
- **对象级 ifnull + 字段级无条件**：doc-4039；
- **嵌套开关门**（第四形态，doc-4252）：`MobileService$3#run()` 两道 ifeq 门——`isAppUpgradeOn()` false 则后 7 字段全不写、`isServerEmbedded()` false 则 embeddedServerName/Url 不写，GUI 折叠区被直译成代码嵌套，「只改了子项、整段静默丢弃，FineDB 回读全是旧值」；同类 `MobileService$2#run()`（setAppMsgProxy）却是单字段无条件覆盖。

> ⚠️ **凡 decision Bean 写入 API，先 dump 其 Worker 的 run() 找嵌套 ifeq 门再写**；App 侧（内置服务器/升级提醒/消息代理）唯一安全写法 = `MobileConfig` 原地 mutate（见 §16.2 中 doc-4252 两行）。

> 来源:帆软官方帮助 doc-879（铁律）；形态变体 doc-4252/3474/3050/4039/2948

---

---


---
