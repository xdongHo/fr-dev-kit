<!--
KB_INDEX: {
  "title": "示例项目 FS 报表页面 DSL — schema.md",
  "stage": "dsl",
  "tags": ["DSL", "schema", "语义层", "guardrails", "编译器", "示例项目"],
  "keywords": ["compile.py", "semantic_layer", "archetype", "panel_org", "compare_main", "account_drill", "G1", "G2", "G3", "G4", "G5", "口径变更"],
  "summary": "示例项目 FS 页面 DSL 的语法与语义权威定义：三 archetype（panel_org/compare_main/account_drill）+ 顶层字段表 + guardrails G1-G5 编译出口闸 + 常用 SQL 片段速查；单向流=口径变更只改 semantic_layer.yaml 重编译，产物 cpt 禁止直接手改（R35 夜间互链时补挂本索引头，与 jcxt/data/_kb_index.yaml 既有登记对齐）"
}
-->

## 相关知识（夜间 R35 互链 2026-09-05）

- [tag_dictionary.yaml](tag_dictionary.yaml) — schema grounding 词表：DSL 引用的 XML 标签以该字典（435 kinds/94 文件普查）为底账校验。
- [ckzl/zsk/tbcw/夜间提炼_历史脚本教训_20260904](../ckzl/zsk/tbcw/夜间提炼_历史脚本教训_20260904.md) — 规则出处：G3 的 numeric/NULLIF、关键字引号、${if} 静态化检查点即其条目 12/13/29 教训的闸门化。
- [ckzl/zsk/tbcw/README](../ckzl/zsk/tbcw/README.md) — 防线呼应：其静默类专节「XML 合法 ≠ 功能正确」与本文「编译出口四闸」是同一验证闭环的检索侧/生成侧两端。

# 示例项目 FS 报表页面 DSL — schema.md

> 读者：后续接手 `compile.py` / `semantic_layer.yaml` 的 agent。
> 本文档定义页面 DSL 的语法与语义；编译出口护栏见同目录 `guardrails.py`（G1-G5）。
> 展开逻辑与 SQL 片段的**实测参照实现**：`_runs/tmp_gen_drill_v2.py`（account_drill 原型，420 行，已生成可打开的 cpt）。

## 0. DSL 定位

- 页面 DSL 是**声明式 YAML 页面描述**：`compile.py` 读 `semantic_layer.yaml`（口径层：数据源/表/列/口径）+ 页面 DSL（本文档定义）→ 展开为完整 FineReport 10 `.cpt`。
- 单向流：**改口径 → 只改 semantic_layer.yaml → 重编译**。产物 cpt 是编译输出，**禁止直接手改**（下次编译即被覆盖，且过不了护栏溯源）。
- Schema grounding：DSL 里引用的 archetype、表、列必须存在于 semantic_layer.yaml（archetypes/datasources），编译器先查语义层再展开；语义层没有的口径不允许出现在 DSL 里。

## 1. 顶层字段表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | str | Y | 页面标题（写入 cpt Report name 与标题块文字） |
| `archetype` | enum | Y | `panel_org` \| `compare_main` \| `account_drill` 三选一，决定展开器 |
| `kind` | enum | account_drill/compare_main 必填 | `actual` \| `budget`。actual：当年列走 HFM ADJ 表（ytd_orig/ytd_post），预算期末固定 '12'；budget：当年列走 budget 表 + `para_scn_cur`，期末用 `para_month_bud` |
| `subject` | map | account_drill 必填 | `{p_code: from_url, p_name: from_url}`——科目编码/名称从 URL 参数注入并声明进 ReportParameterAttr |
| `subject_source` | map | account_drill 必填 | `{cpt: <主表cpt名>}`——科目行/c4 公式源（解析出 VALUES 构成映射），相对语义层 `meta.paths.reportlets_dir` |
| `filters` | map | Y | 面板过滤器声明（org 级联 / entity 只读 / hfm 隐藏 URL 参数），见各 archetype |
| `blocks` | list | Y | 内容块清单，顺序即渲染顺序，见各 archetype |
| `options` | map | N | 开关集合：`before_cr` / `comments` / `ext` / `fy` / `title_block` 等 |
| `output` | str | N | 输出 cpt 文件名。**编译产物默认落 `dsl/build/`，绝不静默覆盖线上**（`--out` 指向既有文件时自动备份） |

## 2. 原型一 panel_org（四级组织级联过滤面板）

| 字段 | 说明 |
|------|------|
| `filters.org.cascade` | legal → bu → region → plant 四级联动，逐级声明依赖 |
| `filters.entity` | `readonly`：只读公式控件，取值回退 plant>region>bu>legal |
| `filters.hfm` | `hidden_url_params`：para_year/para_month/para_scn_* 等无控件、纯 URL 传入 |

展开逻辑：
- 每级一个字典数据集 `dict_legal`/`dict_bu`/`dict_region`/`dict_plant`（DISTINCT 取值 + 级联 WHERE + PERM），下拉框 `<Dictionary>` 引用并以 `<Parameters>` 声明依赖的上级参数。
- entity 控件 widgetValue 为公式 `=IF(LEN($para_plant)>0,$para_plant,IF(...))`，锁定不可编辑。
- `afterinit lock_js`：setTimeout 遍历 para_legal~para_plant，URL 带值（getValue 非空）则 `setEnable(false)` 锁定。

```yaml
archetype: panel_org
filters:
  org: {cascade: [legal, bu, region, plant]}
  entity: readonly
  hfm: hidden_url_params
```

## 3. 原型二 compare_main（对比主表）

74 科目行 × 列组：上年 YTD / 预算 YTD / 当年 YTD + VS LY 差额 / VS PPL 差额。

| 字段 | 说明 |
|------|------|
| `blocks` | `[subject_rows, vs_columns]` 固定 |
| `options.before_cr` | Before-CR 模块开关 |
| `options.comments` | 注释列开关 |
| `options.ext` | ext1~ext5 透传列清单 |
| `options.fy` | true 时期末取 FY（'12'）而非当月 |

```yaml
archetype: compare_main
kind: actual
filters: {org: cascade, entity: readonly}
blocks: [subject_rows, vs_columns]
options: {comments: true, fy: false}
output: 示例实际表-对比主表.cpt
```

## 4. 原型三 account_drill（科目下钻）

| 字段/块 | 展开为 |
|---------|--------|
| `subject.p_code` / `subject.p_name` | `from_url`：URL 参数，声明进 ReportParameterAttr；SQL 以 `'${p_code}'` 关联 |
| `blocks: [title]` | 标题块 `=CONCATENATE("科目下钻：", $p_name)` |
| `blocks: [single_row]` | 数据集 `ds_account`：单科目行，叶子直取、公式科目取构成合计，`COALESCE(leaf, tot, 0)` 出 上年 py / 预算 bud / 当年 cur 三列 |
| `blocks: [compose_region]` | 数据集 `ds_compose`：公式科目按 VALUES(sgn) 拆组件 JOIN 维表，组件小计 5 列（comp/sgn/py/bud/cur）+ 构成合计 SUM 行 |
| `filters.org.locked_levels` | `from_url`：四级由 URL 带值并 afterinit 锁定 |
| `filters.entity` / `filters.hfm` | 同 panel_org |

## 5. 完整示例（可编译粒度）

```yaml
page: 费用明细下钻
archetype: account_drill
kind: actual
subject: {p_code: from_url, p_name: from_url}
subject_source: {cpt: 示例实际表.cpt}    # 科目行/c4 公式源（49 条构成映射）
filters:
  org: {locked_levels: from_url}
  entity: readonly
  hfm: hidden_url_params      # para_year/para_month/para_month_bud/para_scn_*/para_adj/para_curr/para_unit 纯 URL
blocks: [title, single_row, compose_region]
options: {}
output: 示例实际表-科目下钻.cpt    # 产物落 dsl/build/，确认后再放线上
```

编译产物结构（对应 tmp_gen_drill_v2.py）：数据集 `ds_account` + `ds_compose` + `dict_legal~dict_plant` + `param_guard`；面板 5 控件（**para_legal/para_bu/para_region/para_plant/para_entity**——原型用短名 legal/bu 违"控件名=参数名"铁律致锁定 JS 落空，编译器已修复）+ 5 个 `lb_*` 标签 + afterinit 锁定；单元格 r0 标题 / r2 表头 / r3 数据行 / r5-r8 构成区。

## 6. 校验链（guardrails.py）

编译出口四闸 + 可选冒烟，全部通过才允许落盘：

| 闸 | 内容 |
|----|------|
| G1 | XML well-formed（ET.fromstring，行列号定位） |
| G2 | 引用闭合：DSColumn dsName ⊆ TableDataMap；全文 `${}` 引用参数 ⊆ 声明参数（ReportParameterAttr ∪ ParameterUI，豁免 `conventions.global_params`）；面板控件名=参数名（`lb_*` Label 豁免） |
| G3 | SQL 卫生（每条数据集）：varchar 数值保护 = `NULLIF(` + 显式 numeric 转换（`::numeric` / `CAST(... AS numeric)` 两形态任一，2026-09-04 放宽兼容存量 CAST 形态）；含 `${para_month}`/`${para_month_bud}` 必带 period CASE；org_markers 全部 + perm_markers 任一；禁 `${{` 残留；含 `AS sgn` 必带 `UNION ALL`。`conventions.sql_exceptions` 前缀（param_guard/dict_）只做残留检查 |
| G4 | 权限强制：每条 SQL 必含 ORG+PERM 实际过滤片段；`conventions.sql_exceptions` 前缀豁免（`param_guard*` 全免，`dict_*` 仅要求 PERM） |
| G5 | 冒烟（`--smoke`，可选）：psycopg2 替换参数后逐条执行，报告行数（info）或错误 |

```
python guardrails.py <cpt> --semantic semantic_layer.yaml [--smoke] [--param k=v ...]
# 逐条打印 [Gx] rule: message；有错 exit 1；干净打印 GUARDRAILS: 0 errors
```

## 7. 常见 SQL 片段速查（摘自 tmp_gen_drill_v2.py，勿手写变体）

```sql
-- 月份 CASE（mc）：para_month ∈ JAN..DEC → '1'..'12'
(CASE upper('${para_month}') WHEN 'JAN' THEN '1' WHEN 'FEB' THEN '2' ... WHEN 'DEC' THEN '12' END)

-- 数值转换（铁律：字符列 data 参与运算前必须转，G3 numeric_cast 检查点）
round(sum(COALESCE(NULLIF(t.data,'')::numeric,0)),2)

-- COND（四级级联空值穿透）
('${para_legal}'='' OR f.legal_code='${para_legal}') AND ('${para_bu}'='' OR f.bu='${para_bu}')
AND ('${para_region}'='' OR f.region='${para_region}') AND ('${para_plant}'='' OR f.plant_code='${para_plant}')

-- ORG_FILTER（ORG 过滤幅面：四级展开，G3 org_markers / G4 ORG 检查点）
entity IN (
    SELECT legal_code FROM demo_ads.fin_demo_auth_base_info f WHERE <COND>
    UNION ALL SELECT bu         FROM demo_ads.fin_demo_auth_base_info f WHERE <COND>
    UNION ALL SELECT region     FROM demo_ads.fin_demo_auth_base_info f WHERE <COND>
    UNION ALL SELECT plant_code FROM demo_ads.fin_demo_auth_base_info f WHERE <COND>)

-- PERM（关联子查询版，带别名 a 时替换 f）
((EXISTS(SELECT 1 FROM demo_ads.fin_demo_config_user_role WHERE role_id IN ('0','1') AND user_gid='${fine_username}'))
 OR EXISTS(SELECT 1 FROM demo_ads.fin_demo_auth_base_user_map m WHERE m.user_gid='${fine_username}' AND m.plant_code=f.plant_code))

-- PERM_PLAIN（无别名版）
(EXISTS(SELECT 1 FROM demo_ads.fin_demo_config_user_role WHERE role_id IN ('0','1') AND user_gid='${fine_username}')
 OR entity IN (SELECT plant_code FROM demo_ads.fin_demo_auth_base_user_map WHERE user_gid='${fine_username}'))

-- VALUES 构成片段（公式科目拆解；含 AS sgn 必配 UNION ALL，G3 values_union 检查点）
SELECT 'F1-001' AS expr, '6011' AS comp, 1 AS sgn
UNION ALL SELECT 'F1-001', '6012', -1
-- 用法: sum(o.sgn * COALESCE(NULLIF(a.data,'')::numeric,0)) FROM (<VALUES>) o JOIN 维表 a ON a.account = o.comp
```
