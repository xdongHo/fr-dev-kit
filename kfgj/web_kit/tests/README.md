<!--
KB_INDEX: {
  "title": "web_kit/tests — 坏页夹具与验收材料",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["cpt", "error", "check", "fr_check", "web_kit", "tests"],
  "summary": "> 配套 `web_kit/方案-WebKit页面快速体检-20260904.md` 验收标准 B：构造坏页逐一被拦。 > 这两个夹具都是**静态检查全绿、只有真开页面才炸**的页——这正是 webkit 体检相对 guardrails/f"
}
-->

# web_kit/tests — 坏页夹具与验收材料

> 配套 `web_kit/方案-WebKit页面快速体检-20260904.md` 验收标准 B：构造坏页逐一被拦。
> 这两个夹具都是**静态检查全绿、只有真开页面才炸**的页——这正是 webkit 体检相对 guardrails/fr_check 的价值证明。

## 一、夹具与预期行为

### bad_runtime_sql.cpt（运行期数据集错误页）
- 结构：标准 house 格式（WorkBook/Report/TableDataMap/ReportParameterAttr/ParameterUI），连接块照抄 `dsl/compile.py` 的 CONN 写法（`demo_connection`）。
- 毒点：数据集 `ds_bad` 查询不存在的表 `demo_dws.no_such_table_wktest`；单元格 A1 绑定 `ds_bad.v`；参数面板（para_wktest ComboBox+Label）结构合法。
- 静态表现：引用闭合（ds_bad 在 TableDataMap 有定义）、SQL 语法合法 → guardrails 与 fr_check 均拦不住。
  fr_check 实测（2026-09-04）：仅 **1 error（doc-157 template_param 已知族：para_wktest 未被 SQL $ 引用，预期内误报，非新族）** + 21 条常规 WARN，exit 1。
- 预期运行期表现：页面打开必报数据集错误弹窗/加载失败（表不存在）。

### bad_overlap.cpt（参数面板控件重叠页）
- 结构：其余全合法；数据集 `ds_ok` 为无害的 `SELECT 1 AS v`，页面无运行期错误——保证唯一的坏点就是布局。
- 毒点：ComboBox `para_region` 与 `para_subject` 的 BoundsAttr 完全同位（x=59 y=12 w=100 h=26）；标签 `lb_region` 与 `lb_subject` 同位（x=8 y=12 w=45 h=26）。
- 静态表现：fr_check 不查控件重叠 → 实测（2026-09-04）仅 **1 error（doc-157 已知族：para_region/para_subject 未被 SQL 引用）** + 22 条常规 WARN，无新族——正好证明重叠只有 webkit 能抓。
- 预期运行期表现：参数面板渲染时两两控件重叠（webkit widgets 检测的 boundingBox 两两相交应报 ERROR）。

## 二、部署 / 清理

- 部署目录：`C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets\示例报表工程\明细报表\`，命名加前缀 `WKTEST_`（WKTEST_bad_runtime_sql.cpt / WKTEST_bad_overlap.cpt）。
- `run_acceptance.py` 会自动部署并在 **finally 里无条件删除** 部署件；若脚本中断残留，请手动删除 `WKTEST_*.cpt`（**禁止覆盖同名人工文件**：部署前脚本查重，已存在即退出码 3 拒绝部署）。
- 手动部署（仅调试用）：copy 两个夹具到上述目录并加前缀；用完即删。

## 三、验收判定标准

运行（probe.py 集成后）：

```
C:/Users/<你的用户名>/AppData/Local/Programs/Python/Python311/python.exe -X utf8 web_kit/tests/run_acceptance.py
```

| 夹具 | 期待 finding | 通过判据（宽松匹配） |
|------|-------------|---------------------|
| WKTEST_bad_runtime_sql | error 级，check 含 `runtime` | error 级 finding 数 ≥1 且 check 含 runtime；或 message 命中 数据集/加载失败/Exception 类关键词 |
| WKTEST_bad_overlap | error 级，check 含 `widgets` | error 级 finding 的 message 含"重叠/overlap" 或 check 含 widgets/overlap |

- probe 结果读取顺序：stdout JSON（直接或内嵌）→ `_runs/webprobe/` 最新 `*.json` → stdout 关键词兜底。
- 退出码：**0**=两坏页都被抓（验收通过）；**1**=有坏页未被抓（工具缺陷或 FR 服务器未启动——若 findings 全是 entry 类，先确认 localhost:8075 已启动）；**3**=部署目标已存在同名文件（环境问题）；**4**=probe.py 未就绪（打印"等待核心分支集成后重跑"）。

## 四、未来新增检测项的验收套路

新检测 = 新夹具 + 一行断言，三步：

1. **造夹具**：在 `tests/` 新增 `bad_<检测项>.cpt`，要求**静态全绿、只在目标维度上坏**（其余结构与 house 格式一致，避免误伤其他检测的断言）。
2. **登记断言**：在 `run_acceptance.py` 的 `FIXTURES` 表加一行 `(文件名, check维度, 判定规则人话版)`；`judge()` 里按需补一个 `hit_<维度>()` 宽松匹配（check 名优先，message 关键词兜底）。
3. **同步文档**：本 README 第一节加预期行为、第三节判定表加一行；夹具必须能被 ET.parse 通过且 fr_check 无新错误族（已知噪声族在 README 登记）。
