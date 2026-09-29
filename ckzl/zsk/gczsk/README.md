---
keywords: [com.fr, 类名, 方法签名, API 查询, part, class, 零件表, 方法坑]
---
<!--
KB_INDEX: {
  "title": "ckzl/zsk/gczsk（SQLite）— 人机料法环5M1E 零件表/BOM表/工艺表",
  "stage": "report-building",
  "tags": ["ckzl/zsk/gczsk", "SQLite", "5M1E", "人机料法环", "物料管理", "工艺管理", "JavaAPI"],
  "keywords": ["api_kb", "parts", "bom", "routing", "materials", "machines", "personnel", "environments", "工艺路线", "物料清单"],
  "summary": "人机料法环(5M1E)ckzl/zsk/gczsk:personnel人(2)/materials料(43)/machines机(52)/environments环(11)/parts零件(14588)/bom关系(3589)/routing工艺(13条路线75道工序已机械化26道)。查询用 query_kb.py"
}
-->

# ckzl/zsk/gczsk（SQLite）

> 用**人机料法环（5M1E）工程管理范式**归纳 FR 报表开发知识（用户 2026-08-11 定稿，2026-08-12 复盘扩容）。
>
> | 要素 | 含义 | 表 | 数量 |
> |------|------|-----|------|
> | **人** Man | 你（需求方/设计方）+ 我（开发执行） | `personnel` | 2 |
> | **机** Machine | 脚本 / 工具（自动化操作） | `machines` | 52 |
> | **料** Material | 资料（文档/模板/示例/数据） | `materials` | 43 |
> | **法** Method | 工艺 / 需求 / 方法 | `routing` + `parts` + `bom` | 13 路线 75 工序 |
> | **环** Environment | 开发环境（FR/agent/JDK/连接） | `environments` | 11 |
>
> **机械化原则**：工艺（法）中刻板重复的工序 → 挂对应脚本（机）→ 你我操作时省人力。
> 当前 13 条工艺路线 75 道工序中 **26 道已机械化**（挂 MC 脚本编号，机械化率 35%）。
>
> **2026-08-12 复盘扩容**：机表补登 30+ 真实脚本（format_sql/verify_sql/template_snapshot/db_schema/layout_grid/fix_* 系/官方文档沉淀工具），
> 工艺新增 R-010 SQL 格式化与验证、R-011 API 用法调研、R-012 错误排查标准流程。

## 文件

| 文件 | 说明 |
|------|------|
| `api_kb.sqlite` | SQLite 数据库（9 张表：8 业务表 + echarts_fr_map） |
| `build_kb.py` | 建库脚本（parts/bom/routing 三表；`--rebuild` 重建） |
| `build_5m1e.py` | 扩展脚本（personnel/materials/machines/environments + 工艺挂脚本；先跑 build_kb.py） |
| `query_kb.py` | 查询工具 |
| `build_template_bom.py` | 模板构件 BOM 建库脚本（数据源 campaign/rebuild 产物 ET 解析；`--every 8` 抽样 / `--all` 全量） |
| `template_bom.sqlite` | 模板域装配图（2.9MB：节点 8371/关系 13768，抽样 615 件 78 项目族） |
| `query_template_bom.py` | 模板 BOM 查询 CLI：node/edge/assemble/usage/highfreq/dangling/stats；dangling=悬挂引用检测（FS 408 事故形态，复现验证 _runs/night/R67_m2/verify_dangling_408.py） |

## 表结构

### parts 零件表（法：API 方法物料）— 14588 条
> 反向指路（DIG1 2026-09-12）：若你带着 P 编号/类名问法从jcxt/js query_kb.py 空手而回——那是向量索引结构盲区（零件行不入向量库），本目录 `python query_kb.py part|class|methods <编号/类名>` 才是正解（实测 P-5119→NormalTableDataDefinition、class com.fr.general.FRFont→P-9458 均秒回）。
FR Java API 接口方法：part_no / name / class_name / signature / category（FORM_BUILD|CPT_BUILD|CHART|DATASET|PARAM|STYLE|CONTAINER|WIDGET|EVENT|IO|UTIL）/ description / pitfalls / verified（1=实测）

### bom 装配关系表（法：方法间关系）— 3589 条
parent → child，rel_type：COMPOSE（组成）/ REQUIRE（必须前置）/ PREPARE（后续准备）/ METHOD_OF（组件→方法归属 3557 条，自动生成）

### routing 工艺表（法：工艺路线）— 13 路线 75 工序
routing_no / step_no / work_center（JAVA_API|PYTHON_ATTR|VALIDATE|DESIGNER）/ part_id / op_desc / output / **machine（挂脚本编号，机械化标记）**

### personnel 人员表（人）— 2 条
U-001 用户（需求方/设计方）/ A-001 Hermes AI（开发执行方）

### materials 物料表（料）— 43 条
mat_no / type（DOC|TEMPLATE|EXAMPLE|DATA）/ category / path / description / status / **usage_count（WMS 累计使用次数）** / **used_projects（使用过的项目清单）**

### material_usage 使用台账（料,WMS）— 34 条
project（示例驾驶舱/示例报表工程/基础工具链/新项目）/ mat_no / role（PROJECT=项目直接使用 / WIP=半成品(项目内模板/生成产物)使用）/ count / note

> **WMS 语义**：materials.usage_count 是聚合列（= SUM(material_usage.count)），used_projects 是去重项目清单。
> 源是 build_5m1e.py 的 USAGE 列表（先清空再插，幂等），新增项目使用记录 → 往 USAGE 加行 → 重跑 build_5m1e.py。
> **会话裁剪**：开发某项目前 `query_kb.py usage <项目名>` 只加载该项目物料，避免无关物料进上下文。

### machines 机器表（机）— 52 条
m_no / type（PYTHON|JAVA|BATCH|JAR）/ function / usage / related_routing（对应工艺）
核心：MC-001 fr-agent.jar、MC-015 fr_exec.py、MC-014 fr_check.py、MC-011 fmt_copa.py、MC-007 query_kb.py

> **常见问法**：machine 是什么/有哪些脚本工具/机（MC-xxx）清单怎么查？→ `python query_kb.py machine [关键字]`（本表 machines，按脚本名/功能模糊匹配）；「有没有现成脚本先查机」纪律见 AGENTS.md §1.8

### environments 环境表（环）— 11 条
FR 设计器 10.0.19 / fr-agent 18999:19000 / JDK8 / Win11 150%缩放 / demo_connection 连接 / fr_dev_kit 仓库 / jcxt/js embedding（待配置）

### 常见问法：P-5119 这类 P-编号是什么？拿着零件/组件编号怎么查？

P-xxxx 是ckzl/zsk/gczsk parts 零件表的**零件编号**（part_no，14588 条 FR Java API 方法零件）。别名：P-编号/零件编号/组件编号怎么查/这个编号是什么意思。拿到编号三连：

| 想知道 | 命令 |
|---|---|
| 这个编号是什么零件（名称/签名/坑） | `python ckzl/zsk/gczsk/query_kb.py part P-5119` |
| 它装进哪个组件（装配关系/方法归属） | `python ckzl/zsk/gczsk/query_kb.py bom P-5119` |
| 它所在组件的全部方法 | `python ckzl/zsk/gczsk/query_kb.py methods P-5119` |

> 编号查询走**结构化子命令**（上表），jcxt/js对裸编号词面弱——这是编号类查询的正解入口。

## 查询用法

```powershell
python query_kb.py part ChartEditor      # 查 API 零件（含坑）
python query_kb.py part P-0027           # 按 P-编号直查零件（编号型查询勿走向量/hybrid——零特判必落近音噪音）
python query_kb.py part "getCellValue"        # 按类名/方法名关键词查 com.fr API（「com.fr 类名 方法 查询」走这里）
python query_kb.py class WParameterLayout
python query_kb.py cat CHART
python query_kb.py bom P-0039            # 查 Form 装配关系（含方法归属折叠）
python query_kb.py methods P-0054       # 查组件全部方法（新）
python query_kb.py route [R-002]         # 工艺路线列表/详情（含机械化标记）
python query_kb.py mat [骨架]            # 查物料（料）
python query_kb.py machine [fmt]         # 查脚本工具（机）
python query_kb.py env [FR]              # 查环境（环）
python query_kb.py person                # 查人员（人）
python query_kb.py 5m1e                  # 人机料法环总览（含机械化覆盖率）
python query_kb.py echarts [bar]        # ECharts->FR 映射查询（还原 demo 输入接口）
python query_kb.py semantic [问题] [--mock]  # 语义检索零件/物料（向量坐标，需先 embed_parts.py）
```

## 维护规则

- **新增 API 方法** → `build_kb.py` PARTS 加行 → `python build_kb.py --rebuild`
- **新增物料/机/环/人** → `build_5m1e.py` 对应列表加行 → `python build_5m1e.py`
- **工序机械化** → 工艺表 routing 的 machine 列挂脚本编号（MC-xxx），该工序即可脚本代劳
- 数据库是构建产物，两个 build 脚本是源（保持可重建）









## P1-7 增补（2026-09-14）: 脚本工具 manifest

- `python ckzl/zsk/gczsk/build_manifest.py` 生成/刷新 `script_manifest.json`（工具脚本 113 个：名称/相对路径/用途一句话/sha256[:16]/mtime/argparse 检出）。
- `python ckzl/zsk/gczsk/build_manifest.py --check` 漂移检测：新增/删除/哈希变化 → 退出码 1（可挂周五体检半自动闸）。
- 扫描范围：仓库根顶层 *.py（不递归）+ kfgj/fzpy/ ckzl/zsk/gczsk/ jcxt/js/ dsl/ evals/（递归）；资料型目录与 _runs/ 不扫。
- 定位：对齐 MCP Registry 思路（07-审计启示 P1-7）——kernel 只驻"精简工具目录"、脚本正文按需加载的第一步；后续可叠加描述版本化+哈希钉住（防 rug-pull）。
