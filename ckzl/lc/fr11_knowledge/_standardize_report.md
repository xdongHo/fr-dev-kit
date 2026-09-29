<!--
KB_INDEX: {
  "title": "fr11_knowledge SKILL.md frontmatter 标准化报告",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["compatibility", "fr11", "name", "ADD", "chart", "i18n"],
  "summary": "# fr11_knowledge SKILL.md frontmatter 标准化报告"
}
-->

# fr11_knowledge SKILL.md frontmatter 标准化报告

- 日期：2026-09-14（试点：chart图表 + i18n国际化；推广：其余 14 主题同日完成，**16/16 已补齐（2026-09-14 推广完成）**）
- 执行者：Subagent 08（fr-kb-opt 知识库优化）
- 审计锚点：P2-6（07 号文件）

---

## 一、概要

| 项 | 结果 |
|---|---|
| 标准字段 | `name` / `description` / `compatibility: FR11` |
| 试点结果 | chart图表、i18n国际化 补齐 `compatibility: FR11`，原字段全部保留，结构校验 8/8 PASS ×2，幂等复跑 NOCHANGE |
| 全量现状 | **16/16 已补齐（2026-09-14 推广完成）**：16 主题 frontmatter 均含 name/description/`compatibility: FR11`，`--check` all-standard=Y、EXIT_CODE=0 |
| KB_INDEX | 16/16 主题均被 README.md（头部 KB_INDEX 注释）收录 |
| 唯一遗留告警 | **16/16 已补齐（2026-09-14 推广完成）**，compatibility 无遗留；仅剩 name=`fr11-*` 风格 ≠ 目录名 WARN（非达标项、不影响退出码），按「就地增强、保留原字段」原则仅 WARN 不改写 |

## 二、工具说明

- 路径：`ckzl/lc\fr11_knowledge\_standardize_frontmatter.py`（UTF-8 无 BOM，`py_compile` 通过）
- `--check`：全量只读检查，输出 16 主题状态清单（fm 有无 / 缺失字段 / name 是否等于目录名 / KB_INDEX 收录），退出码 **0=全部达标 / 1=有缺失**；name 不一致仅 WARN 不计入失败。
- `--apply --topics <主题1,主题2>`：对指定主题补齐缺失标准字段；改前备份 `SKILL.md.bak_20260914`（已存在则保留首次原始备份）；幂等（字段已齐 NOCHANGE 不写盘）。
- 增强规则：已有 frontmatter → 仅追加缺失标准字段，原字段与取值一律保留；无 frontmatter → 顶部插入标准块。description 文案内嵌于脚本 `DESCRIPTIONS` 字典（人工撰写：触发场景祈使句 + 关键词 + 何时不用边界），不自动生成。
- 写出统一 UTF-8 无 BOM，行尾保持原文件风格（CRLF）；不进解析中间产物目录（已归档）、不删文件、不碰 git。

## 三、试点前后对比

### chart图表（变更加 1 行）

变更前（frontmatter 3 行）：

```yaml
---
name: fr11-chart
description: FR11 图表/chart 开发时使用：选择图表类型、配置图表样式（标题/图例/标签/坐标轴）、地图钻取、ECharts/扩展图表、图表特效与超级链接联动时查阅。
keywords: [echarts, 扩展图表, 图表刷新, 图表类型, 图表样式, 地图钻取]
---
```

变更后（追加第 4 行，其余原样）：

```yaml
---
name: fr11-chart
description: FR11 图表/chart 开发时使用：选择图表类型、配置图表样式（标题/图例/标签/坐标轴）、地图钻取、ECharts/扩展图表、图表特效与超级链接联动时查阅。
keywords: [echarts, 扩展图表, 图表刷新, 图表类型, 图表样式, 地图钻取]
compatibility: FR11
---
```

### i18n国际化（变更加 1 行）

变更前（frontmatter 2 行）：`name: fr11-i18n` + 原有 description（何时使用/触发词长句）。
变更后：末尾追加 `compatibility: FR11`，name 与 description 原样保留。

字段差异小结：两试点均满足「保留原字段 + 只补缺失标准字段」；name 保留 `fr11-chart` / `fr11-i18n`（见风险 R1）。

## 四、全量 --check 结果

### 试点前（16 主题均缺 compatibility）

```
topic                      fm   missing          name==dir     kb   status
chart图表                    Y    compatibility    N(fr11-chart) Y    ADD[compatibility]
data-source数据源             Y    compatibility    N(fr11-data-source) Y    ADD[compatibility]
deploy-cluster部署集群         Y    compatibility    N(fr11-deploy-cluster) Y    ADD[compatibility]
export导出                   Y    compatibility    N(fr11-export) Y    ADD[compatibility]
fill-submit填报提交            Y    compatibility    N(fr11-fill-submit) Y    ADD[compatibility]
formula公式函数               Y    compatibility    N(fr11-formula) Y    ADD[compatibility]
frm-decision决策报表          Y    compatibility    N(fr11-frm-decision) Y    ADD[compatibility]
fvs-dashboard大屏            Y    compatibility    N(fr11-fvs)  Y    ADD[compatibility]
i18n国际化                   Y    compatibility    N(fr11-i18n) Y    ADD[compatibility]
js-api二次开发                Y    compatibility    N(fr11-js-api) Y    ADD[compatibility]
mobile移动端                 Y    compatibility    N(fr11-mobile) Y    ADD[compatibility]
param-control参数控件         Y    compatibility    N(fr11-param-control) Y    ADD[compatibility]
performance性能优化           Y    compatibility    N(fr11-performance) Y    ADD[compatibility]
permission权限               Y    compatibility    N(fr11-permission) Y    ADD[compatibility]
print打印                    Y    compatibility    N(fr11-print) Y    ADD[compatibility]
skin-theme主题样式            Y    compatibility    N(fr11-skin-theme) Y    ADD[compatibility]
summary: 16 topics | all-standard=N | name!=dir WARN: 16 | EXIT_CODE=1
```

### 试点后（2 OK / 14 待补）

```
chart图表     Y  -  OK            i18n国际化   Y  -  OK
其余 14 主题  Y  compatibility  ADD[compatibility]（清单同上）
summary: 16 topics | all-standard=N | name!=dir WARN: 16 | EXIT_CODE=1
```

KB_INDEX：两轮检查 16/16 主题均在 README.md 中被引用（kb=Y）。

## 五、剩余 14 主题推广步骤

1. **第 1 批（7 主题）**：`python _standardize_frontmatter.py --apply --topics data-source数据源,deploy-cluster部署集群,export导出,fill-submit填报提交,formula公式函数,frm-decision决策报表,fvs-dashboard大屏`
2. **第 2 批（7 主题）**：`python _standardize_frontmatter.py --apply --topics js-api二次开发,mobile移动端,param-control参数控件,performance性能优化,permission权限,print打印,skin-theme主题样式`
3. **每批后复核**：`python _standardize_frontmatter.py --check` 确认对应行变 `OK`、各主题生成 `.bak_20260914`；按第四节同法做 frontmatter 结构校验抽查。
4. **收尾确认**：`--check` 输出 `all-standard=Y`、`EXIT_CODE=0`；16 个 `.bak_20260914` 留存至确认无需回滚。
5. **可选终审**：如需落实「name=目录名」最佳实践（§2.4），因涉及引用变更，须另行评审后人工统一改写（本工具刻意不改写 name）；git 提交由主控/人工执行。

## 六、风险说明

- **R1 name≠目录名（已知告警，未改写）**：16 主题 name 为 `fr11-*` 短横线风格。按任务「就地增强、保留原字段」与最小 diff 原则保留原值，`--check` 中 WARN 计数呈现，避免破坏 kit 内可能存在的按 name 的引用。
- **R2 description 兜底文案**：`DESCRIPTIONS` 字典含全部 16 主题人工文案；两试点按正文核对（但实测两试点已有 description 未触发兜底），其余 14 主题文案基于 README「主题范围」列编写、未经正文逐字核对。因 16 主题均已有 description，兜底预计不触发；若未来新增主题需引用该字典，建议先人工过目微调。
- **R3 备份策略**：`.bak_20260914` 仅首次创建（保留真正的原始版），重复 apply 幂等不覆盖备份、不改已达标文件。
- **R4 解析依赖**：环境无 pyyaml，验证采用结构检查（首行 `---`、次行起键值、`---` 收尾）；描述文案已规避 ASCII `": "` 与 `" #"` 等 YAML 特殊序列，安装 pyyaml 后可无损 `yaml.safe_load`。
- **R5 影响面**：仅试点 2 个 SKILL.md 各 +1 行 `compatibility: FR11`；README 主体未动（仅末尾 +3 行指针）；未删除/移动任何文件；未执行任何 git 写操作。

## 七、验证记录（命令与结果）

```
> python -m py_compile _standardize_frontmatter.py
PYCOMPILE_EXIT=0

> python _standardize_frontmatter.py --check            # 试点前
16 topics | all-standard=N | WARN 16 | CHECK_EXIT=1

> python _standardize_frontmatter.py --apply --topics chart图表,i18n国际化
[UPDATED] chart图表  | 追加字段: compatibility | 已备份原始版: SKILL.md.bak_20260914
[UPDATED] i18n国际化 | 追加字段: compatibility | 已备份原始版: SKILL.md.bak_20260914
APPLY_EXIT=0

> 结构校验（validate：无 BOM / utf-8 严格解码 / 首行 --- / --- 收尾 / name、description 存在 / compatibility=FR11 / 备份存在）
chart图表 8/8 PASS；i18n国际化 8/8 PASS；VALIDATE=PASS

> python _standardize_frontmatter.py --apply --topics chart图表,i18n国际化   # 幂等复跑
[NOCHANGE] ×2，IDEMPOTENT_EXIT=0

> python _standardize_frontmatter.py --check            # 试点后
2 OK / 14 ADD[compatibility] | CHECK_EXIT=1
```

- 推广执行记录（2026-09-14，Subagent 06 / fr11推广，8 路并行·按文件分槽·独占 ckzl/lc\fr11_knowledge\）：`python _standardize_frontmatter.py --apply --topics <其余14主题>` 一次批量完成（applied: 14 updated / 0 nochange / 0 skip/error，各生成 SKILL.md.bak_20260914）；复跑 `--check` 16/16 OK、all-standard=Y、EXIT_CODE=0（name=fr11-* 风格 WARN 16 条仅告警不计失败）；frontmatter 结构抽查与全量校验 16/16 PASS（无 BOM、utf-8 严格解码、--- 配对、name/description/compatibility=FR11 在位）。
