<!--
KB_INDEX: {
  "title": "行级数据权限控制模式",
  "stage": "error-analysis",
  "tags": [
    "权限",
    "行级数据隔离",
    "实战验证"
  ],
  "keywords": [
    "行级权限",
    "plant",
    "plant_code",
    "fine_username",
    "TopVerifier",
    "FormulaCondition",
    "auth_base",
    "权限映射表",
    "is_admin",
    "inarray",
    "value函数"
  ],
  "summary": "按登录用户工厂(plant)授权的行级数据权限三层防护模式（原 AGENTS.md §2.1，2026-08-12 实战验证，2026-08-20 v3 拆出）：SQL WHERE 权限子查询 + FormulaCondition 提交条件 + TopVerifier 校验提示",
  "trigger": "何时用：行级数据隔离、按用户/角色过滤数据、权限映射",
  "when_not": "何时不用：无数据权限要求的报表"
}
-->

# 行级数据权限控制模式（2026-08-12 实战验证）

> **本文从 AGENTS.md v2 §2.1 拆出**（2026-08-20 v3 瘦身重构）。
> **何时读**：业务表含 plant 字段、需要按登录用户控制查看/填报/导入的数据可见性时。

> **场景**：按登录用户的工厂(plant)授权，控制**查看 / 填报 / 导入**三个维度的数据可见性与可操作性。
> 管理员(role_id in '0','1')拥有全量数据权限，普通用户只能看到/操作授权工厂的数据。
> **判据**：业务表含 plant 字段 → 需要行级数据权限；不含 plant → 不需要。

## 权限模型

```
权限基础表（两张）:
├─ 数据schema.fin_demo_auth_base_权限映射表  → 用户→工厂授权映射(user_gid, plant_code)
└─ 数据schema.角色表    → 用户角色(user_gid, role_id)
    └─ role_id in ('0','1') = 管理员（全量数据权限）

$fine_username → 帆软内置系统参数，取当前登录用户名
```

## 三层防护架构

```
                    行级数据权限
    ┌─────────────────┼─────────────────┐
    │                 │                 │
  查看层(填报报表)  导入层(导入报表)  填报层(导入报表)
    │                 │                 │
  SQL WHERE          提交条件          TopVerifier
  权限子查询          FormulaCondition   二次校验
  (查询时过滤)        (提交时校验)       (提交时拦截+提示)
```

## ① 查看权限（填报报表）

在业务 SQL 的 WHERE 末尾追加权限子查询：

```sql
AND (
    EXISTS(SELECT 1 FROM 数据schema.角色表
           WHERE role_id IN ('0','1') AND user_gid = '${fine_username}')
    OR plant IN (SELECT plant_code FROM 数据schema.fin_demo_auth_base_权限映射表
                 WHERE user_gid = '${fine_username}')
)
```

**改造范围**：主查询(m_data) + 所有参数下拉数据集 SQL（bu/region/plant/program/month）
**注意**：参数下拉必须也加权限过滤，否则用户在下拉框看到无权限选项；示例模块 等多参数级联报表可只过滤主查询（级联已保证下拉范围收敛）

## ② 导入权限 — 提交条件（FormulaCondition）

在 `<DMLConfig>` 的 `<Condition>` 公式中追加权限校验：

```xml
<Condition class="com.fr.data.condition.FormulaCondition">
<Formula>
<![CDATA[len(A3) > 0 && ... && if(value("is_admin",1,1) = 1, true, if(len(C3) = 0, true, inarray(C3, value("auth_plant",1)) > 0))]]>
</Formula>
</Condition>
```

**机制**：未授权行不满足条件 → 跳过不提交（静默过滤）

## ③ 导入权限 — TopVerifier（提交校验+提示）

在 `</ReportWriteAttr>` 之后加 `<TopVerifier>`：

```xml
<TopVerifier class="com.fr.report.write.ValueVerifier">
<name><![CDATA[权限校验]]></name>
<VerifyItem class="com.fr.data.VerifyItem">
<O t="XMLable" class="com.fr.base.Formula">
<Attributes><![CDATA[=if(value("is_admin",1,1) = 1, true, if(len(C3) = 0, true, inarray(C3, value("auth_plant",1)) > 0))]]></Attributes>
</O>
<message><![CDATA[="你没有工厂 [" + C3 + "] 的数据维护权限"]]></message>
</VerifyItem>
</TopVerifier>
```

**机制**：未授权行弹出提示「你没有工厂 [xxx] 的数据维护权限」，拦截整批提交

## 前置数据集定义（TableDataMap）

导入报表需在 `<TableDataMap>` 中新增两个数据集：

```xml
<!-- 授权工厂列表 -->
<TableData name="auth_plant" ...>
  <SQL>SELECT plant_code FROM 数据schema.fin_demo_auth_base_权限映射表 WHERE user_gid = '${fine_username}'</SQL>
</TableData>

<!-- 是否管理员 -->
<TableData name="is_admin" ...>
  <SQL>SELECT CASE WHEN EXISTS(SELECT 1 FROM 数据schema.角色表 WHERE role_id IN ('0','1') AND user_gid = '${fine_username}') THEN 1 ELSE 0 END</SQL>
</TableData>
```

## 关键公式函数

| 函数 | 用途 | 示例 |
|------|------|------|
| `value("auth_plant",1)` | 取数据集第1列返回数组 | `inarray(C3, value("auth_plant",1))` |
| `value("is_admin",1,1)` | 取数据集第1行第1列值 | `if(value("is_admin",1,1) = 1, ...)` |
| `inarray(x, arr)` | x 在数组中的位置（>0 存在） | `inarray(C3, value("auth_plant",1)) > 0` |

## 实战注意

| 要点 | 说明 |
|------|------|
| **plant 单元格定位** | 各报表 plant 列位置不同：LTA/PACT=C3(col 2), 示例模块=M3(col 12)；必须读 ColumnConfig 的 ColumnRow 确认 |
| **Condition vs TopVerifier** | Condition 控制单行是否参与提交（静默跳过），TopVerifier 控制是否拦截整批（弹提示）；两者都要加 |
| **字段名差异** | 大多数表用 `plant`，示例项目Pline维护表用 `plant_code`，需单独适配 |
| **参数下拉也要过滤** | 填报报表的 bu/region/plant/program/month 下拉 SQL 不加权限过滤 → 用户看到无权限选项 |
| **管理员短路** | 公式首层 `if(is_admin=1, true, ...)` 确保管理员不受限 |
| **表无 plant 则跳过** | 示例映射A / BPC数据表等无 plant 字段的基础数据表不需要行级权限 |

---

*本文为 AGENTS.md v3 kernel 的卫星文件；最后更新 2026-08-20（v3 拆分）。*
