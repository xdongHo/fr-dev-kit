<!--
KB_INDEX: {
  "title": "FR11 · 二次开发与JS API · 图表 / 大屏 / FVS",
  "stage": "fr11-knowledge",
  "tags": [
    "FR11",
    "JS API",
    "二次开发"
  ],
  "keywords": [
    "图表接口",
    "FVS",
    "duchamp",
    "轮播",
    "跑马灯"
  ],
  "summary": "图表 JS 接口、FVS(duchamp) 大屏、轮播与跑马灯条目（35 条 doc-view 条目，ID 1741~5131）；js_api_summary.md 拆分页 4/10，条目原样保留。"
}
-->

# FR11 知识库 · 二次开发与JS API · 图表 / 大屏 / FVS

> 数据源：`D:\fr11_docs\doc-view-{did}.html`（FR11 离线文档，gb2312）。
> 本页为 [js_api_summary.md](js_api_summary.md) 2026-09-29 主题拆分页 **4/10**；条目内容原样搬移、未做改写；归类方法：按条目标题关键词启发式（延续建库打分思路），页内保持原 doc-view ID 升序。
> 本页收录 **35 条**（ID 1741~5131，非连续）。

## 文档条目

> 去重收敛（2026-09-29）：本页 1 条 FVS 条目（doc-view-4904）已收敛为指针，全文统一见 fvs_dashboard_summary.md（FVS 主题权威收录）。


### doc-view-1741｜JS实现普通报表中自动滚屏/跑马灯效果
- **doc-view ID**：1741
- **核心概念**：报表浏览页面上放置很多图表时，由于内容过多，超出了浏览器窗口的大小导致内容展示不全，这时可以使用滚屏或跑马灯来实现内容全部展示，如下图所示： 给报表添加「加载结束」JS 事件实现滚屏和跑马灯的效果。 跑马灯的详细接口介绍可参见：跑马灯接口
- **关键API/代码**：SQL: SELECT * FROM 销量；JS: _g().startMarquee()；JS: _g().startMarquee({；公式: startMarquee()；公式: startMarquee({                
stopOnHover:false    
})；公式: startMarquee({        
 offset: 2,        
 interval: 0.3,        
 stopOnHover:true    
})

#### 常见问法：表格/图表内容太多一次只显示一部分，怎么向上滚动展示全部（拓展滚动/自动滚动）
> 即"跑马灯/滚屏"：普通报表 doc-1741（加载结束 JS，`_g().startMarquee()`）+ doc-3752 跑马灯简介；
> 决策报表版 doc-2393（决策报表应用/06_决策报表JS实例_中）。社区 qid 231590 同型（产线数量不固定、一次最多展示
> 9 个、向上滚动看全部）。注意与"冻结表头滚动位置恢复"（ckzl/lc/10_前端滚动与焦点恢复.md）不同题。
### doc-view-1746｜JS实现首尾相接的跑马灯
- **doc-view ID**：1746
- **核心概念**：在进行一些集团新闻内容展示时，可能需要一种首尾相接的跑马灯滚动效果，如下图所示： 单元格中添加 html 代码，用 html 显示内容，再配合 JS 实现滚动效果。 打开%FR_HOME%\webroot\WEB-INF\reportlets\demo\form\以html实现纵向跑马灯特效.cpt报表
- **关键API/代码**：JS: getWidgetByName('report0')；JS: gotoPage(1, "{}", true)；公式: REPLACE(D3, ",", "<br /><br />")；公式: setTimeout(function()；公式: getElementById("demo")；公式: getElementById("demo1")
### doc-view-1977｜JS实现普通报表自动轮播
- **doc-view ID**：1977
- **核心概念**：在实际工作中，需要实现多张报表自动轮播效果，但区别于 自动切换分页效果 及 图表手动切换。实际效果如下图所示： 给报表添加「加载结束」事件，通过 JavaScript 延时函数，页面加载完成后停留一定时间自动跳转到另一页面来实现自动轮播特效。 准备 3 个需要轮播的模板。
- **关键API/代码**：公式: setTimeout(function()
### doc-view-2300｜统一切换轮播图表接口
- **doc-view ID**：2300
- **核心概念**：某些场景下，需要让一张报表内的多个轮播图表同时切换。那么该如何实现呢？效果如下图所示： 按钮添加点击事件，通过 JS 脚本调用接口统一切换轮播图表，切换成功后，所有的轮播图表的计时器计时归 0。 chart.unifiedSwitchCarouselChart(direction)direction 为可选参数，表示图表切换的方向
- **关键API/代码**：SQL: SELECT * FROM 销量；公式: nifiedSwitchCarouselChart(direction)；公式: nifiedSwitchCarouselChart(1)
### doc-view-2317｜图表刷新接口
- **doc-view ID**：2317
- **核心概念**：点击按钮可以刷新普通报表或决策报表中的图表，以普通报表为例，效果如下图所示： 通过FR.Chart.WebUtils.getChart("chartID").dataRefresh()获取要刷新的图表对象，其中chartID为图表块名称。 注1：该接口不支持扩展图表。
- **关键API/代码**：SQL: SELECT * FROM 销量 limit ${ int (RAND()*40) }；公式: getChart("chartID")；公式: dataRefresh()；公式: RAND()；公式: getChart("A3")
### doc-view-2331｜图表显示部分系列接口
- **doc-view ID**：2331
- **核心概念**：当图表系列较多时，用户希望可以自己设置哪些系列显示，哪些系列不显示。以决策报表为例，实现效果如下图： 通过FR.Chart.WebUtils.getChart("chartID").getChartWithIndex(chartIndex).setSeriesVisible()获取需要显示的系列图表对象，在表单中显示这些系列。 注1：该接口不支持扩展图表。
- **关键API/代码**：SQL: SELECT * FROM 销量，如下图所示：；公式: getChart("chartID")；公式: getChartWithIndex(chartIndex)；公式: setSeriesVisible()；公式: getChart("chart0")；公式: getChartWithIndex(0)
### doc-view-2351｜JS实现暂停和继续轮播报表
- **doc-view ID**：2351
- **核心概念**：在开发大屏报表的时候，有时会让多张大屏轮播，在特定的情况下能停止轮播。如下图所示，两张报表轮播，当鼠标移入报表时，停止轮播。 可以通过 JavaScript 延时函数使页面在规定时间后执行跳转到另一不同页面来实现轮播，JS事件中加上鼠标移入移出停止轮播的语句
- **关键API/代码**：SQL: SELECT * FROM 销量；公式: time()；公式: setTimeout(function()；公式: mouseover(function()；公式: clearTimeout(timer)；公式: mouseleave(function()
### doc-view-2393｜JS实现决策报表中滚屏/跑马灯效果
- **doc-view ID**：2393
- **核心概念**：普通报表可以参考 JS实现自动滚屏/跑马灯效果 实现跑马灯效果，决策报表中报表块同样希望实现跑马灯效果，如下图所示： 通过给报表块添加「初始化后」 JS 事件实现隐藏滚动条的跑马灯的效果。 跑马灯的详细接口介绍可参见：跑马灯接口
- **关键API/代码**：SQL: SELECT * FROM 销量，如下图所示：；JS: _g().getWidgetByName('report0').startMarquee()；JS: _g().getWidgetByName('report0').stopMarquee()；JS: getWidgetByName('report0')；JS: getWidgetByName('REPORT0')；公式: setTimeout(function()
### doc-view-2624｜[通用]JS自动轮播Tab块
- **doc-view ID**：2624
- **核心概念**：可以实现 Tab 块自动跳转效果。 通过 showCardByIndex(Number cardID) 可以实现跳转到指定 Tab 块 cardID  Number  必填，显示的 Tab 序号，从 0 开始
- **关键API/代码**：JS: _g().getWidgetByName("tabpane0").getShowIndex()；JS: _g().getWidgetByName('tabpane0').showCardByIndex(0)；JS: _g().getWidgetByName('tabpane0').showCardByIndex(aa+1)；JS: getWidgetByName("tabpane0")；JS: getWidgetByName('tabpane0')；公式: showCardByIndex(Number cardID)
### doc-view-3043｜JS实现大屏旋转星空背景
- **doc-view ID**：3043
- **核心概念**：大屏场景下给决策报表添加一个酷炫的旋转星空效果。 采用插入动态 GIF 背景图的方式是无法进行自适应的，所以直接用 JS 代码来制作效果更好。 注：需先将 body 背景设置为「自定义>没有背景」。
- **关键API/代码**：公式: background()；公式: prepend('<canvas id="canvas" style="position:absolute;z-index:-2;"></canvas>')；公式: getElementById('canvas')；公式: getContext('2d')；公式: createElement('canvas')；公式: createRadialGradient(half, half, 0, half, half, half)
### doc-view-3178｜JS实现大屏旋转网格背景
- **doc-view ID**：3178
- **核心概念**：大屏场景下，给决策报表添加一个酷炫的大屏旋转网格背景，如下图所示： 采用插入动态 GIF 背景图的方式是无法完美自适应的，所以直接用 JS 代码来制作效果更好。 点击设计器左上角「文件>新建决策报表」。将 body 背景设置为「自定义>没有背景」。
- **关键API/代码**：公式: prepend('<canvas id="canvas" style="position:absolute;z-index:-2;"></canvas>')；公式: sqrt(5)；公式: toLowerCase()；公式: indexOf('firefox')；公式: floor(duration / frameDuration)；公式: getElementById("canvas")
### doc-view-3343｜JS实现文字动态轮播特效
- **doc-view ID**：3343
- **核心概念**：实现文字 2.5D 动态轮播效果，如下图所示： 报表中引用外部 JS 和 CSS 文件，利用公式函数解析，实现轮播效果。 1）将压缩包 Carousel.rar 中的文件解压后放到设计器安装目录%FR_HOME%\webapps\webroot\WEB-INF\classes\com\fr\function下。
- **关键API/代码**：SQL: SELECT * FROM CUSTOMER；公式: Carousel(ds1.select("CUSTOMERNAME")
### doc-view-3670｜轮播插件
- **doc-view ID**：3670
- **核心概念**：轮播显示当前目录打开的模板，如下图所示： 点击下载插件：轮播插件 设计器插件安装方法参照：设计器插件管理
### doc-view-3744｜场景地图场景切换接口
- **doc-view ID**：3744
- **核心概念**：扩展图表插件新版本新增「场景地图跳转接口」，报表中的其他元素可以通过该接口跳转到场景地图的不同场景。 注：该接口仅支持扩展图表。 例如点击柱形图不同分类的柱形，场景地图会跳转到该分类对应的场景，如下图所示：
- **关键API/代码**：公式: getChartBridge({name:'chart0'})；公式: getChartBridge({name:'A1', ecName:'report0'})；公式: getChartBridge({name:'Float1'})；公式: getChartBridge({name:'A1'})；公式: switchScene({
 *       direction:'next', // 可选。切换方向。 下一个(右箭头)；公式: switchScene({index:0})
### doc-view-3752｜跑马灯简介
- **doc-view ID**：3752
- **核心概念**：滚动的消息文本或者表格内容一般被称为跑马灯，如下图所示。跑马灯有比较广泛的应用场景，尤其是在看板和大屏中： 某个区域内容较多但布局有限，就可以通过跑马灯的形式呈现 表格内容较多，可以通过表格滚动将内容全部展示
### doc-view-3936｜键盘事件控制场景地图切换场景
- **doc-view ID**：3936
- **核心概念**：用户实际使用 场景地图 时，可能需要通过翻页笔或者键盘上下键来控制场景切换，那么该如何实现呢？ 大屏场景下，通过给决策报表的 body 添加初始化后 JavaScript 事件，给场景地图绑定键盘的上下键事件, 监听上键跳转上一个场景, 下键跳转下一个场景。 注：支持在场景地图轮播的同时使用键盘事件控制场景切换。
- **关键API/代码**：JS: _g().options.form.getWidgetByName("tabpane0").showCardByIndex(0)；JS: _g().options.form.getWidgetByName("tabpane0").showCardByIndex(1)；JS: getWidgetByName("tabpane0")；公式: getChartBridge({name:'chart0'})；公式: log('up')；公式: switchScene({direction:'previous'})
### doc-view-4299｜跑马灯接口
- **doc-view ID**：4299
- **核心概念**：和 10.0 区别：** 10.0 支持，10.0.19 及之后版本支持 注1：用以下接口实现的跑马灯效果，不支持通过「决策报表内报表块刷新插件」实现刷新。
- **关键API/代码**：JS: _g().startMarquee()；JS: _g().getWidgetByName('report0').startMarquee()；JS: _g().startMarquee({；JS: _g().getWidgetByName('report0').startMarquee({；JS: _g().stopMarquee()；JS: _g().getWidgetByName('report0').stopMarquee()
### doc-view-4347｜FVS大屏支持的JS事件说明
- **doc-view ID**：4347
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关功能。 11.0.6-V1.5.0 新增六类「控件」组件，新增控件支持的事件与接口
- **关键API/代码**：JS: getWidgetByName("组件1")；公式: openAutoTooltip()；公式: on("storychange", (current)；公式: getWidgetByName("组件1")；公式: createElement("audio")；公式: appendChild(audio)
- **FR11版本要点**：JAR包插件版本功能变动 11.0.6-V1.5.0
### doc-view-4468｜ECharts图表集成插件
- **doc-view ID**：4468
- **核心概念**：ECharts 是一个基于 JavaScript 的开源可视化图表库。在使用 FineReport 时，当基础图表的通用配置不足以满足用户需求时，用户可安装「echarts图表插件」通过代码自定义个性化图表。 且 FineReport 在支持用户使用 ECharts 开源接口的同时，也支持引用模板中的数据集，实现参数传递、与其他组件交互等功能，帮助用户在 FineReport 中更好的运用可视化图表
- **关键API/代码**：公式: getData()
### doc-view-4496｜FVS自定义模型组件
- **doc-view ID**：4496
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关功能。 新增：数据图层新增「数据预警」，可设置模型预警条件、模型预警内容及标签。详情参见 5.3 节 优化：模型选中时，不再自动切换视角，可通过点击新增的「聚焦」按钮切换视角。详情参见 4.4 节
- **FR11版本要点**：报表服务器版本插件版本功能变动 11.0.2V1.2.0-；11.0.2V1.2.0- 11.0.5V1.4.0优化：数据图层中，标签可设置多个字段，并支持富文本自定义标签内容。详情参见 5.1、5.2 节；新增：数据图层新增「数据预警」，可设置模型预警条件、模型预警内容及标签。详情参见 5.3 节 11.0.6V1.5.0新增：三维场景属性中，新增相机景深效果，新增三维图像处理功能。详情参见 3.3 节
### doc-view-4515｜图表导出接口
- **doc-view ID**：4515
- **核心概念**：11.0.2新增：开放官方接口 chart.saveAsImage() 当图表勾选了「图表特效>交互属性>工具栏」中的导出图片时，在图表的右上角会出现「导出」图标，点击即可导出为图片。如下图所示： 但有时为了图表更美观，不想要开启工具栏，又希望导出图表，应该怎么做呢？预期效果如下图所示：
- **关键API/代码**：JS: _g().getParameterContainer().getWidgetByName("index").getValue()；JS: getWidgetByName("index")；公式: saveAsImage()；公式: getChart(chartID)；公式: getChartWithIndex(chartIndex)；公式: getParameterContainer()
- **FR11版本要点**：报表服务器版本功能变动 11.0.2新增：开放官方接口 chart.saveAsImage()
### doc-view-4733｜FVS界面概览
- **doc-view ID**：4733
- **核心概念**：V1.9.0优化：支持输出「内置数据集」 新增：模板右上角新增「关闭模板」按钮 11.0.6-V 1.7.0优化：组件列表栏交互优化，可收缩展开文字提示效果
- **FR11版本要点**：JAR包插件版本 功能变更 11.0.9；新增：模板右上角新增「关闭模板」按钮 11.0.6-V 1.7.0优化：组件列表栏交互优化，可收缩展开文字提示效果；11.0.6-V 1.7.0优化：组件列表栏交互优化，可收缩展开文字提示效果 11.0.2-V1.2.0
### doc-view-4770｜FVS自定义模型组件的光源和投影
- **doc-view ID**：4770
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关功能。 优化自定义模型组件的光源和投影效果 V1.11.0 版本之前，在上传模型处可选择「光源」模型，给场景增加光源效果。如下图所示：
- **FR11版本要点**：报表服务器版本 插件版本功能变动 11.0.9V1.11.0
### doc-view-4773｜自定义高德地图GIS图层
- **doc-view ID**：4773
- **核心概念**：地图配置>自定义GIS图层，新增「高德地图」自定义图层功能 11.0.6 版本及之后的设计器平台，地图配置 支持自定义高德地图 GIS 图层，并在设计器地图模板中应用。如下图所示： 注：暂不支持直接在设计器「地图类型>GIS图层」处自定义。
- **FR11版本要点**：报表服务器版本功能变动 11.0.6；### 1.2 功能简介 11.0.6 版本及之后的设计器平台，地图配置 支持自定义高德地图 GIS 图层，并在设计器地图模板中应用。如下图所示：
### doc-view-4834｜FVS大屏编辑模式插件更新日志
- **doc-view ID**：4834
- **核心概念**：插件下载地址：FVS大屏编辑模式 插件安装请参见文档：FVS插件安装及配置要求 适配的报表服务器版本
- **关键API/代码**：公式: setTabVisible()；公式: getShowIndex()；公式: showCardByIndex()
- **FR11版本要点**：适配的报表服务器版本 11.0.9；#### 支持将FRM的扩展图表复制到FVS 满足设计器 11.0.13 版本，FVS大屏编辑模式插件 V1.12.0 版本的条件时，支持将决策报表（FRM）中的扩展图表复制到大屏报表（FVS）中。；#### 支持将FRM的图表和表格复制到FVS 满足设计器 11.0.13 版本，FVS大屏编辑模式插件 V1.11.1 版本的条件时，支持将决策报表（FRM）中的图表块、报表块复制到大屏报表（FVS）中。
### doc-view-4904｜FVS大屏学习路径
- **doc-view ID**：4904
- **已收敛指针**：FVS 专题条目全文见 [fvs_dashboard_summary.md](../../fvs-dashboard大屏/references/fvs_dashboard_summary.md#doc-view-4904)（FVS 主题权威收录）；本页不再重复原文（2026-09-29 去重收敛）。

### doc-view-4919｜FVS模板定时刷新
- **doc-view ID**：4919
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关功能。 许多用户在使用 FVS 大屏模板展示时，由于数据的实时性较高，希望时刻保持模板展示最新数据，但是挨个设置组件的监控刷新效率太低，则可以通过设置「模板定时刷新」来实现模板整体的刷新。 注：上图模板来源于 公司简介 。
- **关键API/代码**：公式: setInterval(()；公式: reload()
- **FR11版本要点**：报表服务器版本 插件版本功能变动 11.0.6V1.7.2新增「模板定时刷新」功能，可设置模板预览时按照刷新间隔时间进行整体刷新
### doc-view-4939｜FVS大屏JS接口汇总
- **doc-view ID**：4939
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 大屏模板相关 JS 接口。 11.0.6-V1.5.0新增六类「控件」组件，新增控件支持的事件与接口 11.0.7-V1.8.0FVS 补充支持决策报表支持的所有接口
- **关键API/代码**：公式: getShowIndex()；公式: showCardByIndex()；公式: setTabVisible()；公式: ajax()；公式: getCell(row, col)；公式: getRow(index)
- **FR11版本要点**：11.02021-11-15V1.0.0 - 11.0.6-V1.5.0新增六类「控件」组件，新增控件支持的事件与接口；11.0.6-V1.5.0新增六类「控件」组件，新增控件支持的事件与接口 11.0.7-V1.8.0FVS 补充支持决策报表支持的所有接口；11.0.7-V1.8.0FVS 补充支持决策报表支持的所有接口 11.0.9-V1.9.1FVS轮播器组件支持接口 getShowIndex()、showCardByIndex()
### doc-view-4941｜FVS页面接口
- **doc-view ID**：4941
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关接口。 V1.8.0支持接口 this，可获取当前的组件对象，获取后可以使用组件的方法和属性 支持接口 getAllWidgets，可获取当前页所有组件
- **关键API/代码**：JS: getWidgetByName(name)；JS: getWidgetByName("表格")；JS: getWidgetByName("组件1")；JS: getWidgetByName("柱形图")；JS: getWidgetByName("组件")；公式: getValue()
- **FR11版本要点**：11.0V1.0.0- 11.0.7；支持接口 getAllWidgets，可获取当前页所有组件 11.0.9V1.9.1refresh 接口支持传参，详情参见本文 refresh 表格说明
### doc-view-4943｜JS实现FVS组件的隐藏或显示
- **doc-view ID**：4943
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关功能。 FVS 大屏模板中通常使用 轮播器组件 实现多个组件的切换展示，但是轮播器的样式或者功能在某些场景下存在限制。 这时我们可以通过 JS 实现预览时手动控制组件的隐藏或显示，预期效果下图所示：
- **关键API/代码**：JS: getWidgetByName("组件名称")；JS: getWidgetByName("柱形图")；JS: getWidgetByName("饼图")；JS: getWidgetByName("折线图")；公式: getWidgetByName("组件名称")；公式: setVisible(false)
- **FR11版本要点**：报表服务器版本插件版本功能变动 11.0.6V1.8.0所有组件均支持 setVisible、isVisible 接口，可通过 JS 实现对当前页面上组件的隐藏或显示
### doc-view-4955｜FVS三维组件接口
- **doc-view ID**：4955
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关接口。 方法getDataLayers()获取三维组件所有的数据图层 **     参数**--
- **关键API/代码**：JS: getWidgetByName("三维组件名称")；公式: getDataLayers()；公式: getWidgetByName("三维组件名称")；公式: getDataLayerByName()；公式: getDataLayerByName("图层1")
### doc-view-4975｜FVS自定义模型组件地面特效
- **doc-view ID**：4975
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关功能。 自定义模型「场景属性>环境>地面」优化，新增「地面特效」设置 在自定义模型组件场景设置中，开启地面，给地面添加地面特效，通过设置「底面贴图」和「扫光贴图」，可实现更多酷炫的动态效果。
- **FR11版本要点**：报表服务器版本 插件版本功能变动 11.0.9V1.11.0
### doc-view-5004｜FVS轮播器组件接口
- **doc-view ID**：5004
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关接口。 方法getShowIndex()获取轮播器组件正在展示的 Tab 页的索引 **     参数**--
- **关键API/代码**：JS: getWidgetByName('轮播器1')；JS: getWidgetByName("轮播器1_页面1")；JS: getWidgetByName('轮播器1_页面1')；JS: getWidgetByName("index")；公式: getShowIndex()；公式: showCardByIndex()
- **FR11版本要点**：报表服务器版本插件版本功能变动 11.0.9V1.9.1FVS轮播器组件 支持接口 getShowIndex()、showCardByIndex()；11.0.9V1.9.1FVS轮播器组件 支持接口 getShowIndex()、showCardByIndex() 11.0.9V1.10.1支持接口 setTabVisible
### doc-view-5103｜FVS大屏报表接口汇总
- **doc-view ID**：5103
- **核心概念**：FVS 大屏报表接口适用于安装了「FVS大屏编辑模式」插件的用户，其他类型的设计模式不可用。 接口一般都用在FVS 大屏报表的 JS事件 中。如下图所示： 小节内容简介文档链接
### doc-view-5131｜FVS实现音频播放与暂停
- **doc-view ID**：5131
- **核心概念**：适用场景：安装了「FVS大屏编辑模式」插件的用户，可参考本文了解 FVS 模板的相关功能。 预览 FVS 大屏时，自动播放背景音乐。 FVS 实现点击按钮播放/暂停音频。
- **关键API/代码**：JS: getWidgetByName("标题1_页面1")；公式: createElement("audio")；公式: appendChild(audio)；公式: getElementById("audio")；公式: play()；公式: pause()

---

> 本页收录 doc-view ID（35 条）：1741、1746、1977、2300、2317、2331、2351、2393、2624、3043、3178、3343、3670、3744、3752、3936、4299、4347、4468、4496、4515、4733、4770、4773、4834、4904、4919、4939、4941、4943、4955、4975、5004、5103、5131
