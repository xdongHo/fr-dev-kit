<!--
KB_INDEX: {
  "title": "ckzl/hbfa(报表骨架库)",
  "stage": "canvas-skeleton",
  "tags": ["画布布局", "骨架", "模板", "导航"],
  "keywords": ["骨架", "cpt模板", "frm模板", "画布布局", "布局方案", "WTitleLayout", "合并单元格", "dashboard", "驾驶舱"],
  "summary": "60套可视化报表骨架(cpt20+frm自适应20+frm绝对20)+配置JSON:agent开发可视化报表/图表/驾驶舱时从此选骨架,标题用表格/标题栏承载(非图表自身标题)"
}-->

# ckzl/hbfa — 报表骨架库(导航主目录)

> 开发**可视化报表 / 图表 / 驾驶舱**时,先到这里选布局骨架,再往容器里填图表/表格——不要自己从零摆格子。

## 使用方法(agent)

1. 按「组件清单→布局」先在 SkinStudio 画布页选型(或直接按本文导航挑);
2. 复制对应 `<组>/<id>.cpt|.frm` 到 reportlets 目标路径,改名;
3. 每容器三件套:**cpt**=标题行+筛选ComboBox+CC单元格图表(改 Plot 换图型);**frm**=标题报表块+筛选ComboBox+网页框(改 src 指向你的组件文件);
4. **换数据**:cpt 把 ds_c* 换业务数据集,同步改 CategoryName/ChartSummaryColumn;frm 侧只留筛选字典数据集,图表数据在组件文件里换;
5. **标题约定**:标题由表格承载(cpt 标题行 s0 / frm 标题报表块),图表自身标题已关闭(TitleVisible=false),不要重复开;
6. 同目录 `<id>.json` 是机器可读方案(容器几何/组件/栅格);

## 架构原则(2026-08-19 定稿)

- **cpt 走单元格内嵌图表**(LTA式):因为 cpt 可导出预览图片,网页框导不出来;
- **frm 走网页框组件化**(IframeEditor):工程文件体积小,组件可单元开发/单元测试,项目解耦;
- 网页框引用 `组件模板/图表组件.cpt`(含 region 模板参数),按容器复制改名后独立开发。

## 组件结构(v4)

| 引擎 | 画布 | 标题 | 筛选控件 | 组件区 | 数据 |
|---|---|---|---|---|---|
| cpt(可导出) | 120×60格,每格5px(存190500) | 容器顶部6行合并带(s=0 蓝底白字粗) | 参数面板 ComboBox(字典=region列) | 合并单元格 `<O t="CC">` 图表 | 内置数据集 ds_c* |
| frm自适应 | **1280×720**(150%缩放环境有效视口) | —(在组件内) | —(在组件内) | Center(WFitLayout)内占位 RHIframe | 组件文件自带 |
| frm绝对 | **1280×720** DesignResolution | —(在组件内) | —(在组件内) | Center(**WAbsoluteLayout**)内 BoundsWidget+RHIframe | 组件文件自带 |

> **v7 尺寸实证**:FR cpt 格宽/行高单位=FU(38100/px),`FU.valueOfPix(5,96)=190500`;旧值47625实际只有1.25px(用户实测150.5×153px的根因)。frm画布从1920×1080改1280×720=1920×1080@150%缩放的有效视口。
> **绝对布局权威编码**(用户样本 FR绝对骨架.frm 实证,v7 的 Center=WAbsoluteLayout 是错误猜想→cast 崩):**Center 恒为 WFitLayout**;绝对画布=一个 `WAbsoluteLayout` 控件(名 absolute0,带 `DesignResolution` + `WidgetScalingAttr`)作为 BoundsWidget 嵌进 body;网页框放画布内;`BodyLayoutType` 恒为 0;RHIframeAttr 占位形态=`<RHIframeAttr ...><Parameters/></RHIframeAttr>`。
> **v9 全 API 生成(铁律)**:三组骨架全部 FR Java API 从零构建 — cpt(build_cpts.js):WorkBook/WorkSheet/setColumnWidth·RowHeight(190500)/merge/TCE(标题样式 deriveFRFont+ColorBackground)/EmbeddedTableData/参数面板(FormParameterUI>WParameterLayout>ComboBox+TableDataDictionary);自适应(build_adapt_frms.js):WFitLayout body+RHIframe占位;绝对(build_abs_frms.js):body>absolute0(WAbsoluteLayout)。frm 两组 40/40 整文件 API 读回;cpt 64/64 CC 块读回(整文件读回 headless NPE 为环境限制,真文件 WorkBook34 同样 NPE)。
> **铁律文本层例外(全部实证在案,内容均 FR 序列化产出)**:①引擎 writeXML 不产出根标签/DesignerVersion 等IO层属性;②RHIframe 插件类加密无法 headless 实例化→占位块=用户权威样本属性参数化;③writeCellElement 对 BaseChartCollection 走 toString 占位(headless)→CC 内容由 FR 自己的 ReportXMLUtils$CC.writeXML 序列化(反射),按占位锚点装配;④StyleList 属 frpx 部件层 plain writeXML 不产出→内容借 FormElementCase 的 StyleList writer 序列化。
> 参数面板控件参考:用户样本 North(WParameterLayout) 内含 TextEditor/ComboBox/DateEditor/NumberEditor/ComboCheckBox/TreeComboBoxEditor/FreeButton/Label 八种绝对定位控件(见 FR绝对骨架.frm)。

## cpt · FR API 从零构建(120×60细网格·合并单元格·可导出图片)(20 套)

WorkBook/WorkSheet API:120列×60行×格值190500;每容器=标题带(6行,税蓝底白字粗体样式)+图表区(合并单元格装 API 柱形组件读回的 ChartCollection);数据=内置数据集 ds_c*(FR 编码直出);参数面板=FormParameterUI>ComboBox(字典=region 列);剩余细格全部空闲可加元素。

| 文件 | 方案名 | 栅格/规模 | 容器 | 说明 |
|---|---|---|---|---|
| [`big_top_3small.cpt`](cpt骨架/big_top_3small.cpt) | 大图上+三小下 | 120列×60行×5px格, 合并单元格布局 | 4 | 主图60%高+下三栏 |
| [`chart_form_stack.cpt`](cpt骨架/chart_form_stack.cpt) | 图表组+表单 | 120列×60行×5px格, 合并单元格布局 | 2 | 上图表下明细: 栅格1×5 |
| [`chart_left_form_right.cpt`](cpt骨架/chart_left_form_right.cpt) | 图表左+表单右 | 120列×60行×5px格, 合并单元格布局 | 2 | 60/40: 栅格5×1 |
| [`cross.cpt`](cpt骨架/cross.cpt) | 十字布局 | 120列×60行×5px格, 合并单元格布局 | 5 | 中心主图+四臂: 栅格4×4 |
| [`dashboard_6.cpt`](cpt骨架/dashboard_6.cpt) | 六宫格(底行加高) | 120列×60行×5px格, 合并单元格布局 | 6 | 上指标+中辅图+底大图: 栅格2×4 |
| [`form_left_chart_right.cpt`](cpt骨架/form_left_chart_right.cpt) | 表单左+图表右 | 120列×60行×5px格, 合并单元格布局 | 2 | 40/60: 栅格5×1 |
| [`form_two_tables.cpt`](cpt骨架/form_two_tables.cpt) | 表单双表 | 120列×60行×5px格, 合并单元格布局 | 2 | 表 表 并排: 栅格2×1 |
| [`full_single.cpt`](cpt骨架/full_single.cpt) | 单容器全屏 | 120列×60行×5px格, 合并单元格布局 | 1 | 栅格1×1; 大图独占 |
| [`kpi_band_2charts.cpt`](cpt骨架/kpi_band_2charts.cpt) | 指标带+双图 | 120列×60行×5px格, 合并单元格布局 | 3 | KPI横带+双图表: 栅格2×5 |
| [`kpi_band_quad.cpt`](cpt骨架/kpi_band_quad.cpt) | 指标带+四宫格 | 120列×60行×5px格, 合并单元格布局 | 5 | KPI带20%+2×2: 栅格2×5 |
| [`left1_right2.cpt`](cpt骨架/left1_right2.cpt) | 左主右双 | 120列×60行×5px格, 合并单元格布局 | 3 | 大图主区+右侧双辅: 栅格2×2 |
| [`left2_right1.cpt`](cpt骨架/left2_right1.cpt) | 左双右主 | 120列×60行×5px格, 合并单元格布局 | 3 | 左辅双图+右主图: 栅格2×2 |
| [`map_side_2.cpt`](cpt骨架/map_side_2.cpt) | 地图+侧栏双图 | 120列×60行×5px格, 合并单元格布局 | 3 | 大图60%+右栏40%: 栅格5×2 |
| [`mixed_dashboard.cpt`](cpt骨架/mixed_dashboard.cpt) | 综合看板 | 120列×60行×5px格, 合并单元格布局 | 5 | KPI+地图+双辅+明细: 栅格5×20 |
| [`quad.cpt`](cpt骨架/quad.cpt) | 四宫格 | 120列×60行×5px格, 合并单元格布局 | 4 | 经典2×2 |
| [`side_nav_right.cpt`](cpt骨架/side_nav_right.cpt) | 右侧窄栏 | 120列×60行×5px格, 合并单元格布局 | 3 | 主区75%+右窄栏25%: 栅格4×10 |
| [`three_cols.cpt`](cpt骨架/three_cols.cpt) | 宽窄三栏 | 120列×60行×5px格, 合并单元格布局 | 3 | 40/30/30 三竖栏: 栅格10×1 |
| [`top_banner_3charts.cpt`](cpt骨架/top_banner_3charts.cpt) | 横幅+三图 | 120列×60行×5px格, 合并单元格布局 | 4 | 顶部横幅20%+下三栏 |
| [`two_cols.cpt`](cpt骨架/two_cols.cpt) | 左右双栏 | 120列×60行×5px格, 合并单元格布局 | 2 | 栅格2×1 |
| [`two_rows.cpt`](cpt骨架/two_rows.cpt) | 上下分栏 | 120列×60行×5px格, 合并单元格布局 | 2 | 上图表下表单: 栅格1×2 |

## FRM · 自适应(FR API 从零构建: Center=WFitLayout, 画布1280×720)(20 套)

RHIframe 占位直接挂 Center(WFitLayout)内;画布=1280×720(1920×1080@150%缩放的有效视口);设计器里选组件路径即挂 图表组件-*.cpt。

| 文件 | 方案名 | 栅格/规模 | 容器 | 说明 |
|---|---|---|---|---|
| [`frm_banner_grid.frm`](frm自适应骨架/frm_banner_grid.frm) | FRM横幅+四图网格 | 5占位网页框(RHIframe) | 5 | 自适应: BodyLayoutType=0 等比 / KPI横幅+2×2 |
| [`frm_big_top_3small.frm`](frm自适应骨架/frm_big_top_3small.frm) | FRM大图上三小下 | 4占位网页框(RHIframe) | 4 | 自适应: BodyLayoutType=0 等比 / 60/40 |
| [`frm_chart_form_stack.frm`](frm自适应骨架/frm_chart_form_stack.frm) | FRM图表组+表单 | 2占位网页框(RHIframe) | 2 | 自适应: BodyLayoutType=0 等比 / 上图下表 |
| [`frm_cross.frm`](frm自适应骨架/frm_cross.frm) | FRM十字布局 | 5占位网页框(RHIframe) | 5 | 自适应: BodyLayoutType=0 等比 / 中心主图+四臂 |
| [`frm_dashboard_6.frm`](frm自适应骨架/frm_dashboard_6.frm) | FRM六宫格 | 6占位网页框(RHIframe) | 6 | 自适应: BodyLayoutType=0 等比 / 上指标+中辅+底大图 |
| [`frm_dashboard_8.frm`](frm自适应骨架/frm_dashboard_8.frm) | FRM八宫格 | 8占位网页框(RHIframe) | 8 | 自适应: BodyLayoutType=0 等比 / 4×2 |
| [`frm_executive.frm`](frm自适应骨架/frm_executive.frm) | FRM高管看板 | 4占位网页框(RHIframe) | 4 | 自适应: BodyLayoutType=0 等比 / KPI+地图+仪表+多层饼 |
| [`frm_form_2tables.frm`](frm自适应骨架/frm_form_2tables.frm) | FRM表单双表 | 2占位网页框(RHIframe) | 2 | 自适应: BodyLayoutType=0 等比 / 表表并排 |
| [`frm_full.frm`](frm自适应骨架/frm_full.frm) | FRM单容器全屏 | 1占位网页框(RHIframe) | 1 | 自适应: BodyLayoutType=0 等比 / 百分比100% |
| [`frm_hero_right_list.frm`](frm自适应骨架/frm_hero_right_list.frm) | FRM主图左+右列表带 | 4占位网页框(RHIframe) | 4 | 自适应: BodyLayoutType=0 等比 / 60+40×3 |
| [`frm_kpi_band_2charts.frm`](frm自适应骨架/frm_kpi_band_2charts.frm) | FRM指标带+双图 | 3占位网页框(RHIframe) | 3 | 自适应: BodyLayoutType=0 等比 / KPI带20%+双图 |
| [`frm_kpi_form_chart.frm`](frm自适应骨架/frm_kpi_form_chart.frm) | FRM指标带+表单图表 | 3占位网页框(RHIframe) | 3 | 自适应: BodyLayoutType=0 等比 / KPI带+左表右图 |
| [`frm_kpi_quad.frm`](frm自适应骨架/frm_kpi_quad.frm) | FRM指标带+四宫格 | 5占位网页框(RHIframe) | 5 | 自适应: BodyLayoutType=0 等比 / KPI带+2×2 |
| [`frm_left1_right2.frm`](frm自适应骨架/frm_left1_right2.frm) | FRM左主右双 | 3占位网页框(RHIframe) | 3 | 自适应: BodyLayoutType=0 等比 / 大图+右侧双辅 |
| [`frm_map_side_2.frm`](frm自适应骨架/frm_map_side_2.frm) | FRM地图+侧栏双图 | 3占位网页框(RHIframe) | 3 | 自适应: BodyLayoutType=0 等比 / 60+40×2 |
| [`frm_quad.frm`](frm自适应骨架/frm_quad.frm) | FRM四宫格 | 4占位网页框(RHIframe) | 4 | 自适应: BodyLayoutType=0 等比 / 2×2 |
| [`frm_side_nav_left.frm`](frm自适应骨架/frm_side_nav_left.frm) | FRM左窄边栏 | 4占位网页框(RHIframe) | 4 | 自适应: BodyLayoutType=0 等比 / 20%边栏+80%内容 |
| [`frm_three_cols.frm`](frm自适应骨架/frm_three_cols.frm) | FRM宽窄三栏 | 3占位网页框(RHIframe) | 3 | 自适应: BodyLayoutType=0 等比 / 40/30/30 |
| [`frm_two_cols.frm`](frm自适应骨架/frm_two_cols.frm) | FRM左右双栏 | 2占位网页框(RHIframe) | 2 | 自适应: BodyLayoutType=0 等比 / 50/50 |
| [`frm_two_rows.frm`](frm自适应骨架/frm_two_rows.frm) | FRM上下分栏 | 2占位网页框(RHIframe) | 2 | 自适应: BodyLayoutType=0 等比 / 上图下表 |

## FRM · 绝对(FR API构建, 权威样本同构: Center=WFitLayout > absolute0画布)(20 套)

结构=用户设计器权威样本 FR绝对骨架.frm 同构:Center 恒为 WFitLayout,绝对画布是一个 WAbsoluteLayout 控件(absolute0+DesignResolution 1280×720)嵌在 body 里,网页框放画布内;BodyLayoutType 恒为 0;全 API 生成+20/20 整文件 API 读回,RHIframe 占位=用户样本属性参数化。

| 文件 | 方案名 | 栅格/规模 | 容器 | 说明 |
|---|---|---|---|---|
| [`frma_banner_grid.frm`](frm绝对骨架/frma_banner_grid.frm) | 绝对·横幅+四图网格 | 5占位网页框(RHIframe) | 5 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_big_top_3small.frm`](frm绝对骨架/frma_big_top_3small.frm) | 绝对·大图上三小下 | 4占位网页框(RHIframe) | 4 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_chart_form_stack.frm`](frm绝对骨架/frma_chart_form_stack.frm) | 绝对·图表组+表单 | 2占位网页框(RHIframe) | 2 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_cross.frm`](frm绝对骨架/frma_cross.frm) | 绝对·十字布局 | 5占位网页框(RHIframe) | 5 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_dashboard_6.frm`](frm绝对骨架/frma_dashboard_6.frm) | 绝对·六宫格 | 6占位网页框(RHIframe) | 6 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_dashboard_8.frm`](frm绝对骨架/frma_dashboard_8.frm) | 绝对·八宫格 | 8占位网页框(RHIframe) | 8 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_executive.frm`](frm绝对骨架/frma_executive.frm) | 绝对·高管看板 | 4占位网页框(RHIframe) | 4 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_form_2tables.frm`](frm绝对骨架/frma_form_2tables.frm) | 绝对·表单双表 | 2占位网页框(RHIframe) | 2 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_full.frm`](frm绝对骨架/frma_full.frm) | 绝对·单容器全屏 | 1占位网页框(RHIframe) | 1 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_hero_right_list.frm`](frm绝对骨架/frma_hero_right_list.frm) | 绝对·主图左+右列表带 | 4占位网页框(RHIframe) | 4 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_kpi_band_2charts.frm`](frm绝对骨架/frma_kpi_band_2charts.frm) | 绝对·指标带+双图 | 3占位网页框(RHIframe) | 3 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_kpi_form_chart.frm`](frm绝对骨架/frma_kpi_form_chart.frm) | 绝对·指标带+表单图表 | 3占位网页框(RHIframe) | 3 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_kpi_quad.frm`](frm绝对骨架/frma_kpi_quad.frm) | 绝对·指标带+四宫格 | 5占位网页框(RHIframe) | 5 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_left1_right2.frm`](frm绝对骨架/frma_left1_right2.frm) | 绝对·左主右双 | 3占位网页框(RHIframe) | 3 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_map_side_2.frm`](frm绝对骨架/frma_map_side_2.frm) | 绝对·地图+侧栏双图 | 3占位网页框(RHIframe) | 3 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_quad.frm`](frm绝对骨架/frma_quad.frm) | 绝对·四宫格 | 4占位网页框(RHIframe) | 4 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_side_nav_left.frm`](frm绝对骨架/frma_side_nav_left.frm) | 绝对·左窄边栏 | 4占位网页框(RHIframe) | 4 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_three_cols.frm`](frm绝对骨架/frma_three_cols.frm) | 绝对·宽窄三栏 | 3占位网页框(RHIframe) | 3 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_two_cols.frm`](frm绝对骨架/frma_two_cols.frm) | 绝对·左右双栏 | 2占位网页框(RHIframe) | 2 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |
| [`frma_two_rows.frm`](frm绝对骨架/frma_two_rows.frm) | 绝对·上下分栏 | 2占位网页框(RHIframe) | 2 | 绝对: BodyLayoutType=1, px=%×1920×1080 / 绝对布局: BoundsWidget 像素 = 百分比 × 1920×1080 |

## 组件模板(网页框引用目标, 19 种图表)

| 文件 | 图表 | 数据集 | 说明 |
|---|---|---|---|
| [`图表组件-柱形.cpt`](组件模板/图表组件-柱形.cpt) | 柱形 | region+amount+amount2 | 类别列+多值列=多系列(MoreNameCDDefinition) |
| [`图表组件-饼图.cpt`](组件模板/图表组件-饼图.cpt) | 饼图 | region+amount | 系列列+单值列(OneValueCDDefinition) |
| [`图表组件-折线.cpt`](组件模板/图表组件-折线.cpt) | 折线 | month+amount×3 | 月份类别+3系列 |
| [`图表组件-组合.cpt`](组件模板/图表组件-组合.cpt) | 组合 | month+amount+amount2 | 柱+线子图各自 DefinitionMap |
| [`图表组件-仪表盘.cpt`](组件模板/图表组件-仪表盘.cpt) | 仪表盘 | region+amount+amount2 | 不绑数据集,值/目标=公式 SUM(ds.select(..)) |
| [`图表组件-地图.cpt`](组件模板/图表组件-地图.cpt) | 地图 | 省+系列+值 / 地点+supplier | 区域层+点层(matchResult 城市→省) |
| [`图表组件-钻取地图.cpt`](组件模板/图表组件-钻取地图.cpt) | 钻取地图 | 城市+amount | 底层区县/城市列须匹配地图区域名 |
| [`图表组件-面积.cpt`](组件模板/图表组件-面积.cpt) | 面积 | region+amount+amount2 | FR权威生成路线 |
| [`图表组件-雷达.cpt`](组件模板/图表组件-雷达.cpt) | 雷达 | region+amount+amount2 | FR权威生成(类别=轴) |
| [`图表组件-散点.cpt`](组件模板/图表组件-散点.cpt) | 散点 | region+amount+amount2 | FR权威生成 |
| [`图表组件-漏斗.cpt`](组件模板/图表组件-漏斗.cpt) | 漏斗 | region+amount | FR权威生成(阶段+值) |
| [`图表组件-多层饼.cpt`](组件模板/图表组件-多层饼.cpt) | 多层饼 | region+amount | FR权威生成 |
| [`图表组件-矩形树图.cpt`](组件模板/图表组件-矩形树图.cpt) | 矩形树图 | region+amount | FR权威生成(类别分层) |
| [`图表组件-词云.cpt`](组件模板/图表组件-词云.cpt) | 词云 | region+amount | FR权威生成(词名+数值) |
| [`图表组件-结构树.cpt`](组件模板/图表组件-结构树.cpt) | 结构树 | region+amount | FR权威生成 |
| [`图表组件-热力图.cpt`](组件模板/图表组件-热力图.cpt) | 热力图 | 省+amount+amount2 | FR权威生成(省名列) |
| [`图表组件-甘特.cpt`](组件模板/图表组件-甘特.cpt) | 甘特 | region+amount | FR权威生成骨架(业务需配起止时间列) |
| [`图表组件-箱线.cpt`](组件模板/图表组件-箱线.cpt) | 箱线 | region+amount+amount2 | FR权威生成 |
| [`图表组件-气泡.cpt`](组件模板/图表组件-气泡.cpt) | 气泡 | region+amount+amount2 | FR权威生成 |

> 前 7 种=真实报表样本手术,后 12 种=FR 引擎 Nashorn 权威生成(`new VanChart(plot)`+`setFilterDefinition`+`writeXML`);
> 19/19 过 FR ChartCollection 回读(plot 类型全对)。条形图无独立 Plot=设计器里柱形切方向。

## 再生成 / 维护

- 校验:`verify_skeletons.py`(结构/绑定/边界/顺序) + `verify_components.py`(7组件绑定) + `verify_comp_embed.js`(FR类回读)
- 新增布局 → 改 canvas.json → 重跑两脚本 → 本 README 重生成(读 JSON 直出,不会漂移)

> ⚠️ frm 布局编码(实测):body 容器恒为 `WFitLayout`,自适应/绝对仅由 `BodyLayoutType` 表达(0/1);
> 组件 Widget 必须插在 Center 的 `ShowBookmarks` 等属性节点**之前**,否则设计器打开为空画布。

