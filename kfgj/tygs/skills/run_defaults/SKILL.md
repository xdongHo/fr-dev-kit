<!--
KB_INDEX: {
  "title": "run_defaults.py — 默认自动档编排器",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["run_defaults", "cpt", "CPT", "skip", "verify", "python"],
  "summary": "--- name: run-defaults description: CPT 模板默认格式一键编排时使用：新明细表生成后的整套默认格式化（SQL 美化+明细样式+冻结表头+参数面板+CSS+按钮）、批量后处理、模板交付前统一格式化时触发。"
}
-->

---
name: run-defaults
description: CPT 模板默认格式一键编排时使用：新明细表生成后的整套默认格式化（SQL 美化+明细样式+冻结表头+参数面板+CSS+按钮）、批量后处理、模板交付前统一格式化时触发。关键词：一键编排、默认格式、run_defaults、--skip、--verify。
---

# run_defaults.py — 默认自动档编排器

一句话：按 Stage 2→3→4→6 串接六个默认格式化脚本，一键把明细 CPT 打磨到默认格式；单步失败不停线，exit code = 失败步骤数（0=全绿）。

## 用法（逐字）

```
python run_defaults.py <cpt路径...> [--skip sql,panel] [--numeric-labels 标签1,标签2]
                       [--freeze-rows 2] [--verify] [--timeout 120]
```

六步流水线（--skip 的合法 key）：
| key | Stage | 脚本 |
|-----|-------|------|
| sql | 2 | format_dataset_sql.py（SQL 美化） |
| detail | 3 | fmt_detail_cells.py（类型化明细样式） |
| freeze | 3 | freeze_header.py（冻结表头） |
| panel | 4 | fmt_panel_safe.py（面板坐标级安全排布，已禁用 run_all 全量版） |
| css | 6 | add_css_import.py（CSS 引用注入） |
| btns | 6 | add_export_btn.py + add_query_btn.py（按钮补齐） |

每步后自动做 XML 良构校验；`--verify` 末尾跑真引擎渲染验证（T+L 断言）。

## 典型调用

```
python kfgj/tygs/CPT模板/默认格式/run_defaults.py <cpt> --verify
python .../run_defaults.py a.cpt b.cpt --skip sql,btns
python .../run_defaults.py <cpt> --numeric-labels 贷款余额,占比 --freeze-rows 2
```

## references（细节指路）

- 脚本本体: `kfgj/tygs/CPT模板/默认格式/run_defaults.py`（STEPS 表/单步 argv 模板见源码）
- 各单项脚本封装: `kfgj/tygs/skills/INDEX.md`
