<!--
KB_INDEX: {
  "title": "FR11 知识库索引（2289 篇离线文档 → 21 篇笔记）",
  "stage": "fr11-knowledge",
  "tags": ["FR11", "知识库", "索引", "离线文档"],
  "keywords": ["FR11", "FineReport 11", "知识库", "离线文档", "doc-view", "图表", "填报", "权限"],
  "summary": "FR11 离线文档（D:\\fr11_docs，2289 篇 doc-view HTML）解析重建的 21 篇知识笔记索引：15 分类 + 5 专题补充 + 本索引。"
}
-->

# FR11 知识库索引

> 数据源：`D:\fr11_docs\doc-view-{did}.html`（FineReport 11.0 离线帮助文档，gb2312 编码，共 **2289** 篇，全部成功解析，0 无法解析）
> 生成时间：2026-08-26
> 生成方式：Python 批量解析（标题 `<h1 id='doctitle'>` + 正文 `content_1 wordcut` div 深度追踪）→ 关键词打分自动分类（标题命中权重 5 / 正文命中权重 1）→ 逐篇提取核心概念（正文前 2-3 句原文）+ 关键 API/代码（正则提取）+ FR11 子版本要点（11.0.x 行）
> 纪律：全部 doc-view ID、标题、核心概念、API 均直接转录自离线 HTML 正文，未做任何推断补充；FR10 内容不混入。

---

> **R2 降级说明（2026-09-02）**：19 篇原文已降级为 16 主题 SKILL（`<主题>\SKILL.md`，frontmatter 触发词 + 核心结论），原文大表整文件移至各主题 `references\` 子目录，原根目录文件已移除。下表「笔记文件」列已更新为新入口路径。

> **R3 拆分说明（2026-09-29）**：references/ 下 8 个 >600 行 summary 大表（js_api 2263 / deploy_cluster 1450 /
> param_control 1440 / chart 1147 / mobile 915 / formula 878 / data_source 872 / frm_decision 621）已按条目标题主题
> 拆为「01_主题.md」编号分页系列（如 [chart图表/references/01_图表类型.md](chart图表/references/01_图表类型.md)；单页 ≤400 行，条目原样保留）+ `references/README.md` 导航；原 summary 文件保留为
> 导航页（速览 + 分页表 + 总结/全量 doc-view ID 清单），SKILL.md 及跨文档引用路径不断链。全量 1936 条 doc-view ID 经校验无丢失。

## 一、15 分类笔记

| # | 分类 | 笔记文件 | 文档数 | 主题范围 |
|---|------|----------|--------|----------|
| 1 | 图表 | `chart图表\SKILL.md` | 240 | 图表类型/图表样式/图表特效/扩展图表/ECharts/地图 |
| 2 | 数据源 | `data-source数据源\SKILL.md` | 179 | 数据连接/数据集/数据库/驱动管理/FineDB |
| 3 | 部署与集群 | `deploy-cluster部署集群\SKILL.md` | 315 | 部署/集群/服务器/Tomcat/Nginx/迁移/升级/运维 |
| 4 | 导出 | `export导出\SKILL.md` | 48 | Excel导出/PDF导出/Word导出/图片导出/CSV |
| 5 | 填报与提交 | `fill-submit填报提交\SKILL.md` | 103 | 填报/提交/智能提交/数据校验/Excel导入/暂存 |
| 6 | 公式与函数 | `formula公式函数\SKILL.md` | 164 | 公式/函数/层次坐标/运算符/自定义函数 |
| 7 | 决策报表 | `frm-decision决策报表\SKILL.md` | 123 | 决策报表/表单/自适应/组件/报表块 |
| 8 | 移动端 | `mobile移动端\SKILL.md` | 192 | 移动端/App/微信/钉钉/HTML5/OEM |
| 9 | 权限 | `permission权限\SKILL.md` | 92 | 权限/角色/用户/认证/单点登录/数据权限 |
| 10 | 参数与控件 | `param-control参数控件\SKILL.md` | 287 | 参数/控件/参数面板/下拉框/联动/查询 |
| 11 | 打印 | `print打印\SKILL.md` | 18 | 打印/分页预览/打印机/纸张/水印 |
| 12 | 二次开发与 JS API | `js-api二次开发\SKILL.md` | 436 | JS/API/插件/自定义/事件/前端 |
| 13 | 主题与样式 | `skin-theme主题样式\SKILL.md` | 58 | 主题/皮肤/配色/样式/外观 |
| 14 | 性能优化 | `performance性能优化\SKILL.md` | 31 | 性能/优化/内存/缓存/并发/大数据量 |
| 15 | 其他 | `other_summary.md` | 3 | FAQ/产品月报/未分类 |

**分类合计：2289 篇**（15 类互斥覆盖全部文档）

## 二、专题补充篇（5 篇）

| 笔记文件 | 内容 | 素材 |
|----------|------|------|
| `i18n国际化\SKILL.md` | FR11 i18n 接口整理：i18n() 公式 / FR.i18nText() / fr_locale / 语言配置 / ZHMONEY 等本地化公式 / 国际化插件 | 41 篇 i18n 命中文档 |
| `i18n国际化\references\fr11_i18n_api_optimization.md` | i18n 优化建议：方案选型、已知局限规避、排障、本地化公式使用 | 同上 |
| `i18n国际化\references\fr10_i18n_verification_report.md` | i18n 验证报告：已核实清单（含 doc-view ID）/ 未出现内容诚实标注 / 验证局限 | 同上 |
| `fvs-dashboard大屏\SKILL.md` | FVS 可视化看板专题（65 篇 FVS 文档聚合） | 标题含 FVS 的 65 篇 |
| `deploy-cluster部署集群\references\fr11_install_survey_report.md` | 安装调研：部署环境要求 / 集群要求 / FVS 插件要求 + 21 篇安装类文档条目 | 标题含 安装/环境准备 的 21 篇 |

注：FVS 与安装专题为跨分类聚合（同一文档在 15 分类中各有归属，此处按专题另列），因此 15 分类合计 2289 篇 = 全量去重覆盖；补充篇素材为子集复用。

## 三、笔记格式说明

每篇笔记统一格式：
- 文件头：数据源路径 + 文档数 + 生成时间
- 主题速览（标题关键词频次表）
- 文档条目：`### doc-view-{did}｜{标题}` → doc-view ID / 核心概念（正文前 2-3 句）/ 关键API/代码（如有）/ FR11版本要点（如有 11.0.x 变更）
- 总结：覆盖范围 + FR11 子版本提及统计 + 全部 doc-view ID 清单

## 四、数据与脚本（内部保留）

- 解析中间产物（2289 篇 all_docs.json 等）已于 2026-09-29 归档至用户目录 kit_archive（含官方文档内嵌的第三方示例 token，不入发布物），可用 `_parse_fr11.py` 从原始抓取重新生成
- 生成脚本：`_parse_fr11.py`（解析+分类）、`_gen_categories.py`（15 分类笔记）、`_gen_supplementary.py`（补充篇）

---

> Frontmatter 标准化指针（2026-09-14）：新增 `_standardize_frontmatter.py` —— `--check` 全量检查各主题 SKILL.md 标准 frontmatter（name/description/compatibility: FR11），`--apply --topics <主题1,主题2>` 就地补齐（改前备份 SKILL.md.bak_20260914）；试点结果与剩余 14 主题推广见 `_standardize_report.md`。
