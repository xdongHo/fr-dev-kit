<!--
KB_INDEX: {
  "title": "FR11 · 二次开发与JS API · Web 集成 / 单点登录 / 安全",
  "stage": "fr11-knowledge",
  "tags": [
    "FR11",
    "JS API",
    "二次开发"
  ],
  "keywords": [
    "iframe",
    "单点登录",
    "跨域",
    "session",
    "Security Headers"
  ],
  "summary": "iframe 集成、跨域与乱码、单点登录、cookie/session、防盗链条目（49 条 doc-view 条目，ID 602~5086）；js_api_summary.md 拆分页 6/10，条目原样保留。"
}
-->

# FR11 知识库 · 二次开发与JS API · Web 集成 / 单点登录 / 安全

> 数据源：`D:\fr11_docs\doc-view-{did}.html`（FR11 离线文档，gb2312）。
> 本页为 [js_api_summary.md](js_api_summary.md) 2026-09-29 主题拆分页 **6/10**；条目内容原样搬移、未做改写；归类方法：按条目标题关键词启发式（延续建库打分思路），页内保持原 doc-view ID 升序。
> 本页收录 **49 条**（ID 602~5086，非连续）。

## 文档条目

### doc-view-602｜FR.ajax
- **doc-view ID**：602
- **核心概念**：补充 FVS 大屏模板相关接口说明 适用于安装了「FVS大屏编辑模式」插件 **V1.8.0 **及之后版本的用户 ajax 是一种与服务器交换数据的技术，可以在不重新载入整个页面的情况下更新网页的一部分。FR.ajax 是封装过的 jQuery.ajax() 函数，在报表中对特定网页进行 ajax 请求， data 参数做了中日韩文编码处理。
- **关键API/代码**：JS: FR.jsonDecode(res.responseText)；公式: ajax()；公式: ajax({
 url: "/webapps/webroot/a.html",
 success: function(data, textStatus)；公式: alert(this.url)；公式: ajax({
 url: "some.jsp",
 error: function(XMLHttpRequest, textStatus, errorThrown)；公式: ajax({
 url: "some.jsp",
 complete: function(XMLHttpRequest, textStatus)
- **FR11版本要点**：报表服务器版本功能变动 11.0.7
### doc-view-855｜不同端口号下跨域调用 JS
- **doc-view ID**：855
- **核心概念**：域（Domain）是 Windows 网络中独立运行的单位，域之间相互访问则需要建立信任关系（即 Trust Relation）。信任关系是连接在域与域之间的桥梁。当一个域与其他域建立了信任关系后，2 个域之间不但可以按需要相互进行管理，还可以跨网分配文件和打印机等设备资源，使不同的域之间实现网络资源的共享与管理。 简而言之，跨域访问，就是 A 网站的 JavaScript 代码试图访问 B 网站，包括提交内容和获取内容
- **关键API/代码**：公式: getElementById("main")；公式: getQueryStringRegExp("tarValue")；公式: getQueryStringRegExp(name)；公式: RegExp("(^|\\?|&)；公式: test(location.href)；公式: unescape(RegExp.$2.replace(/\+/g, " ")
### doc-view-882｜自定义登录页面
- **doc-view ID**：882
- **核心概念**：用户登录数据决策系统时，不希望使用默认的登录界面，可通过自定义登录界面的方式修改默认登录界面，如下图所示： 登录界面，获取到用户名和密码的值，发送到报表系统，报表服务带着这两个参数访问认证地址进行认证。 注：实现 App 自定义登录页请参考文档：[APP]登录页
- **关键API/代码**：公式: getElementById("submitBtn")；公式: addEventListener("click", function ()；公式: doSubmit()；公式: getElementById("inputUsername")；公式: trim()；公式: getElementById("inputPassword")
### doc-view-884｜前台单点登录接口
- **doc-view ID**：884
- **核心概念**：本文将介绍产品支持的单点登录接口。 注：我们提供帆软单点相关的官方接口，只解决官方接口调用相关的问题。若用户在实际操作过程中，出现非接口之外的错误，请联系用户公司的技术人员进行排查解决。 需要将用户名及密码等信息放在 url 后面进行登录验证，配合 iframe 或者 ajax 可实现前台的跨域单点登录行为。只需要在用户的登录页面加上该接口的调用，后台无需进行适配。需要用户系统的账号和密码与帆软平台账号密码相同。
### doc-view-905｜HTML通过iframe嵌套多张模板并设置联动
- **doc-view ID**：905
- **核心概念**：在 HTML 页面中嵌套多张模板，并实现主子表的联动。 比如使用一张主报表和 2 张子报表，通过点击超级链接动态改变子报表的值，效果如下图所示： 在 HTML 中可以通过定义 frameset 标签来组织多个窗口，并在 frame 中设置特定的窗口区域，最终通过 JS 判断实现对不同窗口区域设置不同的模板地址。
- **关键API/代码**：SQL: SELECT * FROM STSCORE，如下图所示：；公式: zhu(classno)；公式: getElementById("zi1")；公式: aa(stuno)；公式: getElementById("zi2")
### doc-view-908｜iframe框架自适应报表高度
- **doc-view ID**：908
- **核心概念**：将报表集成至 Web 页面中时，报表往往只是作为页面的某一部分嵌入在一个框架中如 iframe 中显示出来。 由于报表每页数据是不定的，在最后一页可能只有几条数据，此时 iframe 框架将留有大片的空白，造成空间的浪费也使得界面不美观。 这个时候我们就会希望，要是 iframe 框架大小能够根据报表页面的内容自动调整高度或宽度，如下图效果：
- **关键API/代码**：JS: _g().gotoFirstPage()；JS: _g().gotoPreviousPage()；JS: _g().gotoNextPage()；JS: _g().gotoLastPage()；JS: _g()；JS: contentPane.on
### doc-view-918｜Web页面集成简单示例
- **doc-view ID**：918
- **核心概念**：FineReport 通过各种样式如表格、图表等来呈现数据，进行统计分析。这些数据表格或图表，用户在开发系统的时候也可以自己编程来实现，但是工作量大，维护难。 FineReport 是基于 B/S 架构的浏览器/服务器模式，现在用户开发的系统基本上趋向于 B/S 架构的浏览器/服务器模式，因此有些页面完全可以直接采用 Web 页面嵌入式集成的简易方式完成集成
- **关键API/代码**：JS: FR.doHyperlinkByPost(url, {地区:"华东"},"reportFrame")；公式: autoSubmit()；公式: doHyperlinkByPost(url, {地区:"华东"},"reportFrame")；公式: url('登录页.png')
### doc-view-930｜IE8或9下Web集成页面显示异常
- **doc-view ID**：930
- **核心概念**：本文汇总了一些 Web 集成后在 IE8 或 IE9 浏览器下出现的问题及解决方案。 将一张含有图表的报表通过 iframe 的方式嵌入到 HTML 中，图表在 IE9 的 quirks 模式下显示不出来，其他浏览器比如说：FireFox，Google 等浏览器下显示正常，如下图： IE9 的杂项（quirks）模式下：
### doc-view-935｜iframe嵌入报表滚动条问题
- **doc-view ID**：935
- **核心概念**：用户有时会使用 Web 页面集成 ，在一个网页中嵌入一个 iframe，iframe 中嵌入一张报表。 当报表大小超过 iframe 大小时，iframe 中就会出现滚动条； 当 iframe 超过浏览器大小时，浏览器便会出现滚动条，如下图所示：
### doc-view-936｜集成后参数值显示乱码
- **doc-view ID**：936
- **核心概念**：报表已集成到 Web 页面中，通过在页面传递参数至报表中时，会发现有时某些参数值，传递到报表中是显示为问号（？？？）或乱码等等一系列不能正常显示的情况。 这是由于浏览器和报表服务器的编码不同，字符多次进行编码转换时出现错误导致字符的显示出现乱码，尤其是中日韩文和特殊字符更容易出现乱码问题。 详细的编码原理可参考文档： 编码
- **关键API/代码**：公式: encodeURI("http://localhost:8075/webroot/decision/view/report?viewlet=中文.cpt")；公式: encodeURIComponent("中文.cpt")；公式: frOpen()；公式: autoSubmit()；公式: getElementById('Region')；公式: encodeURIComponent(Region.value)
### doc-view-1136｜URL传递特殊符号
- **doc-view ID**：1136
- **核心概念**：有些符号在 URL 中是不能直接传递的，如'+','%','&'等符号，那么如果要在 URL 中传递这些符号要如何实现呢？ 通过将这些特殊符号转换成 16 进制。 2）常用特殊符号及其编码
- **关键API/代码**：公式: encodeURIComponent()；公式: encodeURIComponent(encodeURIComponent("this%is#te=st&o k?+/")
### doc-view-1153｜cookie与session之间的关系
- **doc-view ID**：1153
- **核心概念**：Cookie 是存储于访问者计算机的变量，每当同一台计算机通过浏览器请求某个页面时，就会发送这个 Cookie。您可以使用 JavaScript 来创建和取回 Cookie 的值。 比如，当我们访问 sina 等邮箱时，会有一个选项提醒我们是否要保存账号和密码，如果选是，我们的账号和密码就被保存在了 Cookie 中。 我们可以通过 document 对象的 Cookie 属性对当前文档的 Cookie 进行读取，创建，修改和删除操作。
- **关键API/代码**：公式: write(document.cookie)；公式: setCookie(c_name,value,expiredays)；公式: Date()；公式: setDate(exdate.getDate()；公式: escape(value)；公式: toGMTString()
### doc-view-1160｜报表里获取session中的值
- **doc-view ID**：1160
- **核心概念**：Session 保存了 key-value 属性对，希望在报表中拿到 Session 中的 key 的值。本文总结了主要的应用场景以及实现思路。 报表应用集成到用户系统中，共用同一个 Session，此时可以直接在报表中获取 Session 的值。 如 Session 中保存了 key a，其值为 123，那么在我们报表中使用 =$a 就能直接获取到 Session 中 a 的值。
- **关键API/代码**：公式: getAttribute(String key)；公式: setAttribute(String key,Object value)；公式: getAttribute("fine_username")；公式: getAttribute("id")；公式: setAttribute("id","Imsession")；公式: alert("session是"+id)
### doc-view-1178｜Web页面事件
- **doc-view ID**：1178
- **核心概念**：Web 页面事件，即添加在报表页面上的事件，在「模板>模板 Web 属性」设置，其中在「分页预览设置」、「填报预览设置」与「数据分析设置」设置后分别作用于对应的预览方式。 如下图所示，在「分页预览设置」处给页面添加了一个「加载结束」事件，事件内容为隐藏报表工具栏。 点击「分页预览」预览报表时，报表工具栏就会被隐藏。如下图所示：
### doc-view-1241｜跨域调用 JS
- **doc-view ID**：1241
- **核心概念**：用户想要实现在自己的 OA 系统里点击按钮，就能触发我们的报表的提交事件
- **关键API/代码**：JS: _g().writeReport()做演示，其他 JS 也都支持。；JS: _g().writeReport()") 则可以实现跨域提交。；JS: _g().writeReport()')"/>；公式: postMessage()；公式: writeReport()；公式: send(val)
### doc-view-1429｜Java防盗链在报表上面的应用
- **doc-view ID**：1429
- **核心概念**：使用防盗链，来预防报表工程里的报表被直接访问或者被其他网站链接访问。 注1：FineReport 11.0.12 版本新增 Referer 校验功能，可参考 Referer校验 进行配置，操作简单，无需处理复杂代码。 注2：需先将 webroot 目录部署在外置 Tomcat 下才可生效（内置的设计器的 Tomcat 现在不读 web.xml 了）。
- **关键API/代码**：Java: com.fr.test；Java: com.fr.test.Dodo；JS: FR.doHyperlinkByGet()；公式: destroy()；公式: doFilter(ServletRequest request, ServletResponse response, FilterChain chain)；公式: getHeader("referer")
- **FR11版本要点**：注1：FineReport 11.0.12 版本新增 Referer 校验功能，可参考 Referer校验 进行配置，操作简单，无需处理复杂代码。
### doc-view-1839｜JS实现动态改变超链URL中的参数值
- **doc-view ID**：1839
- **核心概念**：超级链接的 URL 格式固定，但有时候 URL 后缀参数值不同，打开的网页也不同。 如何通过点击单元格替换对应的 URL 值打开不同的页面呢，效果如下图所示： 通过 JavaScript 脚本实现。
- **关键API/代码**：公式: open('http://bbs.fanruan.com/home.php?mod=space&uid='+p_name+'&do=profile','_blank')
### doc-view-1886｜JS判断操作系统语言(浏览器)
- **doc-view ID**：1886
- **核心概念**：FineReport 作为一款多语种，跨平台的报表设计器，经常会有客户需要使用多个语言环境来配置报表。 那么，如何通过判定操作系统语言环境来自动跳转到对应语种的页面呢？这是多语种并存的企业单位需要解决的问题。 通过 JS 代码，判断浏览器类型。
- **关键API/代码**：公式: substr(0, 2)
### doc-view-1923｜借用浏览器功能写JS语句
- **doc-view ID**：1923
- **核心概念**：报表中很多个性化功能的实现，大多是使用 JavaScript 来实现的，那么我们如何能零基础写 JavaScript 来实现功能呢？ 我们可以通过浏览器中的「审查元素」，获取到报表中每个元素对应的代码，从而能据此快速编辑出需要的 JavaScript 语句添加在模板中，实现想要的功能
- **关键API/代码**：JS: FR.tc(function()；公式: tc(function()；公式: doHyperlink(event||window.event, [{"data":"var as=arguments; return FR.tc(function()；公式: doHyperlink(window.event, [{"data":"var as=arguments; return FR.tc(function()
### doc-view-2175｜通过JS获取当前页面URL网址信息
- **doc-view ID**：2175
- **核心概念**：在平时的报表开发中，我们通常会遇到要获取当前打开报表页面的URL网址相关信息，虽然目前 FineReport 内置的 系统参数 能满足一定的需求，但有一些需求系统参数中没有提供，如要获取 URL 对应的"标签名称"。如下图所示： 可以通过 JavaScript 脚本来获取 URL 网址相关信息
- **关键API/代码**：公式: alert('URL地址:  '+test1)；公式: protocol(设置或获取URL的协议部分)；公式: alert('URL协议:  '+test2)；公式: host(设置或获取URL的主机部分)；公式: alert('URL主机:  '+test3)；公式: port(设置或获取与URL端口号)
### doc-view-2211｜登录
- **doc-view ID**：2211
- **核心概念**：管理员登录数据决策系统，点击「管理系统>系统管理」，可对登录项进行设置。如下图所示： 以管理员身份进入数据决策系统，跳转到登录页，输入正确用户名和密码，点击「登录」进入数据决策系统。如下图所示： 注：数据决策系统初始化配置请参考 决策系统初始化配置
### doc-view-2454｜安全防护
- **doc-view ID**：2454
- **核心概念**：出于安全性的考量，平台在「安全防护」界面内提供了一些安全功能开关，包括：Cookie 增强、HSTS 设置、文件上传校验、脚本调用公式限制、Security Headers、请求响应优化、Token认证增强。 本文对以上安全功能进行了说明，用户可根据需求在「安全防护」界面内一键开启防护措施。如下图所示： 「Cookie 增强」按钮默认关闭。点击开启时对当前协议进行检测：
- **关键API/代码**：公式: addHeader("X-Content-Type-Options", "nosniff")；公式: addHeader("X-XSS-Protection", "1; mode=block")；公式: addHeader("X-Frame-Options", "SAMEORIGIN")；公式: addHeader("Content-Security-Policy", "object-src 'self'")；公式: addHeader("Cache-Control", "no-cache")；公式: addHeader("Pragma", "no-cache")
- **FR11版本要点**：报表服务器版本功能变动 11.0- 11.0.12新增 Referer 校验功能，开启后，将根据白名单内容实现访客控制
### doc-view-2462｜第三方集成推送支持的消息类型
- **doc-view ID**：2462
- **核心概念**：Finereport 版本WeLink 管理插件版本功能变动 11.0.9 V11.0.74定时调度支持推送「图片消息」，无需再通过链接跳转查看 微信、钉钉、飞书、WeLink 定时推送消息时，除了支持推送链接消息，还支持推送图文消息、文件消息和图片消息。
- **关键API/代码**：公式: now()
- **FR11版本要点**：Finereport 版本WeLink 管理插件版本功能变动 11.0.9 V11.0.74定时调度支持推送「图片消息」，无需再通过链接跳转查看；11.0.9 V11.0.74定时调度支持推送「图片消息」，无需再通过链接跳转查看 11.0.2V11.0.54-；### 2.4 图片消息 V11.0.74 版本及之后的微信、钉钉、飞书、WeLink 插件推送的消息类型支持「图片类型」，以快照的形式发送，可直接查看图片，无需再通过链接跳转查看。
### doc-view-2650｜URL 登录插件
- **doc-view ID**：2650
- **核心概念**：URL登录插件 用于直接使用get请求拼接用户名，密码，保持登录，跳转 URL 四个参数，进行登录并跳转。 注：如果开启了短信验证等，则会抛出对应的错误码，此时无法通过此插件登录。 GET  /url/login
### doc-view-2671｜上次登录信息提示
- **doc-view ID**：2671
- **核心概念**：为安全起见，在数据决策系统的「登录」Tab 页下，开启「上次登录信息提示」，开启后每次登录时会提示上一次登录的时间、IP 地址、地点，这样会及时发现登录异常等信息。 管理员登录数据决策系统，点击「管理系统>系统管理>登录」，开启「上次登录信息提示」按钮，如下图所示： 用户登录数据决策系统时，将提示上次登录信息，如下图所示：
- **关键API/代码**：公式: addLoginInfo(function ()；公式: getIpInfo(cb)；公式: done(function (data)；公式: cb(data)；公式: addLoginInfo(cb)；公式: getIpInfo(function (ipInfo)
### doc-view-2700｜iframe跨域调用报表报错
- **doc-view ID**：2700
- **核心概念**：在第三方系统页面集成fr报表时，通常使用的是 iframe 嵌入报表的集成方式： 当第三方系统和 FineReport 工程不在一个域内时，在页面跨域集成报表时，会报错「XXX拒绝了我们的连接请求」，如下图所示： 安全防护 功能中包含了 Security Headers，如需要 iframe 跨域嵌入报表，可使用管理员账号登录决策平台，点击「管理系统->安全管理->安全防护」，选择「Security Headers>高级设置」 ，将「点
### doc-view-2713｜还原登录页设置
- **doc-view ID**：2713
- **核心概念**：用户修改数据决策系统登录页的登录方式为「设置登录网页」后，由于自定义HTML存在错误，导致用户无法打开登录页进行登录。 管理员通过单点接口登录决策系统之后，在平台内将自定义登录页面还原成系统默认的登录页面。 浏览器界面点击 F12 调用控制台，在 console 选项中输入：
### doc-view-2731｜登录登出action监听接口
- **doc-view ID**：2731
- **核心概念**：数据决策平台默认登出时会自动跳转到登录界面，而有的用户可能需要登出时跳转到自定义的登出界面而非登录页。 在决策平台中提供登录登出后事件的接口，用于登录登出后自定义操作。 LoginPageProvider
- **关键API/代码**：Java: com.fr.decision.fun；Java: com.fr.stable.fun.mark.WebCoalition；Java: com.fr.plugin.decision.login.MyLoginPageProvider；Java: com.fr.plugin.demo.loginout.event；Java: com.fr.decision.fun.impl.AbstractLogInOutEventProvider；Java: com.fr.decision.webservice.login.LogInOutResultInfo
### doc-view-3288｜11.0集成CAS后的远程设计
- **doc-view ID**：3288
- **核心概念**：11.0 集成 CAS 之后，远程设计的请求会被 CAS 拦截，导致无法进行远程设计。 点击下载新增拦截和 xml 文件：CAS远程设计.zip 1）需要另外定义一个 RemoteFilter，在请求的一开始就过滤 /remote/design的请求（这个是远程设计走的请求路径）。定义 RemoteFilter 源码如下：
- **关键API/代码**：Java: com.fr.RemoteFilter；公式: destroy()；公式: init(FilterConfig filterConfig)；公式: getRequestDispatcher(req.getServletPath()；公式: getPathInfo()；公式: forward(req, res)
### doc-view-3367｜自定义登录界面
- **doc-view ID**：3367
- **核心概念**：使用该插件可以自定义决策平台登录界面，使其更能彰显个性。效果如下图所示： 支持5种常用的控件：登录窗口，图片控件，文字控件，幻灯图控件，iframe 控件。 每个控件都可以设置对应的属性，其中幻灯图需要根据模板提供的 JSON 进行编写。
### doc-view-3554｜登录页添加粒子联结特效
- **doc-view ID**：3554
- **核心概念**：登录页出现粒子特效，粒子间通过线条动态联结，移动鼠标会聚集粒子，鼠标点击页面会按顺序显示社会主义核心价值观，效果如下图所示： 安装 决策平台注入代码插件 ，修改登录页代码进而实现粒子联结特效。 点击下载插件：决策平台注入代码插件
- **关键API/代码**：公式: translateY(-50px)；公式: addEventListener('click', function (event)；公式: createElement('span')；公式: appendChild(eleText)；公式: addEventListener('animationend', function ()；公式: removeChild(eleText)
### doc-view-3975｜华为云OneAccess集成
- **doc-view ID**：3975
- **核心概念**：帆软系统与华为云OneAccess的单点登录和用户同步集成。 插件功能，实现帆软系统与华为云OneAccess的单点登录和用户信息同步。 基于OAuth2.0的单点认证集成。
### doc-view-4066｜Web页面集成FAQ
- **doc-view ID**：4066
- **核心概念**：可参见文档：Web 页面集成简单示例 可自定义一个批量导出按钮，详情请参见：自定义批量导出按钮 可参见文档：自定义导出按钮
### doc-view-4259｜数知鸟集成数据决策系统
- **doc-view ID**：4259
- **核心概念**：2）集成配置界面交互优化 3）新增小助手权限分配 注：在工程可连接帆软市场、自动获取插件的情况下，数知鸟插件会自动更新到最新适配版本。
### doc-view-4322｜后台单点登录插件
- **doc-view ID**：4322
- **核心概念**：新增 ssoToken 超时设置功能，开启后，ssoToken 将在达到「系统管理>登录>登录超时时间」后过期 通过选择「用户名加密」按钮和「示例接口」按钮，切换用户名加密和不加密这两种方式 URL 重定向，隐去访问链接中的用户名 fine_username 或者加密后的 ssoToken
- **FR11版本要点**：- 通过选择「用户名加密」按钮和「示例接口」按钮，切换用户名加密和不加密这两种方式 11.0.4V1.1.1；FineReport 11.0.4 以及后台单点登录插件 V1.1.1 之前版本的新计算引擎请求无法适配 ssoToken 。
### doc-view-4351｜WeLink集成
- **doc-view ID**：4351
- **核心概念**：Finereport 版本 WeLink 管理插件版本H5移动端展现插件 V11.0.62V11.0.62「成员管理」支持同步多个企业的数据
- **FR11版本要点**：WeLink 管理插件版本H5移动端展现插件 功能变动 11.0.2V11.0.54V11.0.54-；功能变动 11.0.2V11.0.54V11.0.54-；11.0.2V11.0.54V11.0.54-
### doc-view-4354｜飞书集成
- **doc-view ID**：4354
- **核心概念**：V11.0.62「成员管理」支持同步多个企业的数据 V11.0.72「成员管理」支持同步根部门下的用户，需要开放“获取企业信息”权限 管理员安装插件并配置，可实现飞书集成，并进行消息推送。
- **FR11版本要点**：飞书管理插件版本 功能变动 11.0.2；功能变动 11.0.2 V11.0.54；V11.0.54 - V11.0.62「成员管理」支持同步多个企业的数据
### doc-view-4361｜CAS单点登录插件
- **doc-view ID**：4361
- **核心概念**：cas 版本功能变动 支持自定义用户名 支持自定义放行请求
- **FR11版本要点**：11.0V1.0.03.5.2 - 11.0.4V1.1.13.5.2
### doc-view-4441｜后台单点登录RSA示例代码
- **doc-view ID**：4441
- **核心概念**：使用 后台单点登录插件 加密用户名登录的话，访问链接为：http://ip:port/工程名/decision?ssoToken=xxx，本文告诉用户如何生成 ssoToken ，并给出 Java 示例代码。 需安装后台单点登录插件，该插件具体介绍请参见：后台单点登录插件 超管进入平台，点击「管理系统>系统管理>集成后台单点登录>用户名加密>生成RSA Key>保存」。如下图所示：
- **关键API/代码**：SQL: update = cipher.doFinal(fragment)；公式: main(String[] args)；公式: getProperty("text")；公式: getProperty("publicKey")；公式: encrypt(username, publicKey)；公式: println("encrypted username: " + encrypt)
### doc-view-4640｜登录集成插件
- **doc-view ID**：4640
- **核心概念**：通过JWT加密用户信息生成第三方TOKEN，用于实现 2、配置用户创建策略，认证完成后实现在帆软平台中创建用户信息 3、用于换取帆软fine_auth_token（用于帆软平台接口的调用）
- **关键API/代码**：公式: Date(new Date()；公式: getTime()；公式: builder()；公式: setExpiration(expireTime)；公式: signWith(io.jsonwebtoken.SignatureAlgorithm.HS256,
 Base64.getEncoder()；公式: encodeToString(key.getBytes("UTF-8")
### doc-view-4822｜预设浏览器插件
- **doc-view ID**：4822
- **核心概念**：帆软报表设计器预览报表时，使用的浏览器是系统默认浏览器。在日常报表设计预览效果时，需要测试各个不同浏览器下的效果。通过预设浏览器插件，可在设计器预览报表时，直接选择指定的浏览器来预览，减少来回切换浏览器的麻烦。 点击下载插件：预设浏览器 设计器插件安装方法请参见：设计器插件管理
### doc-view-4903｜移动端集成问题排查手册
- **doc-view ID**：4903
- **核心概念**：针对微信、钉钉、飞书、WeLink集成遇到的问题，提供排查手册帮助用户快速定位和解决这些问题。用户也可参考以下文档查找解决方案。 移动端功能常见问题：移动端功能常见问题及解决方案 钉钉集成常见问题：钉钉集成常见问题及解决方案
- **关键API/代码**：公式: http(s)；公式: now()
- **FR11版本要点**：1）是否为多企业用户，若用户添加两个企业，则更新插件至11.0.62，对应版本处理过多企业同名用户匹配的问题。
### doc-view-4947｜类Oauth2单点登录插件
- **doc-view ID**：4947
- **核心概念**：10.0&11.0v1.0.0 支持在 Oauth2 认证标准下，进行单点配置，集成FineReport/FineBI平台 支持配置自定义的单点逻辑（参数加解密、数据请求等）
- **关键API/代码**：公式: URLEncode(requestURL)；公式: Base64Decode(accessToken)；公式: JwtEncode(accessToken, "FineReport2018", 60000)；公式: JwtDecode(accessToken, "FineReport2018")；公式: URLDecode(accessToken)；公式: URLEncode(accessToken)
### doc-view-5019｜微信集成常见问题
- **doc-view ID**：5019
- **核心概念**：本文总结了 FineReport 与微信集成的常见问题及解决方案。 微信钉钉推送/单点/同步失败解决方案可参考：微信钉钉推送/单点/同步失败日志定位 做了企业微信集成，手动匹配，先匹配一遍，保存，再选择不选，点立即更新，这个企业微信用户还是能直接用企业微信端，需要删除用户或者禁用之后，才能立即生效，选择不选，之后立即更新还是没办法立即生效。
- **关键API/代码**：SQL: delete 请求转换插件。；Java: com.fr.plugin.weixin.server.WeiXinTokenMissedException
### doc-view-5051｜JS实现决策报表缓存上一次浏览器查询参数
- **doc-view ID**：5051
- **核心概念**：决策报表在打开时希望参数控件的值可以默认是上一次页面关闭前最后一次查询所选择的值。 每次点击查询后将参数值保存到浏览器缓存中（适用于控件在参数栏内），或每次控件值发生改变后将参数值保存到浏览器缓存中（适用于控件在报表体内）。 报表打开时从浏览器缓存中将参数值读取出来并赋值给对应的控件。
- **关键API/代码**：JS: _g().getParameterContainer().getWidgetByName(key).getValue()；JS: _g().getParameterContainer().getWidgetByName(key).setValue(storageJson[key])；JS: _g().getWidgetByName(key).getValue()；JS: _g().getWidgetByName(key).setValue(storageJson[key])；JS: getWidgetByName(key)；公式: forEach(
  key => {
    localStorageObj[key] = _g()
### doc-view-5074｜FineReport 集成到 FineBI
- **doc-view ID**：5074
- **核心概念**：在实际使用过程中存在需要将 FineReport 工程集成到 FineBI 数据决策系统上使用的情况。 本文将介绍将 FineReport 集成到 FineBI 的步骤。 将 FineReport 集成到 FineBI ，可以将这两个软件合并成一个整体的系统，应用服务只需维护一套。
### doc-view-5082｜Web页面集成接口
- **doc-view ID**：5082
- **核心概念**：FineReport 支持通过 GET 和 POST 两种方式调用接口数据，进行 Web 集成。 本文为你介绍 API 接口相关入门知识，便于后续使用 FineReport 进行 Web 集成。 API接口文档一般分为接口描述、接口地址、请求方法、请求参数、响应内容、错误代码、实例几个部分：
### doc-view-5085｜Web页面集成常见问题
- **doc-view ID**：5085
- **核心概念**：本文主要汇总了 Web 页面集成过程中经常出现的问题以及解决方案。 用户以非管理员身份进入数据决策系统后，访问：http://IP:Port/webroot/decision/接口调用 ，出现如下报错： 需要获得该页面的权限，请参考 分级权限分配
- **关键API/代码**：JS: FR.doURLPDFPring()；公式: postMessage()；公式: doURLPDFPring()
### doc-view-5086｜Web页面集成
- **doc-view ID**：5086
- **核心概念**：FineReport 通过各种样式如表格、图表等来呈现数据，进行统计分析。这些数据表格或图表，用户在开发系统的时候也可以自己编程来实现，但是工作量大，维护难。 因此用户往往选用现成的软件开发，最后将制作好的 FineReport 模板嵌入到自己的系统中，以节省项目开发周期。 用户开发的系统基本上趋于 B/S 架构的浏览器/服务器模式，因此需要将制作好的模板嵌入到系统的某一个页面中，做为页面的一部分。

> 本页收录 doc-view ID（49 条）：602、855、882、884、905、908、918、930、935、936、1136、1153、1160、1178、1241、1429、1839、1886、1923、2175、2211、2454、2462、2650、2671、2700、2713、2731、3288、3367、3554、3975、4066、4259、4322、4351、4354、4361、4441、4640、4822、4903、4947、5019、5051、5074、5082、5085、5086
