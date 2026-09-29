<!--
KB_INDEX: {
  "title": "知识检索系统（无向量·PageIndex 版 + 多维视图）",
  "stage": "jcxt",
  "tags": ["检索", "无向量", "FTS5", "树索引", "PageIndex", "RAG", "多维视图"],
  "keywords": ["keyword", "FTS5", "BM25", "query_kb", "build_fts_index", "build_tree_index", "build_views", "views.yaml", "kb_common", "树导航", "页级阅读", "多维视图", "--tree", "--page", "--view", "--views", "--hot", "--cold"],
  "summary": "纯本地无向量检索与视图层：FTS5 关键词(_kb_fts.db) + 树索引导航(_tree_index.json) + 页级阅读(--page) + 多维视图(scenario 场景/temperature 冷热/practice 实战，views.yaml 规则→build_views.py→_views.json→query_kb --view/--hot/--cold)；向量路已归档至 ~/.fr_dev_kit/kit_archive/removed_kb_20260929/，零 key 零配置，物理文件零移动"
}
-->

# jcxt/js — 知识检索系统（无向量·PageIndex 版 + 多维视图）

> 2026-09-29 改造：参考 **PageIndex** 方案（扔掉向量库，按文档结构建树索引 + 页级存储 +
> 导航式检索）重构为**纯本地无向量**检索。向量组件（embedding 调用 / sqlite-vec vec0 插件 /
> 余弦回退 / config.toml key 配置）已整体归档到
> `~/.fr_dev_kit/kit_archive/removed_kb_20260929/jcxt/js/`，检索零 key、零网络、零配置。
> 同日追加**多维目录视图层**（scenario/temperature/practice 三维投影，`views.yaml` +
> `build_views.py` + `query_kb --view`，物理文件零移动），见下方专节。

## 架构：检索三件套 + 多维视图

```
ckzl/ 知识 md（每文件 = 一"页"，头部 KB_INDEX 注释块含 title/summary/keywords/tags）
  │
  ├─ build_tree_index.py ──→ jcxt/data/_tree_index.json   【树索引】目录树导航 + 扁平页表
  │                            root: 目录层级树（导航用）
  │                            pages: 全量页表（id/path/title/summary/keywords/tags/lines/sections）
  │
  ├─ build_fts_index.py  ──→ jcxt/js/_kb_fts.db           【关键词库】FTS5，按章节分块
  │                            检索字段 = 页标题 + KB_INDEX + 章节路径 + 正文
  │                            分词 = CJK bigram + ASCII 整词（kb_common.tokenize_for_fts）
  │
  ├─ build_views.py      ──→ jcxt/data/_views.json        【多维视图】views.yaml 规则 →
  │                            scenario 场景 / temperature 冷热 / practice 实战 三维投影
  │                            （PageIndex 思路视图层，物理文件零移动）
  │
  └─ query_kb.py          【检索入口】关键词检索 + --tree 导航 + --page 页级阅读
                             + --views / --view 多维视图目录
```

共享底座 `kb_common.py`：CJK bigram 分词、KB_INDEX 解析、章节切分（代码围栏感知）、
ckzl 文件收集（跳过 `_` 开头文件/目录与非 md）、win GBK 控制台保护。

## 用法

```bash
# 1) 关键词检索（默认模式 keyword；--top 条数；--full 打印命中块全文）
python jcxt/js/query_kb.py "打开Excel 转 cpt" --mode keyword --top 3
python jcxt/js/query_kb.py "冻结表头怎么配置" --full

# 2) 目录树导航（可选目录过滤；树叶带页标题与行数）
python jcxt/js/query_kb.py --tree            # 全库顶层
python jcxt/js/query_kb.py --tree ckzl/lc    # 只看 lc 目录（也认 --tree lc）

# 3) 页级阅读（按 id/路径/关键词定位页）
python jcxt/js/query_kb.py --page lc/10_Excel骨架正向工艺          # 元数据 + 章节目录
python jcxt/js/query_kb.py --page ckzl/lc/10_Excel骨架正向工艺.md --full   # 加印整页全文

# 4) 多维视图目录（场景/冷热/实战，见下节）
python jcxt/js/query_kb.py --views                # 列全部视图与页数
python jcxt/js/query_kb.py --view 运维维护        # 支持中文名 / 英文 key（ops / hot / flow_f…）
python jcxt/js/query_kb.py --hot                  # 等价 --view hot（--cold / --warm 同理）
```

命中结果带页 id 与章节数，典型工作流（agent 导航式阅读）：
**关键词命中拿页 id → `--tree` 看该页在目录中的位置 → `--page <id> --full` 整页精读。**

已移除接口的行为：

| 旧用法 | 现行为 |
|--------|--------|
| `--hybrid` / `--mode hybrid` / `--mode vector` | 报错退出（提示改用 keyword） |
| `--mock` | 接受但无效果，打印提示（关键词检索本就零 key） |
| `--engine vec0/blob` | 接受但无效果，打印提示 |
| 默认模式（无参数） | 即 keyword（不再需要选模式） |

## 多维视图（scenario / temperature / practice）

PageIndex 思路的**视图层**：在 `_tree_index.json` 页表之上按选择规则投影出三个维度的目录，
**物理文件零移动**。规则外置在 `views.yaml`（可自行增删视图/改规则），
`build_views.py` 套用规则生成 `../data/_views.json`，`query_kb.py --view` 消费。

三个维度 13 个视图：

| 维度 | 视图 | 选取思路 |
|------|------|---------|
| scenario 场景 | 运维维护(ops) | 部署/集群/性能/权限/调度/备份/监控/升级/迁移：fr11 deploy-cluster/performance/permission/mobile 目录 + lc/08 + 设计器重启预检 + 元数据正则 |
| | 新构建(build) | 从零建模板流程A/F 全链路：lc/00~06 + gzjd/ + hbfa/ + zsk/xqfx + 流程F 页 |
| | 修改改造(modify) | lc/03/04 分篇 + 复杂模板改造协议 + 改造/格式化/通配正则（kfgj/tygs 见视图外置指针） |
| | 排错(debug) | zsk/tbcw 全部 + 错误案例标签 + lc/08 + lc/02 调试技巧 + FR_HEADLESS_GUIDE |
| | API查询(api) | frapi/ 全部 + zsk/gczsk 零件库 + Java 包名速查 + 官方文档资源索引（P-\d+ 零件走结构化通道，见外置指针） |
| | 验收交付(accept) | zsk/csff 全部 + gf/yspj 判级 + gzjd/10 预览验证 + 运行体检页 |
| | 数据开发(data) | lc 数据建模/数据集/级联 + gzjd 01/02 + zsk/dwc 数仓 + zsk/sjfx 数据分析 |
| temperature 冷热 | 热(hot) | AGENTS.md 与 FR_HEADLESS_GUIDE 直链页 + 全库被引用 top30 + 零件库/JavaAPI速查/铁律六件；页附 hot_score（被引用次数） |
| | 温(warm) | 补集：其余主题参考页（fr11 references、tbcw、qdjk 等） |
| | 冷(cold) | fvs/i18n/print/skin/mobile 小众主题 + bb 变更与归档声明 + fr10_deep_learn 深水页（与 hot 不相交） |
| practice 实战 | 流程F实战(flow_f) | 2026-09-29 Excel 骨架正向工艺链：lc/10 + 复杂模板改造协议 + JavaAPI构建速查 + hbfa（kfgj/excelgy 三件套见外置指针） |
| | HFM V2 改造实战(hfm_v2) | 填报链：gzjd/05 + lc Stage5 填报五篇 + 填报类错误 tbcw + csff 验收 |
| | GLM-in-Excel 逆向借鉴(glm) | pending_write_token 两阶段写入/公式风险预检理念页（P-9835/P-9836 零件见外置指针） |

```bash
# 构建与自检（views.yaml 或 ckzl 知识变动后重跑；--verify 校验视图页 id 均存在于树索引、
# 冷热三视图两两不交且覆盖全库、hot 页 hot_score 完整）
python jcxt/js/build_views.py
python jcxt/js/build_views.py --verify

# 查询
python jcxt/js/query_kb.py --views              # 列全部视图（key/中文名/页数/说明）
python jcxt/js/query_kb.py --view 运维维护      # 视图页清单：title [行数] — 摘要60字 | 路径
python jcxt/js/query_kb.py --view ops           # 英文 key 同效（scenario_ops→ops）
python jcxt/js/query_kb.py --hot                # 热视图（--cold / --warm 同理）
python jcxt/js/query_kb.py --view flow_f        # 实战视图（practice_flow_f→flow_f）
```

视图名解析支持：完整 key（`scenario_ops`）→ 中文名（`运维维护`）→ 短名（`ops`/`hot`/`flow_f`）→
`维度/短名`（`scenario/ops`）→ 中文名/短名前缀模糊（命中多个会列出候选）。
视图数据缺失时 `--view` 会提示先跑 `build_views.py`。

维护：改 `views.yaml`（规则字段 dirs/paths/path_regex/keywords_regex/tags/referenced_by/
top_refs/min_refs/complement_of/exclude_paths/external，均为并集组合）后重跑
`build_views.py` 即可；视图引用的页以树索引为准，ckzl 知识变动后先跑 `build_tree_index.py`
再跑 `build_views.py`。views.yaml 用自绘极简格式（两层缩进 + 行内列表 + 块列表），
不引入 pyyaml 依赖，格式说明见该文件头注释。

## 维护流程（改知识后必做）

```bash
# ckzl/ 新增/修改/删除知识文件后，三件按序重跑（均可独立重跑，秒级）：
python jcxt/js/build_fts_index.py      # 重建关键词库（删除旧 _kb_fts.db 全量重写）
python jcxt/js/build_tree_index.py     # 重建树索引（覆盖 _tree_index.json）
python jcxt/js/build_views.py          # 重建多维视图（覆盖 ../data/_views.json）

# 自检：
python jcxt/js/build_fts_index.py --verify    # 页数对账 + 8 个抽样查询
python jcxt/js/build_tree_index.py --verify   # 页表/树叶一致 + 抽样字段
python jcxt/js/build_views.py --verify        # 视图页 id 存在性 + 冷热分区 + hot_score
```

新增知识文件建议带 KB_INDEX 头（否则 title 退化为文件名、summary/keywords 为空，仍可被正文检索命中）：

```html
<!--
KB_INDEX: {
  "title": "...", "stage": "...", "tags": ["..."], "keywords": ["..."], "summary": "..."
}
-->
```

## 文件清单

| 文件 | 作用 |
|------|------|
| `query_kb.py` | 检索入口：keyword 检索 / `--tree` 导航 / `--page` 页阅读 / `--views`·`--view`·`--hot`·`--cold` 多维视图 |
| `build_fts_index.py` | FTS5 关键词库构建（直扫 ckzl，`_kb_fts.db` 唯一写目标） |
| `build_tree_index.py` | 树索引构建（`jcxt/data/_tree_index.json`） |
| `build_views.py` | 多维视图构建（读 `views.yaml` + 树索引 → `../data/_views.json`；`--verify` 自检） |
| `views.yaml` | 多维视图维度规则配置（外置可改；自绘极简格式，无 pyyaml 依赖） |
| `kb_common.py` | 共享底座：分词 / KB_INDEX / 章节切分 / 文件收集 |
| `_kb_fts.db` | FTS5 关键词库（可重建产物） |
| `../data/_tree_index.json` | 树索引（可重建产物） |
| `../data/_views.json` | 多维视图产物（可重建产物） |
| `../data/_kb_vector.db` | 【遗留】旧向量库，不再被任何脚本读取，可手动删除 |

已归档（`~/.fr_dev_kit/kit_archive/removed_kb_20260929/jcxt/js/`）：
`build_vector_index.py`、`vec_engine.py`、`query_kb_origin.py`、`config.toml.example`、
`ext/vec0.dll`，以及两份随向量组件一并归档的说明与回归记录文档（Embedding key 首次配置说明
——无向量版无需任何配置；hybrid 路回归证据记录 2026-09-14）。

## 已知边界

- 排除规则：`_` 开头文件/目录、`__pycache__`、`references_preview`、
  `ckzl/lc/fr10_deep_learn/docs/` 子树（与 fr11_knowledge 同源重复）不入库，
  规则集中在 `kb_common.EXCLUDE_DIRS / EXCLUDE_PREFIXES`。
- FTS5 需 SQLite 编译该模块（Python 官方 Windows 包默认带）；缺失时建库给出明确中文报错。
- 已知盲区（沿袭旧版）：`P-\d+` 零件编号与 com.fr.* 全限定类名请走
  `python ckzl/zsk/gczsk/query_kb.py` 结构化通道。
- AGENTS.md §4.1 中的 `--hybrid` / `--mock` 示例已过时（该文件不在本目录维护范围），
  一律以本 README 为准。
