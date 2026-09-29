<!--
KB_INDEX: {
  "title": "fmt_wildcard.py — 通配格式化器（通用版）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["fmt_wildcard", "run", "python", "targets", "CSS", "隔行换色"],
  "summary": "--- name: fmt-wildcard description: 常规明细表（行式展示）一揽子通配格式化时使用：参数面板 CSS 注入+紧凑单行重排、单元格样式（微软雅黑9号）、列宽内容自适应、冻结表头、隔行换色一次到位时触发。关键词"
}
-->

---
name: fmt-wildcard
description: 常规明细表（行式展示）一揽子通配格式化时使用：参数面板 CSS 注入+紧凑单行重排、单元格样式（微软雅黑9号）、列宽内容自适应、冻结表头、隔行换色一次到位时触发。关键词：通配脚本、fmt_wildcard、隔行换色、列宽自适应、明细表格式化、勿手写。
---

# fmt_wildcard.py — 通配格式化器（通用版）

一句话：常规明细表后处理总入口（原 fmt_copa.py 泛化），按「用户定稿 2026-08-07」通配规则一次套齐 A 类通用样式 + B 类列表展示样式。

## 通配规则（A/B 分类）

- A 通用样式类（所有报表默认执行）：① 参数面板 CSS 注入（param_panel_style 完整样式）② 参数面板紧凑单行重排 ③ 单元格样式（对齐/格式/字体 微软雅黑9号）
- B 列表展示类（常规明细表默认执行，树形/透视报表不启用）：④ 列宽内容自适应（max(数据×2.5mm, 表头×5mm) clamp[15,150]，默认20mm）⑤ 冻结表头（FrozenColumnRow）⑥ 隔行换色（row()%2 条件样式）

## 用法（逐字，源码实际行为）

```
python fmt_wildcard.py        # dry-run：仅列出内置 targets，不写任何文件
python fmt_wildcard.py --run  # 实际执行（对每个目标写 XML，写前自动备份）
```

内置 targets 写死 示例驾驶舱 目录（BASE 常量）；跨项目复用走 import：

```python
from fmt_wildcard import process_cpt
process_cpt(cpt_path, header_row=0, custom_btns=None, blue_ids=None,
            gray_ids=None, add_export=False, row_style=False)
# row_style=True 启用冻结表头+隔行换色（行展示明细表）；树形/透视传 False
```

## 典型调用

```
python kfgj/tygs/CPT模板/默认格式/fmt_wildcard.py --run         # 内置 targets 全量（先 dry-run 预览再 --run）
# 新项目: 改源码底部 targets 列表，或 import process_cpt 传参
```

## references（细节指路）

- 脚本本体: `kfgj/tygs/CPT模板/默认格式/fmt_wildcard.py`（CSS 全文/calc_col_width 算法见源码）
- 同规则单项拆分: freeze_header / fmt_detail_cells / param_panel_style（见 `kfgj/tygs/skills/INDEX.md`）
