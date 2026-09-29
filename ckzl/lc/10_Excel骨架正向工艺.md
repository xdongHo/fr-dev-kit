<!--
KB_INDEX: {
  "title": "流程F: Excel骨架正向工艺(示例数据→xlsx→cpt→数据集→图表)",
  "stage": "pipeline",
  "tags": ["⭐高频", "正向工艺", "Excel转cpt", "骨架生成", "示例数据驱动"],
  "keywords": ["流程F", "Excel骨架", "gen_skeleton", "excel2cpt", "Excel2007ReportImporter", "extract_charts", "示例数据", "ds.field", "表样", "1280×768", "图表管线", "正向生成", "openpyxl合并", "NPE", "转换清源"],
  "summary": "示例数据+业务需求→Excel表样骨架(gen_skeleton)→无头转cpt(Excel2007ReportImporter,52ms实证)→SQL/参数(NODE-02/03)→数据集替换示例行;图表管线1280×768抽取(extract_charts)→hbfa容器JSON→cpt CC/frm网页框。含openpyxl合并区『先merge后样式』铁律与importer选型表(全反射+反编译实证2026-09-29)"
}
-->

# 流程 F：Excel 骨架正向工艺（示例数据驱动）

← [返回 lc 目录](README.md) · 工具模块：[kfgj/excelgy](../../kfgj/excelgy/README.md)

> **定位**：`ckzl/lc/00_需求分析流水线.md` §4「延伸(正向)」箭头的落地实现。
> 用户给**几行示例数据 + 大致业务需求** → 产出带数据集绑定的 cpt/frm。
> 与流程 A 的关系：流程 A 从 `ckzl/hbfa/` 60 套骨架**选型**；流程 F 从业务数据**正向生成**。
> 来源：GLM-in-Excel 插件逆向研究（2026-09-29，`~/.fr_dev_kit/experience/`）+
> GUI 操作追踪 + 设计器 JVM 反射/反编译实证（FR 10.0.19）。

## 0. 全流程图

```
输入契约(JSON: 业务元信息+参数+列定义+两三行示例数据+图表规格)
   │ F1  python kfgj/excelgy/gen_skeleton.py contract.json -o 骨架.xlsx
   ▼
Excel 表样骨架 xlsx（遵守 00_需求分析流水线 §2 表样规范）
   │ F2  python kfgj/fr-agent/exec_js.py kfgj/excelgy/excel2cpt.js   ← 无头，52ms
   ▼      （等价 GUI：文件→打开Excel→另存为；需设计器已注入 fr-agent）
骨架 cpt（此时 fr_check 应只剩"未找到任何数据集"——这是 F3 的入口条件）
   │ F3  NODE-02/03：db_schema 探表 → verify_sql 验证 → 数据集/参数写入
   ▼
带数据集的 cpt
   │ F4  删示例数据行，ds.field 绑定行(蓝字行)设为扩展 DSColumn；公式格核对
   ▼
成品明细 cpt ──F5 图表管线──► extract_charts.py → 布局JSON → hbfa 选型/CC装配
```

## 1. F1 生成 Excel 表样骨架

```bash
python kfgj/excelgy/gen_skeleton.py <contract.json> -o <骨架.xlsx>
```

契约 JSON 结构（完整示例见 `kfgj/excelgy/example_contract.json`）：

| 键 | 内容 |
|----|------|
| `report` | name / type(`detail`网格·`canvas`画布) / sheet / ds_name |
| `params[]` | 参数名/控件类型/示例值 → 顶部 5 行参数面板区（导入后可删） |
| `columns[]` | 列标题/字段名/宽度/numfmt |
| `sample_rows[]` | **几行示例数据**（业务方提供） |
| `summary` | 合计行位置+公式 |
| `charts[]` | detail 模式=🟠占位合并格；canvas 模式=px 坐标组件 |

内置安全协议（继承 GLM-in-Excel 逆向结论）：公式风险预检（除零/INDIRECT/OFFSET
high 级拒绝）+ 生成后回读断言。

## 2. F2 无头转 cpt（实证 2026-09-29）

```bash
python kfgj/fr-agent/exec_js.py kfgj/excelgy/excel2cpt.js   # 先改脚本内 INPUT/OUTPUT
```

**importer 选型表**（设计器 JVM 反射 + jar 反编译实证）：

| 类 | 格式 | 入口 |
|----|------|------|
| `com.fr.io.importer.ExcelReportImporter` | .xls (HSSF) | `generateWorkBookByStream(InputStream)` |
| `com.fr.io.importer.Excel2007ReportImporter` | **.xlsx (XSSF)** | 同签名，public 无参构造 |
| `ExcelReportImporterFactory.createExcelImporter(String)` | — | ⚠ 实测传完整路径仍回 HSSF 版，**不按路径分发**，勿用 |

- doc-view-737 配方：`importer.generateWorkBookByStream(fis)` → `wb.export(fos)`
- 实测：销售订单示例 52ms / 7150 bytes / sheets=1，fr_check 仅缺数据集
- **GUI 等价路径**：设计器 文件→打开Excel→另存为（流程 D 追踪实证可行）

### ⚠ 铁律：openpyxl 合并区域必须「先 merge 后样式」

`Excel2007ReportImporter.traverseByRows → createStyle` 对**合并区右下角格缺失**
无空保护（字节码 offset 302 `endRow.getCell()` 后直接解引用，行 290 NPE）。
openpyxl 先设样式后 `merge_cells()` 会**清掉覆盖格**（保存的 XML 里 B1..G1 消失）
→ 必然 NPE。**先 merge 再对 MergedCell 逐格上样式**则覆盖格落盘（`<c r="G1" s="1"/>`），
转换正常。`gen_skeleton._style_region` 已内置此序，手写 xlsx 时务必遵守。

### 转换后必做：转换清源

按 `ckzl/zsk/xtgt/patterns/复杂模板改造协议.md` 第①步清三垃圾（纯格式空格/
坏 definedNames/外部引用）。生成器产出的骨架样式格可控，垃圾量远小于真实业务簿。

## 3. F3 数据集与参数

走标准节点：`ckzl/gzjd/02_数据集.md` + `03_参数面板.md`
（探表 `db_schema` → 写 SQL → `verify_sql` 过闸 → 数据集写入 cpt 的 TableDataMap）。
骨架顶部 5 行参数区此时提供参数名/控件类型/示例值的**单一事实源**，做完可删。

## 4. F4 示例行 → 数据集数据

- 表样中蓝字浅蓝底 `ds1.field` 行即 DSColumn 绑定意图（00_需求分析流水线 §2 三态）
- 删除示例数据行，将绑定行设为纵向扩展；合计公式核对引用范围
- 出口：`fr_check` 无"未找到数据集"错误，`--online` 全检通过

## 5. F5 图表管线（1280×768）

```bash
python kfgj/excelgy/extract_charts.py <book.xlsx> -o layout.json [--canvas 1280x768]
```

- 抽取：锚点 EMU→px（TwoCellAnchor/OneCellAnchor 双兼容）、类型→FR 图型映射、
  系列（名称/分类/值引用）、grouping
- 输出**hbfa 风格 containers JSON**（百分比栅格 + px 原值），衔接
  `ckzl/hbfa/` 选型装配：cpt 走单元格内嵌图表（`<O t="CC">`），frm 走网页框组件化
- 画布约定：**1280×768**（本流程默认）；frm 骨架库画布为 1280×720
  （1920×1080@150% 有效视口），跨用时 `--canvas` 换算

## 6. 已知边界

- excel2cpt.js 依赖设计器在线（fr-agent /exec 19000）；离线时走 GUI 手动路径
- Excel2007ReportImporter 的 Map 配置入口（按标题/按位置等 GUI 选项）未枚举，
  骨架生成场景用默认整簿转换即可
- 带真实 Excel 图表的 xlsx 转换后图表不会变 cpt 图表元素——图表走 F5 管线重建

## 7. 交叉引用

- 表样契约：`ckzl/lc/00_需求分析流水线.md` §2
- 转换清源：`ckzl/zsk/xtgt/patterns/复杂模板改造协议.md`
- GUI 追踪：`ckzl/lc/09_GUI操作追踪.md` + `kfgj/fr-agent/README.md`
- 骨架选型：`ckzl/hbfa/README.md`
- 安全协议来源：`~/.fr_dev_kit/experience/2026-09-29_GLM-in-Excel插件逆向研究.md`（用户私有，不入包索引）
