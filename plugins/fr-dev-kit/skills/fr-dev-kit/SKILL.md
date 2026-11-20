---
name: fr-dev-kit
description: 用 FR Dev Kit 的 MCP 工具开发/修改/排错 FineReport 报表（cpt/frm）。凡是 FineReport 模板、数据集 SQL、FR 公式、设计器探查类任务，或用户提到 cpt/frm/帆软/FR 时使用本技能。
---

# FR Dev Kit 工具编排（MCP）

工具最终都落到套件 Python 脚本（kit_root 指向套件仓库根）。若工具返回「套件根目录未配置」，
指引用户：ZCode 设置 → 插件 → fr-dev-kit → 填 kit_root，保存后新开会话。

## 标准流程映射（与套件 AGENTS.md SOP 等价）

| 任务 | 工具序列 |
|------|---------|
| 创建新报表（流程 A） | `kb_query` 定流程文档 → `db_schema` 探表（G11）→ 写 SQL 过 `verify_sql`（G08）→ 公式过 `eval_formula`（G09）→ `dsl_build` 生成组件 或 手写 XML → `fr_check` → 收尾 `guard task=create` |
| 修改/格式化（流程 B） | `template_snapshot` 看结构 → `backup_template` 备份（G04）→ 修改 → `fr_check` → `guard task=modify` |
| 排错（流程 C） | `kb_query` 关键词 → `part_query` 零件/类 → `designer_status` / `designer_exec_js` 探查 → `guard task=error` |
| 查 API（流程 E） | `part_query` sub=class/methods；`kb_query` mode=page 精读 frapi 文档 |
| Excel 骨架（流程 F） | 同流程 A，产物骨架由套件侧 excelgy 生成后再走 A 的验证链 |

## 铁律（不可跳过）

- 改模板前先 `backup_template`（G04）。
- 新数据集 SQL 必过 `verify_sql`：执行失败与 0 行都不通过，重试≤3 次（G08）。
- 写 SQL 前先 `db_schema` 探表结构（G11）。
- 新公式写入前 `eval_formula` 三态判定（G09，需设计器已注入）。
- 收尾必 `guard`：退出码 1 = 任务未完成；attest 声明过程闸门（如 attest="G08,G09,G11"）。
- 多组件布局用 `layout_grid` 算坐标，勿手算。
- `designer_exec_js` 高危：仅做只读探查或已备份后的验证。

## 检索技巧

- 工作流：`kb_query` keyword 命中拿页 id → `mode=page` + `full` 整页精读；命中后只读命中块。
- `P-数字` 零件编号与 `com.fr.*` 全限定类名不入关键词索引 → 走 `part_query`。
- 冷热/场景视图：`kb_query mode=view`（或 hot/cold）。

## 产物与状态

- 项目产物落 `%USERPROFILE%\.fr_dev_kit\projects\<项目名>\`（`dsl_build` 的 out 参数给绝对路径）。
- 闸门报告：`list_gate_reports` / `read_gate_report`（或控制台面板浏览）。
- 环境问题先 `kit_selftest`；设计器注入/端口细节见套件 `kfgj/fr-agent/README.md`。
