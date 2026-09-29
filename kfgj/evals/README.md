# evals/ — fr_dev_kit 内部评估集（CAR-019 起步版，2026-09-06）

> 设计依据: `_runs/night/R65_sop_github/T15_内部评估集设计.md`（Anthropic 口径）。
> 起步集 17 条，全部验收命令化；**本目录是长期资产，入 git**（原设计落 `_runs/evals/`，因 `_runs` 不入版本库，改落仓库根 `evals/`）。

## 1. 双轨口径（capability / regression）

| 轨 | 定义 | 何时跑 | 处置 |
|----|------|--------|------|
| **capability** | 新功能首次固化（CAR-009 围栏 / CAR-010 auto-retry / CAR-012 G0 闸 / CAR-014 模板 BOM） | 每次改动对应工具后 + 夜间批次 | 观察通过率找短板；**连续 3 次全绿 → 毕业**为 regression（改 `cases.jsonl` 该条 `kind` 字段，title 注明毕业日期） |
| **regression** | 既有功能防回退（fr_check 前置闸 / link_check / query_kb / 重建产物 / 台账完整性） | 改 guard/铁律/工具输出文案/换模型前必跑 | 任何一条 FAIL = 回退，先修复再交付 |

毕业制是活的流水：新功能上线先立 capability 条目，稳定后转 regression；评估集只增不删（见 §4）。

## 2. 跑法

```powershell
cd 仓库根
python evals/run_evals.py                    # 全量, PASS/FAIL 矩阵, 全绿退出码 0
python evals/run_evals.py --kind capability  # 只跑一轨
python evals/run_evals.py --case E-DSL-CLEAN # 只跑一条
python evals/run_evals.py --list             # 只列清单
```

- 退出码: **0=无 FAIL（SKIP 不算）, 1=有 FAIL**（含 setup 失败）, 2=`--case`/`--kind` 过滤后无匹配用例。矩阵含每条 rc、未命中断言明细。
- harness 冻结纪律：分数只在同一 harness 下可比。**改了被测工具的输出文案/退出码语义 → 必须同步改 `cases.jsonl`，并在本 README §5 登记「评估口径断裂点」**，否则历史通过率不可比（Harness-Bench 结论）。

## 3. cases.jsonl 字段口径

```json
{"id": "E-XXX",            // 唯一 id, 前缀按工具域
 "title": "一句话",
 "kind": "capability|regression",
 "source": "来源卡/出处",
 "setup": ["cmd", ...],    // 前置命令(顺序执行, 任一失败该条判 FAIL 不跑主命令); 无则 []
 "command": "cmd",         // 验收主命令, 仓库根为 cwd
 "expect_exit": 1,         // int / [int,...](任一) / null(不检查, 须在 expect_exit_note 说明原因)
 "expect_contains": ["子串"],   // 全部命中(作用于 stdout+stderr 合并流)
 "expect_regex": ["正则"],      // 可选, 全部 re.search 命中
 "expect_exit_note": "…",       // 可选, expect_exit 置 null 时的原因说明
 "retired": true}               // 可选, 条目退役标记(保留不删, 见 §4)
```

子进程输出按 utf-8→gbk 兜底解码；setup/command 经 `shell=True` 执行（Windows 走 cmd.exe），写命令时避免 bash 专属语法。

## 4. 加新条目规则

1. **来源优先级**: 真实失败轨迹（guard FAIL / 回执卡点 / 用户报障）> 新功能固化 > 覆盖率补洞。失败驱动建集，不造纸上用例。
2. 每条必须**验收命令化**：能一条命令跑出 rc + 可断言输出；断言避免脆弱匹配（钉关键标志串/数字量级，不钉整段输出）。
3. fixture 一律放 `evals/fixtures/<域>/`，**不污染仓库其他位置**；setup 负责把夹具复位到用例前置态（保证可重复跑）。
4. **只增不删**：跑不绿 → 修夹具/修期望，不许删条目；确因工具语义演进而失效的条目加 `"retired": true` 保留在案。
5. 新条目先单跑（`--case <id>`）绿了再入库；入库跑一次全量确认 17→N 全绿。

## 5. 起步集清单（17 条 = capability 7 + regression 10）

| id | 轨 | 验证点 |
|----|----|--------|
| E-FRCHK-ZEROBYTE | regression | fr_check L1: 0 字节判病灶 rc=1 含「0 字节」 |
| E-FRCHK-BAREAMP | regression | fr_check L1: 裸 & 断裂实体 rc=1 含「病灶行」（行列号定位） |
| E-FRCHK-BINARY | regression | fr_check L1: 二进制 rc=1 含「非文本」 |
| E-FRCHK-GBK | regression | fr_check L1: GBK 文件给出「GBK 编码」告警检出 |
| E-LINKCHK-FIXTURE | regression | link_check 小夹具 2 断链精准命中（好链不误报） |
| E-ENC-LANE-VIOLATION | capability | guard --check-enclosure 泳道外探针判违规 rc=1 |
| E-ENC-LANE-CLEAN | capability | guard --check-enclosure 纯合规 rc=0 |
| E-AUTORETRY-G06 | capability | guard --auto-retry: G06 先 FAIL → redo 补头 → 复检 PASS 闭环 |
| E-DSL-G0-REJECT | capability | dsl compile: needs_clarification 拒编译 rc=3 且产物未落盘 |
| E-DSL-CLEAN | regression | dsl compile: 干净样例 rc=0 产物落盘 |
| E-BOM-HIGHFREQ | capability | query_template_bom highfreq 非空（ds1 居首） |
| E-BOM-DANGLING | capability | query_template_bom dangling 悬挂引用 >1000 条（FS 408 量级） |
| E-BOM-NODE-DS1 | capability | query_template_bom node ds1 命中≥1 |
| E-KB-PART | regression | query_kb part ParameterUI 零件命中≥1 |
| E-KB-MACHINE | regression | query_kb machine 机器清单非空（52 条量级） |
| E-REBUILD-ET-SPOT | regression | campaign/rebuild 确定性抽 3 件 ET 解析全过 |
| E-ROUTER-LEDGER | regression | 任务路由台账 R-0001/R-0002 存在且逐行 JSON 可解析 |

### 5.1 W915 战果回归批（10 条，2026-09-15 A64 固化 / A79 迁位登记）

> 夹具：`evals/fixtures/w915_a64/`（chk_w915.py 十子命令统一校验器 + 3 合成 cpt），2026-09-15 由 A64 泳道 `_runs` 迁入（md5 与泳道原件逐一一致）；校验器另**只读**依赖 `_runs/night/campaign/` 既有资产（A57 template_bom_v3_prelim.sqlite / A40 mirror_ledger / v3wave_run / _b2auto），`_runs` 被清理时相关条 FAIL 属环境漂移信号。

| id | 验证点 | 夹具 | 期望 |
|----|--------|------|------|
| E-W915-4FORMS-BOM | 四形态声明全收/2 排除位不收/数据集级 ds_params/两种默认值载体/盲区日志恰 2 | w915_a64/（four_forms_decl.cpt） | rc=0（7 断言） |
| E-W915-FRCHK-4FORMS-BTN | fr_check 四形态与按钮类零误报；doc-299 无 ${LEN} 假阳性、无 ERROR | w915_a64/（frchk_btn_4forms.cpt） | rc=0（7 断言） |
| E-W915-MIRROR-KITSYNC | kit.py 现值 md5 == A40 镜像台账（单侧改=立即告警） | w915_a64/chk_w915.py（读 A40 台账） | rc=0（2 断言） |
| E-W915-MIRROR-DRIFT-MECH | 字节级同副本判 SAME；单侧改 1 字节必判 DRIFT 且定位偏移 | w915_a64/chk_w915.py | rc=0（3 断言） |
| E-W915-BOMV3-GHOST-LEDGER | v3 库无幽灵行/无未裁决 R1/R2/留存行均 R4 附依据 | w915_a64/chk_w915.py（读 A57 v3 库） | rc=0（3 断言） |
| E-W915-BOMV3-DUALCHAN | 双通道判定：B 命中=R4 否决/均未命中=R2 维持/盲区恰 2 | w915_a64/（dual_channel_decl.cpt） | rc=0（8 断言） |
| E-W915-FAMPTR-FACTORY | CAL 族指针 scope 拒产+族指针文本禁令+显式 seq 卡放行 | w915_a64/chk_w915.py | rc=0（5 断言） |
| E-W915-FAMPTR-TRAP | ④负向陷阱证明：伪 seq[1,6] 复现（语义见 §6 注④） | w915_a64/chk_w915.py | rc=0（5 断言） |
| E-W915-DESC13-ARROW | desc13 箭头字符类参数收集（名/默认/控件）+ ASCII `<` 不回退 | w915_a64/chk_w915.py | rc=0（5 断言） |
| E-W915-DOC1197-DET | doc-1197 两规则输出跨 PYTHONHASHSEED 0/1/2 指纹逐字节一致 | w915_a64/chk_w915.py | rc=0（5 断言） |

## 6. 实现备注（评估口径断裂点台账，倒序）

- **2026-09-06 建集基线**（CAR-019 / L15 泳道）：
  - `E-AUTORETRY-G06` 的 `expect_exit=null`：guard 任一 `--task` 都含 G05 全库断链闸，当时仓库有 65-67 处断链（L9/CAR-022 收口中）→ 整体 rc 现为 1、修完变 0；闭环正确性改由 contains 三断言（redo 执行成功 / fix_doc 实际补头 / G06 复检 PASS）钉死。**L9 收口后可把 expect_exit 收紧为 [0,1] 或按当时实况收紧。**
  - `E-ENC-LANE-CLEAN` 用未来 `--since 2027-01-01` 冻结（免受并行泳道写文件干扰）；`E-ENC-LANE-VIOLATION` 用 `--since 2026-09-04`（建集日，fixture 探针必命中）。
  - dsl 两例用 `evals/fixtures/dsl/` 下的 **examples 副本**（clean_page.yaml / 根级 needs_clarification 注入的 clarify_page.yaml），`dsl/examples/` 原件零改动——比「临时标记+还原」更稳，无还原遗漏风险。
  - `E-REBUILD-ET-SPOT` 依赖本机 `_runs/night/campaign/rebuild/`（≥3 件 .cpt/.frm，确定性抽首/中/末件）；换机若目录缺失该条会 FAIL，属环境漂移信号非误报。
  - guard `--task` 流程每次运行会按其自身逻辑落 `_runs/gate_report_*.md`（guard 既有行为，非本套件污染）。


## P0-1 增补（2026-09-14 主线补位）

- 用例扩至 33 条：新增 6 条「错误案例知识回归」（evals/helpers/kb_doc_check.py 断言错误分析文档在库且含关键结论：CDATA 悬空/DSColumn/公式不存在/事件环递归/PageRWorkSheet 强转/CPT 无法查看）+ E-EXPORTGATE-SELFTEST + E-RECEIPT-SCREEN。
- runner 新增 `requires_modules` 字段：当前环境缺模块时该用例判 SKIP（不计 FAIL），防环境噪声污染回归矩阵（E-DSL-G0-REJECT / E-DSL-CLEAN 依赖 PyYAML）。
- 评估口径断裂点登记：E-AUTORETRY-G06 的 redo 命令改 `python -X utf8`——修复 guard run_redo 强制 UTF-8 解码 vs 子进程 GBK 管道输出的解码链脱靶；断言文案未变。
- 基线：`evals/_baseline_run_20260914_mainline.txt`；汇总行含 SKIP 计数，退出码语义=有 FAIL 才非零。
- 增补回归（2026-09-14 续跑）：E-FM-NODE-KEY / E-FM-ROUTE-KEY（17 文件元数据抽检）与 E-FTS-INDEX（FTS 快照在位）已入集；hybrid 双模式对比用例因需 embedding API 调用，留专项执行（对比证据见 _runs 执行报告）。

## P0-P2 续跑增补（2026-09-14 下午）

- 用例 36 → 38 条：新增两条 **G05 终态守门**用例（8 路断链收口分槽，本槽只动 evals/）：
  - **E-REFS-ZERO**（capability）：`python kfgj/check_refs.py`，断言「断链 0 处」（归零文案实测：明细行「✅ 断链 0 处」+ 汇总行「(断链=0)」，失败态打印「断链 N 处」N>0 不会误命中）。语义：断链清零后**必须保持 0，防断链回潮**——断链一旦 >0 该条立即 FAIL。`expect_exit=null`（不 pin 退出码：终态应为 0，但其余 7 路修复完成前全库仍有断链会 rc=1，这正是守门意义；终验后可按 E-AUTORETRY-G06 同款路径收紧为 0）。
  - **E-GUARD-KB-AGENTS**（capability）：`python kfgj/guard.py --task kb --doc AGENTS.md`，`expect_exit=0`——锁 **AGENTS kernel 的 kb 闸门终态**（G01/G05/G06/G07 全过；G06 KB_INDEX 已确认在位）。G05 归零前该条会因 G05 断链闸 FAIL，属预期。
- 收口启动时点实测（2026-09-14 下午）：E-REFS-ZERO FAIL（断链=95，contains 未命中）；E-GUARD-KB-AGENTS FAIL（guard rc=1，PASS=3 / FAIL=1，FAIL 项即 G05 断链闸）。**终验由主控在全路完成后执行**：届时两条应同时转绿（「断链 0 处」+ rc=0），任一回退（断链>0 / guard rc≠0）即 FAIL。

## W915 战果回归批登记（2026-09-15 A64 固化 / A79 迁位，评估口径断裂点三注）

- 用例 51 → 61 条：A64 追加 10 条 W915 战果回归（清单见 §5.1）。夹具 2026-09-15 由 A64 泳道 `_runs` 迁入 `evals/fixtures/w915_a64/`（3 合成 cpt + chk_w915.py，md5 与泳道原件一致），`cases.jsonl` 仅该 10 条 command 路径字段同步改写、其余 51 行逐字节未动。
- **注④ 负向用例语义**：`E-W915-FAMPTR-TRAP` 的 **PASS = 陷阱机制按 A56 实证复现**（执行链 v3wave_run.load_cards 对指针卡解析出伪 seq [1,6]，工厂自检是当前唯一防线，本条把陷阱机制钉桩）。该条转 FAIL ≠ 评估集故障，而是解析器已改为能拒/正确解析指针卡的**预期审计信号**——届时须重审 A56 契约与真池 995 张存量指针卡的处置口径。
- **注 G05 断链态既有 FAIL 归因**：A64 全量时 4 条既有 FAIL 全属 G05 断链收口/G06 auto-retry 状态族，与追加无关（51 条基线复跑同样 FAIL）。断链现值=7（+基线豁免 3）：`E-REFS-ZERO`（守门设计，断链≠0 即 FAIL）、`E-GUARD-KB-AGENTS`、`E-GUARD-AUTORETRY` 三条随 G05 闸固定 FAIL 属预期；`E-AUTORETRY-G06` / `E-W915-AUTORETRY-NOFIX` 为顺序/状态敏感抖动条（PASS/FAIL 交替，自述前提是「G05 断链归零态基线」）。**终验归主控**：全路断链归零后统一复跑转绿。
- **注 doc-158 存量噪声**：合成夹具（frchk_btn_4forms.cpt 等）会命中 doc-158 dataset_param 残留告警，属对合成夹具的存量噪声、非 A39 修复面（doc-299 dataset_conn）；相关用例断言只钉「doc-299 无 ERROR + ${LEN} 假阳性消失」，**不 pin fr_check 整体 rc**，故该噪声不致误判 FAIL。
- 迁位验证闭环（A79）：迁移前后各一次全量 runner，均 58/61 PASS、FAIL 组逐条一致（即上述 G05 三条）、10 条新用例全绿；证据 `_runs/night/campaign/w915/A79_eval_migrate/evidence/full61_{pre,post}_migrate_20260915.txt`。
