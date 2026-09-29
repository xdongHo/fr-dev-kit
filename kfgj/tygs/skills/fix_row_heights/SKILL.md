<!--
KB_INDEX: {
  "title": "fix_row_heights.py — 行高自动修复",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["fix_row_heights", "cpt", "python", "参数面板控件", "布局", "表头"],
  "summary": "--- name: fix-row-heights description: 明细表行高异常/行高不统一修复时使用：表头 10mm、明细 8mm 标准行高、按 DSColumn/公式自动分类行类型时触发。关键词：行高、fix_row_hei"
}
-->

---
name: fix-row-heights
description: 明细表行高异常/行高不统一修复时使用：表头 10mm、明细 8mm 标准行高、按 DSColumn/公式自动分类行类型时触发。关键词：行高、fix_row_heights、RowHeight、表头行高、明细行高、FU。
---

# fix_row_heights.py — 行高自动修复

一句话：行高自动分类修复——表头 10mm (1442289 FU) / 明细 8mm (1153643 FU)，检测 DSColumn 有无比数据集列区分，无则按公式区分。

## 保护规则（逐字，源码 docstring）

- Row 0 强制保护；原高度 ≥1.8M FU 保护（不压扁大行）
- 修改前自动备份至 `_backup_<时间戳>/`

## 用法（逐字）

```
python fix_row_heights.py <cpt路径> [cpt路径...]
```

支持多文件批量；无变化时输出「⚠️ 无变化」。

## 典型调用

```
python kfgj/tygs/CPT模板/默认格式/2.参数面板控件布局/fix_row_heights.py <cpt>
python .../2.参数面板控件布局/fix_row_heights.py a.cpt b.cpt c.cpt
```

## references（细节指路）

- 脚本本体: `kfgj/tygs/CPT模板/默认格式/2.参数面板控件布局/fix_row_heights.py`（H_HEADER/H_DETAIL 常量与 repl 逻辑见源码）
- 知识背景: `ckzl/lc/03_报表构建.md` §5 行高 FU 换算（铁律 C）
