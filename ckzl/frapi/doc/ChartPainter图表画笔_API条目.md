<!--
KB_INDEX: {
  "title": "ChartPainter 图表画笔 API 条目",
  "stage": "api",
  "tags": ["Java API", "ChartPainter", "图表", "com.fr.chart"],
  "keywords": ["ChartPainter", "图表画笔", "绘图", "chart"],
  "summary": "ChartPainter（图表画笔）API 零件条目：类名/方法签名/坑位与验证标记，供查询 com.fr 图表绘制 API 时命中。"
}
-->

# ChartPainter（图表画笔）— com.fr.chart.chartattr.ChartPainter

> FR 10.0 图表服务端"结果画笔"。**2026-09-12 javap 实测条目**（jar: `fine-report-engine-10.0.jar`，探针 `kfgj/fzpy/jar_class_probe.py`）。
> 背景：eng_kb 13 次真实类探查（审计批次03 T-audit03-003）在本库零条目，本条为缺口补录。

## 类定位（实测）

| 项 | 值 |
|----|-----|
| 完整类名 | `com.fr.chart.chartattr.ChartPainter` |
| 所在 jar | `fine-report-engine-10.0.jar` |
| 父类 | `com.fr.chartx.result.ResultChartPainter`（chartx 新图表引擎结果画笔） |
| 父类接口 | `com.fr.base.chart.BaseChartPainter` + `com.fr.report.cell.ColRowChangeListener`（继承自父类） |

## 公有签名（javap 实测，FR 10.0）

| 签名 | 备注 |
|------|------|
| `ChartPainter()` | 无参构造 |
| `ChartPainter(com.fr.chart.chartattr.ChartCollection, com.fr.chart.ChartWebPara)` | 数据+前端参数双参构造 |
| `void addNamedGlyph(java.lang.String, com.fr.chart.chartglyph.ChartGlyph)` | — |
| `void setNamedGlyph(java.lang.String, com.fr.chart.chartglyph.ChartGlyph, int)` | — |
| `java.lang.String getGlyphName(int)` | — |
| `com.fr.chart.chartglyph.ChartGlyph getGlyph(int)` | — |
| `int getGlyphCount()` | — |
| `void setSelectedIndex(int)` / `int getSelectedIndex()` | — |
| `com.fr.base.chart.ChangeConfigProvider getChangConfig()` | ⚠ 官方拼写 `Chang`（少一个 e），引用时禁止"自动纠正" |
| `com.fr.base.chart.result.WebChartIDInfo getChartIDInfo()` | — |
| `java.lang.String[] getWidgetDependenced()` | — |
| `void update(com.fr.base.chart.BaseChartPainter, int)` | — |
| `com.fr.json.JSONObject createChartWidgetConfig(com.fr.stable.web.Repository, int, int)` | 前端部件配置 JSON |
| `com.fr.json.JSONObject createAttributeConfig(com.fr.stable.web.Repository)` | 属性配置 JSON |
| `java.awt.Image covertToClearImage(int, int, int, int, com.fr.base.chart.chartdata.CallbackEvent)` | ⚠ 官方拼写 `covert`（非 convert） |
| `protected java.awt.Image convertToImage(int, int, int, int)` | protected，父类同型方法实测存在 |
| `java.lang.Object clone()` / `boolean equals(java.lang.Object)` | — |
| `boolean useChange(com.fr.stable.web.Repository)` | — |
| `void recordWebPreview()` | — |

## 拼写陷阱清单（0.10c 风格，实测）

| 字面量 | 正确拼写 | 后果 |
|--------|---------|------|
| `getChangeConfig` | 实为 `getChangConfig`（Chang） | NoSuchMethod |
| `convertToClearImage` | 实为 `covertToClearImage`（covert） | NoSuchMethod |

## 角色（推演，待实战标注）


## 检索提示

- 类存在性/包名: `python kfgj/fzpy/jar_class_probe.py --jars C:/frjars find ChartPainter`
- 签名: `javap -cp C:/frjars/1_fine-report-engine-10.0.jar com.fr.chart.chartattr.ChartPainter`