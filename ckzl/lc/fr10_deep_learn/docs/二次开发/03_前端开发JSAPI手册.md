<!--
KB_INDEX: {
  "title": "二次开发 - 前端开发JSAPI手册",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "二次开发",
    "JS API手册",
    "前端开发"
  ],
  "summary": "「二次开发」分页：JS API手册（约 9 篇条目）；FR10 帮助文档「二次开发」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 二次开发 · 前端开发JSAPI手册

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §二次开发


## 前端开发 > JS API手册（9篇）

### 4. AJAX

- **doc-view ID**: 602
- **路径**: 二次开发 > 前端开发 > JS API手册 > 操作 > AJAX
- **核心概念**: ajax 是一种与服务器交换数据的技术，可以在不重新载入整个页面的情况下更新网页的一部分。FR.ajax 是封装过的 jQuery.ajax() 函数，在报表中对特定网页进行 ajax 请求， data 参数做了中日韩文编码处理。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 3）保存模板，点击「分页预览」，效果如应用场景中所示。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: ajax 是一种与服务器交换数据的技术，可以在不重新载入整个页面的情况下更新网页的一部分。

**关键代码/公式/API：**
- 代码片段: `success: function(data, textStatus){   ⏎  // data 为服务器返回的，并根据 dataType 参数进行处理后的数据。 ⏎ //textStatus 为状态值 success ⏎ }`
- 代码片段: `FR.ajax({ ⏎  url: "/webapps/webroot/a.html", ⏎  success: function(data, textStatus) { ⏎  alert(this.url); ⏎  } ⏎ });`
- 代码片段: `error: function(XMLHttpRequest, textStatus, errorThrown){  ⏎ //参数分别为 XMLHttpRequest 对象、错误信息、捕获的异常对象。 ⏎ //通常 textStatus 和errorThrown 之中只有一个会包含信息 ⏎  }`
- URL: `http://env.finedevelop.com`
- Java类/方法: `jQuery.ajax()`
- Java类/方法: `FR.ajax({
 url: "/webapps/webroot/a.html",
 success: function(data, textStatus)`
- Java类/方法: `FR.ajax({
 url: "some.jsp",
 error: function(XMLHttpRequest, textStatus, errorThrown)`
- Java类/方法: `FR.ajax({
 url: "some.jsp",
 complete: function(XMLHttpRequest, textStatus)`

### 5. Msg

- **doc-view ID**: 603
- **路径**: 二次开发 > 前端开发 > JS API手册 > Msg 弹窗 > Msg
- **核心概念**: FR 内置了统一风格的消息框，替代实现了 Window 中的 alert、confirm 以及 prompt。FR.Msg.alert(title, message, callback)，弹出警告框。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FR 内置了统一风格的消息框，替代实现了 Window 中的 alert、confirm 以及 prompt。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FR 内置了统一风格的消息框，替代实现了 Window 中的 alert、confirm 以及 prompt。

**关键代码/公式/API：**
- 代码片段: `FR.Msg.confirm("警告","确定要删除吗？",function(value){ if(value){ alert("即将删除!"); } else{ alert("取消删除!"); } },100)`
- Java类/方法: `FR.Msg.alert(title, message, callback)`
- Java类/方法: `FR.Msg.alert("警告","值错误")`
- Java类/方法: `FR.Msg.confirm(title, message, callback, min_width)`
- Java类/方法: `FR.Msg.confirm("警告","确认要删除吗?")`

### 6. FS决策系统

- **doc-view ID**: 606
- **路径**: 二次开发 > 前端开发 > JS API手册 > 对象 > FS决策系统
- **核心概念**: FineReport.js 中除了包含 FineReport 属性和方法之外，还包含了决策系统相关的属性和方法。报表中的 Web 事件、控件事件、JavaScript 类型的超级链接、决策报表事件中都可以通过 window.parent.FS 来获得 FS 对象。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FineReport.js 中除了包含 FineReport 属性和方法之外，还包含了决策系统相关的属性和方法。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FineReport.js 中除了包含 FineReport 属性和方法之外，还包含了决策系统相关的属性和方法。

**关键代码/公式/API：**
- 代码片段: `window.location.href = window.parent.FS.signOut();`
- 代码片段: `FR.logoutApp();`
- 代码片段: `window.parent.FS.tabPane.closeActiveTab();`
- URL: `http://www.baidu.com`
- Java类/方法: `FS.signOut()`
- Java类/方法: `window.parent.FS.signOut()`
- Java类/方法: `FR.logoutApp()`
- Java类/方法: `FS.tabPane.closeActiveTab()`

### 7. curLGP

- **doc-view ID**: 610
- **路径**: 二次开发 > 前端开发 > JS API手册 > 对象 > curLGP
- **核心概念**: curLGP 即 current logicpane，填报预览和分析预览下 contentPane 下都会有一个 curLGP 对象。1）在 cpt 模板中 在 cpt 模板的 JS 脚本中可以使用 contentPane.curLGP 来获取该对象。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: curLGP 即 current logicpane，填报预览和分析预览下 contentPane 下都会有一个 curLGP 对象。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: curLGP 即 current logicpane，填报预览和分析预览下 contentPane 下都会有一个 curLGP 对象。

**关键代码/公式/API：**
- 代码片段: `var contentPane = document.getElementById('reportFrame').contentWindow.contentPane.curLGP;`
- 代码片段: `var contentPane = document.getElementByID('reportFrame').contentWindow.contentPane.curLGP.write;`
- Java类/方法: `document.getElementById('reportFrame')`
- Java类/方法: `document.getElementByID('reportFrame')`

### 8. contentPane

- **doc-view ID**: 619
- **路径**: 二次开发 > 前端开发 > JS API手册 > 对象 > contentPane
- **核心概念**: contentPane 是 contentWindow 下面的最常用的一个属性，为存放 cpt 报表内容的容器。注：contentPane 只有在 cpt 中才有，frm 中没有 1）在普通模板中 在普通模板的 JS 脚本中直接使用 contentPane 就能获取到该对象。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: contentPane 是 contentWindow 下面的最常用的一个属性，为存放 cpt 报表内容的容器。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: contentPane 是 contentWindow 下面的最常用的一个属性，为存放 cpt 报表内容的容器。

**关键代码/公式/API：**
- 代码片段: `var contentPane=document.getElementById('reportFrame').contentWindow.contentPane;`
- 代码片段: `document.getElementById('reportFrame').contentWindow.contentPane.getWidgetByName('控件名').fireEvent('click');`
- URL: `http://localhost`
- Java类/方法: `document.getElementById('reportFrame')`
- Java类/方法: `contentWindow.contentPane.getWidgetByName('控件名')`
- Java类/方法: `contentPane.writeReport()`
- Java类/方法: `contentPane.writeReport(reportIndex)`

### 9. FineReport内置方法

- **doc-view ID**: 622
- **路径**: 二次开发 > 前端开发 > JS API手册 > 方法 > FineReport内置方法
- **核心概念**: 前端预览报表时，模板会被转为 HTML，这个 HTML 的 head 标签中会引入 FineReport 内置的 JavaScript 文件finereport.js，代码如下： ``` <script type="text/javascript" src="/webroot/decision/view/report?op=emb&resource=finereport.js"></script>

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 前端预览报表时，模板会被转为 HTML，这个 HTML 的 head 标签中会引入 FineReport 内置的 JavaScript 文件finereport.js，代码如下： ``` <script type="text/javascript" src="/webroot/decision/vi
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 前端预览报表时，模板会被转为 HTML，这个 HTML 的 head 标签中会引入 FineReport 内置的 JavaScript 文件finereport.js，代码如下： ``` <script type="text/javascript" src="/webroot/decision/vi

**关键代码/公式/API：**
- 代码片段: `<script type="text/javascript" src="/webroot/decision/view/report?op=emb&resource=finereport.js"></script>`
- 代码片段: `FR.showDialog("Test",600,400,"Hello World")`
- 代码片段: `<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"> ⏎ <html> ⏎  <head> ⏎   <title>FineReport Demo</title> ⏎   <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /> ⏎   <scri`
- SQL: `select 函数。`
- URL: `http://localhost`
- Java类/方法: `FR.showDialog("Test",600,400,"Hello World")`
- Java类/方法: `FR.showDialog("Test", 600, 400, "Hello World")`
- Java类/方法: `FR.remoteEvaluate("sum(A1,A2)`

### 10. FineReport 的 JS API

- **doc-view ID**: 1174
- **路径**: 二次开发 > 前端开发 > JS API手册 > FineReport 的 JS API
- **核心概念**: FineReport 开放了大量的 JS API 给用户，用户利用这些 JS 接口，可实现更多更复杂的功能。根据执行 JS 的主体不同可以将 FineReport 的 JS API 分为三大类：FR、FS、contentWindow。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: FineReport 开放了大量的 JS API 给用户，用户利用这些 JS 接口，可实现更多更复杂的功能。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: FineReport 开放了大量的 JS API 给用户，用户利用这些 JS 接口，可实现更多更复杂的功能。

**关键代码/公式/API：**
- 代码片段: `var contentWindow = document.getElementById("reportFrame").contentWindow.XXX;`
- Java类/方法: `document.getElementById('reportFrame')`
- Java类/方法: `document.getElementById("reportFrame")`

### 11. 引用控件及控件方法列表

- **doc-view ID**: 1181
- **路径**: 二次开发 > 前端开发 > JS API手册 > 方法 > 引用控件及控件方法列表
- **核心概念**: 控件有很多的方法，比如控制控件是否可见，是否可用等等，在调用控件方法前必须要获取到控件。从 6.5.5 版本开始，在cpt 和 frm 的参数界面，在 cpt 的填报界面和在 frm 的 body 主体中，都可以获取到控件，并引用控件的方法。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 控件有很多的方法，比如控制控件是否可见，是否可用等等，在调用控件方法前必须要获取到控件。
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 控件有很多的方法，比如控制控件是否可见，是否可用等等，在调用控件方法前必须要获取到控件。

**关键代码/公式/API：**
- 代码片段: `var Widget = this.options.form.getWidgetByName("WidgetName");`
- 代码片段: `var Widget = contentPane.getWidgetByName("WidgetName");`
- Java类/方法: `this.options.form.getWidgetByName("WidgetName")`
- Java类/方法: `contentPane.getWidgetByName("WidgetName")`
- Java类/方法: `this.getValue()`
- Java类/方法: `Widget.getValue()`

### 12. this

- **doc-view ID**: 1677
- **路径**: 二次开发 > 前端开发 > JS API手册 > 对象 > this
- **核心概念**: 在控件的事件中，可以通过 this 直接获取到当前的控件对象 控件指填报单元格中的控件、参数界面中的控件、决策报表 body 主体中的控件 获得控件后，可以调用控件的操作方法等 cpt 参数界面文本控件的编辑结束事件中获取控件的值 JavaScript 代码如下： ``` var a = this.getValue(); FR.Msg.alert("提示",a); ``` 文本控件值输入 FR，点

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为二次开发/API 说明文档，无具体统计指标）
- 业务场景: 在控件的事件中，可以通过 this 直接获取到当前的控件对象 控件指填报单元格中的控件、参数界面中的控件、决策报表 body 主体中的控件 获得控件后，可以调用控件的操作方法等 cpt 参数界面文本控件的编辑结束事件中获取控件的值 JavaScript 代码如下： ``` var a = this.
- 人员岗位: 未在文中明确指定（面向报表开发者/二次开发人员/系统管理员）
- 功能应用场景: 在控件的事件中，可以通过 this 直接获取到当前的控件对象 控件指填报单元格中的控件、参数界面中的控件、决策报表 body 主体中的控件 获得控件后，可以调用控件的操作方法等 cpt 参数界面文本控件的编辑结束事件中获取控件的值 JavaScript 代码如下： ``` var a = this.

**关键代码/公式/API：**
- 代码片段: `var a = this.getValue(); FR.Msg.alert("提示",a);`
- Java类/方法: `this.getValue()`
- Java类/方法: `FR.Msg.alert("提示",a)`

---
