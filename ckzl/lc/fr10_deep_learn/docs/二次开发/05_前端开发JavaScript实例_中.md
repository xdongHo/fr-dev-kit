<!--
KB_INDEX: {
  "title": "二次开发 - 前端开发JavaScript实例_中",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "二次开发",
    "JavaScript实例",
    "前端开发"
  ],
  "summary": "「二次开发」分页：JavaScript实例（约 28 篇条目）；FR10 帮助文档「二次开发」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 二次开发 · 前端开发JavaScript实例_中

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §二次开发


## 前端开发 > JavaScript实例（28篇）
### 75. JS实现循环遍历单元格

- **doc-view ID**: 2418
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现循环遍历单元格
- **核心概念**: 在实际项目中，有时需要获取所有单元格的值，如下图所示： 按钮控件添加点击事件，用 JavaScript 循环语句实现。新建普通报表，新建数据集 ds1，SQL 语句为：SELECT * FROM 销量 where 地区='华东' and 产品='牛奶' 如下图设计表格，将字段拖入到对应单元格中。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在实际项目中，有时需要获取所有单元格的值，如下图所示： 按钮控件添加点击事件，用 JavaScript 循环语句实现。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在实际项目中，有时需要获取所有单元格的值，如下图所示： 按钮控件添加点击事件，用 JavaScript 循环语句实现。

**关键代码/公式/API：**
- 代码片段: `//_obj是表格tr对象 ⏎ var _obj = $(".x-table tr"); ⏎ //_length是tr行数 ⏎ var _length = _obj.length; ⏎ for(var i = 0; i < _length; i++) { ⏎     //遍历tr中的对象td ⏎     var _td = _obj.eq(i).find("td"); ⏎     for(var `
- 公式: `webroot\WEB-INF\reportlets\doc\JS\分页预览JS实例\`
- SQL: `SELECT * FROM 销量 where 地区='华东' and 产品='牛奶'`
- Java类/方法: `_obj.eq(i)`
- Java类/方法: `_td.eq(j)`

### 76. JS实现点击按钮复制文本内容功能

- **doc-view ID**: 2920
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现点击按钮复制文本内容功能
- **核心概念**: 在平时的报表开发中，我们通常会遇到点击按钮可以实现直接复制文本框里面的这个功能，如何在 FineReport 中实现该功能呢？如下图所示： 可通过 JS 实现该功能。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在平时的报表开发中，我们通常会遇到点击按钮可以实现直接复制文本框里面的这个功能，如何在 FineReport 中实现该功能呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在平时的报表开发中，我们通常会遇到点击按钮可以实现直接复制文本框里面的这个功能，如何在 FineReport 中实现该功能呢？

**关键代码/公式/API：**
- 代码片段: `<textarea rows="20" cols="20" id="biao1">用户复制区域</textarea> <!--定义一个文本域，可以通过rows和cols这2个属性来控制文本域的大小--> ⏎ <input type="button" onclick="copytext()" value="复制"> <!--定义一个按钮，被点击时触发copytext()函数，value属性可以定义按`
- 代码片段: `function copytext(){ ⏎ var copytext2=document.getElementById("biao1");//获取文本框 ⏎ copytext2.select();//选择文本框内容 ⏎ document.execCommand("copy");//执行浏览器复制命令 ⏎ alert("已经复制好了");//输出已经复制好了文本 ⏎ }`
- 公式: `scripts\`
- 公式: `WEB-INF\reportlets\doc\JS\分页预览JS实例\`
- SQL: `select()`
- Java类/方法: `document.getElementById("biao1")`
- Java类/方法: `copytext2.select()`
- Java类/方法: `document.execCommand("copy")`

### 77. JS应用office函数公式formula.js库

- **doc-view ID**: 2933
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS应用office函数公式formula.js库
- **核心概念**: Formula.js 是一个实现 Microsoft Excel 和 Google Spreadsheets 等类似的电子表格应用程序具有的强大公式的功能库，如何利用 Formula.js 库来调用 Office 公式呢？本文以 TREND 函数为例向用户介绍使用 Formula.js 库调用 Office 公式的方法。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: Formula.js 是一个实现 Microsoft Excel 和 Google Spreadsheets 等类似的电子表格应用程序具有的强大公式的功能库，如何利用 Formula.js 库来调用 Office 公式呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: Formula.js 是一个实现 Microsoft Excel 和 Google Spreadsheets 等类似的电子表格应用程序具有的强大公式的功能库，如何利用 Formula.js 库来调用 Office 公式呢？

**关键代码/公式/API：**
- 代码片段: `var data_y=new Array();//新建数组； ⏎ var data_x=new Array();//新建数组； ⏎ var new_data_x=new Array();//新建数组； ⏎ data_y.push(contentPane.curLGP.getCellValue("A1"));//获取单元格的值并添加到数组data_y ⏎ data_y.push(contentPan`
- 代码片段: `exports.TREND = function(data_y, data_x, new_data_x)`
- 代码片段: `var ak=formulajs.TREND(data_y,data_x,new_data_x);//使用函数TREND ⏎ contentPane.setCellValue("D1",null,ak);//将计算结果赋值给单元格D1`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\填报预览JS实例\`
- Java类/方法: `data_y.push(contentPane.curLGP.getCellValue("A1")`
- Java类/方法: `data_y.push(contentPane.curLGP.getCellValue("A2")`
- Java类/方法: `data_x.push(contentPane.curLGP.getCellValue("B1")`
- Java类/方法: `data_x.push(contentPane.curLGP.getCellValue("B2")`

### 78. JS 实现动态选择报表背景色

- **doc-view ID**: 2947
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS 实现动态选择报表背景色
- **核心概念**: 报表开发中，为提升报表美观度，可以使用 JS 实现报表背景色的动态切换。如下图所示： 报表设计时，在参数面板添加按钮控件， 给按钮添加 JS 点击事件实现报表背景色动态切换。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 报表开发中，为提升报表美观度，可以使用 JS 实现报表背景色的动态切换。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 报表开发中，为提升报表美观度，可以使用 JS 实现报表背景色的动态切换。

**关键代码/公式/API：**
- 代码片段: `setTimeout(function() { ⏎     $(".content-container").css("background-color", "LavenderBlush"); ⏎ }, 100);`
- 公式: `webroot\WEB-INF\reportlets\demo\NewbieGuide\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\CSS样式\`

### 79. JS实现文字2.5D动态轮播

- **doc-view ID**: 3343
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现文字2.5D动态轮播
- **核心概念**: 实现文字 2.5D 动态轮播效果，如下图所示： 报表中引用外部 JS 和 CSS 文件，利用公式函数解析，实现轮播效果。1）将压缩包 Carousel.rar 中的文件解压后放到设计器安装目录%FR_HOME%\webapps\webroot\WEB-INF\classes\com\fr\function下。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 实现文字 2.5D 动态轮播效果，如下图所示： 报表中引用外部 JS 和 CSS 文件，利用公式函数解析，实现轮播效果。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 实现文字 2.5D 动态轮播效果，如下图所示： 报表中引用外部 JS 和 CSS 文件，利用公式函数解析，实现轮播效果。

**关键代码/公式/API：**
- 代码片段: `$("#funnyNewsTicker1").funnyNewsTicker({width:"80%",timer:1000,titlecolor:"#FFF", ⏎ itembgcolor:"#1faf6d",infobgcolor:"#1a935c",buttonstyle:"white",bordercolor:"#1a935c"});  ⏎ $("#funnyNewsTicker2").f`
- 公式: `webroot\WEB-INF\classes\com\fr\`
- 公式: `webroot\help\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\`
- SQL: `SELECT * FROM CUSTOMER`
- SQL: `select("CUSTOMERNAME"))，并右边属性面板点击单元格属性>其他，显示内容选择用HTML显示内容。`
- Java类/方法: `ds1.select("CUSTOMERNAME")`

### 80. JS实现双击对话框标题栏最大化

- **doc-view ID**: 3686
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现双击对话框标题栏最大化
- **核心概念**: 报表中添加超链接，点击超链接弹出一个对话框，对话框大小固定，没有最大化功能。那如何实现最大化功能呢，如双击对话框标题栏，对话框实现最大化；最大化情况下，双击标题栏返回默认大小。

**业务场景四要素：**
- 统计指标方案: 2）将 「ds1.销售员」和「ds1.销量」字段拖入 A1 、 B1单元格中，B1单元格数据设置为汇总求和。如下图所示：
- 业务场景: 报表中添加超链接，点击超链接弹出一个对话框，对话框大小固定，没有最大化功能。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 报表中添加超链接，点击超链接弹出一个对话框，对话框大小固定，没有最大化功能。

**关键代码/公式/API：**
- 代码片段: `var frwidth = ""; ⏎ var frheight = ""; ⏎ var frleft = ""; ⏎ var frtop = ""; ⏎ var clicktype = 0; //标记对话框最大化状态 ⏎ var parenthtml = parent; ⏎  ⏎ setTimeout(function() { ⏎  //获取对话框初始大小 ⏎  frwidth = parent`
- 公式: `WEB-INF\reportlets\`
- SQL: `SELECT * FROM 销量 WHERE 地区='${地区}'  如下图所示：`

### 81. JS实现决策报表中添加声音报警

- **doc-view ID**: 3755
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现决策报表中添加声音报警
- **核心概念**: 在决策报表中，监控数据，当不数据不在监控范围内时，声音报警。在决策报表的报表块中添加声音标签及监控数据，报表块动态刷新，添加初始化事件，通过 JS 取监控数据判断，控制声音的播放。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在决策报表中，监控数据，当不数据不在监控范围内时，声音报警。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在决策报表中，监控数据，当不数据不在监控范围内时，声音报警。

**关键代码/公式/API：**
- 代码片段: `<audio id="music1" src="../../help/alarm.mp3" controls="controls"  loop="loop"> Your browser does not support the audio element. </audio>`
- 代码片段: `//获取A1单元格中值，若值<50,则报警 ⏎ setTimeout(function() {  ⏎  setInterval("var a = document.getElementById('music1');var b = _g().options.form.getWidgetByName('report0').element.find('td[id^=A1-]').text();if(b<`
- Java类/方法: `document.getElementById('music1')`
- Java类/方法: `options.form.getWidgetByName('report0')`
- Java类/方法: `element.find('td[id^=A1-]')`
- Java类/方法: `a.play()`

### 82. 对话框背景透明

- **doc-view ID**: 3907
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > 对话框背景透明
- **核心概念**: FineReport 的「对话框」样式固定，报表设计中，为了使「对话框」与整体风格保持一致，会对「对话框」样式做一些修改，如将弹出的「对话框」设置为透明样式，类似于HTML中的遮罩层的效果，如下图所示： 写一个修改弹出框 CSS 样式的 CSS 文件，在设计器中引用 CSS 文件，从而修改「对话框」样式。参考 FineReport 控件的 CSS 样式 2.1节查看「对话框」class 选择器。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FineReport 的「对话框」样式固定，报表设计中，为了使「对话框」与整体风格保持一致，会对「对话框」样式做一些修改，如将弹出的「对话框」设置为透明样式，类似于HTML中的遮罩层的效果，如下图所示： 写一个修改弹出框 CSS 样式的 CSS 文件，在设计器中引用 CSS 文件，从而修改「对话框」
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FineReport 的「对话框」样式固定，报表设计中，为了使「对话框」与整体风格保持一致，会对「对话框」样式做一些修改，如将弹出的「对话框」设置为透明样式，类似于HTML中的遮罩层的效果，如下图所示： 写一个修改弹出框 CSS 样式的 CSS 文件，在设计器中引用 CSS 文件，从而修改「对话框」

**关键代码/公式/API：**
- 代码片段: `/* 设置弹出框样式 */ ⏎ .fr-core-window .fr-core-window-body { ⏎   /* 设置弹出框背景和透明度*/ ⏎   background: rgba(255,255,255,0.2);/*0.2为透明度*/ ⏎   border-top-width: 0; ⏎   border-radius: 0 0 3px 3px; ⏎   -webkit-borde`

### 83. JS实现打开对话框后弱化主报表背景

- **doc-view ID**: 4032
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现打开对话框后弱化主报表背景
- **核心概念**: 一些点击报表中超链或者按钮弹出小框的应用场景中，若主页面和弹出小框风格差异比较大，用户使用时容易没办法聚焦小框内容，尤其是在一些深色背景且色彩较多的大屏应用中。那在这种情况下，如何能让查看报表的人视觉注意力集中到弹窗窗口呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 一些点击报表中超链或者按钮弹出小框的应用场景中，若主页面和弹出小框风格差异比较大，用户使用时容易没办法聚焦小框内容，尤其是在一些深色背景且色彩较多的大屏应用中。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 事件作用为关闭子模板弹窗时，取消主页面透明遮盖。

**关键代码/公式/API：**
- 代码片段: `$(".content-container").css("filter","blur(2px)")//父窗口遮罩 ⏎  ⏎ //以下代码是实现打开iframe窗口 ⏎  ⏎ var $iframe = $("<iframe id='inp' name='inp' width='100%' height='100%' scrolling='no' frameborder='0'>"); ⏎  ⏎ $`
- 代码片段: `setInterval(function(){ ⏎  $(".fr-core-panel-tool-close").mousedown(function(){//重写窗口右上角的关闭按钮点击事件 ⏎  $(".content-container").css("filter","none")//清除父窗口的模糊遮罩 ⏎  window.FR.closeDialog();//关闭对话框 ⏎  }); `
- 代码片段: `$(document).mouseup(function(e){ ⏎   var _con = $('fr-core-window ui-state-enabled');   // 设置目标区域 ⏎    ⏎   if(!_con.is(e.target) && _con.has(e.target).length === 0){  ⏎     FR.closeDialog();          `
- 公式: `webroot\WEB-INF\reportlets\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\填报预览JS实例\`
- Java类/方法: `iframe.attr("src", "${servletURL}?reportlet=/demo/iframe关闭监听-子窗口.cpt&op=write")`
- Java类/方法: `FR.showDialog(o.title, o.width, o.height, $iframe,o)`
- Java类/方法: `window.FR.closeDialog()`
- Java类/方法: `_con.is(e.target)`

### 84. 文档迁移说明

- **doc-view ID**: 4478
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > 文档迁移说明
- **核心概念**: 帮助文档中原有的一些非官方的方案，因为存在兼容性隐患、安全隐患，迁移到论坛。此类方案用户酌情使用，官方版本迭代可能会导致方案失效。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 帮助文档中原有的一些非官方的方案，因为存在兼容性隐患、安全隐患，迁移到论坛。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 帮助文档中原有的一些非官方的方案，因为存在兼容性隐患、安全隐患，迁移到论坛。

**关键代码/公式/API：**
- URL: `https://bbs.fanruan.com/thread-141899-1-1.htm`
- URL: `https://bbs.fanruan.com/thread-133770-1-1.html`
- URL: `https://bbs.fanruan.com/thread-133778-1-1.html`
- URL: `https://bbs.fanruan.com/thread-133781-1-1.html`

---
