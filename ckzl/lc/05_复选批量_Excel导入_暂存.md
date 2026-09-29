<!--
KB_INDEX: {
  "title": "Stage 5 · 复选批量 / Excel 导入 / 暂存",
  "stage": "pipeline",
  "tags": [
    "填报",
    "提交",
    "JS交互",
    "工具栏"
  ],
  "keywords": [
    "复选框全选",
    "批量操作",
    "Excel导入",
    "标记导入插件",
    "显示值转换",
    "暂存"
  ],
  "summary": "复选框全选与批量操作、Excel 标记导入插件、显示值转换（形态数据字典）、填报暂存（自动/手动/清空）"
}
-->

# Stage 5 · 复选批量 / Excel 导入 / 暂存

> 本页为 [05_填报与交互.md](05_填报与交互.md) 拆分分篇 5/5（2026-09-29 断链治理，单篇 ≤400 行）；返回 [导航页](05_填报与交互.md)。

---

## 24. 复选框全选与批量操作（doc-1215）

> 来源: 帆软官方帮助 doc-1215（JS实现复选按钮控件全选和批量操作）

控件事件类 Java 装配链 + 四段 JS 模板（事件 JS 是纯转录内容，沉淀为模板库供生成器直接拼装）：

```java
com.fr.form.ui.CheckBox / TextField / Button        // 控件
+ com.fr.form.event.ChangeEvent(状态改变) / ClickEvent(点击) / EditorEndEvent(编辑结束)
  经 Widget#addEvent 挂载
行级控件绑定数据 = 左父格 setLeftParentCell(A3 左父格=B3)；同名控件随父格扩展为多实例（同名控件数组）
→ _g().getWidgetsByName("box") 返回当前页控件数组（getWidgetsByName 数组批量寻址的前提）
```

**四段 JS 模板（含插件版变体 setCellsQuick/setCellsValueInBatch）**：

- ① 全选赋值：遍历 `_g().getWidgetsByName("box")` + `_g().setCellValue(0, cr.col, cr.row, flag)` 批量赋值（reportIndex=0 即第一个 sheet，多 sheet 按序）；
- ② 行选回写全选框；
- ③ `deleteRows` 批量删行；
- ④ 编辑结束批量修改。

- ⚠ 边界：不支持移动端与新填报预览；大数据量配填报分页（§10.3 四件套）；同名控件应位于扩展单元格（左父格指向数据列），是 getWidgetsByName 数组寻址的前提（fr_check 对单元格填报控件应允许同名、仅参数面板控件要求唯一）。

---

## 25. Excel 标记导入插件（doc-4238）

> 来源: 帆软官方帮助 doc-4238（Excel标记导入）

纯理解级插件文档（无 com.fr.* API）；无头构建只能产出**满足设计规范的模板 + 提示人工配置标记**，唯一编程入口为运行期 JS `FR.MarkExcelImport.markImportExcel()`：

- **模板设计规范（无头构建必须满足，否则导入失败）**：① 待导入列（行）标题须与 Excel 表头一致（按标题匹配）；② 内容区域单元格必须可扩展（CellExpandAttr 既有面）；③ 内容区域有数据集字段须列表展示（ds_cell RG 既有面）；④ 内容区域外待导入单元格必须初始化（任意设置值/样式，不得为空——未初始化单元格导致导入失败，属设计期可查、静默失败类）；
- **配置入口**：「模板>Excel导入标记」（多 sheet 须每页单独设置，否则前端选不到该 sheet）；「标记导入」按钮 = 模板>模板web属性>填报页面设置>为该模板单独设置>工具栏添加；
- **配置存 finedb 而非 .cpt**（`fine_excel_mark_conf` / `fine_excel_mark_sheet_conf`），无公开 com.fr.* API——不要到 .cpt 里找配置节点；
- **选型拦截**：不支持移动端预览与新填报预览（交付目标为移动端时回退传统填报导入）；不支持导入图片/斜线表头/内容区域合并单元格（自动拆成列表）；建议 Excel 2007 及以上。

---

## 26. Excel 导入显示值转换（单元格形态数据字典）（doc-3809）

> 来源: 帆软官方帮助 doc-3809（Excel导入显示值转换）

- **转换链路**：导入值视为「显示值」→ 提交时按**单元格形态数据字典**映射为「实际值」入库（男→1）；不设形态字典则导入值原样入库（静默、无报错）；
- **模板侧配置** = 单元格形态 > 数据字典（自定义，实际值/显示值成对；候选 `com.fr.data.impl.NameDictionary` ⚠待核验）；XML 落点 `<Cell><CellAttr><Form><DataDic><Name>/<Display>>`——与控件数据字典（doc-2116 的 Widget `<Dictionary>`）是**两个挂载点**，不要混；
- **全局侧配置** = 「将数据转换为实际值提交」开关（Excel标记导入插件能力，存 finedb `fine_conf_entity` 的 `CustomConfig.excelImportAttr.showValue`，**不落 .cpt**；漏配时导入值原样入库且无报错）；
- **硬约束**：须装 Excel标记导入插件、不支持数据字典>公式、移动端不支持 Excel 导入。

---

## 27. 填报暂存（自动暂存/手动暂存/清空暂存）（doc-2711）

> 来源: 帆软官方帮助 doc-2711（填报暂存）

- ① **自动暂存开关** XML 落点 `<WebWriteContent>/<OtherAttr autoStash="true">`（已核验，§21.1.1 与 doc-136 逐字吻合）；填报 Web 属性类 `com.fr.web.attr.WriteAttr`（autoStash setter 待核验）；
- ② **手动暂存/清空** = 填报工具栏内置按钮（容器 `<ToolBars>` 已核验，按钮节点名待核验）；
- ③ **暂存运行时表** `PUBLIC.FINE_WRITE_STASH`：ID（主键）/ DATA（CSV：单元格+内容）/ REPORTPATH（报表物理路径，非平台路径）/ USERNAME；按登录用户隔离，清空或提交成功后删除；查表用 FineDB 连接（驱动 `com.fr.third.org.hsqldb.jdbcDriver` / URL `jdbc:hsqldb:file://${ENV_HOME}/embed/finedb/db` / sa）；
- ④ **自定义提交按钮提交后不自动清暂存** → 回调 JS `_g().clear(undefined, false)`（事件链 EventType/JavaScriptAction 已登记）；
- ⑤ **边界**：不支持移动端/图片文件控件/图表模板/按查询参数区分；
- ⚠ 布局缺陷（doc-2711 §5.2，原建议落点 03 铁律/fr_check，收归本节）：**首列为空白列且不扩展 → 填报暂存失效**；自动修复 = 删除空白列或给空白列设扩展（无头生成可静态检测，校验器应提前拦截）。
