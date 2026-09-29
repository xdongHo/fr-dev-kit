<!--
KB_INDEX: {
  "title": "dsl/skills — 标准组件技能库（R39，MCP 技能的前置层）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["name", "spec", "python", "type", "chart_skill", "semantic"],
  "summary": "> 夜间作战 R39 产物。三个标准生成器：**spec（纯数据 dict/yaml）→ 标准 FR XML**， > 全部口径取自 `dsl/semantic_layer.yaml`（唯一事实源），产物内建 guardrails G1-G"
}
-->

# dsl/skills — 标准组件技能库（R39，MCP 技能的前置层）

> 夜间作战 R39 产物。三个标准生成器：**spec（纯数据 dict/yaml）→ 标准 FR XML**，
> 全部口径取自 `dsl/semantic_layer.yaml`（唯一事实源），产物内建 guardrails G1-G4 硬闸，
> G5 真库冒烟由 `golden/run_golden.py --smoke` 实证。这三个技能就是 R29 MCP Server 的首批 tools。

## 快速上手

```bash
cd dsl/skills
# ① 数据集：spec → DBTableData（numeric/ORG+PERM/period CASE 自动织入）
python -X utf8 dataset_skill.py '{"name":"ds1","source":"org_sum_actual","fields":["entity","data"],"numeric_cols":["data"],"filters":["view = ''YTD''"],"permission":"full"}' out.cpt

# ② 参数面板：控件清单 → 参数面板页（para_* 铁律/165px 栅格/entity 公式/lock_js）
python -X utf8 panel_skill.py '{"widgets":[{"type":"label","name":"lb_legal","text":"法人："},{"type":"combo","name":"para_legal","dict":"dict_legal"}]}' out.cpt

# ③ 图表：echarts 类型 + 数据绑定 → FR 图表 cpt
python -X utf8 chart_skill.py '{"echarts_type":"bar","variant":"分组柱状","title":"销售","dataset":{...},"binding":{"category":"entity","values":[{"field":"data","name":"金额"}]}}' out.cpt
python -X utf8 chart_skill.py --types          # 支持清单
python -X utf8 chart_skill.py --unsupported    # 暂不支持清单（含原因）

# golden 回归（9 用例：6 正例 + 3 坏 spec；--smoke 加 G5 真库冒烟，需 VPN）
python -X utf8 golden/run_golden.py [--smoke]
```

Python 代码内调用（R29 MCP 封装口径）：

```python
import sys; sys.path.insert(0, "dsl/skills")
import dataset_skill, panel_skill, chart_skill
doc, meta = dataset_skill.build(spec)   # 产物未过 guardrails 会抛 SkillError（不出坏产物）
doc, meta = panel_skill.build(spec)
doc, meta = chart_skill.build(spec)
```

## ① dataset_skill — spec 契约

| 键 | 必填 | 说明 |
|---|---|---|
| name | ✓ | 数据集名；permission=dict 须 `dict_` 前缀，=none 须 `param_guard` 前缀（G4 豁免口径） |
| source | ✓ | **semantic datasources 键**（如 `org_sum_actual`），自动展开 schema.table 防同名副本 |
| fields | ✓ | 输出列；须在 semantic columns 事实内（有 columns 映射的表强制校验） |
| numeric_cols | full 时 ✓≥1 | varchar 数值列 → `COALESCE(NULLIF(col,'')::numeric,0)`（G3 硬闸） |
| filters | | 原生 SQL 条件（AND 连接；禁分号/禁 `${{`） |
| params | | 引用参数（须在 semantic standard_params/global_params） |
| period_param | | `para_month`/`para_month_bud` → period CASE 自动织入 |
| permission | | `full`=ORG+PERM（缺省）/ `dict`=仅 PERM / `none`=param_guard 回显集 |
| distinct | | SELECT DISTINCT（字典集用） |
| order_by / alias | | 排序 / 表别名（缺省 t） |
| perm_form | | `entity`\|`plant`：表无 columns 事实时显式指定 PERM 形态（见"返工点"） |

声明参数自动 = params ∪ ORG 级联参数（织入 ORG 时）∪ period 参数。

## ② panel_skill — spec 契约

```yaml
widgets:
  - {type: label, name: lb_legal, text: "法人："}          # 标签须 lb_ 前缀
  - {type: combo, name: para_legal, dict: dict_legal}       # 控件须 para_* 前缀（铁律）
  - {type: combo, name: para_bu, dict: dict_bu, dict_deps: [para_legal]}
  - {type: combo, name: para_entity, readonly_formula: true} # entity 只读公式（semantic）
  - {type: date, name: para_year}   # 另支持 combocheckbox/number/text
lock_js: true                         # afterinit 锁定 JS（semantic __w 修 context 版）
```

- 栅格：label(45px)+控件(100px) 一组，组内偏移 +51px，组间 **165px 步进**，y=12 h=26（semantic panel_widgets.layout）
- 命中 `dict_legal/bu/region/plant` 时自动补齐四字典集（仅 PERM，来自 semantic org 模板）
- 校验拒绝：非 para_ 控件名 / lb_ 缺失 / 类型不认识 / dict_deps 引用不存在的控件 / 参数不在 standard_params

## ③ chart_skill — spec 契约

```yaml
echarts_type: bar        # 或 wordCloud/bar+line/pie/line/scatter/radar/funnel/treemap/gauge/...
variant: 分组柱状          # 每类型支持变体见 --types
title: 销售构成
dataset: {…}             # dataset_skill 同契约（ORG+PERM+numeric 硬约束自动继承）
binding:
  category: entity       # 类目列（meter/仪表盘形态可省）
  values: [{field: data, name: 金额, function: sum}]   # function: sum|first|count|com.fr.*
cell: {c: 0, r: 6, cs: 21, rs: 49}
```

**支持 22 型**（bar×4 变体/line×3/pie/scatter×2/radar/funnel/treemap/wordCloud/bar+line/heatmap/boxplot/gauge/custom + FR 原生 multiPie/gantt/structure）——实现方式是**改写在库设计器模板**（`ckzl/hbfa/组件模板/图表组件-*.cpt`，19 件实测 VanChart XML），不是凭空拼 XML。

**暂不支持（返回 SkillError，附原因，绝不编造）**：map/钻取地图（绑定含 matchResult 域配置）、graph 力导向（STALE）、candlestick K线（R1/R5 分歧未定案，保守口径）、sankey/sunburst（插件通道无 XML 模板）、parallel/lines/themeRiver（无证据）、pictorialBar（插件 Provider 架构无模板）。完整清单：`chart_skill.py --unsupported`。

## 证据链与产出分级

| 层 | 证据 | 覆盖 |
|---|---|---|
| 全证据级 | compile.py 线上同构（xcombo/xlabel/房式 cpt） | dataset 全部、panel label/combo、柱形/饼图绑定 |
| 模板改写级 | 在库设计器模板 19 件（Real designer XML） | chart 22 型的 Plot/GI/标题 |
| L2 探针级 | `_runs/night/20260904/L2/widget_facts.md`（roundtrip 断言） | panel date/number/text/combocheckbox 的类映射 |
| Java 实证级 | R1 泳道 jar 实测 | bar 横向 isBar=true、stack 枚举 |

## 验收口径（每个产物出厂即过）

1. guardrails **G1-G4 = 0 错**（build 内建，未过即 SkillError 不出产物）
2. ET.fromstring 合法（build 内建 + 落盘兜底）
3. `golden/run_golden.py` 回读断言（关键属性逐项命中）
4. `--smoke`：G5 真库执行（本轮 VPN 在线全通过，行数见 `_runs/night/R39/results.jsonl`；0 行=FAIL，父级门控字典可 `allow_zero_rows`）
5. fr_check 平行复核：与 compile.py 产物同一噪声族（doc-157/158/4138，见 REPORT ⑥）

## 边界（本版不做的）

- 仅 DBTableData；不做 EmbeddedTableData/内置数据（dsl/compile.py 已有 §1.1 口径）
- 面板仅绝对布局（WParameterLayout 房式）；FRM 自适应面板不在本层
- 图表不改样式主题（样式随模板原样保留）；地图类绑定需人工 matchResult 配置
