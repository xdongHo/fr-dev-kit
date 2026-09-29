<!--
KB_INDEX: {
  "title": "FS 报表 DSL 解释器 · 使用说明（dsl/）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["dsl", "DSL", "cpt", "yaml", "compile", "guardrails"],
  "summary": "> 任务书: `C:Users<你的用户名>Desktop示例需求目录DSL解释器开发任务书-20260902.md` > 语义层 = 唯一事实源；页面 DSL = 声明式描述；compile.py = 编译器；guardrail"
}
-->

# FS 报表 DSL 解释器 · 使用说明（dsl/）

> 任务书: `C:\Users\<你的用户名>\Desktop\示例需求目录\DSL解释器开发任务书-20260902.md`
> 语义层 = 唯一事实源；页面 DSL = 声明式描述；compile.py = 编译器；guardrails.py = 护栏。
> 详细语法见 `schema.md`；本 README 讲"怎么用"。

## 常见问法：业务口径变了，只改配置文件不直接动报表，怎么重新编译生成 cpt？

- 「口径调整 / 指标口径变更 / 只改配置不动报表」→ 只改 `semantic_layer.yaml`（唯一事实源），**禁止直接改 cpt**（下次编译会覆盖）。
- 「重新编译 / 重新生成 cpt 的命令」→ `python dsl/compile.py dsl/examples/<页面>.yaml`：四闸校验后落盘 `build/`（不落线上目录），标准链路见下节。
- 「护栏怎么体检 / 坏文件夹怎么验证」→ `python dsl/guardrails.py <产物> --semantic dsl/semantic_layer.yaml`（G1-G5，可独立跑）；产物另过 `kfgj/fzpy/fr_check.py`。
- 「改口径要不要动参数面板/单元格」→ 不用：语义层声明表结构/权限模板/口径约定，编译器统一落模板，详细语法见 `schema.md`。

## 文件清单

| 文件 | 作用 |
|---|---|
| `semantic_layer.yaml` | 语义层（表结构/组织权限模板/口径约定/主题/原型声明）。**改口径只改这里** |
| `schema.md` | DSL 语法文档 + SQL 片段速查（勿手写变体） |
| `compile.py` | 编译器：DSL + 语义层 → 完整 cpt（写前四闸，--smoke 加库上冒烟） |
| `guardrails.py` | 独立护栏 G1-G5，可 CLI 单独体检任何 cpt |
| `examples/*.yaml` | 已交付页面的 DSL 反推（下钻×2 / 主表(2b 待编译) / 组织面板） |
| `tests/` | 坏文件夹具 ×3 + 好夹具 + 最小语义层 |
| `build/` | 编译产物默认落盘处（**不落线上目录**） |

## 新页面开发流程（标准链路）

```
用户提需求 → agent 出示意图（ASCII/表格，用户确认后才能动文件——开发规范 §1）
  → agent 写页面 DSL（examples/ 抄最近的，~30 行）
  → python dsl/compile.py dsl/examples/xxx.yaml            # grounding+四闸+落盘 build/
  → python dsl/guardrails.py <产物> --semantic dsl/semantic_layer.yaml   # 应 0 errors
  → python kfgj/fzpy/fr_check.py <产物>               # 退出码 1 且仅 doc-157/158/1284 族 = 基线内
  → --smoke 库上冒烟（需 VPN）→ 用户确认 → 备份后放线上目录
```

编译器闸门会**拒绝落盘**：archetype/表/列不在语义层（schema grounding）、XML 不合法、
引用不闭合（数据集/参数/控件名）、SQL 缺 numeric/ORG/PERM、含 `${{` 残留。

## 口径变更流程（重要）

**改 `semantic_layer.yaml` → 重编译。禁止直接改 cpt**（下次编译即被覆盖，且过不了护栏溯源）。
改完语义层跑 `_runs/t1_verify_facts.py`（需 VPN）核对库上事实。

### 常见问法：FS 报表怎么生成/口径变了怎么办/编译报错怎么查？

- **「FS 报表怎么生成/新页面怎么出 cpt？」** → 先在 `examples/` 抄最近的页面 DSL（~30 行），再
  `python dsl/compile.py dsl/examples/xxx.yaml`（`--out` 缺省落 `dsl/build/`，`--smoke` 库上冒烟，`--ext` 加 G6 扩展闸）
  → guardrails → fr_check → 用户确认后备份放线上（本文件「新页面开发流程」节；compile.py --help）。
- **「示例项目 FS 报表口径变了怎么改？」** → **只改 `semantic_layer.yaml`（口径唯一事实源）→ 重编译**：
  `python dsl/compile.py <页面dsl> --semantic dsl/semantic_layer.yaml`；**禁止直接改 cpt**（下次编译被覆盖且过不了护栏溯源）；
  改完跑 `_runs/t1_verify_facts.py`（需 VPN）核对库上事实（本文件「口径变更流程」节、文件清单表）。
- **「编译报错/闸门拒绝落盘怎么查？」** → 编译器四闸会拒绝落盘，逐项对照：archetype/表/列不在语义层（schema grounding）、
  XML 不合法、引用不闭合（数据集/参数/控件名）、SQL 缺 numeric/ORG/PERM 或含 `${{` 残留（本文件「新页面开发流程」节末）。
- **「编译出的 cpt 想单独体检？」** → `python dsl/guardrails.py <cpt> --semantic dsl/semantic_layer.yaml`
  应 0 errors（G1-G5；`--smoke` 真实冒烟、`--ext` 加 R01-R15、`--param K=V` 供 G5）（文件清单表；guardrails.py --help）。
- **「DSL 语法片段在哪查？」** → `schema.md` §2-§5、§7（组织面板/对比列/构成区域/超链传参）；DSL 里**不写 SQL**，
  period CASE/numeric/ORG_FILTER/PERM 由语义层模板供给（本文件「常见 DSL 片段」节）。

## 常见 DSL 片段

组织面板 / 对比列 / 构成区域 / 超链传参 → 见 `schema.md` §2-§5、§7。
period CASE、numeric 转换、ORG_FILTER、PERM、VALUES(sgn) 全部由语义层模板供给，DSL 里**不写 SQL**。

## 现状与已知事项（2026-09-04 交付）

- **已实现（T2-2a）**：`account_drill`（单科目行+构成区域+标题）、`panel_org`（四级联+Entity 只读+锁定 JS）。
  编译产物与线上 `示例预算表-科目下钻.cpt` 对拍 **17/17 PASS**（SQL 归一化逐字一致、单元格逐格一致、
  fr_check 同基线 3 错+26 警告同三族），见 `_runs/t2_compare_report.md`。
- **待实现（T2-2b，任务书允许拆会话）**：`compare_main` 展开器。反推 DSL 已备：
  `examples/panel_org_demo.yaml`（compare_main 类原型未实现时会得到明确的 NotImplementedError 提示）。
- **编译产物的有意修复**：面板控件名 short(legal/bu/…) → `para_*`（原型违"控件名=参数名"铁律，
  锁定 JS 落空、面板选择不回灌参数；产物已修复，对拍列为可接受差异）。
- **guardrails 对存量页的真实发现**（已定性，`_runs/t3_guardrail_tests.py`）：
  1. 示例预算表.cpt 有 2175 处 DSColumn 引用 4 个未定义数据集（ds_cr_ci/lta/pact/vave 基础名；
     表内实为 _bud/_fy 变体；列显隐遮蔽未暴露）——**建议后续修复**；
  2. 示例预算表.cpt para_ext6/7 被引用但未声明；示例实际表.cpt para_adj 未声明（已知）；
  3. ds_cr_* 族/ds_comments 无 ORG/PERM 子句、部分聚合未做 numeric 保护——CR 含金额，建议业务确认补权限。
- **VPN 依赖的验证（2026-09-04 已全部完成）**：
  `_runs/t1_verify_facts.py` 语义层 19 项库上核对 **19/19**（五表行数与快照逐字一致；
  实测 data=''=0 已降级报告项；⚠ demo_ads 存在同名事实表副本，取数必须带 `demo_dws.` 前缀）；
  `t2_paritel_compare.py --db` 两版 SQL 库上执行结果**逐行一致**（叶子 PLH01 三列与文档样例吻合、
  公式科目 0-PLH3102-(64020901+64011104) = 91,426,055,148.18 精确复现转接文档 §六 校验值）；
  `compile.py --smoke` 两页 7 数据集全过库（G5）。数据/口径变更后重跑即可。
