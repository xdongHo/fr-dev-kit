<!--
KB_INDEX: {
    "title": "事件环递归致Maximum call stack size exceeded分析",
    "stage": "error-analysis",
    "tags": [
      "错误案例",
      "🔥新沉淀",
      "事件JS",
      "参数联动",
      "递归爆栈"
    ],
    "keywords": [
      "Maximum call stack size exceeded",
      "RangeError",
      "setValue",
      "afteredit",
      "编辑后事件",
      "getWidgetByName",
      "互清环",
      "护栏",
      "先判值再清",
      "check_cpt_events.py",
      "fr_check盲区",
      "调用图环检测"
    ],
    "summary": "FR 的 widget.setValue() 会触发目标控件自身的编辑后(afteredit)事件；多控件互清构成环(para_legal↔para_bu↔para_region)时链式点火直至爆栈 RangeError: Maximum call stack size exceeded；node --check 只查语法、fr_check 无事件调用图规则，两道校验都检不出；含堆栈帧特征、静态调用图环检测工具(check_cpt_events.py)、'先判值再清'护栏样板与 fr_check 待补规则建议(2026-09-06 示例实际表/预算 实战)"
  }
-->

# 事件环递归致 Maximum call stack size exceeded 分析

> 实战来源：2026-09-06 示例报表工程/明细报表 示例实际表.cpt / 示例预算表.cpt 参数面板联动改造，para_region 编辑后事件新增"清 para_legal"边，与既有的 legal↔bu 互清闭合成三角环，线上编辑任一控件即爆栈。
> 定位工具源起 `kfgj/fzpy\check_cpt_events.py`（2026-09-07 事件环静态检测工具，本文 §5 有用法）。

---

## 1. 现象

线上打开填报/参数页面**不报错**，一旦在任一联动控件（legal/bu/region 下拉）中编辑选择，浏览器控制台立即抛：

```
Uncaught RangeError: Maximum call stack size exceeded
```

页面随之卡死/失控（控件值异常跳变、查询无响应），**必须强刷**。而落盘前的常规校验全绿：`ET.parse` XML 合法、`node --check` 事件 JS 语法全过、`fr_check.py` 通过——**"XML 合法 + JS 语法合法 + fr_check 通过"但"上线编辑即崩"**（三道校验都不做事件间调用关系分析）。

浏览器控制台堆栈摘录（典型形态，非逐字存档）——关键特征是**同一组帧循环重复**：

```
Uncaught RangeError: Maximum call stack size exceeded
    at setValue (finereport.js:…)
    at HTMLDocument.eval (eval-script: 编辑后1 …)   ← 事件 JS 帧
    at fireEvent (finereport.js:…)
    at …
    at setValue (finereport.js:…)                    ← 同样的帧又开始重复
    at HTMLDocument.eval (eval-script: 编辑后1 …)
    at fireEvent (finereport.js:…)
    …（重复至栈耗尽）
```

## 2. 根因：setValue→afteredit 链式点火 + 互清环

**机制**：FR 中 `getWidgetByName("X").setValue(v)` 不只是赋值——它会**触发目标控件 X 自身的编辑后(afteredit)事件**，且**不区分值是否变化**（清空另一个已为空的控件同样点火）。若 X 的 afteredit 又对别的（或原来的）控件 setValue，事件链就继续蔓延。

**本例的互清调用图**（修前定格样本 `*.cpt.bak_20260906_235641`）：

```
para_legal.afteredit  ──清──▶ para_bu / para_region / para_plant / para_entity
para_bu.afteredit     ──清──▶ para_legal / para_region / para_plant / para_entity
para_region.afteredit ──清──▶ para_legal / para_plant          ← "清 para_legal"为新加入边
para_plant.afteredit  ──清──▶ para_entity                       （entity 无编辑后事件, 链在此终止）
```

`para_region → para_legal` 边加入后，图中出现**多步互清环**：

```
para_legal → para_bu → para_legal            （2步环）
para_legal → para_region → para_legal        （2步环）
para_bu → para_region → para_legal → para_bu （3步环）
```

点火过程：用户编辑 para_legal → 其 afteredit 无条件 `para_bu.setValue("")` → 点火 para_bu.afteredit → 无条件 `para_legal.setValue("")` → 点火 para_legal.afteredit → ……值在"有值→空"间被反复无条件改写，**事件链深度无界增长直至调用栈耗尽**。环上每一条边都**没有判值护栏**（setValue 前不检查目标当前值），这是爆栈的必要条件。

**盲区本质**：`node --check` 只查单块 JS 语法（每块都合法）；`fr_check` 只查模板级规则，无事件调用图概念。跨控件的"事件环"只有把所有 Listener 的 setValue 关系拼成有向图才可见——此前没有任何工具做这件事。

## 3. 定位方法：堆栈帧特征 + 静态调用图环检测

**堆栈帧特征（运行期）**：RangeError 堆栈中"setValue → eval(事件JS) → fireEvent"这组帧**循环重复出现**，且 eval 帧携带事件名（如 `编辑后1`）；帧序列里出现几个不同的事件名，环就有几个节点。据此可锁定涉事控件的事件。

**静态调用图分析（落盘前，推荐）**：解析 cpt 全部 `<Listener event="afteredit">`，对每块 JS 提取 `getWidgetByName("X").setValue(...)`（含 `var w = getWidgetByName("X")` 变量绑定与 `clr("X")` 函数包装两种形态），以"当前控件 → X"建边，做控件级有向图环检测：

```
python "<工具包根目录>(个人版)\kfgj/fzpy\check_cpt_events.py" "示例实际表.cpt"
```

退出码 0=PASS（无环）/ 1=ERROR（有环且存在无护栏边，递归风险）/ 2=WARN（有环但全护栏，人工确认）；`--json` 出结构化结果。对修前备份样本的实测输出（2026-09-07）：

```
环: {para_bu, para_legal, para_region}  → ERROR 递归风险
    para_legal → para_bu  ★无护栏★
    para_legal → para_region  ★无护栏★
    para_bu → para_legal  ★无护栏★
    para_bu → para_region  ★无护栏★
    para_region → para_legal  ★无护栏★
    链式点火路径: setValue→目标控件 afteredit→再 setValue→…→Maximum call stack size exceeded
```

## 4. 修复："先判值再清"护栏样板

互清不可避免时，每条清理边都必须带**判值护栏**——目标当前有值才清，清过一次后值为空，护栏短路，事件链自然终止（链上写入的只有空值，值单调不增，不会振荡）：

```js
// ✅ 编辑后事件（para_legal）—— clr 函数式判值包装
var f = _g().parameterEl;
var v = this.getValue();
function clr(n){var w=f.getWidgetByName(n); if((w.getValue()||"")!==""){w.setValue("");}}
clr("para_bu"); clr("para_region"); clr("para_plant");
f.getWidgetByName("para_entity").setValue(v == null ? "" : v);
```

要点：`clr` 内先 `w.getValue()` 判非空再 `w.setValue("")`；环上**所有**边都要走 `clr`（漏一条无护栏边即仍有 ERROR 风险）。修后两文件经 check_cpt_events.py 复检为 WARN（环仍在、全护栏识别），线上验证爆栈消失。

**更优结构（能免则免）**：互清本身就危险，优先改为**单向清理**（只从细粒度往粗粒度方向清，构造无环图），或仿照本工程 query 按钮的**查询前聚合**模式——编辑后事件不做互清，点查询时按 `plant > region > bu > legal` 优先级聚合一次写入 entity 并清其余。

## 5. 预防

1. **落盘前工具门禁**：凡程序化/手工改动控件联动（新增或修改 afteredit 里的 setValue），落盘前跑 `check_cpt_events.py <cpt>`，**ERROR 即中止落盘**；WARN 需人工确认环上确为"先判值再清"且不写入非空值。三样本回归基线（2026-09-07）：修前备份两文件=ERROR(1)、修后两文件=WARN(2)、示例映射A.cpt=PASS(0) 不误报。
3. **联动设计纪律**：新增一条"清别人"的边前，先画全量互清图（工具输出即调用图）确认不闭环；确需闭环则全环 clr 化；禁止在环上任一边做无判值 setValue 或写入非空值。

## 6. 触发案例

示例实际表.cpt / 示例预算表.cpt（示例报表工程/明细报表），2026-09-06：参数面板联动改造中给 para_region 的编辑后事件加入"清 para_legal"，与既有 para_legal↔para_bu、para_legal→para_region 等清理边闭合成 {legal, bu, region} 三角互清环，环上全部无护栏；线上编辑任一联动控件即 `Maximum call stack size exceeded` 页面卡死。同日以"先判值再清" clr 护栏修复（修前形态定格于 `示例实际表.cpt.bak_20260906_235641`、`示例预算表.cpt.bak_20260906_235641`），2026-09-07 工具回归确认 ERROR→WARN。同工程 示例映射A.cpt 事件无跨控件 setValue，为无环对照样本。

## 7. 置信度

- **机制定论（setValue 触发目标控件 afteredit、互清环链式点火致爆栈）**：**高**。修前样本静态调用图与线上爆栈行为吻合；加护栏后链终止、爆栈消失，改动仅此一处，因果闭环。
- **护栏终止性论证（值单调清空→护栏短路→链断）**：**中高**。静态推理+线上修复生效验证；未做逐值自动回放，故全护栏环判 WARN 而非 PASS。
- **堆栈帧摘录**：**中**。为浏览器控制台典型形态与帧序特征，非逐字日志存档（定位以帧循环重复特征为准，帧内行号随 FR 版本不同）。
- **护栏启发式的局限**：仅识别"先判值再清"形态，对其他等效防递归写法（如标志位、一次性锁）会误报 ERROR，属保守方向（可接受，人工复核兜底）。
- **fr_check 待补规则**：**建议未实现**，待台账裁决。
