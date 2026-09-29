# AGENTS.md — FR 报表模板开发工具包（comm 版）

> **本文件是本工具包的唯一入口。** 先读本文件，再按路由表按需读取细节文件。
> 全局铁律见 `ckzl/gf/铁律速查.md`（无头作业完整路由见 `ckzl/gf/FR_HEADLESS_GUIDE.md`）；
> 本机路径与环境见 `kfgj/env.md`。

---

## 0. 快速开始（首次使用三步）

1. **初始化用户环境**：`python kfgj/init_user_env.py` —— 检测 `%USERPROFILE%\.fr_dev_kit\`，
   不存在则引导创建（目录骨架 + FR/JDK 路径自动探测登记 + 项目经验/记忆文件夹）。
   用户私有数据（备份/快照/经验/记忆）都在该目录，不随套件分发。
2. **配环境（按需）**：读 `kfgj/env.md` 按需安装外部依赖（FineReport 10.0 设计器 / JDK8 /
   Python 3.11+；只做离线模板生成可不装 FR）。路径检测不对时直接编辑 `~/.fr_dev_kit/fr_env.toml`。
3. **自检**：`python kfgj/guard.py --selftest` —— 环境/断链/契约同源自检，全 PASS 即就绪。

> 检索说明：本包内置**本地无向量**知识检索（FTS5 关键词 + 树索引导航 + 页级阅读，PageIndex 式），
> **零 key、零配置、零网络**——不需要任何 API key，开箱即用。改知识后跑两个 build：
> `python jcxt/js/build_fts_index.py` + `python jcxt/js/build_tree_index.py`（详见 §4）。

---

## 1. 根目录结构（4 分类）

| 分类 | 内容 | 何时进入 |
|------|------|---------|
| `ckzl/` | 参考资料：开发流程知识(`lc/`)、工作流节点(`gzjd/`)、知识库(`zsk/`：工程知识库/帆软文档/错误案例/测试/需求/数据分析/前端接口/协同沟通)、FR Java 资料(`frapi/`)、规范与铁律(`gf/`)、画布骨架(`hbfa/`)、版本变更(`bb/`) | 查知识/规范/文档 |
| `kfgj/` | 开发工具：辅助脚本(`fzpy/`)、格式化脚本(`tygs/`)、fr-agent(`fr-agent/`)、DSL 编译器(`dsl/`)、运行期体检(`web_kit/`)、渲染预览(`xlyl/`)、插件工艺流水线(`plugin_pl/`)、评测(`evals/`)、闸门(`guard.py`+`EXEC_CONTRACT.md`)、断链检查(`check_refs.py`)、索引同步(`sync_kb_index.py`)、环境指南(`env.md`) | 干活时用工具 |
| `jcxt/` | 检索系统：无向量检索 CLI（`js/`：FTS5 关键词 + 树索引导航 + 页级阅读）、索引产物（`data/`：树索引/文件级索引） | 关键词检索/目录导航查知识 |
| `scwj/` | 输出产物：套件内演示/临时落地（**按项目组织的产物/契约/骨架脚本放 `%USERPROFILE%\.fr_dev_kit\projects\<项目名>\`，随人走不随套件走**） | 存放产出 |

> 检索三件套（全部可重建）：`jcxt/js/_kb_fts.db`（FTS5 关键词库）、`jcxt/data/_tree_index.json`（树索引）、`jcxt/data/_kb_index.yaml`（文件级索引）。改知识后跑 `python jcxt/js/build_fts_index.py` + `python jcxt/js/build_tree_index.py` 重建（详见 §4）。
> 用户私有数据（模板备份/结构快照/项目经验/主人 key）在 `%USERPROFILE%\.fr_dev_kit\`，**不随套件分发**（详见 `kfgj/env.md` §6）。

## 2. 接到任务后的标准操作流程（SOP）

```
STEP 0: 复杂度定档：单点问题直答不进流程；标准开发走本 SOP。
STEP 1: 判断任务类型
├─ 创建新报表      → §3 流程 A（有示例数据/Excel骨架 → §3 流程 F）
├─ 修改/格式化模板 → §3 流程 B
├─ 排查报错        → §3 流程 C
├─ 追踪 GUI 操作   → §3 流程 D
└─ 查 API/文档     → §3 流程 E
STEP 1.5: 开发类任务（创建/修改报表）可先走节点式工作流路由：
        ckzl/gzjd/00_工作流节点导航.md（判定题 Q1-Q7 → NODE-01~10 按需渐进加载，
        节点出口门禁配置见 ckzl/gzjd/node_gates.yaml；与 §3 流程 A/B 配合使用）
STEP 2: 用关键词检索定位章节（§4），命中后只读命中块，不要整文件读
STEP 2.5: 强制选型：生成模板→优先 FR Java API（fr-agent /exec）；格式化/样式→
        优先通配脚本（kfgj/tygs/，先查索引目录）；探查/校验→Python 脚本
STEP 3: 执行前查 ckzl/gf/铁律速查.md 全局铁律速查页（读速查即可；完整路由见 FR_HEADLESS_GUIDE.md）
STEP 4: 执行任务（每步用工具实际执行，不要只描述意图）：
        - 多组件布局坐标：python kfgj/fzpy/layout_grid.py -W <宽> -H <高> -n <组件数>
        - 改模板前先备份再取结构快照：python kfgj/fzpy/backup_template.py <模板> ；python kfgj/fzpy/template_snapshot.py [模板] --save
        - 写数据集 SQL 前先探表结构：python kfgj/fzpy/db_schema.py <schema.table>
        - 新数据集 SQL 必须过验证：python kfgj/fzpy/verify_sql.py -s "<SQL>" -p para=值
        - 新公式写入前用引擎验证：python kfgj/fr-agent/exec_js.py eval_formula.js（需 Designer 已注入，/exec 19000）
STEP 5: 验证
        - XML 合法性：python -c "import xml.etree.ElementTree as ET; ET.parse('file.cpt')"
        - 快速自检：python kfgj/fzpy/fr_check.py <cpt>  （--online 部署前全检）
        - 页面运行期体检：python kfgj/web_kit/probe.py <cpt>
STEP 6: 收尾闸门（不可跳过）：python kfgj/guard.py --task <create|modify|format|error> \
        --cpt <产物> [--attest G08,G09,G11] ；退出码非 0 = 任务未完成（契约见 kfgj/EXEC_CONTRACT.md）
```

## 3. 六种任务的标准读取路径

**流程 A：创建新报表**
```
0. 节点式入口（可选）：ckzl/gzjd/00_工作流节点导航.md → 判定题 Q1-Q7 渐进加载 NODE-01~10
1. ckzl/lc/01_环境与工具链.md           → 环境就绪
2. ckzl/zsk/xqfx/README.md              → 确定报表类型（查看/填报/导入）
3. ckzl/lc/02_数据建模.md               → 设计数据集 SQL + 级联参数
4. ckzl/lc/04_参数面板.md               → 控件/布局（铁律 F-G）
5. ckzl/lc/03_报表构建.md §2-§5         → 单元格/样式/行高（铁律 B-C）
6. 如需填报: ckzl/lc/05_填报与交互.md §9
7. 如需 CSS: ckzl/lc/06_Web呈现层.md §22
8. ckzl/zsk/csff/README.md              → 验证流程
```
骨架起步：可视化报表从 `ckzl/hbfa/`（60 套 cpt/frm 骨架+配置 JSON）选型。

**流程 B：修改/格式化已有模板**
```
1. 读 ckzl/lc/03 或 04（取决于改什么）
2. 读 kfgj/tygs/ 索引目录              → 找到对应格式化脚本（通配脚本优先，勿手写）
3. 执行修改 → fr_check 验证 → 预览
```

**流程 C：排查报错**
```
1. 提取错误关键词 → ckzl/zsk/tbcw/README.md 错误索引表
2. 没有 → python jcxt/js/query_kb.py "<错误关键词>" --mode keyword 关键词检索
3. 还没有 → ckzl/lc/08_技术选型与调试.md §16.2 常见问题表
4. GUI 相关 → kfgj/fr-agent/README.md（本地 18999 /status·/events 查设计器状态与事件流；19000 /exec 执行探查脚本）
```

**流程 D：追踪 GUI 操作**
```
1. 确认 FR Designer 已启动（经 designer.bat 注入启动）
2. kfgj/fr-agent/README.md             → 注入流程 + HTTP API
3. ckzl/lc/09_GUI操作追踪.md           → 事件 JSON 结构
4. python kfgj/fr-agent/inject.py → 用户操作 → python kfgj/fr-agent/trace3.py
```

**流程 E：查 API / 文档**
```
1. ckzl/frapi/doc/README.md            → 包名速查表
2. ckzl/lc/03_报表构建.md §2           → 验证过的正确包名
3. com.fr.* 零件/装配关系（结构化）→ python ckzl/zsk/gczsk/query_kb.py part <编号或关键字>
4. 帆软官方文档入口 → ckzl/zsk/frwd/资源索引.md
```

**流程 F：Excel 骨架正向生成（示例数据驱动）**
```
0. ckzl/lc/10_Excel骨架正向工艺.md      → 主文档（铁律：openpyxl 合并区先 merge 后样式，否则转换 NPE）
1. 契约 JSON（示例数据+参数+列定义）    → 模板 kfgj/excelgy/example_contract.json
2. python kfgj/excelgy/gen_skeleton.py <契约> -o %USERPROFILE%\.fr_dev_kit\projects\<项目名>\骨架.xlsx
3. python kfgj/fr-agent/exec_js.py kfgj/excelgy/excel2cpt.js  → 无头 xlsx→cpt（需设计器已注入）
4. 数据集+参数→替换示例行：走 NODE-02/03 + 流程 A 步骤 3-4
5. 图表管线：python kfgj/excelgy/extract_charts.py <xlsx> --canvas 1280x768 → hbfa 容器 JSON 装配
```

## 4. 知识检索（无向量：关键词 + 页导航 + 结构化查询）

### 4.1 关键词检索与页导航（无向量三件套，零 key 零配置）

```
# 建库/重建（改知识后按序重跑，秒级）：
python jcxt/js/build_fts_index.py                            # ① 关键词库 jcxt/js/_kb_fts.db（FTS5，按章节分块）
python jcxt/js/build_tree_index.py                           # ② 树索引 jcxt/data/_tree_index.json（目录树+全量页表）

# 检索入口：
python jcxt/js/query_kb.py "<问题>" --mode keyword --top 8   # ③ 关键词检索（默认即 keyword，BM25）
python jcxt/js/query_kb.py "<问题>" --full                   # 打印命中块全文
python jcxt/js/query_kb.py --tree [目录]                     # 目录树导航（如 --tree ckzl/lc，树叶带页 id 与行数）
python jcxt/js/query_kb.py --page <id|路径> [--full]         # 页级阅读：元数据+章节目录，--full 整页全文
```

- 典型工作流（导航式阅读）：**关键词命中拿页 id → `--tree` 看该页在目录中的位置 → `--page <id> --full` 整页精读**。命中后只读命中块，不要整文件读。
- 多维视图：`--views` 列全部视图 / `--view <中文名|key>`（如 `--view 运维维护`）/ `--hot` / `--cold` 冷热快捷；产物 `jcxt/data/_views.json` 由 `python jcxt/js/build_views.py` 按 `jcxt/js/views.yaml` 规则生成（场景/冷热/实战三维度 13 个视图，物理文件零移动，改 views.yaml 后重跑 build_views.py）。
- 维护口诀：**改知识后跑两个 build**（`build_fts_index.py` + `build_tree_index.py`）；两者均支持 `--verify` 自检。
- 已知盲区（沿袭旧版）：`P-\d+` 零件编号与 com.fr.* 全限定类名不入关键词索引，请走 §4.2 结构化通道。

### 4.2 工程知识库（结构化 5M1E 查询）

```
python ckzl/zsk/gczsk/query_kb.py part <编号或关键字>     # 零件本体
python ckzl/zsk/gczsk/query_kb.py methods <编号>          # 组件全部方法
python ckzl/zsk/gczsk/query_kb.py class <全限定类名>      # 按类查
```

### 4.3 文件级索引

`jcxt/data/_kb_index.yaml` 由 `python kfgj/sync_kb_index.py` 生成（KB_INDEX 头/H1/摘要），用于大模型定位"知识在哪个文件"。**新增/修改知识文件后**：先 `sync_kb_index.py`，再跑 `jcxt/js` 两个 build（`build_fts_index.py` + `build_tree_index.py`）。

## 5. 知识维护

- 本 comm 版不带云同步、不带自动自进化回写链路（个人版特有组件已移除）。
- 新增/修改知识：放到 `ckzl/` 对应子目录（带 KB_INDEX 头更佳），跑 §4.3 索引命令（sync + jcxt/js 两个 build），收尾跑 `python kfgj/guard.py --task kb --doc <文件>`。
- 版本变更记录写 `ckzl/bb/CHANGELOG.md`。

## 6. 与旧版的差异（个人版 → comm 版）

| 项 | 说明 |
|----|------|
| 云端 pgvector 共享库 | 已移除。comm 版检索全本地；2026-09-29 起向量路整体下线（见下两行） |
| 向量检索（2026-09-29） | 已移除，改 PageIndex 式树索引 + FTS5 关键词 + 页导航（`--tree`/`--page`），零 key 零配置零网络；向量组件（embedding 调用/vec0 插件/key 配置文档等）归档于 `~/.fr_dev_kit/kit_archive/removed_kb_20260929/` |
| 向量 key | 随向量检索一并移除，检索不再需要任何 key |
| 知识平台/无感审计（kb_platform） | 已移除；query_kb.py 的审计挂点自动静默降级，检索行为不变 |
| 自进化备注（evolve_kb）、云同步（migrate_to_pgvector/sync_hub） | 已移除 |
| 全局铁律 | FR_HEADLESS_GUIDE 铁律区拆分为独立速查页 `ckzl/gf/铁律速查.md`，GUIDE 回归纯路由（2026-09-29） |
| 根目录结构 | 收敛为 4 个分类目录 + 本文件；目录/文件名改为拼音/英文简写（开源裁剪与外部归档见 `ckzl/bb/外部依赖与归档声明.md`） |

## 7. 决策树（简版）

```
用户要做什么？
├─ 从零创建模板 → 流程 A（八步链）
├─ 有示例数据/Excel骨架要转cpt → 流程 F（Excel 骨架正向工艺）
├─ 修改/格式化已有模板 → 流程 B
├─ 排查报错 → 流程 C
├─ 追踪 GUI 操作 → 流程 D
├─ 查 API 包名/方法 → 流程 E
└─ 查帆软官方文档 → ckzl/zsk/frwd/资源索引.md
```

扩展决策分支（排序/打印/权限/图表/定时调度/联动/公式）见 `ckzl/gf/jcfz.md`；
专项主题路由（调度/邮件/集群/移动端等）见 `ckzl/gf/zxzt.md`；
行级数据权限三层防护见 `ckzl/gf/xjqx.md`；
交付验收断言与判级见 `ckzl/gf/yspj.md`；
布局样式统一规范见 `ckzl/gf/bjys.md`。

---

*comm 版 v3.1 开源适配 · 2026-09-28 · 基于个人版 v3.0 kernel 裁剪重构；2026-09-29 检索无向量改造（树索引+关键词+页导航）与知识库治理拆页*
