<!--
KB_INDEX: {
  "title": "部署集成 - 前台单点登录与CAS 单点登录",
  "stage": "deep-learn",
  "tags": [
    "FR10",
    "deep-learn",
    "⭐分页"
  ],
  "keywords": [
    "部署集成",
    "前台单点登录",
    "CAS 单点登录",
    "单点登录"
  ],
  "summary": "「部署集成」分页：前台单点登录、CAS 单点登录（约 15 篇条目）；FR10 帮助文档「部署集成」分类 压缩提取，条目型检索语料（deep-learn 分页）。"
}
-->

# 部署集成 · 前台单点登录与CAS 单点登录

> 来源: [拆分图谱](../00_拆分图谱与来源.md) §部署集成


## 单点登录 > 前台单点登录（5篇）

### 53. iframe跨域单点登录

- **doc-view ID**: 879
- **路径**: 部署集成 > 单点登录 > 前台单点登录 > iframe跨域单点登录
- **核心概念**: 企业往往会有多个报表平台或多个相关的平台，用户希望只登录一次就可以访问其他的系统，例如登录 OA 系统的同时登录报表系统，即将输入的用户名密码也发送到报表服务器进行认证，从而访问报表时不需要再次登录。在上一节介绍了 Ajax 跨域异步单点登录 ，那么如何通过 iframe 方式实现 OA 系统和报表系统的跨域单点登录呢？

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 企业往往会有多个报表平台或多个相关的平台，用户希望只登录一次就可以访问其他的系统，例如登录 OA 系统的同时登录报表系统，即将输入的用户名密码也发送到报表服务器进行认证，从而访问报表时不需要再次登录。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 企业往往会有多个报表平台或多个相关的平台，用户希望只登录一次就可以访问其他的系统，例如登录 OA 系统的同时登录报表系统，即将输入的用户名密码也发送到报表服务器进行认证，从而访问报表时不需要再次登录。

**关键代码/公式/API：**
- 代码片段: `<!DOCTYPE html> ⏎ <html> ⏎   <head>  ⏎   <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"> ⏎   <meta http-equiv="X-UA-Compatible" content="IE=10" /> ⏎   <script type="text/javascript`
- 代码片段: `<meta http-equiv="X-UA-Compatible" content="IE=10" />`
- 公式: `doSubmit()`
- 公式: `getElementById("username")`
- 公式: `getElementById("password")`
- 公式: `createElement("iframe")`
- JS API: `window.location`
- JS API: `window.location后面的`
- URL: `http://localhost`

### 54. Ajax 跨域异步单点登录

- **doc-view ID**: 881
- **路径**: 部署集成 > 单点登录 > 前台单点登录 > Ajax 跨域异步单点登录
- **核心概念**: OA 系统与报表系统集成，将报表绑定在 OA 系统的节点上，对于 OA 系统中想实现对 FineReport 的单点登录，用户需要在 OA 的登录界面中将用户名和密码传入到报表的认证地址进行认证。若 OA 系统和报表系统不是部署在同一台服务器上，在登录时进行跨域，那么要如何通过 Ajax 实现 OA 系统和报表系统的跨域登录呢？

**业务场景四要素：**
- 统计指标方案: 注2：内网环境中，下面代码引用的 jquery.min.js 文件无法生效，需下载 JS 文件到本地并修改对应的路径，具体步骤请参见：单点登录问题汇总 文档中的 2.4 节内容。
- 业务场景: 注：本章示例适用于 PC 端。
- 人员岗位: 1）以管理员身份进入端口号为 8075 工程的平台，点击「管理系统>安全管理」，关闭「内容嗅探攻击防护」、「点击劫持攻击防护」，如下图所示：
- 功能应用场景: 注：本章示例适用于 PC 端。

**关键代码/公式/API：**
- 代码片段: `<!DOCTYPE html> ⏎ <html> ⏎ <head> ⏎     <meta http-equiv="Content-Type" content="text/html; " charset="UTF-8"> ⏎     <script type="text/javascript" src="https://cdn.bootcss.com/jquery/1.9.1/jquery.min`
- 代码片段: `var url = "http://localhost:8080/webroot/decision/login/cross/domain" + "?fine_username=" +encodeURIComponent(username) ⏎  + "&fine_password=" + encodeURIComponent(password) + "&validity=" + -1;`
- 代码片段: `data:{"fine_username":username,"fine_password":password,validity:-1},`
- 公式: `doSubmit()`
- 公式: `getElementById("username")`
- 公式: `trim()`
- 公式: `getElementById("password")`
- JS API: `window.alert`
- JS API: `window.location`
- URL: `http://localhost`
- URL: `https://cdn.bootcss.com/jquery/1.9.1/jquery.min.js`

### 55. 前台单点登录接口

- **doc-view ID**: 884
- **路径**: 部署集成 > 单点登录 > 前台单点登录 > 前台单点登录接口
- **核心概念**: 本文将介绍产品支持的单点登录接口。注：我们提供帆软单点相关的官方接口，只解决官方接口调用相关的问题。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 本文将介绍产品支持的单点登录接口。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 需要将用户名及密码等信息放在 url 后面进行登录验证，配合 iframe 或者 ajax 可实现前台的跨域单点登录行为。只需要在用户的登录页面加上该接口的调用，后台无需进行适配。需要用户系统的账号和密码与帆软平台账号密码相同。

**关键代码/公式/API：**
- 代码片段: `http://localhost:8080/webroot/decision/login/cross/domain?fine_username=XX&fine_password=XX&validity= ⏎ -2&callback=`
- URL: `http://localhost`

### 56. 前台单点登录之AES加密示例

- **doc-view ID**: 4616
- **路径**: 部署集成 > 单点登录 > 前台单点登录 > 前台单点登录之AES加密示例
- **核心概念**: 前台单点登录 时，用户在自定义登录页面内输入的用户信息需要发送到数据决策系统中进行登录验证。在发送过程中，以明文形式传输的用户密码易受到劫持攻击。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 前台单点登录 时，用户在自定义登录页面内输入的用户信息需要发送到数据决策系统中进行登录验证。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 用户在自定义登录页面内输入的明文密码会经过以下步骤从前台传输至后台，最终用于登录验证。如下图所示：

**关键代码/公式/API：**
- 代码片段: `<html><head> ⏎     <meta charset="utf-8"> ⏎     <meta http-equiv="X-UA-Compatible" content="IE=edge"> ⏎     <meta name="viewport" content="width=device-width, initial-scale=1"> ⏎     <title>跨域登录加密Demo`
- 代码片段: `<html><head> ⏎     <meta charset="utf-8"> ⏎     <meta http-equiv="X-UA-Compatible" content="IE=edge"> ⏎     <meta name="viewport" content="width=device-width, initial-scale=1"> ⏎     <title>跨域登录加密Demo`
- 公式: `aesEncrypt(password, frontSeed)`
- 公式: `aesEncrypt(password, 密钥)`
- 公式: `getElementById("submitBtn")`
- 公式: `addEventListener("click", function ()`
- JS API: `window.alert`
- JS API: `window.location`
- SQL: `select value from FINE_CONF_ENTITY where id = 'SecurityConfig.frontSeed'，点击「预览」，得到的「value」值即为工程初始化密钥。如下图所示：`
- URL: `https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css`
- URL: `http://localhost`

### 57. 前台单点登录之密文传输示例

- **doc-view ID**: 4617
- **路径**: 部署集成 > 单点登录 > 前台单点登录 > 前台单点登录之密文传输示例
- **核心概念**: 用户在使用自定义登录页时，需要将输入的明文密码发送到数据决策系统中进行登录验证。在传输过程中，明文密码的安全性较低，用户希望能够对密码进行加密，以密文形式传输来保障信息的安全性。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 用户在使用自定义登录页时，需要将输入的明文密码发送到数据决策系统中进行登录验证。
- 人员岗位: 1）管理员登录数据决策系统，点击「管理系统>用户管理>所有用户」，点击「同步用户」。
- 功能应用场景: 5）同步用户信息至数据决策系统，用于登录验证。

**关键代码/公式/API：**
- 代码片段: `var hexcase = 1; ⏎ var b64pad = ""; ⏎ var chrsz = 8; ⏎ var mode = 16; //模式选择 (16为16位的加密 32 为32位的加密) ⏎ function preprocess(form) ⏎ { ⏎ var str = ""; ⏎ str += form.verifycode.value; ⏎ str = str.toUpperC`
- 代码片段: `<script type="text/javascript" src="./md5.js"></script>  //引入 md5.js ⏎ var password = md5(document.getElementById("password").value.trim()); // 使用 md5 加密方法对用户输入密码进行加密`
- 代码片段: `<!DOCTYPE html> ⏎ <html> ⏎ <head> ⏎     <meta charset="utf-8"> ⏎     <meta http-equiv="X-UA-Compatible" content="IE=edge"> ⏎     <title>自定义登录页加密Demo</title> ⏎  ⏎     <!-- 自定义样式，根据实际需求使用 --> ⏎     <lin`
- 公式: `preprocess(form)`
- 公式: `toUpperCase()`
- 公式: `binl(s)`
- 公式: `hex(tmp)`
- JS API: `window.alert`
- JS API: `window.location`
- SQL: `select * from 同步用户`
- URL: `https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css`
- URL: `https://cdn.bootcss.com/html5shiv/3.7.3/html5shiv.min.js`
- URL: `https://cdn.bootcss.com/respond.js/1.4.2/respond.min.js`
- URL: `https://cdn.bootcss.com/jquery/1.9.1/jquery.min.js`

---

## 单点登录 > CAS 单点登录（10篇）

### 80. 配置 FineReport 作为 CAS 客户端

- **doc-view ID**: 974
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > 配置 FineReport 作为 CAS 客户端
- **核心概念**: 本文介绍如何配置 FineReport 作为 CAS 客户端。在配置 FineReport 之前，需要按如下步骤配置好环境： 1）CAS 服务器搭建，若用户已有 CAS 环境，可忽略该操作。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 本文介绍如何配置 FineReport 作为 CAS 客户端。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 本文介绍如何配置 FineReport 作为 CAS 客户端。

**关键代码/公式/API：**
- 代码片段: `<?xml version="1.0" encoding="UTF-8"?> ⏎ <web-app  ⏎    xmlns="http://java.sun.com/xml/ns/j2ee"  ⏎    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ⏎    xsi:schemaLocation="http://java.sun.com`
- 代码片段: `package com.fr; ⏎ import com.fr.data.NetworkHelper; ⏎ import com.fr.decision.mobile.terminal.TerminalHandler; ⏎ import com.fr.decision.webservice.utils.DecisionServiceConstants; ⏎ import com.fr.decisi`
- 公式: `FrFilter()`
- 公式: `init(FilterConfig filterConfig)`
- 公式: `getLogger()`
- 公式: `info("fr cas login")`
- JS API: `getLogger().info`
- JS API: `getSession().getAttribute`
- JS API: `getPrincipal().getName`
- JS API: `getLogger().error`
- URL: `http://java.sun.com/xml/ns/j2ee`
- URL: `http://www.w3.org/2001/XMLSchema-instance`
- URL: `http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd`
- URL: `https://roxy`

### 81. 配置 SSL 证书实现 HTTPS 访问

- **doc-view ID**: 1430
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > 配置 SSL 证书实现 HTTPS 访问
- **核心概念**: **本文方案由番薯提供，提供给具备自主开发能力的用户使用。** **若您的场景方案与文档不完全一致，技术支持不负责文档的维护和使用问题解答。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: **本文方案由番薯提供，提供给具备自主开发能力的用户使用。
- 人员岗位: 1）以管理员身份进入Tomcat安装目录，创建cert文件夹。
- 功能应用场景: **本文方案由番薯提供，提供给具备自主开发能力的用户使用。

**关键代码/公式/API：**
- URL: `https://your_domain`

### 82. CAS服务器搭建

- **doc-view ID**: 1431
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > 选择性操作 > CAS服务器搭建
- **核心概念**: 进行 CAS 单点登录需要 CAS 服务器环境，本文介绍如何搭建 CAS 服务器。注：该文档用于模拟用户 CAS 环境，若用户已有 CAS 环境，可忽略该文档中的步骤。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 进行 CAS 单点登录需要 CAS 服务器环境，本文介绍如何搭建 CAS 服务器。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 注：该文档用于模拟用户 CAS 环境，若用户已有 CAS 环境，可忽略该文档中的步骤。

**关键代码/公式/API：**
- URL: `https://localhost`
- URL: `https://roxy`

### 83. 实现基于数据库的身份验证

- **doc-view ID**: 1432
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > 选择性操作 > 实现基于数据库的身份验证
- **核心概念**: 进行基于数据库的身份验证，允许不同用户都能够实现登录。本文以 MySQL 数据库为例进行操作。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 进行基于数据库的身份验证，允许不同用户都能够实现登录。
- 人员岗位: 1）以管理员身份启动文本编辑工具，打开%TOMCAT_HOME%\webapps\cas\WEB-INF\deployerConfigContext.xml，找到下面的代码：
- 功能应用场景: 进行基于数据库的身份验证，允许不同用户都能够实现登录。

**关键代码/公式/API：**
- 代码片段: `<bean id="authenticationManager" ⏎     class="org.jasig.cas.authentication.AuthenticationManagerImpl">`
- 代码片段: `<bean id="dataSource" class="org.springframework.jdbc.datasource.DriverManagerDataSource"> ⏎     <property name="driverClassName"><value>驱动器</value></property> ⏎     <property name="url"><value>url</v`
- 代码片段: `<bean class="org.jasig.cas.authentication.handler.support.SimpleTestUsernamePasswordAuthenticationHandler" />`
- 公式: `jar(Feb. 2018版本)`
- SQL: `select userpass from userinfo where username=?" />`
- URL: `https://roxy`
- 驱动类: `com.mysql.jdbc.Driver`
- JDBC URL: `jdbc:mysql://ip:port/databaseName，同时数据库用户名和密码替换为实际使用的用户名和密码。`

### 84. CAS 报错解决方案

- **doc-view ID**: 1433
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > CAS 单点登录 FAQ > CAS 报错解决方案
- **核心概念**: javax.net.ssl.SSLHandshakeException: java.security.cert.CertificateException: No name matching xxx.xxx.xx found 检查 web.xml 中的配置 ``` <init-param> <param-name>edu.yale.its.tp.cas.client.filter.loginUrl<

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: javax.net.ssl.SSLHandshakeException: java.security.cert.CertificateException: No name matching xxx.xxx.xx found 检查 web.xml 中的配置 ``` <init-param> <para
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: javax.net.ssl.SSLHandshakeException: java.security.cert.CertificateException: No name matching xxx.xxx.xx found 检查 web.xml 中的配置 ``` <init-param> <para

**关键代码/公式/API：**
- 代码片段: `<init-param> ⏎ <param-name>edu.yale.its.tp.cas.client.filter.loginUrl</param-name> ⏎ <param-value>https://susie:8443/cas/login</param-value> ⏎ <!--这里的server是服务端的IP--> ⏎ </init-param> ⏎ <init-param> ⏎ `
- URL: `https://susie`

### 85. CAS 登出方案

- **doc-view ID**: 2416
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > CAS 登出方案
- **核心概念**: 通过 配置 FineReport 作为 CAS 客户端 ，可以实现通过 CAS 认证登录 FineReport 。但是存在一个问题，如果直接退出 FineReport 决策系统，会进入到 FineReport 的登录界面，并不是 CAS 登录系统，说明没有完全退出 CAS 系统。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 通过 配置 FineReport 作为 CAS 客户端 ，可以实现通过 CAS 认证登录 FineReport 。
- 人员岗位: 用管理员账号登录决策系统后，打开「系统管理>外观配置>登录页」，设置登录页面为 logout.jsp ，如下图所示：
- 功能应用场景: 配置 FineReport 的退出页面及 CAS 系统退出页面，并进行关联，即可实现 FineReport 退出后退出 CAS 系统。

**关键代码/公式/API：**
- 代码片段: `<bean id="logoutController" class="org.jasig.cas.web.LogoutController" ⏎         p:centralAuthenticationService-ref="centralAuthenticationService" ⏎         p:logoutView="casLogoutView" ⏎         p:wa`
- 代码片段: `<!-- 填写退出的URL -->    ⏎ <context-param>     ⏎   <param-name>casServerLogoutUrl</param-name>     ⏎   <param-value>https://josie:8443/cas/logout</param-value>     ⏎ </context-param>     ⏎ <!--单点退出配置 --> `
- 代码片段: `<%@ page language="java" contentType="text/html; charset=UTF-8" ⏎     pageEncoding="UTF-8"%> ⏎ <%@ page import="java.io.*,java.util.*" %> ⏎ <% ⏎ session.removeAttribute("edu.yale.its.tp.cas.client.fil`
- 公式: `removeAttribute("edu.yale.its.tp.cas.client.filter.user")`
- 公式: `removeAttribute("_const_cas_assertion_")`
- 公式: `invalidate()`
- URL: `https://josie`

### 86. 集群下 CAS 方案

- **doc-view ID**: 2867
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > 集群下 CAS 方案
- **核心概念**: CAS 单点登录方案配置完成，配合Nginx的时候，访问nginx/webroot/decision，URL 会变化成集群节点的地址。仅配置一个 CAS 服务端，每个集群节点作为 CAS 的一个客户端，FineReport 工程未配置 HTTPS 。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 注：本文提供方案只适用于 yale 策略，不适用于 jasig 。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 注：本文提供方案只适用于 yale 策略，不适用于 jasig 。

**关键代码/公式/API：**
- 代码片段: `<?xml version="1.0" encoding="UTF-8"?> ⏎ <web-app  ⏎    xmlns="http://java.sun.com/xml/ns/j2ee"  ⏎    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ⏎    xsi:schemaLocation="http://java.sun.com`
- 代码片段: `<%@ page language="java" import="java.util.*" pageEncoding="gb2312"%> ⏎ <%@ page import="java.net.URLEncoder" %> ⏎ <%@ page import="edu.yale.its.tp.cas.client.filter.CASFilter" %> ⏎ <%@ page import="c`
- 公式: `deleteTicket(request, response)`
- 公式: `deleteToken(request)`
- 公式: `encode("http://192.168.1.127/webroot/decision")`
- 公式: `sendRedirect(application.getInitParameter("casServerLogoutUrl")`
- URL: `http://java.sun.com/xml/ns/j2ee`
- URL: `http://www.w3.org/2001/XMLSchema-instance`
- URL: `http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd`
- URL: `https://yina`

### 87. CAS单点登录插件

- **doc-view ID**: 3232
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > CAS单点登录插件
- **核心概念**: 用户可下载 cas 单点登录插件，无需代码，简单快速地实现通过 cas 认证登录数据决策系统的效果。注：远程设计时不走 CAS 认证，默认放行。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 用户可下载 cas 单点登录插件，无需代码，简单快速地实现通过 cas 认证登录数据决策系统的效果。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 用户可下载 cas 单点登录插件，无需代码，简单快速地实现通过 cas 认证登录数据决策系统的效果。

**关键代码/公式/API：**
- URL: `http://ip`
- URL: `http://cas服务器IP地址/cas`
- URL: `http://IP`
- URL: `https://cas服务器域名/cas`

### 88. 10.0集成CAS后的远程设计

- **doc-view ID**: 3288
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > CAS 单点登录 FAQ > 10.0集成CAS后的远程设计
- **核心概念**: 10.0 集成 CAS 之后，远程设计的请求会被 CAS 拦截，导致无法进行远程设计。点击下载新增拦截和 xml 文件：CAS远程设计.zip 1）需要另外定义一个 RemoteFilter，在请求的一开始就过滤 /remote/design的请求（这个是远程设计走的请求路径）。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 10.0 集成 CAS 之后，远程设计的请求会被 CAS 拦截，导致无法进行远程设计。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 10.0 集成 CAS 之后，远程设计的请求会被 CAS 拦截，导致无法进行远程设计。

**关键代码/公式/API：**
- 代码片段: `package com.fr;  ⏎ import javax.servlet.*; ⏎ import javax.servlet.http.HttpServletRequest; ⏎ import javax.servlet.http.HttpServletResponse; ⏎ import java.io.IOException;  ⏎ public class RemoteFilter i`
- 代码片段: `<filter>      ⏎      <filter-name>RemoteFilter</filter-name>            ⏎      <filter-class>com.fr.RemoteFilter</filter-class>        ⏎   </filter>        ⏎  <filter-mapping>            ⏎            `
- 公式: `destroy()`
- 公式: `init(FilterConfig filterConfig)`
- 公式: `getRequestDispatcher(req.getServletPath()`
- 公式: `getPathInfo()`

### 89. CAS单点登录

- **doc-view ID**: 3504
- **路径**: 部署集成 > 单点登录 > CAS 单点登录 > CAS单点登录
- **核心概念**: 用户需要实现通过 CAS（统一身份认证服务）认证登录数据决策系统，本文提供配置 CAS 单点登录及登出方法索引。CAS 架构包括：CAS 服务器和 CAS 客户端。

**业务场景四要素：**
- 统计指标方案: 不涉及（本文为部署/集成/运维操作说明，无具体统计指标）
- 业务场景: 注：文档提供的该方案，不适用于移动端；若想实现移动端 CAS 单点登录，请参考本文第二章内容。
- 人员岗位: 未在文中明确指定（面向系统管理员/运维人员/实施人员）
- 功能应用场景: 注：文档提供的该方案，不适用于移动端；若想实现移动端 CAS 单点登录，请参考本文第二章内容。

---
