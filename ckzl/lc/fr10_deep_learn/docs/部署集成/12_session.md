<!--
KB_INDEX: {
  "title": "部署集成 - session",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "部署集成",
    "session"
  ],
  "summary": "「部署集成」分页：session（约 8 篇条目）；FR10 帮助文档「部署集成」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 部署集成 · session

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §部署集成


## session（8篇）

### 92. 给session赋值实现报表间参数共享

- **doc-view ID**: 1152
- **路径**: 部署集成 > session > 给session赋值实现报表间参数共享
- **核心概念**: 有几张不同的报表，希望某一张报表的日期控件选择好日期后，其他报表日期控件的参数都变成该日期，那么该如何实现呢？可以利用 Session 赋值来实现。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 有几张不同的报表，希望某一张报表的日期控件选择好日期后，其他报表日期控件的参数都变成该日期，那么该如何实现呢？
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 有几张不同的报表，希望某一张报表的日期控件选择好日期后，其他报表日期控件的参数都变成该日期，那么该如何实现呢？

**关键代码/公式/API：**
- 代码片段: `var str=this.getValue();    //获取当前控件的值 ⏎ FR.ajax({   ⏎    url: "/webroot/session/report?id="+encodeURIComponent(str)  //将值传递给 Session 这个 Servlet 中 ⏎ });`
- 代码片段: `<?xml version="1.0" encoding="UTF-8"?> ⏎ <web-app ⏎    xmlns="http://java.sun.com/xml/ns/j2ee" ⏎    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ⏎    xsi:schemaLocation="http://java.sun.com/x`
- 公式: `getValue()`
- 公式: `encodeURIComponent(str)`
- URL: `https://code.fanruan.com/demo/example/src/branch/release/10.0/src/main/java/com/fr/data/session.java`
- URL: `http://java.sun.com/xml/ns/j2ee`
- URL: `http://www.w3.org/2001/XMLSchema-instance`
- URL: `http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd`

### 93. cookie

- **doc-view ID**: 1153
- **路径**: 部署集成 > session > cookie
- **核心概念**: Cookie 是存储于访问者计算机的变量，每当同一台计算机通过浏览器请求某个页面时，就会发送这个 Cookie。您可以使用 JavaScript 来创建和取回 Cookie 的值。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: Cookie 是存储于访问者计算机的变量，每当同一台计算机通过浏览器请求某个页面时，就会发送这个 Cookie。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: Cookie 是存储于访问者计算机的变量，每当同一台计算机通过浏览器请求某个页面时，就会发送这个 Cookie。

**关键代码/公式/API：**
- 代码片段: `document.write(document.cookie);`
- 代码片段: `function setCookie(c_name,value,expiredays) ⏎ { ⏎ var exdate=new Date() ⏎ exdate.setDate(exdate.getDate()+expiredays) ⏎ document.cookie=c_name+ "=" +escape(value)+ ⏎ ((expiredays==null) ? "" : ";expir`
- 代码片段: `function getCookie(c_name) ⏎ { ⏎ if (document.cookie.length>0) ⏎   { ⏎   c_start=document.cookie.indexOf(c_name + "=") ⏎   if (c_start!=-1) ⏎     {  ⏎     c_start=c_start + c_name.length+1  ⏎     c_en`
- 公式: `write(document.cookie)`
- 公式: `setCookie(c_name,value,expiredays)`
- 公式: `Date()`
- 公式: `setDate(exdate.getDate()`

### 94. 在JavaScript中获取session中的值

- **doc-view ID**: 1154
- **路径**: 部署集成 > session > 在JavaScript中获取session中的值
- **核心概念**: 有时我们需要在 Javascript 中使用 Session 的值 Session 是后台服务器端的变量，而 JS 是前段脚本，在 JS 中是没有现成的方法获取 Session 的值的，需要通过服务器语言来获取。比如java就可以用来获取 Session 的值，再赋值给 JS 变量。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 有时我们需要在 Javascript 中使用 Session 的值 Session 是后台服务器端的变量，而 JS 是前段脚本，在 JS 中是没有现成的方法获取 Session 的值的，需要通过服务器语言来获取。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 有时我们需要在 Javascript 中使用 Session 的值 Session 是后台服务器端的变量，而 JS 是前段脚本，在 JS 中是没有现成的方法获取 Session 的值的，需要通过服务器语言来获取。

**关键代码/公式/API：**
- 代码片段: `var id = '<%=session.getAttribute("id")%>';`
- 代码片段: `<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%> ⏎ <html>     ⏎  <head>  ⏎  <title>自定义浏览页面</title>      ⏎  <script type="text/javascript">        ⏎  function x(){`
- 公式: `getAttribute("id")`
- 公式: `x()`
- 公式: `setAttribute("id","Imsession")`
- 公式: `alert("session是"+id)`

### 95. cookie跟session之间的关系

- **doc-view ID**: 1155
- **路径**: 部署集成 > session > cookie跟session之间的关系
- **核心概念**: Cookies 是一种能够让网站服务器把少量数据储存到客户端的硬盘或内存，或是从客户端的硬盘读取数据的一种技术。Session 介绍可参考文档：报表 Session 与应用 Session。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: Cookies 是一种能够让网站服务器把少量数据储存到客户端的硬盘或内存，或是从客户端的硬盘读取数据的一种技术。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: Cookies 是一种能够让网站服务器把少量数据储存到客户端的硬盘或内存，或是从客户端的硬盘读取数据的一种技术。

### 96. request、response与session

- **doc-view ID**: 1156
- **路径**: 部署集成 > session > request、response与session
- **核心概念**: 该对象封装了用户提交的信息，通过调用该对象相应的方法可以获取封装的信息，即使用该对象可以获取用户提交的信息。request.getAttribute("key") 可得到 JSP 页面存入 Value。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 该对象封装了用户提交的信息，通过调用该对象相应的方法可以获取封装的信息，即使用该对象可以获取用户提交的信息。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: Session：用于保存每个用户的专用信息。Session 中的信息保存在 Web 服务器的内存中，保存的数据量可大可小。当 Session 超时或被关闭时将自动释放保存的数据信息。对于小量的数据 Session 对象保存还是一个不错的选择。

**关键代码/公式/API：**
- 公式: `getAttribute("key")`
- 公式: `setAttribute(key, value)`
- 公式: `setAttribute(key，value)`
- 公式: `forward()`

### 97. 权限中使用session

- **doc-view ID**: 1159
- **路径**: 部署集成 > session > 权限中使用session
- **核心概念**: 权限中使用 Session，一般是用来存放用户名和密码，下面分两种情况介绍用户名和密码的保存。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 权限中使用 Session，一般是用来存放用户名和密码，下面分两种情况介绍用户名和密码的保存。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 权限中使用 Session，一般是用来存放用户名和密码，下面分两种情况介绍用户名和密码的保存。

### 98. 报表里获取session中的值

- **doc-view ID**: 1160
- **路径**: 部署集成 > session > 报表里获取session中的值
- **核心概念**: Session 保存了 key-value 属性对，希望在报表中拿到 Session 中的 key 的值。直接在报表模板中获取 Session 中的值 报表应用集成到用户系统中，共用同一个 Session，此时可以直接在报表中获取 Session 的值。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: Session 保存了 key-value 属性对，希望在报表中拿到 Session 中的 key 的值。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: Session 保存了 key-value 属性对，希望在报表中拿到 Session 中的 key 的值。

**关键代码/公式/API：**
- 代码片段: `<%@ page language="java" contentType="text/html; charset=utf-8" pageEncoding="utf-8"%> <html> <body> <iframe width=100% height=100% src='/webroot/decision/view/report?viewlet=getkey.cpt&country=<%=ses`
- 代码片段: `contentPane.currentSessionID`
- 代码片段: `_g().sessionID`
- 公式: `getAttribute(String key)`
- 公式: `setAttribute(String key,Object value)`
- 公式: `getAttribute("fine_username")`
- 公式: `getElementById('reportFrame')`
- JS API: `contentPane`
- JS API: `_g().sessionID`

### 99. 报表session与应用session

- **doc-view ID**: 1161
- **路径**: 部署集成 > session > 报表session与应用session
- **核心概念**: 报表集成到项目中可能会有一个疑问就是系统应用和报表应用在一个 Web 服务器下，那系统 Session 和报表 Session 是不是一个 Session 呢？如果不是那会不会有冲突呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 报表集成到项目中可能会有一个疑问就是系统应用和报表应用在一个 Web 服务器下，那系统 Session 和报表 Session 是不是一个 Session 呢？
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 报表集成到项目中可能会有一个疑问就是系统应用和报表应用在一个 Web 服务器下，那系统 Session 和报表 Session 是不是一个 Session 呢？

**关键代码/公式/API：**
- 公式: `getSession(true)`
- 公式: `invalidate()`
- JS API: `window.oncolose`

---
