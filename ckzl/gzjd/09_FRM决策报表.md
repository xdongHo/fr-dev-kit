<!--
KB_INDEX: {
  "title": "FRM 决策报表",
  "stage": "workflow-node",
  "tags": [
    "ckzl/gzjd",
    "FRM",
    "决策报表",
    "组件"
  ],
  "keywords": [
    "决策报表",
    "组件",
    "布局",
    "跨块联动"
  ],
  "summary": "组件化布局、跨块联动、决策报表对象",
  "trigger": "何时用：FRM决策报表/大屏：组件布局、报表块、body容器",
  "when_not": "何时不用：CPT普通报表任务（走NODE02-08）"
}
-->

# NODE 09 FRM 决策报表

> 本节点为ckzl/gzjd,自包含:判定题 → 知识点 → Java API → 常见错误 → 验证清单 → 路由。
> 详细展开见 ckzl/lc/ 对应章节(见导航文件 §四),本文件保持轻量。

## 判定题(先回答,再往下读)

- 模板类型确认是 FRM?
- 布局:组件化拖拽/绝对布局?
- 跨块联动:报表块↔图表块(按组件名)?
- FRM 也能用 Java API 创建(form.export 写盘)?

## 核心知识点(工程向,标注 来源 doc-XXXX)

<!--KB:NODE09-K01-->
- FRM 组件模型与 Java 创建:Form ↔ `<Form>`,组件=Widget 子类(图表=ChartEditor),数据集=DBTableData + SQL ${宏};扩展图表插件(WebGL 大屏图表)为独立插件,不支持导出/移动端/任何图表接口,见 ckzl/lc/01 §3;组件骨架见 ckzl/lc/07 §12。来源: doc-651 / doc-2474
<!--KB:NODE09-K02-->
- 组件联动核心机制:图表超链携带动态参数驱动另一组件数据集重查;充要条件=超链参数名 == 目标数据集 SQL 宏名;参数空值由 SQL if(len()==0) 兜底选全部;「当前决策报表对象」链接触发同表单组件刷新;见 ckzl/lc/07 §12.7。来源: doc-651 / doc-3556
<!--KB:NODE09-K03-->
- 报表块↔图表块跨块刷新:图表块点击事件 JS 里 FR.Chart.WebUtils.getChart("chart1").dataRefresh() 强制刷新;setTimeout(500ms) 规避报表块数据刷新时序;见 ckzl/lc/05 §14.4。来源: doc-1392
<!--KB:NODE09-K04-->
- 决策报表定时刷新:body「初始化后」事件 setInterval('location.reload()',10000);取消须存句柄 clearInterval;见 ckzl/lc/06 §24 + ckzl/lc/07 §12.6。来源: doc-1457
<!--KB:NODE09-K05-->
- 组件显隐与点击标题排序 JS:_g().getWidgetByName('report0').setVisible(false/true);gotoPage(1,{a:a},true) 动态传参 + 排序公式 if($a==1,$$$,-$$$) 参数驱动升降序;见 ckzl/lc/05 §10.5 + ckzl/lc/03 §8。来源: doc-1736 / doc-1894
<!--KB:NODE09-K06-->
- 组件命名规范:widgetName 生成器统一分配;跨容器 _g().getWidgetByName,同容器 this.options.form.getWidgetByName;未命名组件 JS 永远够不着;见 ckzl/lc/07 §12.14。来源: doc-1736
<!--KB:NODE09-K07-->
- 报表块滚动条根治:服务端属性 ElementCaseEditor.setFitStateInPC(DOUBLE_FIT=2) 优于官方 JS(减 17/16px 仅把滚动条挤出可视区:横向需滚动时无效、不支持移动端、依赖 setTimeout);两套 FitAttrState 枚举见 ckzl/lc/03。来源: doc-2425
<!--KB:NODE09-K08-->
- 冻结无独立持久化字段:ReportPageAttr#writeXML 不输出 setFreezeColumnRow 的设置(调用等于空操作);正确写法=setRepeatHeaderRowFrom/To + setUsePageFrozenRow(true);见 ckzl/lc/03 §6。来源: doc-2425
<!--KB:NODE09-K09-->
- FRM 单报表块导出:op=ec_export&sessionID=&widgetName=REPORT0(全大写)&format=excel&extype=simple;只能 Excel、组件须可见、不支持移动端;四条硬约束见 ckzl/lc/07 §12.9。来源: doc-4104
<!--KB:NODE09-K10-->
- 控件事件 Listener 铁律与 widgetName 大写:挂控件事件统一两参 `new Listener(Widget.AFTERINIT, js)`,禁用三/四参(targetWidget 首参,写错落成 `<Listener target="afterinit">` 静默失效);createJSONConfig 下发前 widgetName 转大写 → 前端 DOM div[widgetname] 恒大写,JS/CSS 选择器一律大写;supportedEvents() 只返回 {"click"} 不可作白名单(设计器能力≠引擎能力,见 ckzl/lc/06 §11.10)。来源: doc-2425
<!--KB:NODE09-K11-->
- **三层事件白名单全集(实读)+ 回读铁律**:①`com.fr.form.ui.container.WLayout` = `{afterinit, click}`(WFitLayout/WAbsoluteBodyLayout 继承之)——.frm body 级挂点;②`com.fr.form.ui.ElementCaseEditor` = `{click}` 一项——报表块**不支持 afterinit**;③`com.fr.form.ui.FieldEditor` = `{afterinit, beforeedit, afteredit, stopedit}`——参数面板控件级;另 `WCardLayout`(Tab 块)= `{afterinit, cardchange}` **无 click**。`Observer#addListener` 白名单不命中即静默 return 且 readXML 同样走它——**挂完必须 `getListenerSize()` 回读断言**;`Form#getContainer()`(真实根 body,写操作用它)vs `Form#getBodyContainer()`(clone,只读)。来源: doc-1629/3836,详见 ckzl/lc/07 §12.13
<!--KB:NODE09-K12-->
- **扩展图表不再一刀切判「不可做」**:`com.fr.extended.chart.AbstractChart`(extends `com.fr.chart.chartattr.Chart`)通用可写面=`setRefreshEnabled(boolean)`(监控刷新)/`setAutoRefreshTime(double)`(默认 10.0)/`setLinkGroup(NameJavaScriptGroup)`(图形超链)/`getDataConfig()` 系;装配侧 49 类全在 fine-report-engine、不需要装插件即可编译链接;插件私有属性(场景列表/视角坐标/轮播/背景特效)引擎侧无契约不可预测——判据:`com.fr.extended.chart.*` 里没有的 setter 就是插件私有。来源: doc-3836/3135,详见 ckzl/lc/03 §9.13

## Java API 要点(com.fr.* 类名/方法/与 XML 对应)

- FRM 骨架:`com.fr.form.main.Form` ↔ `<Form>`;图表组件 `com.fr.chart.form.ChartEditor` ↔ `<Widget widgetName="饼图" class="com.fr.chart.form.ChartEditor">`;数据集 `com.fr.data.impl.DBTableData` SQL 内 ${宏} ↔ `<TableData><DBTableData><SQL>`;参数 `com.fr.report.parameter.Parameter` 注册模板参数表 ↔ `<Parameter name="product">`;表单 IO 写 .frm 方法名各小版本不稳定以 jar 为准。来源: doc-651
- 联动超链:`com.fr.js.ChartHyperlink.setParameters(Parameter[])`,每个参数 `new Parameter("product","${系列名称}")`(「动态参数」=仅设参不跳转,刷新同表单数据集);`com.fr.js.FormHyperlink.setFormName("柱形图")+setParameters(...)`(「当前决策报表对象」);XML `<Hyperlink><ChartHyperlink><Parameters><Parameter name="product" value="${系列名称}"/>`。来源: doc-651
- 图表超链基类:`com.fr.chart.chartattr.Chart` 承载交互属性超链列表(设计器「特效>交互属性>超级链接」);`com.fr.chart.web.ChartHyperlink` 基类持超链名/目标/参数映射;「当前表单对象」实现类名各版本不稳定不杜撰;XML `<ChartWidget name="chart0"><Chart><hyperlink>`;超链参数值=系列名称/分类名是运行时变量,Java 侧以公式/变量占位。来源: doc-3556
- 报表块显示适配:`ElementCaseEditor#setFitStateInPC(int)`;取值 com.fr.report.fit.FitAttrState:DEFAULT=0/HORIZONTAL_FIT=1/DOUBLE_FIT=2/NOT_FIT=3;XML `<ReportFitAttr fitStateInPC="2" fitFont="false"/>`;取报表块 ElementCase 须把 `ElementCaseEditor#getElementCase()` 返回值(静态类型 FormElementCaseProvider,接口上无 setReportPageAttr)下转 `com.fr.report.worksheet.FormElementCase`。来源: doc-2425
- 控件事件注入:`new com.fr.form.event.Listener(Widget.AFTERINIT, javaScriptImpl)` + `Widget#addListener`;XML `<Listener event="afterinit" class="com.fr.form.event.Listener"><JavaScript class="com.fr.js.JavaScriptImpl">`;挂载形态与控件级/表单级分叉见 ckzl/lc/07 §12.13。来源: doc-2425
- 冻结正确 API:`ReportPageAttr#writeXML` 实读只输出 `<HR F T/><FR F T/><HC F T/><FC F T/><UPFCR COLUMN ROW/>`;`setFreezeColumnRow(ColumnRow)` 存在但 writeXML 不写=空操作;正确=`setRepeatHeaderRowFrom/To` + `setUsePageFrozenRow(true)`;见 ckzl/lc/03 §6。来源: doc-2425
- 前端 JS 类无 Java API:dataRefresh/gotoPage/setVisible/location.reload/op=ec_export 均预览期 JS 或 servlet 参数,.frm 仅存事件 `<JavaScript>` 文本节点,无 com.fr.* 构建路径。来源: doc-1392 / doc-1457 / doc-1736 / doc-1894 / doc-4104

## 常见错误

<!--KB:NODE09-E01-->
- Listener 三/四参重载把事件名写在 targetWidget 位 → `<Listener target="afterinit" event="report0">` XML 合法、fr_check 通过、前端不执行(来源: doc-2425)
<!--KB:NODE09-E02-->
- JS/CSS 选择器用小写 widgetName → DOM 上 div[widgetname] 恒大写,选择器落空(来源: doc-2425)
<!--KB:NODE09-E03-->
- 用 supportedEvents() 判断控件能否挂事件 → 报表块只返回 {"click"},误报合法 afterinit(来源: doc-2425)
<!--KB:NODE09-E04-->
- 按方法名直觉用 setFreezeColumnRow 冻结 → 设置了但无效(来源: doc-2425)
<!--KB:NODE09-E05-->
- 报表块隐藏时导出 → 导出文件损坏无法打开;widgetName 小写 → 导不出来且不报错(来源: doc-4104)
<!--KB:NODE09-E06-->
- 联动参数名 ≠ 目标数据集 SQL 宏名 → 点击无刷新(来源: doc-651)
<!--KB:NODE09-E07-->
- getWidgetByName 取未命名组件或跨容器用错 API → undefined 哑故障(来源: doc-1736,见 ckzl/lc/07 §12.14)
<!--KB:NODE09-E08-->
- 控件级 afterinit 挂到 Form Body(表单级)或反之 → 同名不同位,挂错静默无反应(来源: doc-1178 / doc-2425,见 ckzl/lc/07 §12.13)

## 验证清单

- [ ] .frm fr_check 校验通过;组件全部显式命名且与 JS 引用一致(含大小写)
- [ ] 事件挂载点正确(控件级 vs 表单级),事件名拼写正确
- [ ] 联动:点击源组件 → 目标组件刷新且参数正确;参数名==SQL 宏名
- [ ] 报表块滚动条:DOUBLE_FIT 后无滚动条;移动端实测
- [ ] 冻结/显隐/排序交互在 PC+App 各实测一遍
- [ ] 单报表块导出:widgetName 大写、组件可见、Excel 格式
- [ ] 定时刷新 clearInterval 可取消,无泄漏

## 机器校验（出口门禁）

> 单一事实源: `ckzl/gzjd/node_gates.yaml`；汇总执行: `python kfgj/fzpy/node_gate.py --node 09 --task-dir <task目录>`；以下命令可单跑。

<!--KB:NODE09-C01-->
- [ ] `python kfgj/fzpy/template_snapshot.py <frm>` — 改前结构快照
<!--KB:NODE09-C02-->
- [ ] `python kfgj/fzpy/fr_check.py <frm>` — 对 .frm 的适用性待核验（勿当已验证）
<!--KB:NODE09-C03-->
- [ ] `python web_kit/probe.py <frm>` — 运行期体检(.frm 入口推导已支持, 2026-09-11 入库; grid 类检查对 frm 自动跳过)


## 下一步路由

- FRM 完成 → 需要跨块联动?NODE-08;最后 NODE-10 预览与验证;FRM 创建参考 NODE-01 的容器模型链(来源 doc-4047)

