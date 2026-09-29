<!--
KB_INDEX: {
  "title": "CHANGELOG — fr_dev_kit 能力面变更日志",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["kfgj", "ckzl", "jcxt", "AGENTS", "evals", "key"],
  "summary": "> 本文件管**能力面变更**（新增/变更/废弃/兼容声明/实验能力），每版一节，节标题用日期版号。 > 版本号规则：v<大版本>-<YYYYMMDD>；实验能力连续两个版本无变更且通过周体检 → 转 stable。"
}
-->

# CHANGELOG — fr_dev_kit 能力面变更日志

> 本文件管**能力面变更**（新增/变更/废弃/兼容声明/实验能力），每版一节，节标题用日期版号。
> 版本号规则：v<大版本>-<YYYYMMDD>；实验能力连续两个版本无变更且通过周体检 → 转 stable。

## v3.1-20260929 (2026-09-29)

无向量库改造 + 知识库大规模治理拆页 + 归档清理（检索零 key、零配置、零网络化）。

### Added
- 检索三件套（PageIndex 式无向量架构）：`jcxt/js/build_fts_index.py`（FTS5 关键词库 `_kb_fts.db`，按章节分块，CJK bigram + ASCII 整词）、`jcxt/js/build_tree_index.py`（树索引 `jcxt/data/_tree_index.json`，目录树 + 全量页表）、`jcxt/js/query_kb.py` 页导航（`--tree [目录]` 目录树 / `--page <id|路径> [--full]` 页级阅读）
- `jcxt/js/build_views.py` + `jcxt/js/views.yaml`：多维目录视图（场景/冷热/实战三维度 13 视图，产物 `jcxt/data/_views.json`，物理文件零移动）；query_kb.py 加 `--views` / `--view <中文名|key>` / `--hot` / `--cold` 入口
- `ckzl/gf/铁律速查.md`：FR_HEADLESS_GUIDE 铁律区拆分为独立速查页（528→182 行），GUIDE 回归纯路由

### Changed
- AGENTS.md 同步无向量说法：§0 快速开始去掉 Embedding key 登记、顶部检索说明改零 key 零配置；§4 整章重写为「关键词 + 页导航 + 结构化查询」（含维护口诀：改知识后跑两个 build）；§4.3 维护口径改为 sync_kb_index.py + jcxt/js 两个 build；流程 C 去「混合」字样；STEP 3 改指铁律速查.md；jcxt 行与索引三件套说明同步
- 知识库治理拆页：fr10_deep_learn 217 页、fr11 8 大 summary 48 页、lc 根导航页 + 34 分篇、qdjk 17 页、i18n 6 页
- `kfgj/init_user_env.py`：移除 Embedding key 登记步骤（step_embedding 降级为兼容空操作），「下一步」改指两个 build；`kfgj/env.md` 同步去 sqlite-vec/Embedding 表述
- 重复知识收敛：进行中（fr10_deep_learn/docs 与 fr11_knowledge 同源去重等，收口后另行记录）

### Removed（均在用户目录 `~/.fr_dev_kit/kit_archive/`，不随套件分发）
- 向量检索组件整体归档 `removed_kb_20260929/jcxt/js/`：build_vector_index.py、vec_engine.py、vec0.dll 插件、config.toml.example、key 配置文档等；`jcxt/data/_kb_vector.db`（约 128MB）删除
- `ckzl/zsk/dwc/` 华为数仓整目录（数仓团队职责，与报表开发无关）
- 学习路径类知识件、抓取中间产物 89 项等

### Compatibility
- query_kb.py 旧向量/混合用法（`--hybrid` / `--mode hybrid|vector`）报错退出并提示改用 keyword；`--mock` / `--engine` 接受但无效果
- 检索零 key、零配置、零网络；`jcxt/data/_kb_index.yaml`（sync_kb_index.py 产物）保留，改知识后跑 sync + 两个 build
- 旧 `~/.fr_dev_kit/embedding.toml` 不再被读取，留在原处无影响

## v3.1-20260928 (2026-09-28)

开源发布适配波：用户环境初始化向导 + 项目/隐私内容整体迁出 + 工具链环境参数化。

### Added
- `kfgj/init_user_env.py`：首次初始化向导（检测 `%USERPROFILE%\.fr_dev_kit\`，引导创建目录骨架/登记用户自己的 Embedding key/自动探测登记 FR、JDK 路径/种子 experience、memory；支持 `--status`/`--mock`/`--provider --api-key` 非交互）
- `kfgj/fzpy/userdir.py`：用户目录路径助手扩展——新增 `memory/`、`fr_env.toml`、`load_fr_env()`、`resolve_fr_home()`、`resolve_jdk_home()`（解析优先级：fr_env.toml > 环境变量 > 常见位置扫描）
- `kfgj/fr-agent/gen_cp.py`：按本机 FR 安装重新生成 cp.txt（编译 classpath 不再绑定默认安装路径）
- `ckzl/bb/外部依赖与归档声明.md`：开源版外部引用总声明（practice/ 等外部工作区不随包分发；全库 64 处「（comm版已移除）」悬空标记统一改指本文件）
- `~/.fr_dev_kit/` 用户私有数据目录体系（backup/snapshot/experience/memory/embedding.toml/fr_env.toml；AGENTS.md §0 快速开始改为「初始化 → 配环境 → 自检」三步）

### Changed
- 环境参数化：`check_env.py` 重写（读 fr_env.toml/环境变量，`C:/frjars`、`C:/fr_boot_ws`、反编译源码降为可选参考项，不再 FAIL）；`inject.py` FR/JDK 改走 userdir 解析；`build.cmd`/`start_fr.cmd`/`start_fr_with_agent.cmd` 改环境变量 + `%~dp0` 自适应；`fmt_wildcard.py`/`batch_optimize_cpt.py`/`web_kit/tests/run_acceptance.py` 支持 `FR_REPORTLETS` 环境变量并加存在性检查
- 开源脱敏（详见 kit_archive 迁移记录）：项目专属术语全库中性化（连接/表/插件/人设/内网标识 → demo_* 系中性名）；dsl 换中性 demo 语义层（`hfm_*` 键统一 `org_*`）；gczsk 三个 sqlite 文本列同步脱敏 + VACUUM
- `kfgj/check_refs.py` G05 断链基线登记表迁移：`_runs/.../g05_baseline.json` → `kfgj/evals/fixtures/link_check/g05_baseline.json`（_runs 不再入树）
- 检索首用引导（`build_vector_index.py`）指向 `init_user_env.py` 一键初始化

### Removed（迁出至套件主人本机 `~/.fr_dev_kit/kit_archive/`，共 60+ 项）
- `scwj/nightops/`（项目夜间作战全套产物）、`scwj/mb/verify_lta.py`
- `ckzl/bb/` 5 个项目/审计件（YFI 业务库、FS 拆分沉淀、新旧名称映射、隐私扫描报告、移除清单）
- `kfgj/fzpy/` 约 30 个写死业务路径的一次性脚本；`kfgj/fr-agent/` 项目脚本与项目案例教程
- `kfgj/dsl/` 项目语义层原件与 6 个反推示例；`kfgj/evals/` 内部基线运行日志
- `kfgj/plugin_pl/flks/`（内部仓库复刻件，版权风险）与个人插件台账
- `ckzl/zsk/xtgt/` 3 个个人平台研究件；`_runs/` 运行时证据；两个评测运行库

### Compatibility
- Embedding key 个人档新位置 `~/.fr_dev_kit/embedding.toml`，旧「文档」位置向后兼容（取先检测到者）
- evals 回归用例与 w915 合成夹具保留（内容为合成测试件，无业务数据）；dsl 编译/护栏测试在语义层替换后全过（compare 6/6）
- 向量库按开源后内容全量重建（--force）；`jcxt/data` 三个索引库维持 gitignore（可重建，且 _kb_vector.db 超 GitHub 100MB 单文件上限）

## v3.0-20260916 (2026-09-16)

多代理核对（知识链/工具链/v3.0 对齐三路）后的修复波：SOP 断引用归零 + 节点式工作流挂回 + 误执行安全闸。

### Added
- 根 README.md：LLM/人类导航入口（KB_INDEX 头 + 三步快速开始 + 标准工作循环 + 4 分类目录速览 + 常用命令速查；声明权威入口仍为 AGENTS.md）
- AGENTS.md：节点式工作流挂回 SOP——新增 STEP 1.5（ckzl/gzjd/00_工作流节点导航.md 判定题 Q1-Q7 → NODE-01~10 渐进加载）+ 流程 A 增补第 0 步节点式入口（修复 comm 裁剪时把 v3.0「开发任务首选入口」从路由表脱钩的弱化）

### Changed
- AGENTS.md 两处断引用修正：STEP 4 公式验证 `python kfgj/fr-agent/eval_formula.js`（.js 无法由 python 执行）→ `python kfgj/fr-agent/exec_js.py eval_formula.js`；流程 C「本地 18999 /sql 查错误日志」（端点不存在）→ `/status·/events 查设计器状态与事件流；19000 /exec 执行探查脚本`
- kfgj/plugin_pl/scripts/sn_gate.py：L242 f-string 表达式内反斜杠移出（Python 3.11 SyntaxError → 兼容 3.11/3.12+）
- kfgj/tygs/CPT模板/默认格式/fmt_wildcard.py：加 CLI 安全闸——默认 dry-run 仅列内置 targets（含存在性检查），`--run` 才实际写入（写前自动备份不变）；docstring 用法同步改写。起因：2026-09-16 冒烟 `--help` 被吞参数直接改写 5 个 示例驾驶舱 报表（已从自动备份逐字节还原，详见当日会话记录）
- kfgj/tygs/索引目录.md：FRM模板/ 分区标注「未落地」（磁盘无此目录）并给出 FRM 样式现走 frm_apply_style.py 的替代路径；风格一/风格二标注「规划占位」；fmt_wildcard「已知不一致」注记按新 CLI 更新
- kfgj/tygs/skills/fmt_wildcard/SKILL.md：用法/典型调用按 dry-run + --run 同步
- kfgj/fr-agent/README.md：快速开始 `_check_trace.py`（文件不存在）→ `trace3.py`（/events 拉取过滤 SQL/菜单类动作）

### Compatibility
- 向后兼容：fmt_wildcard.py 的 import process_cpt 通道不变；sn_gate 检查项与报告格式不变（仅转义实现调整）；AGENTS.md 路由为增量挂回，原 §3 流程 A-E 不变。
- 环境说明：本机存在个人级 Embedding 配置（dashscope text-embedding-v4，向量库 meta mock=false），jcxt/js/config.toml 仍无需创建。

## v3.0-20260915 (2026-09-15)

### Added
- ckzl/gf/FR_HEADLESS_GUIDE.md：新增铁律 AF/AG/AH（夜间批次 波实战沉淀；AF=字节对成对同步——改副本组成员前 md5 验孪生、成对改或成对弃；AG=执行棒三件套——避让双查/备份→ET.parse→复扫归零三重验证/diff 判读；AH=rebuild≠live——扫描结论需 verdict 映射+live 复验，中文路径读文件 errors=replace）；铁律分档声明改写（L77：**A-K 核心档 / L-AH 专项档**，来源补「2026-09 夜间批次 波实战」）+ frontmatter 铁律范围 A-AD→A-AH
- ckzl/lc/04_参数面板.md：新增 §22.5「模板参数声明的 4 种 XML 形态判别」与 §22.6「参数裸名陷阱——补声明前先辨裸名语义」（L568/L586，2026-09-15 夜间批次 波实测增补）
- ckzl/zsk/tbcw/README.md：新增「误报类专节」（fr_check 两误报面已修复：doc-299 把 SQL 宏内函数名当参数名 + template_param 命中按钮类控件，定性 correction；含残留 exit=1 的真实缺陷甄别判读法）+ 索引表新增误报行（L58）+ KB_INDEX summary 更新（L19）
- evals/：cases.jsonl 新增 E-夜间批次-* 用例 ×10（61 例基线）：4FORMS-BOM / FRCHK-4FORMS-BTN / MIRROR-KITSYNC / MIRROR-DRIFT-MECH / BOMV3-GHOST-LEDGER / BOMV3-DUALCHAN / FAMPTR-FACTORY / FAMPTR-TRAP / DESC13-ARROW / DOC1197-DET；fixtures/w915_a64/（chk_w915.py 十子命令统一校验器 + 3 合成 cpt，A64 泳道 _runs 迁入、md5 一致）；evals/README.md 用例表+夹具说明登记（L78/L82-91）

### Changed
- AGENTS.md：铁律范围四处 A-AD→A-AH（实测 4 处）
- kfgj/fzpy/fr_rules_doc.py：check_template_param 增按钮类控件跳过（{FreeButton, FormSubmitButton, CustomButton} 类名判定优先 + btn* 前缀双保险；RadioButton 等可绑定控件不受影响）→ 断言段 −19 全为按钮类误报
- kfgj/fzpy/fr_rules_export.py：doc-299 SQL 宏内函数名（${LEN}/${IF} 大小写敏感）不再误判为参数名（同链 doc-1197 漂移，A54 已修）
- _runs/night/campaign/_b2auto.py（⚠不入库资产，git status 不可见属正常）：desc13 箭头字符类参数收集 regex 修正（desc13 老样件零感知，输出逐字节不变）；_runs 清理后以 evals/fixtures/w915_a64/chk_w915.py 只读依赖口径为准

### Deprecated
- （无）

### Compatibility
- 向后兼容：card_factory v3.2 仅收紧生成端（存量卡池/已发卡不受影响）；fr_rules_doc/export 两修复只减误报、不改真实缺陷判定（漏报面不变）；evals 旧用例与格式不变。
- 预期信号（落笔时点终态）：evals **61/61 全 PASS**（2026-09-15 收口实测）——原 3 例固定 FAIL（E-REFS-ZERO/E-GUARD-KB-AGENTS/E-GUARD-AUTORETRY）经 G05 断链归零治理（A122 六处改写 + #7 EXCLUDE 登记）后全部转绿，退出码 0。后续若 G05 断链回潮（如新文档引入断链），这 3 例会再次连坐翻红——按 FAIL id 集合判读，勿按 PASS 总数。
- **git pull 后须知（迁移须知，逐条执行）**：
  1. 无 schema 迁移、无手工口令/配置步骤；
  3. 跑 evals 前先读 evals/README.md 基线说明（见上「预期信号」），勿按退出码一刀切判回归；
  4. jcxt/js命中的章节行号以重建后索引为准：本波增补使部分文件行号偏移（ckzl/lc/04 §22.5=L568、§22.6=L586；ckzl/gf/FR_HEADLESS_GUIDE.md 分档声明=L77；ckzl/zsk/tbcw/README.md 误报专节=L106）；
  5. 更新本机 `_local_read_state.ini` → `last_read_version=v3.0-20260915`。

### Experimental
- 「字节对台账波末重刷」固化为收尾闸门（R-0009 suggest：每写波收尾全量重扫 md5 与上波台账 diff；改副本组成员必须成对同步或显式声明分叉）——待裁决，未落地
- 维护台账 stale 行与订正行并存模式（R-0007 快照行 + R-0009 订正行同留）——待周体检观察后定去留

## v3.0-20260914 (2026-09-14)

### Added
- evals/ evals/ 评测集扩至 61 条（知识回归×8、工具自检×2 等）；run_evals.py 支持 `requires_modules` 环境跳过（SKIP 不计 FAIL）；helpers/kb_doc_check.py
- kfgj/fzpy/receipt_screen.py：外部回执指令性内容筛查（数据/指令分离，P1-6；自检 5/5）
- ckzl/zsk/gczsk/build_manifest.py + script_manifest.json：121 个工具脚本 registry（--check 漂移检测，P1-7）
- jcxt/js/build_fts_index.py + _kb_fts.db（15,487 块）+ query_kb.py `--hybrid`（BM25+向量 RRF 融合，代理层，P0-2）
- llm_call_logger.py `span_kind`（agent/tool/llm 自动推断）+ `cost_est`；llm_trace_report.py "预算与失败分类"节（P2-1）
- node_gate.py `--circuit-breaker N`（opt-in 熔断，P2-2）
- kfgj/fzpy/templates/task_todo_template.md（P2-3）
- ckzl/lc/fr11_knowledge/_standardize_frontmatter.py（16 主题 frontmatter 标准化，P2-6）
- patches/ 8 份提案（P0-4、P1-1~P1-3、P1-6、P2-3~P2-5；除 P1-1 部分项外均已应用）

### Changed
- 17 个知识文件 KB_INDEX 就地补 trigger/when_not 字段（ckzl/gzjd×11 + 卫星×6，P0-3）
- AGENTS.md kernel：STEP 0 复杂度档位表（P1-3）、todo/失败留痕纪律行（P2-3）、冲突裁决与回执筛查路由行（P1-2/P1-6）、§1.7.1 连接信息下沉 kfgj/env.md、sync_hub/ckzl/zsk/gczsk用法块压缩为指针、§5 历史段与文末元注记移除（P1-1，45,057→43,055B）
- ckzl/lc/fr11_knowledge/：16 主题 SKILL.md 补齐 compatibility: FR11（P2-6 推广完成）

### Deprecated
- （无）

### Compatibility
- 断裂点：guard 的 redo 链修复依赖 `python -X utf8`（E-AUTORETRY-G06 已登记）；bundled Python 3.13 无 PyYAML，dsl/compile 类用例经 requires_modules 跳过。
- 口令轮换：AGENTS.md 不再承载 §1.7.1 连接信息（下沉 kfgj/env.md）；**pgvector 口令轮换为手工步骤**，轮换后同步两机 LOCAL_ENV。

### Experimental
- node_gate.py --circuit-breaker 熔断阈值策略
- query_kb.py --hybrid 代理层实现（若重装 kb_platform 代理桩需回放补丁，见 _runs 执行报告）

## v3.0-20260911 (2026-09-11)

### Added
- ckzl/gzjd/node_gates.yaml 节点出口门禁（单一事实源）+ kfgj/fzpy/node_gate.py 执行器
- kfgj/fzpy/llm_call_logger.py 动作级日志 + llm_trace_report.py 周五复盘
- AGENTS.md §1.2 STEP4 动作日志纪律行；§3 路由表新增 node_gate/llm_call_logger/llm_trace_report 三行

### Changed
- AGENTS.md §1.3 流程 A 对齐节点序列；STEP5 probe --layout 改口（未交付占位参数）

### Compatibility
- 详见 _runs/SOP提速执行报告_20260911.md（当时登记口径）。

### 插件工艺流水线（pipeline_v1 v1.1 + 复刻实践首跑）2026-09-15

### Added
- kfgj/plugin_pl/：插件开发工艺流水线 v1.1 全套（七阶段+SN-01~12 标准节点+复盘问题台账 v1.1 共 37 条含复刻实践 D 段 P27-P37+sn_gate.py v1.1 机器闸门 C01-C13+sn_scaffold.py 骨架生成器+AGENTS 修订建议稿+交接手册+干跑校验报告+知识沉淀判定+瑞士网格总览 HTML；基线=AGENTS.md v3 kernel+归档盘点 demo_plugin_repo 四快照+示例插件A demo_copilot 交付记录）
- kfgj/plugin_pl/flks/：流水线首跑实践（内部代码托管平台 demo_plugin_repo v2.1.12 五路并行 agent 复刻 46 类 10504 行；集成编译 0 错+jar 5.3MB+ProUnitTest 78/78；sn_gate 三跑实录 C06 断点修复+C13 新增；35 条发现收敛 P27-P37；实践报告+五路代理回执+gate 报告三份+unit-baseline.json）
- 入库排除：复刻实践 reference/（嵌套 clone 按报告命令重取）与 replica build//test classes/（可重建产物）；CHANGELOG 本条由流水线会话追加，文件含并行会话在途修改故本会话不提交此文件
