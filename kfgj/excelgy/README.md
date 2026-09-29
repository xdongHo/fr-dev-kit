<!--
KB_INDEX: {
  "title": "kfgj/excelgy(Excel骨架正向工艺工具)",
  "stage": "tools",
  "tags": ["工具", "流程F", "Excel", "骨架", "转换"],
  "keywords": ["gen_skeleton", "excel2cpt", "extract_charts", "Excel2007ReportImporter", "契约JSON", "示例数据", "图表抽取"],
  "summary": "流程F工具模块: 契约JSON→表样xlsx(gen_skeleton.py)/无头xlsx→cpt(excel2cpt.js,经fr-agent /exec)/图表→hbfa容器JSON(extract_charts.py)。主文档见ckzl/lc/10_Excel骨架正向工艺.md"
}
-->

# kfgj/excelgy — Excel 骨架正向工艺工具（流程 F）

主文档：`ckzl/lc/10_Excel骨架正向工艺.md`（含铁律与实证）

| 脚本 | 作用 | 用法 |
|------|------|------|
| `gen_skeleton.py` | 契约 JSON → 表样骨架 xlsx（detail 网格 / canvas 画布 1280×768） | `python gen_skeleton.py <contract.json> -o <out.xlsx>` |
| `excel2cpt.js` | 无头 xlsx→cpt（等价 GUI 打开Excel→另存为） | 改脚本内路径后 `python ../fr-agent/exec_js.py excel2cpt.js`（需设计器已注入） |
| `extract_charts.py` | Excel 图表 → hbfa 风格布局 JSON（几何/类型/系列） | `python extract_charts.py <book.xlsx> [-o layout.json] [--canvas 1280x768]` |
| `example_contract.json` | 契约示例（销售订单两行明细） | — |

实测战绩（2026-09-29，FR 10.0.19）：骨架生成→52ms 转换→fr_check 仅缺数据集
（F3 入口条件）；图表抽取还原类型/锚点/系列引用。
