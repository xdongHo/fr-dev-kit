<!--
KB_INDEX: {
  "title": "二次开发 - 前端开发JavaScript实例_上",
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

# 二次开发 · 前端开发JavaScript实例_上

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §二次开发


## 前端开发 > JavaScript实例（28篇）
### 57. JavaScript实例

- **doc-view ID**: 1175
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > JavaScript实例
- **核心概念**: 设计模板时，可以通过 JavaScript 对一些功能进行二次开发。如下图所示，填报提交后某些工具栏按钮设置为不可用。

**业务场景四要素：**
- 统计指标方案: 填报相关示例可参考：填报JS文档汇总
- 业务场景: 设计模板时，可以通过 JavaScript 对一些功能进行二次开发。
- 人员岗位: 通过 JavaScript 进行前端开发应用广泛，有丰富的示例可供用户参考使用。如下：
- 功能应用场景: 设计模板时，可以通过 JavaScript 对一些功能进行二次开发。

### 58. JS获取分页预览单元格

- **doc-view ID**: 1200
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS获取分页预览单元格
- **核心概念**: 有时我们也需要获取分页预览的报表中的某些单元格的值进行其他操作，比如报表总行数保存在某固定单元格中，在工具栏中显示报表总行数。下面效果图中，我们获取了某单元格的值，然后对其进行了修改，如下所示： 通过添加「加载结束」事件，利用 JS 代码获取到单元格中的值。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 有时我们也需要获取分页预览的报表中的某些单元格的值进行其他操作，比如报表总行数保存在某固定单元格中，在工具栏中显示报表总行数。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 有时我们也需要获取分页预览的报表中的某些单元格的值进行其他操作，比如报表总行数保存在某固定单元格中，在工具栏中显示报表总行数。

**关键代码/公式/API：**
- 代码片段: `var a = $("tr[tridx=2]","div.content-container").children().eq(1).html(); ⏎ alert("第3行第2列值为："+a); ⏎ $("tr[tridx=2]","div.content-container").children().eq(1).html(1001); ⏎ alert("第3行第2列值被修改为1001");`
- 代码片段: `var a=$("td[id^=B3-]").text(); ⏎ alert("B3单元格值为："+a);//B3 是指预览后所扩展出来的单元格 ⏎ $("td[id^=B3-]").text(1001); ⏎ alert("第B3单元格的值被修改为1001");`
- 公式: `WEB-INF\reportlets\doc\Advanced\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\分页预览JS实例\`

### 59. 在报表中调用客户JS的方法

- **doc-view ID**: 1204
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > 在报表中调用客户JS的方法
- **核心概念**: 当报表嵌入在某个页面 iframe 框架中时，如何在获取主页面里定义的方法、如何获取主页面另外的内嵌 iframe 中的报表呢？即： 1）报表嵌入在某个页面的 iframe 框架中，报表模板中如何获取承载报表的 iframe 页面里定义的方法。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 当报表嵌入在某个页面 iframe 框架中时，如何在获取主页面里定义的方法、如何获取主页面另外的内嵌 iframe 中的报表呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 当报表嵌入在某个页面 iframe 框架中时，如何在获取主页面里定义的方法、如何获取主页面另外的内嵌 iframe 中的报表呢？

**关键代码/公式/API：**
- 代码片段: `<html> ⏎   <head>  ⏎     <title>page1</title> ⏎ <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> ⏎ <script type="text/javascript"> ⏎ function fun1(){ ⏎ alert("这是主页面中的方法！"); ⏎ } ⏎ `
- 代码片段: `<html> ⏎   <head>  ⏎     <title>page2</title> ⏎ <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> ⏎     <script type="text/javascript"> ⏎ function fun2(){ ⏎ var name = alert("这是嵌在另`
- 代码片段: `var page1 = parent.window; ⏎ page1.fun1(); ⏎ var page2 = page1.document.getElementById("page2").contentWindow; ⏎ page2.fun2();`
- 公式: `webroot\`
- URL: `http://localhost`
- Java类/方法: `parent.window.fnname()`
- Java类/方法: `parent.window.getElementById("iframename")`
- Java类/方法: `contentWindow.fnname()`
- Java类/方法: `page1.fun1()`

### 60. 其它JS

- **doc-view ID**: 1364
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > 其它JS
- **核心概念**: 借助外部途径较多，通过前端代码，并官方接口实现的的一些 JS 示例和方法，代码和浏览器关联较大，使用时请根据实际情况调整，特别注意兼容性问题。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 借助外部途径较多，通过前端代码，并官方接口实现的的一些 JS 示例和方法，代码和浏览器关联较大，使用时请根据实际情况调整，特别注意兼容性问题。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 借助外部途径较多，通过前端代码，并官方接口实现的的一些 JS 示例和方法，代码和浏览器关联较大，使用时请根据实际情况调整，特别注意兼容性问题。

### 61. JS实现键盘翻页效果

- **doc-view ID**: 1755
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现键盘翻页效果
- **核心概念**: 当我们报表有多页时，在展示时想使用键盘的上下键、左右键或空格键实现对报表的操作，如上下键实现翻页，该如何实现呢？通过 JS 获取按下按键的键值，根据键值对报表进行判断翻页操作。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 当我们报表有多页时，在展示时想使用键盘的上下键、左右键或空格键实现对报表的操作，如上下键实现翻页，该如何实现呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 当我们报表有多页时，在展示时想使用键盘的上下键、左右键或空格键实现对报表的操作，如上下键实现翻页，该如何实现呢？

**关键代码/公式/API：**
- 代码片段: `//获取键盘按键按下事件 ⏎ $(document).bind('keydown', function(e) { ⏎ //获取按键键值 ⏎ var key = window.event ? e.keyCode : e.which; ⏎ //alert(key); ⏎ if (key.toString() == "33"|| key.toString() == "37" || key.toStrin`
- Java类/方法: `key.toString()`
- Java类/方法: `contentPane.gotoPreviousPage()`
- Java类/方法: `contentPane.gotoNextPage()`

### 62. JS设置报表主体不可用

- **doc-view ID**: 1764
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS设置报表主体不可用
- **核心概念**: 报表开发中，很多情况下需要将报表主体或工具栏设置为不可用，即置灰且不能点击；或初始化设置为不可用，点击某个按钮恢复可用。报表置灰显示如下图所示，那如何实现此效果呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 报表开发中，很多情况下需要将报表主体或工具栏设置为不可用，即置灰且不能点击；或初始化设置为不可用，点击某个按钮恢复可用。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 报表开发中，很多情况下需要将报表主体或工具栏设置为不可用，即置灰且不能点击；或初始化设置为不可用，点击某个按钮恢复可用。

**关键代码/公式/API：**
- 代码片段: `$('<div/>').css({ ⏎     position:'absolute',//绝对定位 ⏎     top:$('.x-toolbar').height(),//元素距离顶部的高度为工具栏的高度 ⏎     width: '100%',//宽度100%显示 ⏎     height: '100%',//高度100%显示 ⏎     filter: 'alpha(opacity=50)`
- 代码片段: `$('<div/>').css({ ⏎     position:'absolute',//绝对定位 ⏎     top:0,//元素距离顶部的高度为0 ⏎     width: '100%',//宽度100%显示 ⏎     height: '100%',//高度100%显示 ⏎     filter: 'alpha(opacity=50)',//透明度是0.5 ⏎     opacity: 0`
- 代码片段: `$('<div id="lock"/>').css({ ⏎     position:'absolute',//绝对定位 ⏎     top:$('.x-toolbar').height(),//元素距离顶部的高度为工具栏的高度 ⏎     width: '100%',//宽度100%显示 ⏎     height: '100%',//高度100%显示 ⏎     filter: 'alpha(o`
- 公式: `webroot\WEB-INF\reportlets\doc\Form\FreeFrom\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\填报预览JS实例\`
- Java类/方法: `document.getElementById("lock")`

### 63. 在JS中使用FR公式

- **doc-view ID**: 1785
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > 在JS中使用FR公式
- **核心概念**: 有时报表设计时涉及到写 JavaScript 代码，利用 JavaScript 处理某些计算或转换时特别复杂，比如日期格式化、字符串截取替换等等，如利用原生 JavaScript 将当前日期显示成 “2017 年 02 月 24 日” 这种格式时需要写如下代码： ``` var da = new Date(); var year = da.getFullYear()+'年'; var month 

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 有时报表设计时涉及到写 JavaScript 代码，利用 JavaScript 处理某些计算或转换时特别复杂，比如日期格式化、字符串截取替换等等，如利用原生 JavaScript 将当前日期显示成 “2017 年 02 月 24 日” 这种格式时需要写如下代码： ``` var da = new D
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 有时报表设计时涉及到写 JavaScript 代码，利用 JavaScript 处理某些计算或转换时特别复杂，比如日期格式化、字符串截取替换等等，如利用原生 JavaScript 将当前日期显示成 “2017 年 02 月 24 日” 这种格式时需要写如下代码： ``` var da = new D

**关键代码/公式/API：**
- 代码片段: `var da = new Date(); ⏎ var year = da.getFullYear()+'年'; ⏎ var month = da.getMonth()+1+'月'; ⏎ var day = da.getDate()+'日'; ⏎ if (month.length < 3) month = '0' + month; ⏎ if (day.length < 3) day = '0' + `
- 代码片段: `var rq='${=today()}';  ⏎ alert(rq);`
- 代码片段: `var rq=FR.remoteEvaluate('=format(today(),"yyyy年MM月dd日")'); ⏎ alert(rq);`
- SQL: `SELECT 地区 from 销量 where 销售员=\''+sale+'\'",1,1)')`
- Java类/方法: `da.getFullYear()`
- Java类/方法: `da.getMonth()`
- Java类/方法: `da.getDate()`
- Java类/方法: `FR.remoteEvaluate('=公式')`

### 64. JS实现点击按钮实现全屏预览

- **doc-view ID**: 1788
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现点击按钮实现全屏预览
- **核心概念**: 决策平台中预览报表提供了全屏显示功能，但如果不通过决策平台预览，如何全屏预览单张报表呢？注：本文实现的是普通报表点击按钮全屏显示的实现方法，决策报表中点击按钮实现全屏的方法参见文档：JS 实现点击决策报表实现全屏效果 添加按钮点击事件实现全屏预览功能。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 注：该方法仅适用于谷歌、火狐、360（极速模式）浏览器。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 注：该方法仅适用于谷歌、火狐、360（极速模式）浏览器。

**关键代码/公式/API：**
- 代码片段: `var docElm = document.documentElement; ⏎ //W3C ⏎ if (docElm.requestFullscreen) { ⏎  docElm.requestFullscreen(); ⏎ } ⏎ //FireFox ⏎ else if (docElm.mozRequestFullScreen) { ⏎  docElm.mozRequestFullScreen`
- 公式: `webroot\WEB-INF\reportlets\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\分页预览JS实例\`
- Java类/方法: `docElm.requestFullscreen()`
- Java类/方法: `docElm.mozRequestFullScreen()`
- Java类/方法: `docElm.webkitRequestFullScreen()`

### 65. JS实现控制报表最长预览时间，超时自动退出

- **doc-view ID**: 1815
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现控制报表最长预览时间，超时自动退出
- **核心概念**: 多用户并发一直是服务器部署中头一个关键考虑因素，目前 FineReport 已经提供了相对较好的多用户 Session 控制方案，也提供了 防宕机插件 来控制报表的生命周期。除以上两种方法外，本文提供了一种 JS 控制报表最长预览时间，超时自动退出的方法。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 多用户并发一直是服务器部署中头一个关键考虑因素，目前 FineReport 已经提供了相对较好的多用户 Session 控制方案，也提供了 防宕机插件 来控制报表的生命周期。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 多用户并发一直是服务器部署中头一个关键考虑因素，目前 FineReport 已经提供了相对较好的多用户 Session 控制方案，也提供了 防宕机插件 来控制报表的生命周期。

**关键代码/公式/API：**
- 代码片段: `setTimeout(function () { ⏎     jQuery.ajax({ ⏎         url: "/webroot/decision/logout",//单点登录的报表服务器   ⏎         data: {}, ⏎         timeout: 5000, ⏎         success: function (data) { ⏎             wi`
- 公式: `webroot\`

### 66. JS判断PC和移动设备类型

- **doc-view ID**: 1875
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS判断PC和移动设备类型
- **核心概念**: 有时需要判断当前登录的环境是手机端还是电脑端，如下图所示： 可以通过 JavaScript 来实现判断当前的设备类型： navigator 是 JavaScript 中的一个独立的对象，用于提供用户所使用的浏览器以及操作系统等信息，以 navigator 对象属性的形式来提供。所有浏览器都支持该对象。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 有时需要判断当前登录的环境是手机端还是电脑端，如下图所示： 可以通过 JavaScript 来实现判断当前的设备类型： navigator 是 JavaScript 中的一个独立的对象，用于提供用户所使用的浏览器以及操作系统等信息，以 navigator 对象属性的形式来提供。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: navigator 是 JavaScript 中的一个独立的对象，用于提供用户所使用的浏览器以及操作系统等信息，以 navigator 对象属性的形式来提供。所有浏览器都支持该对象。

**关键代码/公式/API：**
- 代码片段: `if(!window.navigator) {   ⏎     FR.Msg.alert("提示","当前设备：移动端APP") ⏎     } ⏎     else{ ⏎         if(/Mobile|Android|webOS|iPhone|iPad|Phone/i.test(navigator.userAgent)){ ⏎ FR.Msg.alert("提示","当前设备：移动端H5"`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\`
- Java类/方法: `FR.Msg.alert("提示","当前设备：移动端APP")`
- Java类/方法: `i.test(navigator.userAgent)`
- Java类/方法: `FR.Msg.alert("提示","当前设备：移动端H5")`
- Java类/方法: `FR.Msg.alert("提示","当前设备：PC端")`

### 67. JS判断操作系统语言(浏览器)

- **doc-view ID**: 1886
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS判断操作系统语言(浏览器)
- **核心概念**: FineReport 作为一款多语种，跨平台的报表设计器，经常会有客户需要使用多个语言环境来配置报表。那么，如何通过判定操作系统语言环境来自动跳转到对应语种的页面呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FineReport 作为一款多语种，跨平台的报表设计器，经常会有客户需要使用多个语言环境来配置报表。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FineReport 作为一款多语种，跨平台的报表设计器，经常会有客户需要使用多个语言环境来配置报表。

**关键代码/公式/API：**
- 代码片段: `var type = navigator.appName ⏎ if (type == "Netscape") { ⏎  var lang = navigator.language ⏎ } else { ⏎  var lang = navigator.userLanguage ⏎ } ⏎ //取得浏览器语言的前两个字母 ⏎ var lang = lang.substr(0, 2) ⏎ // 判断英语`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\`
- URL: `http://www.英文.com/`
- URL: `http://www.中文.com/`
- URL: `http://www.其他.com/`
- Java类/方法: `lang.substr(0, 2)`

### 68. JS实现报表标题动态滚动效果

- **doc-view ID**: 1917
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现报表标题动态滚动效果
- **核心概念**: 有时报表页面显示内容较多时，为了能突出提示某些内容，我们需要一些特殊效果，比如需要实现浏览器标题栏动态滚动效果。如下图所示： 利用 JS 中 document.title="标题"方法，结合定时函数功能来设置标题动态展示 注：适用于后台中存在一个长时间定时刷新的页面，当有内容变化时，通过JS判断，并动态滚动标题栏，来突出显示结果。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 注：适用于后台中存在一个长时间定时刷新的页面，当有内容变化时，通过JS判断，并动态滚动标题栏，来突出显示结果。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 注：适用于后台中存在一个长时间定时刷新的页面，当有内容变化时，通过JS判断，并动态滚动标题栏，来突出显示结果。

**关键代码/公式/API：**
- 代码片段: `if(window.interval) clearInterval(window.interval); ⏎ //当页面刷新时，清除定时器 ⏎ $(function(){   ⏎    var cnt1=$('td[id^=A1]').text();   ⏎         if(parseInt(cnt1)<=8000) { ⏎         t='正常完成！'; ⏎         docum`
- 公式: `webroot\WEB-INF\reportlets\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\分页预览JS实例\`
- Java类/方法: `t.split("")`
- Java类/方法: `s.push(s[0])`
- Java类/方法: `s.shift()`
- Java类/方法: `s.join("")`

### 69. JS实现普通报表自动轮播

- **doc-view ID**: 1977
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现普通报表自动轮播
- **核心概念**: 在实际工作中，需要实现多张报表自动轮播效果，但区别于 自动切换分页效果 及 图表手动切换。实际效果如下图所示： 给报表添加「加载结束」事件，通过 JavaScript 延时函数，页面加载完成后停留一定时间自动跳转到另一页面来实现自动轮播特效。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在实际工作中，需要实现多张报表自动轮播效果，但区别于 自动切换分页效果 及 图表手动切换。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在实际工作中，需要实现多张报表自动轮播效果，但区别于 自动切换分页效果 及 图表手动切换。

**关键代码/公式/API：**
- 代码片段: `setTimeout(function(){ ⏎ window.location="${servletURL}?viewlet=doc/JS/分页预览JS实例/普通报表自动轮播2.cpt"; ⏎ },3000)`
- 代码片段: `setTimeout(function(){ ⏎ window.location="${servletURL}?viewlet=doc/JS/分页预览JS实例/普通报表自动轮播3.cpt"; ⏎ },3000)`
- 代码片段: `setTimeout(function(){ ⏎ window.location="${servletURL}?viewlet=doc/JS/分页预览JS实例/普通报表自动轮播1.cpt"; ⏎ },3000)`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\分页预览JS实例\`

### 70. JS实现为报表页面添加提示声音

- **doc-view ID**: 1978
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现为报表页面添加提示声音
- **核心概念**: 在对于关键指标实时性要求较高的报表中，需要及时掌握某些关键指标的。当某些关键指标值发生较大变化时，需要第一时间给予用户提醒，声音警报提示就是常用的一种。

**业务场景四要素：**
- 统计指标方案: 在对于关键指标实时性要求较高的报表中，需要及时掌握某些关键指标的。当某些关键指标值发生较大变化时，需要第一时间给予用户提醒，声音警报提示就是常用的一种。
- 业务场景: 在对于关键指标实时性要求较高的报表中，需要及时掌握某些关键指标的。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在允许播放的网页中添加 http://IP:端口/webroot/decision，即可实现自动播放报警声音。如下图所示：

**关键代码/公式/API：**
- 代码片段: `var $alramDiv; ⏎ //判断报警提示alarmDiv是否存在，如果不存在，则初始化 ⏎ if($("#alarmDiv").length>0){ ⏎ $alramDiv=$("#alarmDiv"); ⏎ } else{ ⏎ $alramDiv=$('<div id="alarmDiv"></div>').appendTo($(document.body)); ⏎ } ⏎ //清空报`
- 公式: `webroot\`
- URL: `http://IP`
- Java类/方法: `alramDiv.empty()`
- Java类/方法: `FR.Browser.isIE()`
- Java类/方法: `FR.Msg.confirm("警告","销售额低于8000,【确认】报警信息？",function(value)`

### 71. JS实现自动报警声音

- **doc-view ID**: 1982
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现自动报警声音
- **核心概念**: 当填报人填报内容与实际不相符时，对填报内容发出警告。对于填报模板，简单的信息提示可能会被忽略，这里提供一个警告音提示的方法。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 当填报人填报内容与实际不相符时，对填报内容发出警告。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在允许播放的网页中添加 http://IP:端口/webroot/decision，即可实现自动播放报警声音。如下图所示：

**关键代码/公式/API：**
- 代码片段: `setInterval("self.location.reload();",36000);`
- 公式: `webroot\WEB-INF\reportlets\doc\Form\LineForm\`
- 公式: `webroot\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\填报预览JS实例\`
- URL: `http://IP`
- Java类/方法: `self.location.reload()`

### 72. 通过JS获取当前页面URL网址信息

- **doc-view ID**: 2175
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > 通过JS获取当前页面URL网址信息
- **核心概念**: 在平时的报表开发中，我们通常会遇到要获取当前打开报表页面的URL网址相关信息，虽然目前 FineReport 内置的 系统参数 能满足一定的需求，但有一些需求系统参数中没有提供，如要获取 URL 对应的"标签名称"。如下图所示： 1.2 实现思路 可以通过 JavaScript 脚本来获取 URL 网址相关信息。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在平时的报表开发中，我们通常会遇到要获取当前打开报表页面的URL网址相关信息，虽然目前 FineReport 内置的 系统参数 能满足一定的需求，但有一些需求系统参数中没有提供，如要获取 URL 对应的"标签名称"。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在平时的报表开发中，我们通常会遇到要获取当前打开报表页面的URL网址相关信息，虽然目前 FineReport 内置的 系统参数 能满足一定的需求，但有一些需求系统参数中没有提供，如要获取 URL 对应的"标签名称"。

**关键代码/公式/API：**
- 代码片段: `//设置或获取整个 URL 为字符串 ⏎ var test1 = window.location.href; ⏎ alert('URL地址:  '+test1); ⏎ //window.location.protocol(设置或获取URL的协议部分) ⏎ var test2 = window.location.protocol; ⏎ alert('URL协议:  '+test2); ⏎ //win`
- 公式: `webroot\WEB-INF\reportlets\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\`
- Java类/方法: `window.location.protocol(设置或获取URL的协议部分)`
- Java类/方法: `window.location.host(设置或获取URL的主机部分)`
- Java类/方法: `window.location.port(设置或获取与URL端口号)`
- Java类/方法: `window.location.pathname(设置或获取与URL的路径部分（文件地址）)`

### 73. JS实现点击报表实现全屏效果

- **doc-view ID**: 2372
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现点击报表实现全屏效果
- **核心概念**: 在浏览器上大家都习惯于 F11 让报表达到全屏效果，但是对于有些仅用于展示的电脑而言，有时候是不配备键盘，稍做调整只能用鼠标来实现。效果如下图所示，鼠标点击决策报表主体，报表全屏显示；再点击，恢复为原来的样子。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 效果如下图所示，鼠标点击决策报表主体，报表全屏显示；再点击，恢复为原来的样子。适用于某些不配备键盘，大屏讲解的场景。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 效果如下图所示，鼠标点击决策报表主体，报表全屏显示；再点击，恢复为原来的样子。适用于某些不配备键盘，大屏讲解的场景。

**关键代码/公式/API：**
- 代码片段: `var docElm = document.documentElement; ⏎ var explorer = window.navigator.userAgent.toLowerCase(); ⏎ if(explorer.indexOf('chrome') > 0) { //webkit ⏎     if(document.body.scrollHeight === window.screen.`
- 公式: `webroot\WEB-INF\reportlets\demo\analytics\sales\`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\表单JS实例\`
- Java类/方法: `window.navigator.userAgent.toLowerCase()`
- Java类/方法: `explorer.indexOf('chrome')`
- Java类/方法: `document.exitFullscreen()`
- Java类/方法: `document.msExitFullscreen()`

### 74. JS实现根据不同设备显示不同内容

- **doc-view ID**: 2407
- **路径**: 二次开发 > 前端开发 > JavaScript实例 > 其它JS > JS实现根据不同设备显示不同内容
- **核心概念**: 当一张报表中内容太多，想根据预览的设备不同显示不同的内容，该怎么实现？如下图所示，模板在移动端和 PC 端预览时，展示内容不同。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 当一张报表中内容太多，想根据预览的设备不同显示不同的内容，该怎么实现？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 当一张报表中内容太多，想根据预览的设备不同显示不同的内容，该怎么实现？

**关键代码/公式/API：**
- 代码片段: `var self = this; ⏎ debugger; ⏎ /*获取url中的参数*/ ⏎ function GetQueryString(name) { ⏎ var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); ⏎ var r = window.location.search.substr(1).match(reg); ⏎ if(r !`
- 公式: `webroot\WEB-INF\reportlets\doc\JS\分页预览JS实例\`
- Java类/方法: `window.location.search.substr(1)`
- Java类/方法: `self.setValue("移动端")`
- Java类/方法: `window.navigator.userAgent.toLowerCase()`
- Java类/方法: `i.test(userAgent)`
