<!--
KB_INDEX: {
  "title": "二次开发 - FineReport事件与前端常用知识",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "二次开发",
    "FineReport事件",
    "前端常用知识",
    "前端开发"
  ],
  "summary": "「二次开发」分页：FineReport事件、前端常用知识（约 15 篇条目）；FR10 帮助文档「二次开发」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 二次开发 · FineReport事件与前端常用知识

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §二次开发


## 前端开发 > FineReport事件（4篇）

### 85. 控件事件

- **doc-view ID**: 1176
- **路径**: 二次开发 > 前端开发 > FineReport事件 > 控件事件
- **核心概念**: 根据控件响应时间的不同，我们把控件的事件分为九种：初始化后、编辑前、编辑后、编辑结束、点击、状态改变、值改变、上传后及节点生成。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 状态改变：状态改变事件是指控件的值发生改变时触发，该事件只能适用于复选框、单选按钮组和复选框组中。状态改变事件示例请查看 点击单选按钮弹出对话框输入值。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 状态改变：状态改变事件是指控件的值发生改变时触发，该事件只能适用于复选框、单选按钮组和复选框组中。状态改变事件示例请查看 点击单选按钮弹出对话框输入值。

**关键代码/公式/API：**
- 代码片段: `contentPane.setFireStopEditOnChange(false);`
- Java类/方法: `contentPane.setFireStopEditOnChange(false)`

### 86. Web页面事件

- **doc-view ID**: 1178
- **路径**: 二次开发 > 前端开发 > FineReport事件 > Web页面事件
- **核心概念**: Web 页面事件在模板>模板 Web 属性里面的分页预览设置，填报页面设置与数据分析设置几个标签页中均可设置，分别作用于不同的预览方式，下面以分页预览为例，进入分页预览设置标签，选择为该模板单独设置，点击事件设置下的+按钮，增加事件，如下图：

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: Web 页面事件在模板>模板 Web 属性里面的分页预览设置，填报页面设置与数据分析设置几个标签页中均可设置，分别作用于不同的预览方式，下面以分页预览为例，进入分页预览设置标签，选择为该模板单独设置，点击事件设置下的+按钮，增加事件，如下图：
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: Web 页面事件在模板>模板 Web 属性里面的分页预览设置，填报页面设置与数据分析设置几个标签页中均可设置，分别作用于不同的预览方式，下面以分页预览为例，进入分页预览设置标签，选择为该模板单独设置，点击事件设置下的+按钮，增加事件，如下图：

### 87. 事件响应方式

- **doc-view ID**: 1180
- **路径**: 二次开发 > 前端开发 > FineReport事件 > 事件响应方式
- **核心概念**: 当事件触发时，就会引起相应的响应，在 FR 的事件 中已经介绍了各种事件对应的事件响应方式，下面一一介绍事件响应方式 FR 中提供了 5 种响应方式：Javascript 脚本、提交入库、发送邮件、自定义提交和内置 SQL。其中自定义提交和内置 SQL 在 报表填报属性 介绍过了，下面详细介绍另外三种响应方式的使用。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 注：提交入库适用于除填报提交事件以外的所有事件。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 注：提交入库适用于除填报提交事件以外的所有事件。

### 88. FineReport 的事件

- **doc-view ID**: 1229
- **路径**: 二次开发 > 前端开发 > FineReport事件 > FineReport 的事件
- **核心概念**: 根据添加事件的位置不同，FineReport 报表中有以下几种事件： - **控件事件**：在控件上添加的事件，在「控件设置>事件」处添加，控件介绍可查看 控件类型。- **Web 页面事件**：给 Web 页面添加的事件，在「模板>模板 Web 属性」处添加，模板 Web 属性介绍可参考 模板 Web 属性。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 按钮自定义事件与控件事件的事件执行方式是一致的，所有适用于控件事件的方法均适用于按钮自定义事件。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 按钮自定义事件与控件事件的事件执行方式是一致的，所有适用于控件事件的方法均适用于按钮自定义事件。

---

## 前端开发 > 前端常用知识（11篇）

### 89. jQuery语法

- **doc-view ID**: 1183
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > jQuery语法
- **核心概念**: FR 报表使用 jQuery 框架，因此可以在模板中使用 jQuery 的 each 函数来遍历整个对象集合，对集合中每个对象进行统一处理。使用 $.each(objects,function(i,item){...}); 遍历整个 object 集合，对每个 object 执行函数 function。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FR 报表使用 jQuery 框架，因此可以在模板中使用 jQuery 的 each 函数来遍历整个对象集合，对集合中每个对象进行统一处理。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FR 报表使用 jQuery 框架，因此可以在模板中使用 jQuery 的 each 函数来遍历整个对象集合，对集合中每个对象进行统一处理。

**关键代码/公式/API：**
- 代码片段: `$.each(this.options.form.name_widgets,function(i,item) ⏎ {item.reset()});`
- Java类/方法: `item.reset()`

### 90. 字符串对象

- **doc-view ID**: 1184
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > 字符串对象
- **核心概念**: JavaScript 中会需要对字符串进行操作，比如如何判断字符串是否为空，计算字符串的长度，替换、查找、截取字符串，或者将字符串转换为其他类型等操作。文本将介绍 JavaScript 中如何对字符串进行操作。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: JavaScript 中会需要对字符串进行操作，比如如何判断字符串是否为空，计算字符串的长度，替换、查找、截取字符串，或者将字符串转换为其他类型等操作。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: search(regexp) 方法用于检索字符串中指定的子字符串。

**关键代码/公式/API：**
- 代码片段: `var txt= "Hello FR"; ⏎ alert("字符串长度为："+txt.length);       //返回长度`
- 代码片段: `var strCtl = this.options.form.getWidgetByName("控件名");  ⏎ alert("字符串长度为："+strCtl.getText().length); //返回长度`
- 代码片段: `var txt= ""; ⏎ if(txt.length==0||txt=='') alert("字符串为空"); //为空  ⏎ else alert("字符串不为空"); //不为空`
- Java类/方法: `this.options.form.getWidgetByName("控件名")`
- Java类/方法: `strCtl.getText()`
- Java类/方法: `txt.replace(/Visit/, "Hello")`
- Java类/方法: `txt.search("abc")`

### 91. 数组对象

- **doc-view ID**: 1185
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > 数组对象
- **核心概念**: JavaScript 中，我们有时需要对数组进行操作，比如创建数组，遍历数组元素，排序等等。本文将介绍一些数组的基本使用方法。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: JavaScript 中，我们有时需要对数组进行操作，比如创建数组，遍历数组元素，排序等等。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: Array 对象用于在单个变量中存储多个值。创建数组的方法如下

**关键代码/公式/API：**
- 代码片段: `var txt = new Array("I","love","FR"); ⏎ alert(txt);`
- 代码片段: `var txt = new Array(); ⏎ txt[0] = "I"; ⏎ txt[1] = "love"; ⏎ txt[2] = "FR"; ⏎ alert(txt);`
- 代码片段: `var txt = new Array("I","love","FR"); ⏎ for(i=0;i<txt.length;i++)    ⏎ {alert(txt[i]);}`
- Java类/方法: `Object.toString()`
- Java类/方法: `txt.toString()`
- Java类/方法: `document.write(txt.sort()`
- Java类/方法: `document.write(arr.sort(sortNumber)`

### 92. 日期对象

- **doc-view ID**: 1186
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > 日期对象
- **核心概念**: JavaScript 中经常需要对日期型的数据进行操作，操作后给日期控件赋值。在对日期数据进行操作时，需要用 JavaScript 中的日期函数来处理日期对象。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: JavaScript 中经常需要对日期型的数据进行操作，操作后给日期控件赋值。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: JavaScript 中经常需要对日期型的数据进行操作，操作后给日期控件赋值。

**关键代码/公式/API：**
- 代码片段: `var mydate = new Date(); //创建日期对象，返回值为当前日期（包含时分秒）  ⏎ this.options.form.getWidgetByName("date").setValue(mydate); //赋值给日期控件`
- 代码片段: `var mydate = new Date(); //创建日期对象，返回值为当前日期（包含时分秒） ⏎ mydate.setDate(mydate.getDate()-1); //设置日期对象中的“日”，为当前日-1 ⏎ this.options.form.getWidgetByName("date").setValue(mydate); //赋值给日期控件`
- 代码片段: `var mydate = new Date(); //创建日期对象，返回值为当前日期（包含时分秒） ⏎ mydate.setMonth(mydate.getMonth()-1); //设置日期对象中的“月”，为当前月-1 ⏎ this.options.form.getWidgetByName("date").setValue(mydate); //赋值给日期控件`
- Java类/方法: `this.options.form.getWidgetByName("date")`
- Java类/方法: `mydate.setDate(mydate.getDate()`
- Java类/方法: `mydate.setMonth(mydate.getMonth()`

### 93. JS中引用HTML

- **doc-view ID**: 1187
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > JS中引用HTML
- **核心概念**: HTML DOM 是 W3C 标准（是 HTML 文档对象模型的英文缩写，Document Object Model for HTML）。HTML DOM 定义了用于 HTML 的一系列标准的对象，以及访问和处理 HTML 文档的标准方法。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: HTML DOM 是 W3C 标准（是 HTML 文档对象模型的英文缩写，Document Object Model for HTML）。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: DOM 定义了用于 HTML 的一系列标准的对象，以及访问和处理 HTML 文档的标准方法。

### 94. Window对象

- **doc-view ID**: 1189
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > Window对象
- **核心概念**: Window 对象表示浏览器中打开的窗口。如果文档包含框架（frame 或 iframe 标签），浏览器会为 HTML 文档创建一个 Window 对象，并为每个框架创建一个额外的 Window 对象。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: Window 对象表示浏览器中打开的窗口。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 用于打印当前窗口的内容。

**关键代码/公式/API：**
- 代码片段: `<script type="text/javascript"> ⏎ function display_alert() ⏎   { ⏎   alert("I am an alert box!!") ⏎   } ⏎ </script>`
- 代码片段: `<html> ⏎ <head> ⏎ <script type="text/javascript"> ⏎ function display_alert() ⏎   { ⏎   alert("I am an alert box!!") ⏎   } ⏎ </script> ⏎ </head> ⏎ <body> ⏎ <input type="button" onclick="display_alert()`
- 代码片段: `<script type="text/javascript"> ⏎ function show_confirm() ⏎ { ⏎ var r=confirm("Press a button!"); ⏎ if (r==true) ⏎   { ⏎   alert("You pressed OK!"); ⏎   } ⏎ else ⏎   { ⏎   alert("You pressed Cancel!")`
- URL: `https://help.fanruan.com/finereport10.0/`
- Java类/方法: `window.alert()`
- Java类/方法: `self.close()`
- Java类/方法: `document.write("你好，" + name + "！")`
- Java类/方法: `window.open(URL,name,features,replace)`

### 95. location对象

- **doc-view ID**: 1190
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > location对象
- **核心概念**: Location 对象包含有关当前 URL 的信息。Location 对象是 Window 对象的一个部分，可通过 window.location 属性来访问。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: Location 对象包含有关当前 URL 的信息。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: reload() 方法用于重新加载当前文档。

**关键代码/公式/API：**
- 代码片段: `window.location.reload()`
- Java类/方法: `window.location.reload()`

### 96. document对象

- **doc-view ID**: 1191
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > document对象
- **核心概念**: 每个载入浏览器的 HTML 文档都会成为 Document 对象。Document 对象使我们可以从脚本中对 HTML 页面中的所有元素进行访问。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 每个载入浏览器的 HTML 文档都会成为 Document 对象。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 每个载入浏览器的 HTML 文档都会成为 Document 对象。

**关键代码/公式/API：**
- 代码片段: `document.close()`
- 代码片段: `document.getElementById(id)`
- 代码片段: `<html> ⏎ <head> ⏎ <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">  ⏎ <script type="text/javascript"> ⏎ function getValue() ⏎ { ⏎ var x=document.getElementById("myHeader") ⏎ alert(x`
- Java类/方法: `document.close()`
- Java类/方法: `document.getElementById(id)`
- Java类/方法: `document.getElementById("myHeader")`
- Java类/方法: `document.write(exp1,exp2,exp3,....)`

### 97. setInterval

- **doc-view ID**: 1679
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > setInterval
- **核心概念**: setInterval() 方法可按照指定的周期（以毫秒计）来调用函数或计算表达式。setInterval() 方法会不停地调用函数，直到 clearInterval() 被调用或窗口被关闭。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: setInterval() 方法可按照指定的周期（以毫秒计）来调用函数或计算表达式。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: setInterval() 方法可按照指定的周期（以毫秒计）来调用函数或计算表达式。

**关键代码/公式/API：**
- 代码片段: `setInterval("self.location.reload();",10000); //10000ms 即每 10s 刷新一次页面。`
- Java类/方法: `self.location.reload()`

### 98. 借用浏览器功能写JS语句

- **doc-view ID**: 1923
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > 借用浏览器功能写JS语句
- **核心概念**: 报表中很多个性化功能的实现，大多是使用 JavaScript 来实现的，那么我们如何能零基础写 JavaScript 来实现功能呢？我们可以通过浏览器中的「审查元素」，获取到报表中每个元素对应的代码，从而能据此快速编辑出需要的 JavaScript 语句添加在模板中，实现想要的功能。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 报表中很多个性化功能的实现，大多是使用 JavaScript 来实现的，那么我们如何能零基础写 JavaScript 来实现功能呢？
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 保存模板，选择「填报预览」，点击按钮，也可实现超级链接弹出对话框的效果。效果同第一章预览效果图。

**关键代码/公式/API：**
- 代码片段: `<span class="linkspan" style="cursor:pointer;" onclick="FR.doHyperlink(event||window.event, [{&quot;data&quot;:&quot;var as=arguments;  ⏎ return FR.tc(function(){FR.doHyperlinkByGet4Reportlet({\&quot;`
- 代码片段: `FR.doHyperlink(event||window.event, [{&quot;data&quot;:&quot;var as=arguments; return FR.tc(function() ⏎ {FR.doHyperlinkByGet4Reportlet({\&quot;para\&quot;:{\&quot;__pi__\&quot;:true},\&quot;feature\&`
- 代码片段: `FR.doHyperlink(event||window.event, [{"data":"var as=arguments; return FR.tc(function(){FR.doHyperlinkByGet4Reportlet ⏎ ({\"para\":{\"__pi__\":true},\"feature\":\"width=600,height=400,\",\"title\":\"网`
- 公式: `&quot;:{\&quot;__pi__\&quot;:true},\&quot;feature\&quot;:\`
- 公式: `&quot;:\&quot;网络报表1\&quot;,\&quot;url\&quot;:\`
- 公式: `&quot;,\&quot;target\&quot;:\&quot;_dialog\`
- 公式: `&quot;:\&quot;_dialog\`
- Java类/方法: `FR.tc(function()`
- Java类/方法: `FR.doHyperlink(event||window.event, [{"data":"var as=arguments; return FR.tc(function()`
- Java类/方法: `FR.doHyperlink(window.event, [{"data":"var as=arguments; return FR.tc(function()`

### 99. 自定义JS事件中快速选择指定DOM

- **doc-view ID**: 2469
- **路径**: 二次开发 > 前端开发 > 前端常用知识 > 自定义JS事件中快速选择指定DOM
- **核心概念**: Finereport 中控件的「事件」功能非常强大，用户可通过自定义 JS 做出想要的效果。但是 JS 对于大多数非专业报表开发者较为陌生，需要额外的学习成本，尤其是 jQuery 选择器。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: Finereport 中控件的「事件」功能非常强大，用户可通过自定义 JS 做出想要的效果。
- 人员岗位: Finereport 中控件的「事件」功能非常强大，用户可通过自定义 JS 做出想要的效果。但是 JS 对于大多数非专业报表开发者较为陌生，需要额外的学习成本，尤其是 jQuery 选择器。而报表设计中，自定义 JS 事件又非常需要获取指定
- 功能应用场景: Finereport 中控件的「事件」功能非常强大，用户可通过自定义 JS 做出想要的效果。

**关键代码/公式/API：**
- 公式: `webroot\WEB-INF\reportlets\`

---
