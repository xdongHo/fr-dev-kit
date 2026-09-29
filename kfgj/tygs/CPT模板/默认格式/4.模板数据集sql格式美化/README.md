<!--
KB_INDEX: {
  "title": "模板数据集 SQL 格式美化",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["SQL", "自动格式化", "CPT", "python", "format_dataset_sql", "cpt"],
  "summary": "```powershell # 格式化明细报表目录下所有 CPT python format_dataset_sql.py"
}
-->

# 模板数据集 SQL 格式美化

使用 `sqlglot` 自动格式化 CPT 文件中所有数据集的 SQL 查询。

## 用法

```powershell
# 格式化明细报表目录下所有 CPT
python format_dataset_sql.py

# 格式化指定文件
python format_dataset_sql.py FS实际.cpt FS预算.cpt
```

## 功能

- 自动格式化 SELECT / UNION ALL / JOIN 等 SQL
- 保护 FR 公式 `${if(len(...)...)}` 不被破坏
- 自动创建 `_backup_YYYYMMDD_HHMMSS/` 备份
