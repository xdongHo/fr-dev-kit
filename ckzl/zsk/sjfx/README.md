<!--
KB_INDEX: {
    "title": "ckzl/zsk/sjfx",
    "stage": "data-analysis",
    "tags": [
      "字段映射",
      "SQL设计",
      "数据质量"
    ],
    "keywords": [
      "字段映射",
      "SQL设计规范",
      "数据质量校验",
      "除零保护"
    ],
    "summary": "数据设计方法论：业务字段→数据库列→数据集列的映射、SQL 设计规范、数据质量校验（知识主体在 ckzl/lc/02）"
  }
-->

# ckzl/zsk/sjfx

> FR 报表开发中涉及的ckzl/zsk/sjfx论：从需求到字段到 SQL。

← [返回主路由](../../gf/FR_HEADLESS_GUIDE.md)

---

## 文件结构

```
ckzl/zsk/sjfx/
└── README.md           ← 本文件（方法论索引；知识主体在 ckzl/lc/02_数据建模.md）
```

> ⚠️ 本目录曾规划 字段映射模板.md / SQL设计规范.md / 数据质量校验.md 三个独立文件，
> 实际内容已沉淀进 `ckzl/lc/02_数据建模.md`（数据集构建/级联SQL/模板转换），此处不再重复建文件。

## 数据分析流水线

```
业务需求(表格/截图)
    │
    ▼
字段清单(中文名+类型+来源)
    │
    ▼
数据表定位(表名+Schema+数据连接)
    │
    ▼
SQL 编写(SELECT/WHERE/级联${if()})
    │
    ▼
数据预览(FR SQL编辑器执行)
    │
    ▼
字段映射(CPT数据集列名 = SQL列别名)
    │
    ▼
报表绑定(DSColumn columnName)
```

## 关键规范速查

| 规范 | 说明 | 参考 |
|------|------|------|
| 级联SQL | `WHERE 1=1 ${if(len(para)==0,"","and f in ('"+para+"')")}` | `ckzl/lc/02_数据建模.md` §8 |
| SQL多行格式化 | SELECT/DISTINCT/FROM/WHERE/ORDER BY 各占一行 | `ckzl/lc/02_数据建模.md` §8 |
| 除零保护 | `=if(len(x)=0\|\|x=0,'',num/x)` | `kfgj/fzpy/fix_div_zero.py` |
| ORDER BY 位置 | 必须在所有 `${if()}` 之后 | `ckzl/lc/02_数据建模.md` §8 |

## 引用

- 数据集构建 → `ckzl/lc/02_数据建模.md`
- 级联参数 SQL → `ckzl/lc/02_数据建模.md` §8.1
- 模板转换 → `ckzl/lc/02_数据建模.md` §14
