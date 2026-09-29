<!--
KB_INDEX: {
  "title": "执行契约（v2 核心增量）",
  "stage": "root",
  "tags": ["入口", "执行契约", "闸门", "guard"],
  "keywords": ["EXEC_CONTRACT", "kfgj/guard.py", "闸门", "G01-G12", "收尾"],
  "summary": "v2 新增的执行契约层：把指南中的强制项收敛为 12 条硬闸门，由 kfgj/guard.py 强制执行，跑不过=任务未完成"
}
-->

# kfgj/EXEC_CONTRACT.md — 执行契约（v2 核心增量）

> **v1 的教训**：指南里写了 1000+ 处"必须/禁止"，全部依赖大模型自觉执行 → 实际频繁被跳过。
> **v2 的对策**：把"必须做的动作"收敛为 **12 条硬闸门**，由 `kfgj/guard.py` 强制执行。
> **契约规则**：任何模板产出/修改/知识变更任务，**收尾必须跑 kfgj/guard.py 并全部通过**；跑不过 = 任务未完成，交付物无效。

---

## 一、为什么 v1 的"配置项"不被执行

| # | 根因 | v1 表现 | v2 对策 |
|---|------|---------|---------|
| 1 | **强制项无机器执行点** | "必须备份/必须验XML/必须过fr_check"散落在 128 个 md 的自然语言里，读不到就执行不到 | 收敛为 G01–G12 闸门，`kfgj/guard.py` 一条命令收尾判定 |
| 2 | **入口分裂** | AGENTS.md / CLAUDE.md / README / FR_HEADLESS_GUIDE 四个入口各说各话（铁律范围 A-K vs A-AD 不一致） | 统一"铁律 A–AD"口径；四入口全部指向本契约 |
| 4 | **知识规模标错** | "本知识库有 44 个文件"（实际 700+），模型据此错误估计读取量 | 修正为实际规模 + 明确懒加载边界 |
| 5 | **环境耦合写死** | fr_check.py 硬编码 `C:\Program Files\FineReport_10.0\...`，换机即失效 | 改为 kfgj/env.md 优先、硬编码仅作回落 |
| 6 | **agent 配置缺位** | .claude/settings.local.json 是另一台机器(uhoux010)的残留权限，对本机无效 | 替换为本机 hooks（PostToolUse 自动跑 guard） |

---

## 二、闸门清单（G01–G12）

> 详见 `python kfgj/guard.py --list`。**文档与代码同源由 G07 保证**（改任一侧都必须同步另一侧）。

| 闸门 | 标题 | 类型 | 判定 | 适用任务 |
|------|------|------|------|---------|
| G01 | 本机环境已加载(kfgj/env.md 可解析) | 自动·WARN | 文件存在且含 FR 路径信息 | 全部 |
| G02 | XML 合法性(ET.parse 通过) | 自动·硬 | python ET.parse 退出码 0 | create/modify/format |
| G03 | fr_check 静态+98条官方规则校验 | 自动·硬 | 退出码 0 或 2(仅警告) | create/modify/format |
| G04 | 修改前备份目录存在(_backup_*) | 自动·硬 | cpt 同级/上级 3 层内可见 `_backup_*` | modify/format |
| G05 | 全库引用完整(断链=0) | 自动·硬 | kfgj/check_refs.py 退出码 0 | 全部 |
| G06 | 知识文件含 KB_INDEX 元数据头 | 自动·硬 | 文件头 2000 字符内含 `KB_INDEX` | kb |
| G07 | 契约文档与 kfgj/guard.py 同源 | 自动·硬 | 两边 G 编号集合相等 | 全部 |
| G08 | 新数据集 SQL 过 verify_sql 闭环 | 声明·硬 | `--attest G08`（0行=不通过,重试≤3） | create |
| G09 | 新公式过 eval_formula.js 三态判定 | 声明·硬 | `--attest G09` | create/modify |
| G10 | 改模板前已取 template_snapshot 快照 | 声明·硬 | `--attest G10` | modify/format |
| G11 | 写 SQL 前已用 db_schema 探查表结构 | 声明·硬 | `--attest G11` | create |
| G12 | 浏览器预览 HTTP 200 无报错 | 人工·硬 | FR 运行时人工确认（报告留 WARN 提示） | create/modify/format |

### 常见问法：G05 断链检查是什么/断链怎么查？
> G05 = 全库引用完整(断链=0)，自动·硬闸门，判定 = `kfgj/check_refs.py` 退出码 0，适用全部任务（见上表）。
> 收尾由 `python kfgj/guard.py --task <类型>` 自动执行；单看闸门全集 `python kfgj/guard.py --list`（L38）。
> 节点级出口门禁（node_gate）路由见 AGENTS.md §3「节点出口门禁」行。

**类型说明**：
- **自动**：kfgj/guard.py 直接执行，无法绕过；
- **声明（attest）**：过程闸门发生在流程中间（如"写 SQL 前先探查表结构"），guard 无法事后复现，必须由执行者在收尾命令中显式声明 `--attest G08,G11` —— **声明即留痕**（报告落盘 `_runs/`），事后可审计；未声明 = FAIL；
- **人工**：需要浏览器/人眼确认的项，guard 提示后留 WARN。

### 「G05 是什么？断链怎么处理？」（口语问句锚点，2026-09-12 增补：审计实测 `G05 断链` 查询 13 次 top5 未命中本表）

**G05 是什么**：收尾闸门之一 = **全库引用完整性**——所有 .md 里写的库内路径（链接/反引号路径/「根目录 X」）必须真实存在，断链数必须为 0。立法原因见本文件 §一第 3 条：断链指令=模型照做必然失败的死路。

**「断链」怎么查/怎么修**：

| 步骤 | 命令/去处 |
|------|----------|
| 手动全库查一次 | `python kfgj/check_refs.py`（在**仓库根**执行；断链时退出码 1，报告列出 FAIL 明细） |
| 收尾闸门跑法 | `python kfgj/guard.py --task <类型>`（G05 自动执行）；换机/怀疑环境坏先 `python kfgj/guard.py --selftest` |

**易混淆**：G 编号闸门（G01-G12，收尾契约）只在本文件与 kfgj/guard.py；`ckzl/gzjd/node_gates.yaml` 是另一套**节点出口门禁**（N01-SCHEMA 等，按 NODE 编号），两者不互通。

---

## 三、标准收尾命令（按任务类型）

```powershell
# 创建新报表（全过程声明 G08/G09/G11）
python kfgj/guard.py --task create --cpt <路径.cpt> --attest G08,G09,G11

# 修改已有模板（改前快照 + 新公式验证）
python kfgj/guard.py --task modify --cpt <路径.cpt> --attest G09,G10

# 纯格式化（改前快照）
python kfgj/guard.py --task format --cpt <路径.cpt> --attest G10

# 排错任务（无模板产出）
python kfgj/guard.py --task error

# 知识库维护（新增/修改 md 后）
python kfgj/guard.py --task kb --doc <文件.md>

# 自检（环境/断链/契约同源；换机后先跑这个）
python kfgj/guard.py --selftest
```

**退出码**：`0`=通过；`1`=存在 FAIL（任务未完成）；`2`=通过但有 WARN/SKIP。

**豁免纪律**：
- `--no-backup`：仅限"只读校验/全新文件"场景，豁免会写进报告；**连续两次以上豁免 = 流程违规**；
- `--draft`：草稿模式把未声明的过程闸门降为 WARN，**仅限开发中自测，正式交付禁止**。

---

## 四、与 v1 既有体系的关系

| v1 组件 | v2 中的角色 |
|---------|------------|
| AGENTS.md 决策树/路由表 | 不变，仍是任务路由入口；SOP 增补"STEP 7 收尾闸门" |
| ckzl/gf/FR_HEADLESS_GUIDE.md 铁律 A–AD | 不变，是**知识层**规则（写什么、怎么写）；契约是**动作层**（做没做） |
| fr_check.py | 被 G03 调用，成为闸门的实现件 |
| kfgj/sync_kb_index.py / build_vector_index.py | 不变；G05/G06 保证其输入（链接/元数据）完好 |
| _runs/gate_report_*.md | 新增：每次闸门执行留痕，可审计 |

**一句话**：铁律告诉你"该怎么写"，契约保证你"该做的都做了"。

---

## 五、维护规则

1. 新增/修改闸门：改 `kfgj/guard.py` 的 `GATES` 表 **和** 本文档第二节表格（G07 会校验两边同源，漏一边直接 FAIL）；
2. 闸门只增不删：废弃的闸门标记 `severity: warn` 并在文档注明原因，不删除编号；
3. 每次会话第一条命令建议 `python kfgj/guard.py --selftest`（换机/克隆后尤其必要）。

---

