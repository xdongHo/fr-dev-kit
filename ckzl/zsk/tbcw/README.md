<!--
KB_INDEX: {
    "title": "ckzl/zsk/tbcw — 错误案例索引",
    "stage": "error-analysis",
    "tags": [
      "错误索引",
      "排错",
      "案例"
    ],
    "keywords": [
      "错误索引",
      "ORDER BY",
      "死循环",
      "Index 0 Size 0",
      "级联失败",
      "PageRWorkSheet",
      "AnalyReport"
    ],
    "summary": "填报开发错误案例索引表：现象→原因→解法，排错时先查此表再搜全库；2026-09-04 夜间批新增静默类专节（历史脚本教训 30 条，其中静默 14 条：XML/SQL 合法≠功能正确）；2026-09-15 夜间批次 批新增误报类专节（fr_check doc-299/template_param 误报面已修复 + 残留真实缺陷判读法）"
  }
-->

## 相关知识（夜间 R35 互链 2026-09-05）

- [夜间提炼_历史脚本教训_20260904](夜间提炼_历史脚本教训_20260904.md) — 索引↔正文：本 README 静默类专节（14 条）与显式条目表的案例正文（场景/报错/根因/正确做法/出处脚本）全在该文件。
- [dsl/schema.md](../../kfgj/dsl/schema.md) — 静默类防线：静默类专节「XML 合法 ≠ 功能正确」的第二道闸门思想，在生成侧的落点即该文 §6 guardrails 编译出口闸（G1-G5）。

# ckzl/zsk/tbcw

> 填报报表开发中遇到的错误案例与解决方案归档。
> 主指南只写正确做法——错误归档在这里。

← [返回主路由](../../gf/FR_HEADLESS_GUIDE.md)

---

## 错误索引

| 错误信息 | 可能原因 | 对应文档 |
|---------|---------|---------|
| `非常抱歉，您无法查看该页面，如需访问请联系管理员` | 平台目录权限未授权 / 模板加密 / license 异常 | 本目录新增案例卡（KV2-C-011 提案） |
| `11300003 单元格计算死循环` | 公式行偏移引入循环引用 | [填报报表开发错误分析.md](填报报表开发错误分析.md) |
| `Index: 0, Size: 0` | 导入模板 `<TableDataMap/>` 自闭合 | 主指南全局铁律 E |
| `ClassNotFoundException: LicenseContext` | 独立运行 FR API（无服务器容器） | 主指南全局铁律 K |
| 级联参数静默失败 | Parameter 自闭合 / SQL 未多行格式化 | 主指南全局铁律 D + J |
| 下拉框为空 | Dictionary class 错误 | [ckzl/lc/08_技术选型与调试.md](../../lc/08_技术选型与调试.md) §16.2 |
| 字体过大 | FRFont size 参数理解为 pt×8 | [ckzl/lc/08_技术选型与调试.md](../../lc/08_技术选型与调试.md) §16.2 |
| 行高不协调 | FU 换算值错误 | 主指南全局铁律 C |
| `PageRWorkSheet cannot be cast to AnalyReport` | 程序化生成 cpt 的非默认分页属性组合（CellPageAttr repeat/HR 退化/冻结盖扩展行）触发 view_content 数据分析管道强转分页结果失败 | [渲染报错-PageRWorkSheet强转AnalyReport.md](渲染报错-PageRWorkSheet强转AnalyReport.md) |
| `SyntaxError: Invalid or unexpected token`（打开页面即崩） | 事件 CDATA 的 JS 字符串字面量内有裸换行（程序化拼接 CSS 多段文本残留 0x0A/0x0D0A）→ 字符串未闭合；XML/fr_check 均不查 JS 语法 | [事件CDATA裸换行-SyntaxError.md](事件CDATA裸换行-SyntaxError.md) |
| `Maximum call stack size exceeded`（选组织控件即爆栈） | 编辑后事件互清构成调用环（legal↔bu↔region），FR setValue 触发对方 afteredit 链式点火递归爆栈；XML/语法检查均不查运行期递归 | [事件环递归-Maximum call stack size exceeded.md](事件环递归-Maximum call stack size exceeded.md) |
| `no function found: ISNUMBER`（公式函数不存在） | 高亮/条件公式使用引擎注册表外函数（ISNUMBER），语法合法但服务端逐格求值报错、高亮静默失效 | [公式函数不存在-no function found.md](公式函数不存在-no function found.md) |
| DSColumn 悬空数据集引用（列展开即空白） | 单元格绑定 dsName 在 TableDataMap 无定义，被列显隐遮蔽平时零报错，版本选中展开即整列空白 | [DSColumn悬空数据集引用.md](DSColumn悬空数据集引用.md) |
| 实体列名值域核对（名字比对编码） | 视图 entity=中文名 / entity_code=编码 错配致权限与层级过滤恒空：五步定位法与列名-值域核对表 | [附-实体列名值域核对方法论-entity vs entity_code.md](附-实体列名值域核对方法论-entity vs entity_code.md) |
| fr_check 误报（工具假阳性，非模板缺陷） | doc-299 把 SQL 宏内函数名当参数名（${LEN}/${IF} 大小写敏感）+ template_param 命中按钮类控件（FreeButton/FormSubmitButton/CustomButton、btn* 前缀）——两类已于 2026-09-15 修复（A39，同链 doc-1197 漂移 A54）；残留 exit=1 判读法与真实缺陷甄别见下方「误报类专节」 | 本 README「误报类专节」（2026-09-15） |

### ⚠️ 静默类专节：历史脚本教训批（2026-09-04 R6 夜间提炼，30 条）

> **本批最大特色：静默类——XML 合法 + SQL 合法 ≠ 功能正确。** 无报错、fr_check/ET.parse 全绿，
> 全靠「库上执行对拍 / 差值断言 / r0-r3 扫描」第二道闸门抓获——验证闭环不是可选项。
> 来源：[夜间提炼_历史脚本教训_20260904.md](夜间提炼_历史脚本教训_20260904.md)（`_runs/` 下 122 个历史 tmp_*.py 批量提炼；「条目 N」= 该文同名条目，含场景/报错原文/根因/正确做法/出处脚本）。

#### ⚠️ 静默类：XML/SQL 合法但功能错（14 条，无报错最危险）

| 错误信息 | 可能原因 | 对应文档 |
|---------|---------|---------|
| 无报错（静默）：条件属性"参数为空→列宽0"永不生效，隐藏列功能整体无效 | RelatedFormula 公式参数未包 `${}`（`LEN('para_ext1')` 只是字符串字面量恒≠0）；XML/fr_check 均不报 | 条目 2 |
| 无报错（静默）：obp_qs 列全 NULL（改错 CTE） | 同名片段 `NULL AS obp_qs` 在两个 CTE 重复出现，`re.sub(count=1)` 按文本顺序打中 month_data 而非 join_final | 条目 6 |
| 无报错（静默）：XML 合法但数据集运行期取数失败 | 整块替换 TableData 截掉尾部 `<Connection>`/`<Attributes>`；参见「Index: 0, Size: 0」条目（同族：TableData 块残缺） | 条目 8 |
| 无报错（静默）：级联/参数切换失效 | 数据集 Parameters 声明与 SQL `${name}` 集合不同步（漏声明/反向残留） | **同「级联参数静默失败」条目**（补根因：参数清单不同步）；条目 9 |
| 无报错（静默）：FR 宏在视图里失效 | DDL 写入链路 `\$` 反斜杠转义残留；`pg_get_viewdef` 回读断言无残留 | 条目 10 |
| 无报错（静默）：两表对账数值不齐 | 同名维度列取值格式不一致（'Apr' vs '9'、Actual/ACTUAL）；对账先 `SELECT DISTINCT` 盘点两边取值域 | 条目 14 |
| 无报错（静默）：ADJ 填报 join 不中（页面汇总差为 0） | 期间前导零文本等值比较 '03' vs '3'；join 键两侧 `::int` 归一 | 条目 16 |
| 无报错（静默）：同键重复填报页面汇总翻倍 | FR 提交是 INSERT 语义；读侧视图 `ROW_NUMBER()` 取最新 + 只统计 `delete_flag=1` | 条目 17 |
| 无报错（静默）：汇整视图缺科目（页面行缺失） | 源无数据 vs 过滤条件剔除两种成因混杂；先差集回源不带实体过滤查行数（三分排查法） | 条目 21 |
| 无报错（静默）：硬编码 32 叶子映射悄悄过期 | 科目树变化而写死清单无 diff 巡检机制 | 条目 22 |
| 无报错（静默）：科目映射 NULL/错挂中间汇总节点 | 只看直接父级；叶子判定用反向闭包，最近祖先沿 parent_of 多跳上爬（hop 上限防环） | 条目 23 |
| 无报错（静默）：换源后 entity 权限失效/钻取丢维度 | 新源合并口径 entity 置 ''；换源前先列下游消费的全部维度（权限列/钻取参数/展示维度） | 条目 24 |
| 无报错（静默）：r3 表头静态标签被批量覆盖成数据格 | 挂格脚本按列全行号替换、缺 `row<4` 行守卫；守卫要回写进脚本本身 | 条目 25 |
| 无报错（静默）：Var% 口径混用（比率减法当差值展示） | 复制示例区公式未同步口径；改口径须作用域白名单 + 旧公式残留归零确认 | 条目 28 |

#### 其余 16 条（显式报错 / 方案返工 / 正面范式）

| 错误信息 | 可能原因 | 对应文档 |
|---------|---------|---------|
| `XML ✗ ... Attribute redefined`（`<C c="58" r="3" c="58" r="3" s="4">>`） | 正则重建单元格标签，捕获组自带属性串和 `>`，拼出属性重复+`>>` 双料损坏；写盘后立即 `ET.parse` | 条目 1 |
| 显隐列 JS 方案被推翻（setTimeout 时机脆弱/reload 丢状态/catch 吞错） | 用前端 JS 模拟 FR 引擎能力；列显隐优先 FR 原生条件属性 ColumnWidthColumn，替换时先删旧 JS Listener | 条目 3 |
| 一次性脚本 NameError/IndexError 从未跑通 | `m.group(3)` 越界 + 函数定义在使用之后；一次性脚本也要先 1 格 dry-run 再全量 | 条目 4 |
| 库上执行 SQL 报语法错误 | SELECT 列表中间插行漏了上一行逗号；模板应写成 `old + "," + "\n" + new_line` | 条目 5 |
| 验证脚本 `NameError: name 'qs' is not defined` | 复制上一脚本改局部时变量改名不全（qs_i/qs）；小改后先空跑再当模板 | 条目 7 |
| f-string 里 `${para}` KeyError 或被替换成空 | Python f-string `{}` 转义与 FR 宏 `${}` 冲突；f-string 内一律双写 `${{para}}` | 条目 11 |
| `invalid input syntax for type numeric` | varchar 列空串直接 `::numeric`（''≠NULL）；先 `COALESCE(NULLIF(col,'')::numeric,0)` 再进表达式 | 条目 12 |
| SQL 语法错误（dec 被解析为 DECIMAL 关键字） | `dec` 月列/别名未加引号；列名 `"dec"`、别名改安全名（dec_total） | 条目 13 |
| 填报表结构一天内推翻回退（宽表→长表，视图重建两次） | 宽表(m01~m12) 不符 FR 逐格提交模型（键=年/实体/科目/期间 天然长表）；填报输入表按长表设计 | 条目 15 |
| 测试数据污染生产表口径 | 库上冒烟未隔离；`BEGIN→INSERT(create_by='test')→验传导→ROLLBACK→count 归零`，无法回滚则标记+清理+残留断言 | 条目 18 |
| YTD 列 eyeball 校验不可靠 | 派生列必须有独立机器判定：逐月 run_sum 对拍 ytd、`abs(diff)<1e-6` 逐行断言（维度含 NULL 用 `IS NOT DISTINCT FROM`） | 条目 19 |
| 权限验证漏判（越权可见/管理员看不到数） | 只测"代码能跑"不测"两态数据面"；从权限表取真实样本用户，代入 `${fine_username}` 各跑一遍比对行数/实体集 | 条目 20 |
| 重跑挂格重复注入/覆盖公式 | 无幂等守卫；三规则：有公式保留、有同款绑定跳过、行上无科目标识跳过并计数，结束汇报可审计 | 条目 26 |
| Excel 表头公式断链/#REF（打开文件求值错误） | 裁剪行不处理引用方；先 `data_only=True` 读缓存值换字面量，`=` 开头描述文本强制 `data_type='s'` | 条目 27 |
| 库上验证 SQL 报未定义参数 `${...}` | FR 条件宏 `${if(...)}` 不是数据库语法；按五步闭环：提 CDATA→静态替换→leftover 检查 `\$\{[^}]*\}` 非空即停→执行报行数→失败打印异常前 400 字 | 条目 29 |
| 74 科目 IN 清单在 ≥6 个脚本复制粘贴（漂移风险） | 常量无单一真源；落 `_runs/accounts74.json` 统一加载，与条目 22 diff 巡检配套（未然风险） | 条目 30 |

### 误报类专节：fr_check 两误报面已修复（2026-09-15 夜间批次/A39+A54，定性 correction）

> 定性: **correction**（工具规则与真实语料不符→修复闭环）。正文单一事实源=本节；修复证据：`_runs/night/campaign/w915/A39_scanfix/扫描器修复报告.md`、`_runs/night/campaign/w915/A54_doc1197/doc1197修复报告.md`（规则实现仅 kit 本体一处：`kfgj/fzpy/fr_check.py` Layer 1.5 按同目录加载 `fr_rules_doc.py`/`fr_rules_export.py`，campaign 下无副本）。

**修复前现象**：
1. **doc-299（dataset_conn）函数名假阳性**：`${if(LEN(p)==0,...)}` 的 `LEN` 被报"SQL 引用参数 ${LEN} 但未声明"（根因：`fr_rules_export.py _sql_refs` 停用词表大小写敏感）；
2. **template_param（doc-157）命中按钮类控件**：FreeButton/FormSubmitButton/CustomButton 及 btn_* 命名按钮被报"控件[X]无对应模板参数定义"（根因：`fr_rules_doc.py check_template_param` 只按名称黑名单，无类结构判定）；
3. **同链**：doc-1197 消息文本随 PYTHONHASHSEED 漂移（`check_date_range_validate` 控件名 set 迭代序不定；级别/命中集合不受影响，仅消息文本漂移）。

**已修复（2026-09-15）**：
- `fr_rules_export.py`：`_sql_refs` 停用词表改**大小写不敏感**并补 `concatenate` → `${LEN}` 类假阳性清零（回归：dataset_conn ERROR 34→32，−2 恰为假阳性；PYTHONHASHSEED=0 冻结段级 diff，其他规则**零新增段**）；
- `fr_rules_doc.py`：`check_template_param` 增**按钮类跳过**（类名判定优先 {FreeButton, FormSubmitButton, CustomButton} + btn* 前缀双保险；RadioButton 等可绑定控件不受影响）→ 断言段 **−19** 全为按钮类误报；
- `fr_rules_doc.py`（A54）：控件名集合构建后 `sorted()` → doc-1197 输出跨 seed **5/5 逐字节一致**，判定语义不变（8 样本语义快照 IDENTICAL）。

**残留判读法（当前 fr_check 报"未声明/无绑定"如何定性）**：
- 剩余 doc-299 多为 **SQL 侧真实未声明**（如 4009 P_Entity_CD/P_YM、4028 P_Biz_C1/P_Biz_M/P_Src）——先查 SQL 宏再疑工具；
- template_param 报"数据集级声明但无同名控件绑定"属 doc-157 三要素断言**设计行为**，非误报（漏控件=真缺陷）；
- `btn*` 前缀跳过是启发式：名为 btn_xxx 的**真实参数控件**会被漏检（假阴性方向，风险低，代码注释已声明）；
- 参数声明 4 形态知识见 `ckzl/lc/04_参数面板.md` §22.5（A39 纠偏：现行版校验器本就兼容 4 形态，历史报告的"形态盲区"归因不成立）。

**处置纪律**：修复类任务 fr_check **基线即 exit=1** 时，修后 exit=1 **不判失败**——逐条对照备份 diff：全部继承自原件=零回归，新增段=判责（已入主指南铁律 AG 三件套之③）。

---

## 文件清单

| 文件 | 内容 |
|------|------|
| `填报报表开发错误分析.md` | 填报报表全流程中的错误案例与修复记录 |
| `渲染报错-PageRWorkSheet强转AnalyReport.md` | 程序化生成 cpt 触发分页/数据分析渲染管道强转报错的字节码证据链与修复骨架 |
| `事件CDATA裸换行-SyntaxError.md` | 程序化写事件 JS 的裸换行致字符串未闭合：node --check 定位脚本、修复样板与预防三原则 |
| `事件环递归-Maximum call stack size exceeded.md` | 编辑后事件互清环致递归爆栈：clr 护栏样板、check_cpt_events.py 调用图环检测工具与预防门禁 |
| `公式函数不存在-no function found.md` | ISNUMBER 三层证据、NVL 替换法与公式函数白名单工具化 |
| `DSColumn悬空数据集引用.md` | 悬空引用遮蔽机制、408/213/2175 数字勘误与 check_cpt_integrity.py 三合一体检 |
| `附-实体列名值域核对方法论-entity vs entity_code.md` | 空白列五步定位法 + 列名-值域核对表（entity/entity_code 错配案例） |

## 查阅建议

1. 遇到错误 → 先查本目录的错误索引
2. 索引没有 → 查 [ckzl/lc/08_技术选型与调试.md](../../lc/08_技术选型与调试.md) §16.2 常见问题表
3. 还没有 → 查 [帆软 AI 助理](https://robot.fanruan.com/chat/finereport)
4. 最后 → 查服务器日志 `C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\logs\`

<!--
KB_INDEX: {
  "title": "排错三级分诊（B7 草稿·待主控收口）",
  "stage": "error-analysis",
  "tags": ["排错", "分诊", "triage", "流程C增补"],
  "keywords": ["L1显性", "L2中等", "L3复杂", "Triage Gate", "复杂度分级", "升级规则"],
  "summary": "排错流程按复杂度三级分诊：L1显性(索引直查)→L2中等(需探查)→L3复杂(全链路+渲染断言+长预算)；含分诊判据表(每级2-3判据)与升级/降级规则。出处 R65 T01 agent-workflows Triage Gate"
}
-->

# 排错三级分诊（流程 C 前置闸）

> **出处**：R65 T01《agent SOP/Runbook 框架》——agent-workflows 的 Triage Gate：bug-fix 开头强制分 Obvious/Moderate/Complex 三档走不同深度流程。本仓任务决策树只按**任务类型**路由，没有**复杂度**分级；本条补排错维度的复杂度闸。
> **一句话**：排错第一步不是搜，是分诊——30 秒判 L1/L2/L3，按档配流程深度与预算。禁止 L1 的错上 L3 的排场（烧上下文），更禁止 L3 的错按 L1 硬查（烧轮次）。

## 分诊判据表（命中任一即入档；多档命中取高）

| 级 | 判据 | 典型信号 |
|---|---|---|
| **L1 显性** | ① 报错完整含可搜关键词（异常类名/错误码/中文短语）② 现象稳定必现 ③ 疑似范围单一（单模板/单 SQL/单控件） | "ORDER BY"级联失效 / "Index 0 Size 0" / "死循环" / XML 解析失败 |
| **L2 中等** | ① 报错笼统或无报错但结果不对（数据/样式/不触发）② 需先探查现状才能定位（模板结构/表结构/参数链）③ 多配置点串联（数据集+参数+单元格任一链） | 静默错误（XML/SQL 合法≠功能正确）/ 级联不刷新 / 样式不生效 |
| **L3 复杂** | ① 跨服务/跨层（前端 JS↔引擎↔数据库↔服务器配置）② 间歇性/环境相关（偶现、换机表现不同）③ L2 流程两轮假设-验证未收敛，或修过 7 天内复发 | 页面偶发白屏 / 集群环境独有 / 日志无异常但行为异常 |

## 各级流程

```
L1 显性 → 索引直查（预算：≤2 次检索，≤15 分钟）
  ① ckzl/zsk/tbcw/README.md 错误索引表 → 命中即按「原因→解法」执行
  ② 未命中 → search_files 搜错误关键词（§1.2 流程 C 顺序不变）
  ③ 修复后必须过验证闭环（verify_sql / probe.py 对应项）
  ④ 两查不中 → 升 L2（记录一句升级原因）

L2 中等 → 探查定位（预算：≤3 轮「假设→验证」）
  ① 先探查后动手：template_snapshot.py 取现状 + db_schema.py 查表结构（禁止凭空假设模板内容）
  ② search_files 关键词 + jcxt/js query_kb.py 语义双路（关键词搜不到≠知识没有）
  ③ fr_check.py <cpt> 静态校验缩范围；每轮假设落一个可证伪的验证命令
  ④ 3 轮未收敛 → 升 L3；或降级待裁决（写明已排除项）

L3 复杂 → 全链路（预算：显式声明，分段时间盒）
  ① 全链路取证一次取齐：web_kit/probe.py --layout 运行期体检 + fr-agent 事件/日志
    + db_schema/verify_sql；证据先落 _runs/ 再分析
  ② 渲染断言：probe 截图+JS 异常清单对拍，先证「哪一层没问题」再攻可疑层
  ③ 时间盒：单段 ≤30 分钟，段间必须写一句「已排除 X」；超预算动作降级为
    待裁决（标记人工跟进），不硬上
  ④ 最后手段按序：ckzl/lc/08 §16.2 → 帆软 AI 助理 → 转接文档交接
```

## 升级/降级规则
- **只升不跳**：L1→L2→L3 逐级升；升级时把已做检索与排除项带过去（禁止 L3 从零重查）。
- **复发即升**：同一错误 7 天内二次出现，直接按上一级处理。
- **降级出口**：任一级判定为「知识缺口/需产品裁决/需环境变更」→ 停止消耗，将 gap 写入项目经验（~/.fr_dev_kit/experience/，个人版 evolve_kb 已移除） + 进待裁决清单。

---
> **挂点建议**：ckzl/zsk/tbcw/README.md「相关知识」段之后新增本同名小节（排错入口先经此表，与错误索引表天然衔接）；备选 ckzl/lc/08_技术选型与调试.md §16.2「常见问题」表之前作前置闸。二者取一，建议前者。
