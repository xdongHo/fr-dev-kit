<!--
KB_INDEX: {
  "title": "图表应用 - 基础图表ECharts图表",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "图表应用",
    "ECharts图表",
    "基础图表"
  ],
  "summary": "「图表应用」分页：ECharts图表（约 13 篇条目）；FR10 帮助文档「图表应用」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 图表应用 · 基础图表ECharts图表

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §图表应用


## 基础图表 > ECharts图表（13篇）

### 242. ECharts图表引用模板数据集

- **doc-view ID**: 4410
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表引用模板数据集
- **核心概念**: 在 FineReport 中使用 ECharts 图表引用模板中的数据集时，需要先添加数据结构，再在代码编辑器中通过 getData('name') 实现数据调用，name 指的是数据结构的名称。本文将用一个简单的示例作下示范：将 FRDemo 中「销量」表的产品字段和销量字段取出，并转换为一个二维数组，再调用生成图表。

**业务场景四要素：**
- 统计指标方案: 数据集选择 ds1，计算方式保持「汇总计算」，字符串字段添加一个「产品」字段，数值字段添加一个「销量」字段，汇总方式为「求和」。
- 业务场景: 在 FineReport 中使用 ECharts 图表引用模板中的数据集时，需要先添加数据结构，再在代码编辑器中通过 getData('name') 实现数据调用，name 指的是数据结构的名称。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 在 FineReport 中使用 ECharts 图表引用模板中的数据集时，需要先添加数据结构，再在代码编辑器中通过 getData('name') 实现数据调用，name 指的是数据结构的名称。

**关键代码/公式/API：**
- 代码片段: `var TABLE_DATA = getData('data1'); ⏎ option = { ⏎   legend: {}, ⏎   tooltip: {}, ⏎   dataset: { ⏎     source: TABLE_DATA, ⏎   }, ⏎   xAxis: { type: "category" },   ⏎   yAxis: {}, ⏎   series: [{ type: `
- 公式: `getData('name')`
- 公式: `getData()`
- 公式: `getData('data1')`
- SQL: `SELECT * FROM 销量。`

### 243. 单元格联动ECharts图表

- **doc-view ID**: 4411
- **路径**: 图表应用 > 基础图表 > ECharts图表 > 单元格联动ECharts图表
- **核心概念**: 当使用 ECharts 图表引用模板数据集 时，若该数据集中设置了参数，那么 ECharts 图表也是可以根据参数动态显示的，但如果想将参数传递给 ECharts 图表，例如 图表超链-联动单元格 文档中，将单元格中的地区字段作为参数传递给柱形图的标题，该如何做呢？

**业务场景四要素：**
- 统计指标方案: text: titleText + '地区销量统计图',
- 业务场景: 当使用 ECharts 图表引用模板数据集 时，若该数据集中设置了参数，那么 ECharts 图表也是可以根据参数动态显示的，但如果想将参数传递给 ECharts 图表，例如 图表超链-联动单元格 文档中，将单元格中的地区字段作为参数传递给柱形图的标题，该如何做呢？
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 这样做可实现将点击的「地区」赋值给参数 area，再将参数传递给 A5 单元格的图表。

**关键代码/公式/API：**
- 代码片段: `var titleText; ⏎   ⏎ if (window.FR) { ⏎   titleText = window.FR && window.FR.remoteEvaluate("$area"); ⏎ } ⏎   ⏎ var TABLE_DATA = getData('data1'); ⏎   ⏎ option = { ⏎   title: { ⏎     text: titleText +`
- 公式: `remoteEvaluate()`
- 公式: `if(len(area)`
- 公式: `remoteEvaluate("$area")`
- 公式: `getData('data1')`
- JS API: `window.FR`
- SQL: `SELECT * FROM 销量。获取销量表中全部数据。`

### 244. ECharts图表联动其他组件

- **doc-view ID**: 4412
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表联动其他组件
- **核心概念**: 在 FineReport 中，使用普通图表时，可在图表特效中通过 超级链接 进行传参，实现组件之间的联动效果。那么 ECharts 图表该如何传参联动其他组件呢？

**业务场景四要素：**
- 统计指标方案: 其数据是来源于有参数的 ds2 数据集，其中 C2 单元格的数据设置为「汇总>求和」。展示时会根据接收到的参数进行展示，初始状态参数为空时，则展示全部数据。如下图所示：
- 业务场景: 在 FineReport 中，使用普通图表时，可在图表特效中通过 超级链接 进行传参，实现组件之间的联动效果。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 2）gotoPage 接口：可实现传参给决策报表中的报表块。

**关键代码/公式/API：**
- 代码片段: `var TABLE_DATA=getData('data1') ⏎ option = { ⏎   title: { ⏎     text: '各地区销量', ⏎     left: 'center' ⏎   }, ⏎    tooltip: { ⏎     trigger: 'item' ⏎   }, ⏎    legend: { ⏎     top: '50%', ⏎     left: '85`
- 公式: `if(len(area)`
- 公式: `=getData('data1')`
- 公式: `on('click', function (params)`
- 公式: `getWidgetByName('report0')`
- JS API: `_g().getWidgetByName`
- JS API: `window.FR`
- SQL: `SELECT * FROM 销量 。`
- SQL: `SELECT * FROM 销量 WHERE 1=1  ${if(len(area) == 0,"","and 地区 = '" + area + "'")} ，该语句可实现参数为空时选择全部数据。`

### 245. ECharts图表实现动态参数联动效果

- **doc-view ID**: 4413
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表实现动态参数联动效果
- **核心概念**: 在 ECharts图表联动其他组件 文档中，ECharts 图表使用的 changeParameter 和 gotoPage 接口实现的是局部刷新联动效果，且存在某些场景无法实现：例如决策报表中无法对组件标题传参、普通报表中无法对单元格数据传参。那要如何实现这些场景呢？

**业务场景四要素：**
- 统计指标方案: 数据集选择 ds1，计算方式保持「汇总计算」，字符串字段添加一个「地区」字段，数值字段添加一个「销量」字段，汇总方式为「求和」。
- 业务场景: 在 ECharts图表联动其他组件 文档中，ECharts 图表使用的 changeParameter 和 gotoPage 接口实现的是局部刷新联动效果，且存在某些场景无法实现：例如决策报表中无法对组件标题传参、普通报表中无法对单元格数据传参。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: ds2 ：SELECT * FROM 销量 WHERE 1=1 ${if(len(area) == 0,"","and 地区 = '" + area + "'")} ，该语句可实现参数为空时选择全部数据。

**关键代码/公式/API：**
- 代码片段: `var TABLE_DATA=getData('data1') ⏎ option = { ⏎   title: { ⏎     text: '各地区销量', ⏎     left: 'center' ⏎   }, ⏎    tooltip: { ⏎     trigger: 'item' ⏎   }, ⏎    legend: { ⏎     top: '50%', ⏎     left: '85`
- 公式: `doHyperlinkByGet(url,config,target,feature)`
- 公式: `if(len(area)`
- 公式: `=getData('data1')`
- 公式: `on("click", function(params)`
- SQL: `SELECT * FROM 销量。`
- SQL: `SELECT * FROM 销量 WHERE 1=1  ${if(len(area) == 0,"","and 地区 = '" + area + "'")} ，该语句可实现参数为空时选择全部数据。`

### 246. ECharts图表实现系列条件显示

- **doc-view ID**: 4424
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表实现系列条件显示
- **核心概念**: 在使用 ECharts 图表引用模板数据集时，用户可能希望对图表数据进行一些处理，使图表可以实现条件显示等个性化的设置。本文将用一个简单示例作为示范，预期效果为： - 用柱形图展示产品的成本价和单价数据，且柱子带有背景。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为图表配置/功能说明，无具体统计指标）
- 业务场景: 在使用 ECharts 图表引用模板数据集时，用户可能希望对图表数据进行一些处理，使图表可以实现条件显示等个性化的设置。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 在使用 ECharts 图表引用模板数据集时，用户可能希望对图表数据进行一些处理，使图表可以实现条件显示等个性化的设置。

**关键代码/公式/API：**
- 代码片段: `var TABLE_DATA = getData("data1"); ⏎ var seriesNames = TABLE_DATA[0].slice(1); // 获取系列名 ⏎ var columnValues = TABLE_DATA.slice(1); ⏎ var categoryNames = columnValues.map(function(value){ ⏎ return value`
- 公式: `getData("data1")`
- 公式: `slice(1)`
- 公式: `map(function(value)`
- 公式: `map(function(seriesName, index)`
- SQL: `SELECT 产品名称,成本价,单价 FROM 产品 WHERE 类别ID = 2 limit 6 。`

### 247. ECharts图表实现旭日图

- **doc-view ID**: 4425
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表实现旭日图
- **核心概念**: 本文将使用 ECharts 图表引用模板数据集制作一个旭日图： - 第一层为地区、第二层为销售员、第三层节点名为产品类型，值为销量。- 最外层值大于 1000 时显示为红色。

**业务场景四要素：**
- 统计指标方案: 数据集选择 ds1，添加三个节点，第一层为「地区」，第二层为「销售员」，第三层为「产品类型」。前两层不设置数值，第三层设置数值为「销量」汇总方式为「求和」，那么前两层的值由第三层级的值汇总得来。如下图所示：
- 业务场景: 本文将使用 ECharts 图表引用模板数据集制作一个旭日图： - 第一层为地区、第二层为销售员、第三层节点名为产品类型，值为销量。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 本文将使用 ECharts 图表引用模板数据集制作一个旭日图： - 第一层为地区、第二层为销售员、第三层节点名为产品类型，值为销量。

**关键代码/公式/API：**
- 代码片段: `var TABLE_DATA = getData("data1"); ⏎ function setCustomStyle(datas) { ⏎   datas.forEach(function (item) { ⏎     // 可以在这里做一些个性化样式配置（即条件显示） ⏎     // 比如最外层值大于1000时颜色为红色 ⏎     if (item.value > 1000 && !it`
- 公式: `getData("data1")`
- 公式: `setCustomStyle(datas)`
- 公式: `forEach(function (item)`
- 公式: `setCustomStyle(item.children)`
- SQL: `SELECT * FROM 销量 。`

### 248. ECharts图表实现定时刷新

- **doc-view ID**: 4427
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表实现定时刷新
- **核心概念**: 使用 ECharts 图表引用模板数据集时，由于 getData 在浏览器预览环境时不能动态获取数据，不能像普通图表一样实现 监控刷新 ，但是可以通过给 ECharts 图表添加事件，利用autoRefresh(time) 接口实现定时刷新。预期效果如下图所示： - 普通报表中，在「模板>模板Web属性」中添加「加载结束事件」。

**业务场景四要素：**
- 统计指标方案: 数据集选择 ds1，计算方式保持「汇总计算」，字符串字段添加一个「销售员」字段，数值字段添加一个「销量」字段，汇总方式为「求和」。
- 业务场景: 使用 ECharts 图表引用模板数据集时，由于 getData 在浏览器预览环境时不能动态获取数据，不能像普通图表一样实现 监控刷新 ，但是可以通过给 ECharts 图表添加事件，利用autoRefresh(time) 接口实现定时刷新。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 使用 ECharts 图表引用模板数据集时，由于 getData 在浏览器预览环境时不能动态获取数据，不能像普通图表一样实现 监控刷新 ，但是可以通过给 ECharts 图表添加事件，利用autoRefresh(time) 接口实现定时刷新。

**关键代码/公式/API：**
- 代码片段: `var TABLE_DATA = getData('data1'); ⏎ option = { ⏎   legend: {}, ⏎   tooltip: {}, ⏎   dataset: { ⏎     source: TABLE_DATA, ⏎   }, ⏎   xAxis: { type: "category" }, ⏎   yAxis: {}, ⏎   series: [{ type: "b`
- 代码片段: `setTimeout(function() { ⏎     var chart = FR.Chart.WebUtils.getChart("A1"); // 获取echarts图表对象 ⏎     chart && chart.autoRefresh(3000); ⏎ }, 1000);`
- 公式: `autoRefresh(time)`
- 公式: `int(rand()`
- 公式: `getData('data1')`
- 公式: `setTimeout(function()`
- JS API: `setTimeout`
- SQL: `SELECT * FROM 销量 limit ${int(rand()*8)} ，即随机取出销量表中的前几条数据。`

### 249. ECharts图表集成

- **doc-view ID**: 4468
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表集成
- **核心概念**: ECharts 是一个基于 JavaScript 的开源可视化图表库。在使用 FineReport 时，当基础图表的通用配置不足以满足用户需求时，用户可安装「echarts图表插件」通过代码自定义个性化图表。

**业务场景四要素：**
- 统计指标方案: - 二维数组结构支持选择计算方式为「汇总计算」或「明细计算」
- 业务场景: ECharts 是一个基于 JavaScript 的开源可视化图表库。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: ECharts 是一个基于 JavaScript 的开源可视化图表库。

**关键代码/公式/API：**
- 公式: `getData()`

### 250. ECharts图表复用官方主题

- **doc-view ID**: 4470
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表复用官方主题
- **核心概念**: 在 FineReport 中使用 ECharts图表集成插件 时，只有一种默认的主题，若要自己修改样式、颜色等，会比较麻烦。这时希望将 ECharts 官网 主题编辑器 中现成的主题拿来复用，该如何做呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为图表配置/功能说明，无具体统计指标）
- 业务场景: 在 FineReport 中使用 ECharts图表集成插件 时，只有一种默认的主题，若要自己修改样式、颜色等，会比较麻烦。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 在 FineReport 中使用 ECharts图表集成插件 时，只有一种默认的主题，若要自己修改样式、颜色等，会比较麻烦。

**关键代码/公式/API：**
- 代码片段: `// 先获取dom节点 ⏎ var dom = myChart.getDom(); ⏎ // 重新初始化echarts实例 ⏎ myChart.dispose(); ⏎ // 主题样式 ⏎ var theme = ⏎ { ⏎     "color": [ ⏎         "#dd6b66", ⏎         "#759aa0", ⏎         "#e69d87", ⏎        `
- 代码片段: `$.getJSON('/webroot/help/dark.json', function (themeJSON) { ⏎   // 先获取dom节点 ⏎   var dom = myChart.getDom(); ⏎   // 重新初始化echarts实例 ⏎   myChart.dispose(); ⏎   echarts.registerTheme('dark', themeJSON); ⏎`
- 公式: `getDom()`
- 公式: `dispose()`
- 公式: `rgba(51,51,51,1)`
- 公式: `rgba(255,215,0,0.8)`

### 251. 参数查询联动ECharts图表

- **doc-view ID**: 4526
- **路径**: 图表应用 > 基础图表 > ECharts图表 > 参数查询联动ECharts图表
- **核心概念**: 当使用 ECharts 图表引用模板数据集 时，希望 ECharts 图表通过参数查询实现动态变化。预期效果如下图所示： 在普通报表或决策报表的「参数面板」中，设置参数和查询控件，ECharts 图表利用 FR.remoteEvaluate() 接收参数实现 ECharts 图表动态展示。

**业务场景四要素：**
- 统计指标方案: text: titleText + '地区销量统计图',
- 业务场景: 当使用 ECharts 图表引用模板数据集 时，希望 ECharts 图表通过参数查询实现动态变化。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 当使用 ECharts 图表引用模板数据集 时，希望 ECharts 图表通过参数查询实现动态变化。

**关键代码/公式/API：**
- 代码片段: `var titleText; ⏎   ⏎ if (window.FR) { ⏎   titleText = window.FR && window.FR.remoteEvaluate("$area"); ⏎ } ⏎   ⏎ var TABLE_DATA = getData('data1'); ⏎   ⏎ option = { ⏎   title: { ⏎     text: titleText +`
- 公式: `remoteEvaluate()`
- 公式: `if(len(area)`
- 公式: `remoteEvaluate("$area")`
- 公式: `getData('data1')`
- JS API: `window.FR`
- SQL: `SELECT * FROM 销量。获取销量表中全部数据。`

### 252. 决策报表控件联动ECharts图表

- **doc-view ID**: 4528
- **路径**: 图表应用 > 基础图表 > ECharts图表 > 决策报表控件联动ECharts图表
- **核心概念**: 在决策报表的 body 中，直接使用控件绑定参数是可以实现 自动查询 的。但是，对 ECharts 图表来说，并不支持直接使用 body 中的控件实现联动。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为图表配置/功能说明，无具体统计指标）
- 业务场景: 在决策报表的 body 中，直接使用控件绑定参数是可以实现 自动查询 的。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 在决策报表的 body 中，直接使用控件绑定参数是可以实现 自动查询 的。

**关键代码/公式/API：**
- 代码片段: `FR.Chart.WebUtils.changeParameter({ ⏎  chartID:'chart0', ⏎  para:{  ⏎  area:this.getValue() ⏎        } ⏎ })`
- 代码片段: `try ⏎ {var area = FR.remoteEvaluate('$area');} ⏎ catch(err){} ⏎ const TABLE_DATA = getData("data1"); ⏎ option = { ⏎       title: {subtext: area}, ⏎   legend: {}, ⏎   tooltip: {}, ⏎   dataset: { ⏎     `
- 公式: `changeParameter()`
- 公式: `remoteEvaluate()`
- 公式: `if(len(area)`
- 公式: `changeParameter({
 chartID:'chart0',
 para:{ 
 area:this.getValue()`
- SQL: `SELECT * FROM 销量。获取销量表中全部数据。`

### 253. ECharts图表调用百度地图

- **doc-view ID**: 4595
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表调用百度地图
- **核心概念**: 用户在使用 ECharts 图表调用百度地图资源时，发现预览的时候地图无法拖动。而在 ECharts 官网测试时，是可以拖动的，参考 ECharts 官网示例：https://echarts.apache.org/examples/zh/editor.html?c=effectScatter-bmap 。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为图表配置/功能说明，无具体统计指标）
- 业务场景: 用户在使用 ECharts 图表调用百度地图资源时，发现预览的时候地图无法拖动。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 用户在使用 ECharts 图表调用百度地图资源时，发现预览的时候地图无法拖动。

**关键代码/公式/API：**
- 代码片段: `createChart() { ⏎   option = { ⏎     ... // 自行配置地图数据 ⏎   }; ⏎   myChart.setOption(option); ⏎ } ⏎ function loadScript() { ⏎   var script = document.createElement("script"); ⏎   script.type = "text/java`
- 代码片段: `const data = [ ⏎   { name: '海门', value: 9 }, ⏎   { name: '鄂尔多斯', value: 12 }, ⏎   { name: '招远', value: 12 }, ⏎   { name: '舟山', value: 12 }, ⏎   { name: '齐齐哈尔', value: 14 }, ⏎   { name: '盐城', value: 15`
- 公式: `createChart()`
- 公式: `setOption(option)`
- 公式: `loadScript()`
- 公式: `createElement("script")`
- JS API: `setTimeout`
- URL: `https://echarts.apache.org/examples/zh/editor.html`
- URL: `https://api.map.baidu.com/api`
- URL: `http://www.pm25.in`

### 254. ECharts图表制作关系图

- **doc-view ID**: 4646
- **路径**: 图表应用 > 基础图表 > ECharts图表 > ECharts图表制作关系图
- **核心概念**: 本文将使用 ECharts 图表引用模板数据集制作一个关系图： 1）点击设计器左上角「文件>新建普通报表」。2）准备数据：需准备一个节点表，和一个关系表。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为图表配置/功能说明，无具体统计指标）
- 业务场景: 本文将使用 ECharts 图表引用模板数据集制作一个关系图： 1）点击设计器左上角「文件>新建普通报表」。
- 人员岗位: 未在文中明确指定（面向图表制作/报表模板开发人员）
- 功能应用场景: 本文将使用 ECharts 图表引用模板数据集制作一个关系图： 1）点击设计器左上角「文件>新建普通报表」。

**关键代码/公式/API：**
- 代码片段: `var TABLE_DATA = getData("data1"); ⏎ var TABLE_DATA1 = getData("data2"); ⏎ var columnValues = TABLE_DATA.slice(1); ⏎ var columnValues1 = TABLE_DATA1.slice(1); ⏎ var nodes = columnValues.map(function(i`
- 公式: `getData("data1")`
- 公式: `getData("data2")`
- 公式: `slice(1)`
- 公式: `map(function(item)`

---
