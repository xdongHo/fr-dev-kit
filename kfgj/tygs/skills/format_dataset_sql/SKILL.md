<!--
KB_INDEX: {
  "title": "format_dataset_sql.py — 数据集 SQL 格式美化",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["SQL", "format_dataset_sql", "cpt", "CPT", "sql", "sqlglot"],
  "summary": "--- name: format-dataset-sql description: CPT 数据集 SQL 格式美化时使用：SQL 缩进排版、sqlglot 格式化、保护 FR 参数占位符 ${...} 宏不被破坏时触发。关键词：SQL 美"
}
-->

---
name: format-dataset-sql
description: CPT 数据集 SQL 格式美化时使用：SQL 缩进排版、sqlglot 格式化、保护 FR 参数占位符 ${...} 宏不被破坏时触发。关键词：SQL 美化、format_dataset_sql、sqlglot、数据集格式化、SQL 缩进。
---

# format_dataset_sql.py — 数据集 SQL 格式美化

一句话：用 sqlglot（mysql 方言 pretty）格式化 CPT 内所有数据集 SQL；正则占位保护 FR 公式 `${...}` 不被破坏，格式化失败原样返回（不损数据）。

## 用法（逐字）

```
python format_dataset_sql.py                    # 格式化明细报表目录下所有 CPT
python format_dataset_sql.py <cpt路径> [cpt...]  # 格式化指定文件
```

⚠ 默认目录 DEFAULT_DIR 写死「示例报表工程/明细报表」安装路径——跨项目务必显式传 cpt 路径。依赖 `pip install sqlglot`。修改前自动备份。

## 典型调用

```
python kfgj/tygs/CPT模板/默认格式/4.模板数据集sql格式美化/format_dataset_sql.py <cpt>
python .../4.模板数据集sql格式美化/format_dataset_sql.py a.cpt b.cpt
```

## references（细节指路）

- 脚本本体: `kfgj/tygs/CPT模板/默认格式/4.模板数据集sql格式美化/format_dataset_sql.py`（format_sql/process_file 见源码）
- 知识背景: `ckzl/lc/02_数据建模.md`（级联 SQL `${if(len(...)...}` 宏规范）
- 一键编排入口: `kfgj/tygs/skills/run_defaults/SKILL.md`（Stage 2）
