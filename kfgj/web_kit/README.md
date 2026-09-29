<!--
KB_INDEX: {
  "title": "web_kit — WebKit 页面快速体检（FineReport 10 运行期）",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["probe", "runtime", "console", "URL", "pageerror", "error"],
  "summary": "# web_kit — WebKit 页面快速体检（FineReport 10 运行期）"
}
-->

# web_kit — WebKit 页面快速体检（FineReport 10 运行期）

> 定位：fr_check（落盘前静态）之后的"**运行期体检层**"。真开 headless chromium
> 打开报表页，抓 JS 异常 / console / FR 业务错误信号 / 加载卡死，出截图+报告。

## 常见问法：页面打不开/JS 报错/表格空白/控件叠在一起，怎么自动检查？

| 业务症状（口语） | probe 动作 |
|---|---|
| 页面打不开/被踢到登录页/加载转圈 | `python web_kit/probe.py <cpt绝对路径或URL>`：entry 探针报最终 URL/HTTP 状态/登录页跳转/加载>10s |
| JS 报错、console 一片红 | runtime：pageerror（附崩溃点行号）/console error 逐条/数据集错误弹窗/ErrorMarkWidget 计数 |
| 表格空白不渲染 | runtime.grid 主动 view_content 复核（FR10 静默吞渲染错误，被动探针抓不到，见下「关键实测发现」） |
| 必填校验不过 | widgets.validation 逐控件 getErrorMsg（warn）；控件重叠走 `--layout`（⚠占位未交付勿依赖） |
| 报出的告警像误报 | 已知噪声登记 `baseline.yaml`（global/页面级正则，必须带 reason）命中降 info；真问题→新检测项（见「迭代机制」） |

> 交付前体检 SOP：AGENTS.md STEP5——`python web_kit\probe.py <cpt>`，退出码 0 且 error=0 才交付；报告落 `_runs/webprobe/`（full_page.png/report.md/result.json）。

## 用法

```bash
PY="C:/Users/<你的用户名>/AppData/Local/Programs/Python/Python311/python.exe -X utf8"
$PY web_kit/probe.py "C:/Program Files/FineReport_10.0/webapps/webroot/WEB-INF/reportlets/示例报表工程/明细报表/示例实际表.cpt"
$PY web_kit/probe.py "http://localhost:8075/webroot/decision/view/report?viewlet=..."   # 直接给 URL 也行
```

| 参数 | 说明 |
|------|------|
| `<cpt绝对路径\|完整URL>` | cpt 路径自动推导 viewlet URL；URL 则原样导航 |
| `--params k=v ...` | 追加报表参数到 query |
| `--op write` | 查看方式，默认 write（填报态） |
| `--layout` / `--links` | 启用对应 check 模块（B 分支交付；不存在则提示跳过） |
| `--timeout 60` | 导航/加载遮罩探针超时（秒） |
| `--skip-login` | 不做自动登录（会话失效时直接报"被踢到登录页"） |

## 退出码

`0`=干净 / `2`=仅 warn / `1`=有 error（与 fr_check 对齐）

## 报告位置

`_runs/webprobe/<yyyyMMdd_HHmmss>_<页面名>/`
- `full_page.png` 全页截图（人工/审阅 agent 直接看图）
- 运行期报告 findings 表（check/level/message/evidence/hint；生成于 `_runs/webprobe/` 运行目录内）
- `result.json` 结构化结果（供后续 diff/批量矩阵消费）
- 登录态缓存：`_runs/webprobe/state.json`（storage_state，过期自动重登）

## URL 格式（2026-09-04 本机 FR10 实测）

probe 按候选链导航，404 自动降级，可用格式缓存到 `_runs/webprobe/url_format.json`：

| 格式 | 实测 |
|------|------|
| `/webroot/decision/view/report?viewlet=<相对路径>&op=write` | **可用（最终格式）**，cookie 登录态即可，无需 token |
| `/webroot/decision/view/ReportView?viewlet=/...` | 404（本机 FR10 不存在该路由） |
| `/WebReport/ReportServer?reportlet=...` | 404（旧格式，本机未部署） |

登录：JSONP 端点 `/webroot/decision/login/cross/domain?fine_username=..&fine_password=..&validity=-1`
（同 `kfgj/fzpy/fr_check.py` login_fr），经 `context.request` 调用使 cookie 直接落入浏览器 context。

## 检测项（当前骨架）

- **entry**：最终 URL / HTTP 状态 / 被踢到登录页 / 加载耗时 >10s
- **runtime**：pageerror 未捕获异常、console error/warning 逐条、requestfailed 计数、
  加载遮罩卡死（轮询至消失，超时=error）、数据集错误弹窗（"错误/Exception/数据集"）、
  ErrorMarkWidget 计数、`_g()`/contentPane 可用性、**runtime.grid**（网格未渲染时主动
  POST `op=fr_view&cmd=view_content&sessionID=..&reportIndex=0` 复核服务端渲染结果）
- 全部 DOM 探针在 `find_report_frame` 找到的报告 frame 与主 frame 上都执行

> ⚠️ **关键实测发现（2026-09-04）**：FR10 前端会**静默吞掉服务端渲染错误**——数据集
> SQL 报错时不弹窗、无 console.error、无 pageerror，只是网格不渲染（viewPane 不挂载）。
> 被动探针全抓不到，靠 runtime.grid 的主动 view_content 复核才能定性（带数据集名+
> SQL 错误位置的证据）。骨架自测 4 页全部栽在该类问题上且此前无任何告警。

## 误报治理（baseline.yaml）

已知噪声按正则登记（`global` 全局 / `pages.<页面名>` 页面级），命中的 console 类
finding 降为 info 并标注 "baseline 豁免"。每条必须写 reason。

## 迭代机制

**用户反馈页面展示问题 → 两步转化，不让同类问题二次人肉：**
1. 先判断是"已知噪声"还是"真问题"：真问题 → 新检测项（写进既有 checks 模块或
   新建 `checks/<主题>.py`，暴露 `run(ctx)` 即被自动发现）；固有噪声 → 登记进
   `baseline.yaml`（必须带 reason）。
2. 回归：对出问题的页面重跑 probe，确认新检测项能拦住、baseline 豁免生效。
   契约（新增 check 模块必读）：见 `kit_core.py` 模块头注释（ProbeCtx 字段、
   finding 结构、模块发现规则：`layout*`/`links*` 文件名分别由 `--layout`/`--links` 门控）。

## 文件清单

| 文件 | 职责 |
|------|------|
| `probe.py` | CLI 主入口：导航/登录/事件采集/模块发现/baseline/退出码/by-post 批量矩阵 |
| `render_assert.py` | **无头渲染对拍闸门（R28）**：纯 HTTP 零浏览器，cpt+params→服务端渲染→断言网格行列/关键词 |
| `kit_core.py` | 契约层：ProbeCtx / find_report_frame / 登录与登录态判断 |
| `checks/entry.py` | 入口层体检 |
| `checks/runtime.py` | 运行期体检（JS/console/FR 信号） |
| `report.py` | 报告落盘 + 控制台摘要 + 批量矩阵（页×检测项 + error 定性清单） |
| `baseline.yaml` | 误报豁免基线（console 与 requestfailed 类） |

## render_assert — 第三验证档位（R28, 2026-09-04 夜）

fr_check（静态）/ probe（浏览器）/ **render_assert（服务端渲染真相）**。配方源出 R13：
`GET view/report?viewlet=X&op=view` 建 ViewActor 分析会话（**默认无 op 的 page 会话渲染链死，禁用**）
→ `POST op=fr_view&cmd=view_content&sessionID=..` 取 JSON 信封网格 → 断言 tr/td/关键词。
支持 `--by-post`（`__parameters__` 双层编码 POST-first，复刻主表超链 byPost=true 语义）与
`--recipe B`（分页 `op=page_content&cmd=html&pn`）。dsl 验收链挂载示例：

```bash
$PY web_kit/render_assert.py "示例报表工程/明细报表/示例预算表-科目下钻.cpt" \
    --by-post --params p_code=PL1100 para_year=2026 para_month=SEP para_scn_py=ACTUAL \
    --expect-rows 5 --expect-text 科目下钻 --json-out _runs/night/render_assert.json
```

三 oracle 实测（2026-09-04 夜）：下钻页 byPost tr=9/td=54 PASS；示例实际表空参引擎错误
（11300001 ds_cr_lta）如实 FAIL 带原文；示例明细表B tr=2926/td=55522 PASS。dsl 编译产物
与线上页活渲染格数一致（9/54 vs 9/54）。退出码 0=PASS / 1=FAIL。

## 迭代日志

### v1.2（2026-09-04 夜间 L7+R28）
- **--by-post 翻案落地**：参数通道（`__parameters__` 双层编码 POST）本就正确，此前 rows=0 的根因是**入口选错**——POST-first 直打 `op=view` 建 ViewActor 分析会话（默认 page 会话渲染链死：parameterCommit 空转 + view_content ClassCast + 前端挂载被模板 JS 崩溃打断）。实测下钻页 tr=9/td=54、p_name 进入渲染标题
- 新增 `_mount_server_grid()`：页面 JS 挂载链被模板缺陷（pageerror 'reading form'）打断时，以会话 sid 取 view_content 已渲染网格注入 DOM 供 checks 测量（注入前口子打印 note）
- pageerror 采集补 `stack`，runtime.pageerror evidence 附首个 `at` 崩溃点（定位到 eval 片段行号）
- runtime.grid view_content 复核分类顺序修复：11300001/数据集配置错误优先判**真 error**（此前被 Oops 分支吞成"探针伪影"）；`PageRWorkSheet→AnalyReport` ClassCast 判已知伪影降 info
- `apply_baseline` 豁免范围扩展到 runtime.requestfailed；baseline.yaml 登记 `op=closesessionid` 卸载期心跳噪声
- 新增 `render_assert.py`（R28，见上节）

### v1.1（2026-09-04 下午，集成验收轮）
- 修复：`--op` 默认 write 会把查看型页面当填报打开（FR 抛 `PageRWorkSheet cannot be cast to AnalyReport`），默认改为不带 op（分析视图），仅 `--op write` 拼参数
- 新增：`widgets.validation` 探针——逐控件采集 `getErrorMsg()`，运行期校验未过（必填未填/值不在字典内）逐个点名（warn）
- 修复：`runtime.grid` view_content 复核判级分级——Oops/ClassCastException 类"渲染前置异常"降为 warn 并指向真因（必填拦截/初始化 JS 崩溃），避免探针伪影误报数据集错误
- 迭代：grid 空表格时无条件尝试 `parameterCommit()`（不再要求声明查询按钮），并逐 frame 尝试
- 编译器联动修复：语义层 `lock_js_template` 的 setTimeout 内 `this` 上下文丢失（存量下钻页 pageerror 根因），改 `__w` 捕获——编译产物实测 pageerror 消失
- 已知限制（下轮迭代）：①生产主表超链用 byPost=true 传参绕过控件必填校验，GET 注入模式无法完全复现（计划 --by-post 模式）；②主表 view 模式需填 bu/region/plant 必填项才首渲染，probe 对这类页面的 grid 结论按"校验拦截"解读


## 组件容器覆盖(2026-09-12 扩容, 对照 jsdoc http://dev.fanruan.com/jsdoc/)

新增检查模块(checks/ 自动发现):
- `comp_types.py` — 全类型组件枚举与分布: comptypes.distribution(类分布: 声明n/运行期n)/
  comptypes.missing_types(某类运行期 0 命中→warn)/comptypes.locate(getWidgetByName+DOM 双通道定位证明)。
  类型分类: 容器(Tab/卡片/手风琴/自适应/边框/网格/标题/绝对)/图表/表格块/编辑器/按钮/文本/树。
- `containers.py` — 容器感知检查: containers.inventory(容器/图表/表格块清单+渲染矩形)/
  containers.title(WTitleLayout 标题文本; chart* 图表标题容器空文本属正常降 info)/
  containers.tab(WTabLayout DOM tab 页数)/containers.chart(声明数 vs fr_api.chart_list 运行期数)/
  containers.elementcase(表格块渲染矩形/零尺寸)。

依赖变更: cpt_facts.py 对 .frm 目标新增 `_frm_widgets()` 全控件树遍历(此前参数面板正则只覆盖
面板区, body 的表格块/图表/嵌套布局容器不可见——对 66 控件以上的大屏 frm 只能看到个位数控件)。
frm 全树遍历同时标记 wrap=chart(子树含 Chart 类), 供 title 检查区分图表标题容器。

实测基线: AMP_工厂级.frm — 分类 7 类/9 控件(图表2/标题容器2/编辑器/按钮), chart_list 运行期 4 图全加载,
exit=0。FSV报表复刻 — 2 类/66 控件, exit=0。
