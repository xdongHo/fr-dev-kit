<!--
KB_INDEX: {
  "title": "kfgj/tygs — Skills 封装索引",
  "stage": "formatting",
  "tags": ["skills", "格式化", "Agent Skills 标准", "渐进加载"],
  "keywords": ["SKILL.md", "触发条件", "通配脚本", "加载顺序", "frontmatter"],
  "summary": "kfgj/tygs工具包的 Agent Skills 标准化封装索引：8 个高频脚本 SKILL.md 清单+加载顺序（三级渐进加载：描述常驻→正文触发读→脚本本体执行才取）"
}
-->

# kfgj/tygs/skills — 封装索引

> Agent Skills 开放标准（agentskills.io）封装：每个子目录一个 SKILL.md（frontmatter name/description 含触发条件关键词）。
> **三级渐进加载**：① frontmatter 描述（常驻路由）→ ② SKILL.md 正文（触发才读）→ ③ references 指向的脚本本体（执行才取）。SKILL.md 一律薄封装（≤60 行），细节不复制、只指路。

## 加载顺序（决策路径）

```
1. 先判断任务形态：
   ├─ 新明细表生成后整套默认格式化 → load ① run-defaults（一键编排，含 6 步）
   ├─ 单模板一揽子通配样式（明细行式表）→ load ② fmt-wildcard（A/B 通配规则总入口）
   └─ 单项微调 → 按症状直取 ③-⑧
2. 单项症状路由：
   ├─ 单元格样式/数值百分比日期格式 → ③ fmt-detail-cells
   ├─ 滚动时表头要固定 → ④ freeze-header
   ├─ 参数面板布局/控件对齐（怕损坏模板）→ ⑥ fmt-panel-safe（索引目录推荐,替代全量版）
   ├─ 行高不统一 → ⑦ fix-row-heights
   ├─ SQL 排版乱 → ⑧ format-dataset-sql
   └─ 参数面板按钮 CSS（禁手写,必须复用）→ ⑤ param-panel-style
3. 冲突规则：① 编排器已含 ③④⑥⑧ 及 css/btns 步——用 ① 时不要再单独跑重叠单项；
   ② 与 ① 二选一（② 适合 示例驾驶舱 内置 targets/需要列宽自适应场景）。
```

## 封装清单（Top 8，按 machines 表登记 + AGENTS.md 点名 + 引用频度选定）

| # | skill | 封装路径 | 脚本本体（references 落点） |
|---|-------|---------|---------------------------|
| ① | run-defaults | `skills/run_defaults/SKILL.md` | `CPT模板/默认格式/run_defaults.py` |
| ② | fmt-wildcard | `skills/fmt_wildcard/SKILL.md` | `CPT模板/默认格式/fmt_wildcard.py` |
| ③ | fmt-detail-cells | `skills/fmt_detail_cells/SKILL.md` | `CPT模板/默认格式/fmt_detail_cells.py` |
| ④ | freeze-header | `skills/freeze_header/SKILL.md` | `CPT模板/默认格式/freeze_header.py` |
| ⑤ | param-panel-style | `skills/param_panel_style/SKILL.md` | `CPT模板/默认格式/param_panel_style.py` |
| ⑥ | fmt-panel-safe | `skills/fmt_panel_safe/SKILL.md` | `CPT模板/默认格式/2.参数面板控件布局/fmt_panel_safe.py` |
| ⑦ | fix-row-heights | `skills/fix_row_heights/SKILL.md` | `CPT模板/默认格式/2.参数面板控件布局/fix_row_heights.py` |
| ⑧ | format-dataset-sql | `skills/format_dataset_sql/SKILL.md` | `CPT模板/默认格式/4.模板数据集sql格式美化/format_dataset_sql.py` |

## 落选说明（高频但未封装，待二波）

- `batch_optimize_cpt.py`(引用 13 次)/`run_all.py`(8 次)：索引目录已标注 1200px 阈值拆散多列网格坑，编排器已弃用——封装优先级让位安全脚本 fmt_panel_safe；若二波封装须把坑写进 description。
- `add_query_btn.py`/`add_css_import.py` 等 add_* 系：功能已被 ① run-defaults 的 css/btns 步覆盖，独立触发场景少。

> 维护：新增封装 → 本表加一行 + 加载顺序路由补一条；格式与 frontmatter 风格对齐 `ckzl/lc/fr11_knowledge/*/SKILL.md`。
