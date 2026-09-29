---
keywords: [FRM, 决策报表, 驾驶舱, frm, frm决策报表, FRM决策报表]
---
<!--
KB_INDEX: {
    "title": "Stage 7: FRM 决策报表",
    "stage": "pipeline",
    "tags": [
      "FRM",
      "决策报表",
      "驾驶舱"
    ],
    "keywords": [
      "FRM",
      "决策报表",
      "驾驶舱",
      "frm"
    ],
    "summary": "FRM 决策报表/驾驶舱的构建要点与与普通 CPT 的差异、图表轮播联动、组件间联动(FormHyperlink/DynamicParamHyperlink)、扩展图表数据绑定、组件级导出、导出与定时调度约束"
  }
-->

# Stage 7: FRM 决策报表
> 问法入口（2026-09-13 收官补，S-016）：「frm 决策报表」「frm 跟 cpt 什么区别、什么时候用 frm」→ 本文件全卷（决策报表专册）；FR11 新自适应引擎另见 ckzl/lc/fr11_knowledge/frm-decision决策报表/。

> 来源: `ckzl/gf/FR_HEADLESS_GUIDE.md` 流水线拆分

---

## 12. FRM 决策报表/驾驶舱

### 常见问法：frm 决策报表怎么从零搭？绝对布局还是自适应布局怎么选？

| 症状/口语问题 | 动作 | 出处（本文件§+行号） |
|---|---|---|
| 想无头生成一个 .frm，body 的 XML 骨架怎么写 | 外层恒为 `WFitLayout("body")`，绝对布局时内挂唯一 `WAbsoluteBodyLayout`（两层嵌套，不是二选一）；骨架照抄 §12.1 代码块 | §12.1 L31-49 |
| 自适应还是绝对布局、双向还是横向怎么选 | 查 GUI 选项↔API↔XML 四组合对照表（双向自适应/横向自适应/适应区域/固定大小）；两套 `setCompState` 同名不同义，设错对象静默失效 | §12.16 L301-312 |
| 移动端绝对画布块怎么放组件 | `com.fr.form.ui.container.WAbsoluteLayout` + `BoundsWidget`/`<BoundsAttr x/y/width/height>`；画布块本体禁止设隐藏/全屏 | §12.17 L316-323 |
| 带页签(Tab)的看板页面怎么搭 | `WTitleLayout`+`ChangeAttr(enable/timeInterval)`；Tab 实为四层结构，事件挂标题面板；隐藏标题=标题区 `BoundsAttr height="0"` | §12.2 L68-92 |
| 组件怎么命名、JS 怎么取组件 | widgetName 全表单唯一、生成器统一分配映射表；跨容器取用 `_g().getWidgetByName(name)` | §12.14 L278-287、§12.11 L222-234 |
| 手工新建 frm / 目录树组件在哪学 | 本文件未沉淀（无头生成路线）；选骨架→`ckzl/hbfa/README.md`，FR11 新自适应引擎→`ckzl/lc/fr11_knowledge/frm-decision决策报表/SKILL.md` | 边界（两入口 ls 实测存在） |

### 12.1 布局骨架
```xml
<Form xmlVersion="20170720" releaseVersion="10.0.0">
  <Layout class="com.fr.form.ui.container.WBorderLayout">
    <WidgetName name="form"/>
    <Center class="com.fr.form.ui.container.WFitLayout">
      <Widget class="...WAbsoluteLayout$BoundsWidget">
        <InnerWidget class="...WAbsoluteBodyLayout">
          <!-- 所有组件 BoundsAttr 绝对定位 -->
        </InnerWidget>
        <BoundsAttr x="0" y="0" width="960" height="540"/>
      </Widget>
      <BodyLayoutType type="1"/>
    </Center>
  </Layout>
</Form>
```

> **勘误补充：body 是两层结构而非二选一（doc-958，全部签名/常量已用字节码探针实读）** —— 外层恒为 `com.fr.form.ui.container.WFitLayout`（`new WFitLayout("body")`，管 布局类型/组件缩放/组件间隔/内边距/主体填充），绝对布局时内挂唯一 `WAbsoluteBodyLayout`（管 缩放逻辑/设计分辨率/组件坐标）。§12.1 的写法容易被读成「绝对布局要换 body 类」，实际是两层嵌套。
>
> **11 项属性映射表**：
>
> | 属性 | Java API | XML |
> |------|---------|-----|
> | 组件名称 | `Widget#setWidgetName` | `<WidgetName>` |
> | 布局类型 | `WFitLayout#setLayoutType(WBodyLayoutType.FIT/ABSOLUTE)` | `<BodyLayoutType type="0/1"/>` |
> | 组件缩放 | `WFitLayout#setCompState(STATE_FULL=0 双向/STATE_ORIGIN=1 横向)` | `<WidgetZoomAttr compState/>` |
> | 缩放逻辑 | `WAbsoluteBodyLayout#setCompState(STATE_FIT=0 适应区域/STATE_FIXED=1 固定大小)` | `<WidgetScalingAttr compState/>` |
> | 组件间隔 | `AbstractGapWidget#setCompInterval` | `<LCAttr compInterval/>` |
> | 内边距 | `AbstractBorderStyleWidget#setMargin(PaddingMargin(t,l,b,r))` | `<Margin/>` |
> | body 大小 | `setContainerWidth/Height` | `<Size/>` |
> | 分辨率折算 | `setResolutionScaling(double)` | `<ResolutionScalingAttr percent/>`（1920→1.2/1440→1.0/1366→0.9/1280→0.85/1024→0.6；宽度<1024 按 1024、>1920 按 1920） |
> | 设计分辨率 | `setDesigningResolution(Dimension)` | `<DesignResolution absoluteResolutionScaleW/H/>` |
> | 主体填充 | `setBackground(com.fr.general.Background)` | `<Background/>` |
>
> ⚠️ 两套 `setCompState` **同名不同义**、常量都是 0/1，设错对象既不报错也不报警，是典型的静默失效点；分辨率折算系数无头生成必须自己算，漏了会让同一模板在不同设计机上尺寸对不上。

### 12.2 WTitleLayout — Tab 切换面板
```xml
<InnerWidget class="com.fr.form.ui.container.WTitleLayout">
  <ChangeAttr enable="true" changeType="button" timeInterval="5"
              buttonColor="-8421505" carouselColor="-8421505" showArrow="true">
    <TextAttr><Attr alignText="0"/></TextAttr>
  </ChangeAttr>
  <!-- Tab 内容: WAbsoluteLayout$BoundsWidget → ElementCaseEditor 或 ChartEditor -->
</InnerWidget>
```
- `enable="true"` → 启用轮播自动切换
- `changeType="button"` → 标签页按钮模式
- `timeInterval="5"` → 秒

> **勘误补充：Tab 块实为四层结构（doc-1481，对照 doc-3864）** —— 官方 JS 里 `_g().getWidgetByName("tabpane0").getShowIndex()` 取到的是 Tab 块的**标题面板**，说明不能把 Tab 块理解成单个 `WTitleLayout`。四层模型：
>
> 1. Tab 块容器（`...container.cardlayout.WCardMainBorderLayout` [待核]）；
> 2. 标题面板（`WCardTitleLayout` [待核]，WidgetName 默认 tabpane0）；
> 3. 卡片区（`WCardLayout` [待核]）；
> 4. 每页（`WTabFitLayout` [待核]）。
>
> 三条关键性质：
> - ① `<ChangeAttr enable/timeInterval>` 与「Tab块切换」`<Listener>`（事件名 `tabchange` [待核]）**都挂在标题面板上**；挂到 Tab 块整体或某个 Tab 页 = 事件永不触发且无报错（最难的静默失效）；
> - ② 「隐藏 Tab 标题」= 标题区 `<BoundsAttr height="0"/>`，不是 `setVisible(false)`；高度置 0 后轮播照常生效（「自动播放 + 无标题」效果的来源）；
> - ③ 移动端不支持 Tab 轮播（需手动切，切后联动仍生效）。

### 12.3 ElementCaseEditor — FRM 内嵌报表块
```xml
<InnerWidget class="com.fr.form.ui.ElementCaseEditor">
  <FormElementCase>
    <ReportPageAttr><HR/><FR/><HC/><FC/></ReportPageAttr>
    <CellElementList>...</CellElementList>
  </FormElementCase>
</InnerWidget>
```

### 12.4 Label — 标题文字
```xml
<InnerWidget class="com.fr.form.ui.Label">
  <LabelAttr>
    <O><![CDATA[标题文字]]></O>
    <FRFont name="微软雅黑" style="1" size="200" foreground="-1"/>
  </LabelAttr>
</InnerWidget>
```

### 12.5 设计分辨率
```xml
<DesignResolution absoluteResolutionScaleW="960" absoluteResolutionScaleH="540"/>
<Size width="960" height="540"/>
<BodyLayoutType type="1"/>   <!-- 1=绝对布局 -->
```

### 常见问法：frm 里图表点了不联动、轮播不动，怎么排查？

| 症状/口语问题 | 动作 | 出处（本文件§+行号） |
|---|---|---|
| 图表轮播联动怎么配才会动 | 落地四要素：ds1 全量绑源图 / ds2 含参**带默认值**绑所有目标图 / 联动项按 WidgetName / 动画∈{重新加载,增量刷新}；仅 7 类扩展图表支持、仅 PC | §12.6 L121-138 |
| Tab 轮播和图表轮播分不清 | 两种「轮播」方向不同：Tab 轮播切标签页（§12.2）；图表轮播联动把当前值当参数推给目标组件（doc-2857） | §12.6 L123-126 |
| 点组件下游没反应，联动方式怎么选 | 一个点击让多个/跨数据集动→动态参数 `DynamicParamHyperlink`(doc-651)；点对点推给具体组件→`FormHyperlink`(doc-3556)；无人值守自动轮播→隐藏控件桥接 `_g().getWidgetByName('area').setValue(x)`(doc-1481) | §12.7 L140-177 |
| 扩展图表调 dataRefresh() 没反应 | 扩展图表不支持 `chart.dataRefresh()`，必须 `FR.Chart.WebUtils.getChart("chartN").dealReloadChartAjax()`；不支持移动端 | §12.8 L179-185 |
| XML 合法、页面能开、就是没反应 | 静默失效共性：651 断链=参数未双声明/SQL 未引用/缺默认值；3556 断链=target/参数名/默认值四链不一致 | §12.7 L159 |

### 12.6 图表轮播联动

.frm 里存在**两种「轮播」**,方向完全不同,勿混淆：

1. **Tab 轮播** = WTitleLayout/ChangeAttr（§12.2 已有，切换的是标签页）；
2. **图表轮播联动** = 扩展图表「特效 > 轮播联动」（doc-2857）：源图表每轮播一项，就把当前值作为参数推给目标组件，目标组件重查含参数据集后刷新。

落地四要素（断一处即静默失效，全在 XML 层可静态验证）：

- ds1 全量绑源图（决定轮播序列）；
- ds2 含参（**带默认值**）绑**所有**目标图；
- 联动项按 WidgetName 引用目标；
- 联动动画 ∈ {重新加载, 增量刷新}。

能力白名单：只有 7 类扩展图表有「轮播联动」（轮播GIS点地图/轮播三维组合地图/轮播KPI指标卡/轮播目录齿轮/轮播夜光仪表盘/水球图/像素点图）；粒子计数器走「特效 > 刷新联动」。联动对象随模板类型分叉：.cpt → 联动单元格/联动悬浮元素（按单元格坐标）；.frm → 当前决策报表对象（按组件名）。

> 联动参数取值来自源图表内置字段（非单元格值）；目标图表标题动态化走模板参数（`=$区域名+"销售进度"`，须在 ReportParameterAttr 声明）；仅 PC 端预览，不支持移动端。
> 来源:帆软官方帮助 doc-2857

### 12.7 组件间联动（两种 .frm 联动机制）

**机制一：当前表单对象超链（doc-3556）** —— 点对点把值推给某具体组件：

- 源组件挂 `<Hyperlink class="com.fr.form.main.FormHyperlink" target="chart1">` + `<Parameters><Parameter name="area" .../></Parameters>`；图表块入口=「特效 > 交互属性 > 超级链接 > 当前表单对象」，报表块单元格入口=「超级链接 > 当前决策报表对象」——同一套 XML 载体，可共用一个注入函数。
- 联动四链：[1] target=真实 WidgetName；[2] 超链参数名=目标组件所绑数据集参数名；[3] 该数据集 SQL 含 `${参数}`；[4] 该参数有默认值（首屏不空）。
- 取值来源随源组件类型分叉：图表源用内置枚举（系列名称/分类名/值），单元格源用公式 `=A2` 或 `=$$$`。
- 目标图表标题动态化需「数据集参数 + 模板参数」双声明（标题 `=$area+"..."` 里的 `$area` 走模板参数）。
- 官方样本：`%FR_HOME%\webapps\webroot\WEB-INF\reportlets\doc\Advanced\Chart\图表联动表单对象.frm`；节点名为推断待核验。
- PC / App / HTML5 均支持（优于仅 PC 的联动悬浮元素）。

**机制二：动态参数超链（doc-651）** —— 一个点击让多个/跨数据集动：

- 源组件挂 `<Hyperlink class="com.fr.js.DynamicParamHyperlink">`，把被点击值（系列名称等）写进模板参数（如 product）；凡 SQL 在 `${}` 块内引用该参数的数据集（ds2）自动重查、目标图刷新。
- 参数流向是「模板参数 → 数据集 `${参数}`」，而非机制一的「超链 → 目标 WidgetName 的数据集参数」；两套路混用即「点了没反应」。
- 官方判别铁律：「如果是直接超级链接到当前决策报表的不同组件，超级链接的方式应该选择当前决策报表对象」。

**二选一决策树**：想「一个点击让多个/跨数据集动」→ 动态参数（doc-651）；想「点对点把值推给某具体组件」→ 当前表单对象（doc-3556）。

> 两种机制的静默失效形态一致（XML 合法/页面能开/点了没反应），断链点分别是「参数未双声明/SQL 未引用/缺默认值」（651）与「target/参数名/默认值四链不一致」（3556）。
> 来源:帆软官方帮助 doc-3556/651

**机制三：隐藏控件桥接（doc-1481，对照 doc-3864）** —— 无人值守自动轮播 + 联动的唯一形态：

- body 放一个 `com.fr.form.ui.ComboBox` 且 `<WidgetAttr invisible="true">`，控件名 == 模板参数名（.frm 下同名即绑定）；
- JS `_g().getWidgetByName('area').setValue(x)` 直接改参数，所有以 `$area` 过滤的报表块/图表块自动重算，**全程无 `parameterCommit()`**。

与前两机制的判别（选型表）：

| 维度 | 机制一 当前表单对象 | 机制二 动态参数 | 机制三 隐藏控件桥接 |
|------|------|------|------|
| 触发源 | 用户点击 | 用户点击 | 点击 / **轮播 / 定时器自动驱动** |
| 目标 | 点对点 | 广播（跨数据集） | 广播（按模板参数） |
| 载体 | Hyperlink | Hyperlink | 参数（同名绑定） |

> ⚠️ 桥接控件不可因「反正不可见」而删除：删掉即参数无处承载、JS 取到 null 整段中断。另注意「.frm 控件即参数、无需 parameterCommit」与 .cpt 参数面板（doc-1825 必须 commit）相反，勿互相套用。

> 来源:帆软官方帮助 doc-1481

### 12.8 扩展图表数据绑定与刷新

- 扩展图表特有绑定字段：播放维度/指标值/目标值（轮播夜光仪表盘示例取值 `=report0~B2/~~C2/~~D2`），与普通图表的「分类轴/系列值」绑定区分开，无头生成时勿套错绑定形态。
- 刷新 API 与普通图表不同：普通图表用 `chart.dataRefresh()` 单组件刷新；**扩展图表不支持 dataRefresh()**，必须改用 `FR.Chart.WebUtils.getChart("chartN").dealReloadChartAjax()`。用错 API 时页面能开、点了没反应、浏览器控制台无报错（静默故障）。
- ⚠️ 该刷新方案**不支持移动端**。
- **扩展图表(AbstractChart)通用属性面（doc-3836/3135）**：撤回「扩展图表 = 插件 = 无头不可控」口径——`com.fr.extended.chart.*` 整套契约预置在 **fine-report-engine**：`AbstractChart extends com.fr.chart.chartattr.Chart`，通用可写面 = `setRefreshEnabled(boolean)`（监控刷新）/ `setAutoRefreshTime(double)`（默认 10.0）/ `setLinkGroup(com.fr.js.NameJavaScriptGroup)`（图形超链）/ `getDataConfig()`（配套 `AbstractDataConfig`/`ExtendedField`/`ExtendedTableDataSet`）；XML 落点 `<Chart class="<插件类全名>"><attr refreshEnabled=".." refreshTime=".."/><DataSet ..><NameJavaScriptGroup ..>`。`writeAttr` **零跳转指令**（两属性恒写出）、`readAttr` 缺省 false/10.0 与 `<init>` 一致 ⇒ Java 建模与手拼 XML 可互换。边界：插件私有属性（场景列表/视角坐标/轮播/背景特效/自动简化模型）引擎侧无契约、不可预测。
- 来源:帆软官方帮助 doc-3115

### 常见问法：frm 怎么只导出一个报表块？定时调度导出为什么自适应失效/报重叠？

| 症状/口语问题 | 动作 | 出处（本文件§+行号） |
|---|---|---|
| 只要导出某一个报表块 | FreeButton 挂 click：`window.open("${servletURL}?op=ec_export&sessionID="+a+"&widgetName=REPORT0&format=excel&extype=simple")`；配套参数 a=公式 `sessionID`（两段式，JS 里直接写 ${sessionID} 会 a is not defined） | §12.9 L189-192 |
| 导出按钮点了没文件/文件损坏 | 四条硬约束：widgetName **全大写** / 只能 format=excel / 块必须可见（隐藏导出损坏）/ 不支持移动端 | §12.9 L194-199 |
| 定时调度导出出现滚动条和空白 | 自适应布局在结果文件中失效（按固定大小导出），要自适应用「文件处理→结果链接」而非结果文件 | §12.10 L210 |
| 定时导出报「存在报表块或图表重叠」 | 绝对布局组件间留 >=8px 安全间隙；重叠时预览正常、定时导出抛 RuntimeException（静默缺陷） | §12.10 L209 |
| frm 定时调度选什么执行类型 | 只能「预览」；word 附件不支持 FRM 图表组件；需定时导出 word/pdf 优先 .cpt+单元格元素图表 | §12.10 L212-218 |
| 报表块怎么翻页/局部刷新 | `widget.gotoPage(pn,para,noCache)`：pn 从 1 起；noCache 用 `"lazy"`（true 会重算所有报表块）；para 点击后才生效，首屏靠模板参数默认值兜底 | §12.12 L238-252 |

### 12.9 组件级导出

.frm 导出**单个报表块**与模板级导出属性（doc-1118/1128/1141 的 `<WorkBook><ReportExportAttr>`）不同宗，走组件级链路：

- 按钮 FreeButton 挂 `<Listener event="click">`，JS 为 `window.open("${servletURL}?op=ec_export&sessionID="+a+"&widgetName=REPORT0&format=excel&extype=simple")`；
- 配套事件参数 `a` = 公式 `sessionID`（两段式传参，不能直接在 JS 里写 `${sessionID}`，否则 `a is not defined`）。

四条硬约束：

1. `widgetName` 必须**全大写**（写小写不报错、只是导不出来）；
2. **只能** `format=excel`（不支持 pdf/word/image）；
3. 目标报表块必须**可见**：隐藏时导出文件损坏、无法打开，唯一解法是导出前改回可见（装新自适应插件的新版决策报表除外）；
4. **不支持移动端**。

> 与 .frm 定时调度导出（「全组件转聚合报表」，doc-3185）并列区分：模板级属性、组件级导出、定时调度导出是三条不同链路。
> 来源:帆软官方帮助 doc-4104

### 12.10 导出与定时调度约束

铁律三条（doc-3185 §18/§20）：

1. **决策报表的导出能力是定时调度推送能力的上界** —— 决策报表导出不支持的功能，定时调度推送同样不支持；
2. 绝对布局排布组件时留 **>=8px 安全间隙**，禁止重叠，也不要刚好相接（后续微调宽度即越界）；组件重叠在定时导出时抛 `java.lang.RuntimeException: 存在报表块或图表重叠，导出失败`，而直接预览完全正常（静默缺陷）；
3. 自适应布局在定时调度结果文件中失效（按固定大小导出，出现滚动条与空白）；需要自适应就在「文件处理」里用**结果链接**而非结果文件。

模板形态硬约束（doc-2208）：

1. 决策报表（.frm）在定时调度里**只能选「预览」**执行类型（普通报表才有 预览/填报/分析/新填报）；
2. word 附件不支持 FRM 图表组件，只支持单元格元素图表；
3. 决策报表 + excel03/07/word/pdf 附件不支持 body 背景色。

**选型建议**：需求含「定时导出 word/pdf」时优先 .cpt + 单元格元素图表。

> 来源:帆软官方帮助 doc-1457/2208/3185

### 12.11 .frm 命名空间与跨区取值

.frm 特有铁律：`_g()` 返回整张 Form，body 组件与参数面板控件**共用一个平面命名空间**，故 `.frm` 内 `<WidgetName>` 必须全表单唯一（重名时 `getWidgetByName` 取到哪个未定义）。

取值前缀对照表：

| 位置 | 写法 | 可见范围 |
|------|------|---------|
| `.frm` 任意位置 | `_g().getWidgetByName()` | 可跨 body/参数面板（doc-1864） |
| `.cpt` 参数面板 | `this.options.form.getWidgetByName()` | 只见面板控件（doc-1197） |
| `.cpt` 单元格/填报 | `contentPane.getWidgetByName()` | （doc-1434/pipeline05 §10.2） |

> 与 ckzl/lc/04 §21 互链。差异决定了 fr_check 的重名规则要按模板类型分叉：.cpt 重名无害、.frm 重名致命，一条规则通吃会误报或漏报。

> 来源:帆软官方帮助 doc-1481

### 12.12 报表块局部刷新与翻页（gotoPage）

`widget.gotoPage(pn, para, noCache)` 完整语义：

| 参数 | 语义 |
|------|------|
| `pn` | **从 1 开始**；越界或块只有 1 页时静默无反应 |
| `para` | 形如 `"{month:12, name:'FR'}"`（数字裸写、字符串单引号；无参传 `"{}"`），是**运行期注入**、只在点击之后存在 |
| `noCache` | **三态**：不写=走缓存不重算 / `true`=不走缓存并**重算所有报表块**（官方 doc-1304 1.2 明示大模板不推荐）/ `"lazy"`=不走缓存但**只重算当前块** |

- **kit 生成器默认策略应写死 `"lazy"`**（1 秒定时刷新 + `true` = 「重算所有报表块」每秒执行一次，是可预见的线上事故点）；
- 生成契约：块 WidgetName ↔ 块内分页断点 ↔ para 键名 ↔ 模板参数默认值，四者由同一张表供给；
- **para 只在点击后生效，首屏 `$month` 靠模板参数默认值兜底，缺默认值 = 第一页空白**。

> 来源:帆软官方帮助 doc-4068

### 12.13 .frm 控件事件注入（Listener）

事件挂载形态：`com.fr.form.event.Listener` + `com.fr.js.JavaScriptImpl` + `Widget#addListener(..)`，XML 落点：

```xml
<InnerWidget class="com.fr.form.ui.ElementCaseEditor">
  <WidgetName name="report0"/>
  <Listener event="afterinit">
    <JavaScript class="com.fr.js.JavaScriptImpl">
      <Content><![CDATA[..]]></Content>
    </JavaScript>
  </Listener>
</InnerWidget>
```

- **控件级 afterinit（this=该控件，可用 this.isVisible()/this.options.form）与表单级 afterinit（`<Form><Body><Events>`，见 06 §24）是两个挂载点**，同名不同位，挂错即静默无反应；
- 写方向 API（Listener 构造器 / addListener / JavaScriptImpl.setContent）标 probe，读方向 kit 已核验。
- **表单级(body)支持的事件名不止 afterinit（doc-2372）**：`<Form><Body><Events>` 同一挂载点也支持 `click`（实证「点击 body 全屏」）；宿主用 `Form#getContainer()`（真实根 body WLayout），**严禁 `Form#getBodyContainer()`**（返回 clone+removeWidget 的只读克隆，改动落盘即丢）。
- **三层事件名白名单实读全集（doc-1086/1629）**：①`com.fr.form.ui.container.WLayout` = `{afterinit, click}`（`WFitLayout`/`WAbsoluteBodyLayout` 未覆写，继承之）→ .frm body 级挂点；②`com.fr.form.ui.ElementCaseEditor` = `{click}` 一项 → 报表块**不支持 afterinit**；③`com.fr.form.ui.FieldEditor` = `{afterinit, beforeedit, afteredit, stopedit}` → 参数面板控件级。铁律：`addListener` 后**必须 `getListenerSize()` 回读断言**——不命中白名单是无异常无日志的静默丢弃（`Observer#readXML` 也走 `addListener`，手拼 XML 同样被挡）。

> 决策报表几乎所有交互（跑马灯/局部刷新/显隐切换/联动）都从这一步开始；06 §24 只讲了表单级 afterinit，不点明分叉，模型很容易把控件级 JS 挂到 Body 上（反之亦然）。

> 来源:帆软官方帮助 doc-306

### 12.14 组件命名规范与 JS 契约

生成 .frm 时 widgetName 由生成器统一分配并落一张 `name → 组件类型` 映射表，所有 JS 片段只从该表取名拼接，**禁止手写字符串**。配套铁律两条：

1. 跨容器取组件一律 `_g().getWidgetByName(name)`；`this.options.form.getWidgetByName` 只在同容器内使用（参数面板里写它取不到 body 组件）；
2. 组件必须显式命名，未命名组件等同于「JS 永远够不着」。

> 名字对不上时前端返回 undefined 且**不抛任何错误**——是决策报表最典型的哑故障；名字在无头链路里是 Java/XML 生成的，属可控项，不该靠人肉对齐。

> 来源:帆软官方帮助 doc-3811

### 12.15 决策报表内 value() 不联动

.frm 特有坑：在 .frm 的 body（控件/报表块/图表块）里用 `value('ds1',col)` 取数据集值**不会随输入控件变化重算**（无联动）。

- 需联动时一律改用 `$参数名` 引用模板参数（建立响应式依赖）；
- 或把输入控件放进**参数界面**（`<ParameterUI>` ⚠待核）配查询按钮走整页重算；
- **生成器默认取值表达式优先 `$参数`**，仅在需「整页查询刷新」才走参数界面；spec 层加「是否需要联动」字段，静态拦截「需联动却用 value()」。

> 它会被误当成「公式能取到值就够了」而漏掉联动语义；选型写错不报错（表现「改了输入下游不动」），归因成本极高。practice/doc-3812 已给出 value() vs $参数 对照片段。

> 来源:帆软官方帮助 doc-3812

### 12.16 移动端 body 布局四组合（GUI 选项名 ↔ API/XML 对照）

§12.1 只记了两套 `setCompState` 的 API 常量、未标 GUI 选项名，生成器按需求文字（「双向自适应」等）选型时无法直接映射；四组合对照表（均字节码实读）：

| GUI 选项 | 布局类型 + 旋钮 | Java API | XML |
|---------|----------------|----------|-----|
| 双向自适应 | 自适应布局 + 组件缩放 | `WFitLayout#setLayoutType(WBodyLayoutType.FIT)` + `setCompState(STATE_FULL=0)` | `<BodyLayoutType type="0"/><WidgetZoomAttr compState="0"/>` |
| 横向自适应 | 自适应布局 + 组件缩放 | FIT + `setCompState(STATE_ORIGIN=1)` | `<BodyLayoutType type="0"/><WidgetZoomAttr compState="1"/>` |
| 适应区域 | 绝对布局 + 缩放逻辑 | `WFitLayout#setLayoutType(WBodyLayoutType.ABSOLUTE)` + 内层 `WAbsoluteBodyLayout#setCompState(STATE_FIT=0)` | `<BodyLayoutType type="1"/><WidgetScalingAttr compState="0"/>` |
| 固定大小 | 绝对布局 + 缩放逻辑 | ABSOLUTE + `setCompState(STATE_FIXED=1)` | `<BodyLayoutType type="1"/><WidgetScalingAttr compState="1"/>` |

⚠️ 外=组件缩放（WFitLayout）→ `<WidgetZoomAttr>`；内=缩放逻辑（WAbsoluteBodyLayout）→ `<WidgetScalingAttr>`；两套 setCompState 同名不同义、常量均 0/1，设错对象静默失效。版本门槛：报表服务器 10.0 / App v9.3 / HTML5 报表展现 v10.0。官方基线模板 `%FR_HOME%\webapps\webroot\WEB-INF\reportlets\doc\frm\绝对画布块.frm`。

> 来源:帆软官方帮助 doc-2447

### 12.17 绝对画布块 WAbsoluteLayout（移动端高频容器）

- 组件类 `com.fr.form.ui.container.WAbsoluteLayout`（决策报表容器组件，命名 `Widget#setWidgetName` → `<WidgetName>`）；内部子组件（控件/图表/报表块/嵌套画布块）由 `WAbsoluteLayout$BoundsWidget` 包裹 + `<BoundsAttr x/y/width/height>` 绝对定位（容器内 add 方法签名【未核实】）；
- 内部缩放逻辑与 body 绝对布局同构：「适应区域（全显无滚动条）/固定大小（等比缩放、超限出滚动条）」同为 `setCompState(0/1)`；
- **隐藏/全屏限制（静默行为差异，构建时禁止对画布块本体设隐藏/全屏）**：Tab（WTitleLayout）与绝对画布块**自身不支持隐藏/全屏**（隐藏画布=隐藏其内部组件、会占位空白）；内部控件/图表/报表块支持隐藏、图表/报表块支持全屏；
- 移动端两种角色：作为组件=整体参与 body 重布局/缩放（内部嵌套画布块恒按「布局-绝对布局」显示）；作为容器=内部组件按「适应区域/固定大小」缩放。

> 来源:帆软官方帮助 doc-2447

### 12.18 手机重布局（移动端 body 流式布局）与移动端限制清单

**手机重布局**（doc-1555）= .frm body 组件的移动端属性（HTML5 移动端展现插件实现），勾选后对**整张 .frm** 生效（含绝对布局/Tab 内组件），不勾选=保留布局。场景三选一：PC/Pad/手机共用 + 手机端流式布局 → 勾选；共用但手机端保留原始布局 → 不勾选（设计以移动端效果为先）；手机专用模板 → 不勾选。

- 四设置项：内边距（内容距边框）、组件间隔（组件纵向间距）、组件冻结（上滑时固定顶部）、控件顺序（从上到下排列，可拖拽）；
- **冻结范围**：仅 body 第一层非容器组件可冻结（报表块 `com.fr.form.ui.ReportBlock` / 图表块 / 文本 `com.fr.form.ui.Text`，插件扩展非容器组件亦可）；容器（WAbsoluteLayout/WTabLayout）**不可冻结**；多选时**连续**冻结组件到顶后合并固定，**不连续**冻结互相覆盖（先到顶的失效）；
- 版本门槛：组件冻结需 JAR 2019-12-05+（10.0.11）；重布局下图表自定义数据点提示需 HTML5 移动端插件 10.4.975+（2020-12-02）；
- 图表提示优化：横向超最大宽度直接省略、纵向最多 6 行（标准字体）超需下滑；「使用html解析文本」样式不勾只返回计算数据；饼图被点击的饼块自动转到正上方=预期行为；
- ⚠️ 重布局专属 setter/XML 节点名**未核实**，反查基线 = `%FR_HOME%\webapps\webroot\WEB-INF\reportlets\demo\NewbieGuide\决策报表入门示例.frm`（§0.14 read→改→write 路线：设计器勾选重布局另存后 diff body 节点 XML）。

**移动端限制清单**（doc-2447/1555，均静默表现、无报错）：绝对画布块/Tab 自身不支持隐藏与全屏（见 §12.17）；移动端不支持 Tab 轮播（需手动切换，切后联动仍生效，与 §12.2 一致）。

> 来源:帆软官方帮助 doc-1555（限制清单 doc-2447）

---


---

