<!--
KB_INDEX: {
  "title": "fmt_detail_cells.py — 明细报表单元格格式化（通配规则）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["numeric", "fmt_detail_cells", "labels", "序号", "kfgj", "tygs"],
  "summary": "--- name: fmt-detail-cells description: 明细报表单元格按列类型套样式时使用：数值/百分比/文本/序号/日期分类对齐与格式、微软雅黑9号字体、细边框时触发。关键词：单元格样式、fmt_detail_ce"
}
-->

---
name: fmt-detail-cells
description: 明细报表单元格按列类型套样式时使用：数值/百分比/文本/序号/日期分类对齐与格式、微软雅黑9号字体、细边框时触发。关键词：单元格样式、fmt_detail_cells、numeric-labels、数值右对齐、隔行样式、明细表。
---

# fmt_detail_cells.py — 明细报表单元格格式化（通配规则）

一句话：按列标签自动分类（数值/百分比/文本/序号/日期）套对齐+格式+字体，用户定稿 2026-08-06 通配规则。

## 规则速览

- 字体默认 微软雅黑 9号(size=72)；统一细边框+白底
- 数值 → 右对齐 `#,##0.00`（判断：numeric 列，或标签含 累计/月/金额类词）
- 百分比 → 右对齐 `#0.00%`（标签含 % 或 Rate）
- 文本 → 左对齐；序号 → 居中（标签 序号/Seq/SEQ）；日期 → 左对齐 `yyyy-MM-dd`（标签含 Date/日期）

## 用法（逐字）

```
python fmt_detail_cells.py <cpt路径> [--numeric-labels 标签1,标签2,...]
```

`--numeric-labels`: 数值列标签清单（建议从建表 SQL 的 numeric 列提取，最准）；run_defaults.py 编排时经 `--numeric-labels` 透传。

## 典型调用

```
python kfgj/tygs/CPT模板/默认格式/fmt_detail_cells.py <cpt> --numeric-labels 贷款余额,不良率
python kfgj/tygs/CPT模板/默认格式/fmt_detail_cells.py <cpt>          # 纯标签推断
```

## references（细节指路）

- 脚本本体: `kfgj/tygs/CPT模板/默认格式/fmt_detail_cells.py`（make_style/classify 实现见源码）
- 一键编排入口: `kfgj/tygs/skills/run_defaults/SKILL.md`
