<!--
KB_INDEX: {
  "title": "FR11 · 二次开发与JS API · Java 引擎与平台 API",
  "stage": "fr11-knowledge",
  "tags": [
    "FR11",
    "JS API",
    "二次开发"
  ],
  "keywords": [
    "引擎API",
    "Java",
    "AbstractFunction",
    "调度",
    "FTP"
  ],
  "summary": "引擎 API、Java 编译与 classpath、上传 FTP、定时调度平台侧条目（18 条 doc-view 条目，ID 597~5076）；js_api_summary.md 拆分页 8/10，条目原样保留。"
}
-->

# FR11 知识库 · 二次开发与JS API · Java 引擎与平台 API

> 数据源：`D:\fr11_docs\doc-view-{did}.html`（FR11 离线文档，gb2312）。
> 本页为 [js_api_summary.md](js_api_summary.md) 2026-09-29 主题拆分页 **8/10**；条目内容原样搬移、未做改写；归类方法：按条目标题关键词启发式（延续建库打分思路），页内保持原 doc-view ID 升序。
> 本页收录 **18 条**（ID 597~5076，非连续）。

## 文档条目

### doc-view-597｜JavaScript脚本
- **doc-view ID**：597
- **核心概念**：11.0.3新增 JavaScript 高级编辑器，详情可见 2.4 节 JavaScript 脚本是 FineReport 事件响应方式的一种，当事件发生时，执行 JavaScript 代码，通常用于给报表添加一些交互动作和页面特效
- **关键API/代码**：JS: _g().parameterCommit()，即可实现不点击查询按钮，选择值后就查询报表内容。；公式: parameterCommit()
- **FR11版本要点**：报表服务器版本 功能变动 11.0.3新增 JavaScript 高级编辑器，详情可见 2.4 节；添加界面分三部分，引用 JavaScript 脚本、参数、JavaScript 脚本。如下图所示： [图片] 11.0.3 及之后新增 JavaScript 高级编辑器，用户可以直接在编辑器中搜索、查看官方 JS 接口，且会根据接口推荐帮助文档相关示例。如下图所示：；### 2.4 使用 JavaScript 高级编辑器 11.0.3 及之后新增 JavaScript 高级编辑器，用户可以直接在编辑器中搜索、查看官方 JS 接口，且会根据接口推荐帮助文档相关示例。用户使用高级编辑器可方便快捷的编写 JS 代码，且能保证代码规范可兼容。如下图所示：
### doc-view-632｜引擎API
- **doc-view ID**：632
- **核心概念**：FineReport 设计器与服务器已经能够满足大部分的需求，但某些个性化需求可能无法实现，这时就需要通过二次开发的方式来实现这些需求。 FineReport 开放了一些后台接口供应用开发人员进行深入的开发与控制。想要使用这些接口，首先必须了解 FineReport 内核结构。如下图所示： Finereport 报表分两个基本面，模板和结果，没有执行过的工作薄或者报表就是模板，而执行过后就是结果。
- **关键API/代码**：Java: com.fr.report.io
### doc-view-744｜编译Java程序
- **doc-view ID**：744
- **核心概念**：用户通过 Java 类代码进行Finereport 二次开发，实现某些功能时，通常需要编译 Java文件，生成 Class 类，如在程序数据源、程序报表、自定义函数、自定义后台导出、自定义打印的应用中都需要 Class 类。那在进行二次开发时，如何编译 Java文件，需要哪些准备工作呢？本文将详细讲述。 编译程序前，用户首先需要有一个Java工程环境，并且需要一个 Java 编辑器，如 Eclipse 或 Idea
### doc-view-911｜JavaScript超链传参
- **doc-view ID**：911
- **核心概念**：JavaScript 类型的超链是支持传递参数的，参数名可以任意取，这些参数会传递给 JavaScript 代码，代码中直接通过参数名来引用，如下图所示： 新建普通报表，A1 单元格写入文本：超链到百度并传参搜索。 给单元格添加一个 JavaScript 类型的超链，设置参数id，其值为字符串环比，并在下方写 JavaScript 代码，如下图所示：
- **关键API/代码**：公式: open("https://www.baidu.com/s?&wd="+id)
### doc-view-1023｜报错：Java heap space
- **doc-view ID**：1023
- **核心概念**：当从数据库中查询大量的数据，每个模板取出来几百万条数据，或者是频繁的刷新项目、模板时就会占用 Java 虚拟机 JVM 的大量内存，超过内存就会出现报java.lang.OutOfMemoryError:Java heap space 内存溢出的错误，具体报错如下： 由于服务器的 JVM 不够用而抛出的错误，JVM 在启动的时候会自动设置 heap size 的值，初始空间(即-Xms)是物理内存的 1/64，最大空间(-Xmx)是物理
### doc-view-1175｜JavaScript实例
- **doc-view ID**：1175
- **核心概念**：设计模板时，可以通过 JavaScript 对一些功能进行二次开发。如下图所示，填报提交后某些工具栏按钮设置为不可用。 JavaScript 可在控件事件、Web 页面事件、按钮自定义事件、超级链接等多处添加使用。详细介绍可参考 ：前端开发指南 用户编写添加代码时，除  JavaScript 自身的语法和 jQuery 的基础语法外，FineReport 也提供了JS API 接口，可以参考使用。
### doc-view-2523｜Java IO 操作临时目录剩余空间不足解决方法
- **doc-view ID**：2523
- **核心概念**：服务器在运行过程中，偶尔会遇到Java io操作的临时目录满了或无权限操作的情况，此时会报错，下面是常见的解决方案。 通常不同系统的 tmpdir 路径有所不同 Windows 下：C:\Users\[用户名]\AppData\Local\Temp
### doc-view-3894｜数据JSON服务API
- **doc-view ID**：3894
- **核心概念**：FR系统提供了强大的数据支持功能，支持多种数据库和类型，并提供了异构数据源模型，使得同一张报表的数据可以来源于同一数据库的多个不同表，或多个不同数据库。 数据JSON服务API功能插件是将报表数据集、报表结果输出为JSON格式内容，并作为WEB接口服务开放，提供给报表系统前端或者其他系统使用。 插件功能提供JSON数据接口服务功能。
- **关键API/代码**：公式: MD5(密钥code+report_path+timestamp)；公式: alert("导出成功" + data.toString()；公式: alert("baocuo")
### doc-view-4204｜超级链接-JavaScript脚本
- **doc-view ID**：4204
- **核心概念**：JavaScript 脚本自由度较高，可以实现很多报表展示效果，设计该类型的超链需要您有一定的 JavaScript 基础。 当然文档里面也提供一些 JavaScript 类型的超级链接方案，您可以直接使用。 本文示例将通过 JavaScript 脚本类型的超链将报表导出为 Excel ，效果如下图所示：
- **关键API/代码**：公式: encodeURI(encodeURI("${servletURL}?reportlet=/订单明细表.cpt&订单号=" + ID + "&format=excel")
### doc-view-4285｜JS API
- **doc-view ID**：4285
- **核心概念**：FineReport 11.0 提供了全新的 JS API 手册，每个接口都有详细的使用说明，方便用户对报表进行前端设计。相比于 10.0  的 JS 接口，11.0 的接口具有以下优点： 接口统一规整，同样的功能，除特殊情况外决策报表和普通报表一致；同时对移动端的支持情况也做了说明。 结构清晰，范围明确，具有整体性；每个接口都有详细的使用说明，对用户使用和学习友好，简单易上手。
- **关键API/代码**：JS: _g() 获取报表对象。；JS: _g() 的 getParameterContainer 方法获取参数面板对象，即：；JS: _g().getParameterContainer；JS: _g().getParameterContainer().getWidgetByName("comboBox0")；JS: _g().getParameterContainer().getWidgetByName("comboBox0").setVisible(false)；JS: _g().writeReport()
### doc-view-4327｜JS API接口汇总
- **doc-view ID**：4327
- **核心概念**：11.0.7「FVS大屏编辑模式」插件 V1.8.0** 及之后版本，适配了部分接口，详情见 FVS大屏JS接口汇总 11.0.7决策报表新增多个报表块接口，详情见： 报表块对象接口、报表块行列对象接口、报表块单元格对象接口 本页汇总了JS API 所有接口，可简单查看每个接口的功能和移动端支持情况，详细介绍请阅读对应的接口介绍。
- **关键API/代码**：JS: _g() 获取的报表对象上的方法外，还包括 FR 对象 和 FS 对象上的方法。；JS: _g()获取报表对象，获取后结合报表对象的方法使用支持支持，但 10.0 支持的范围和方法较少，11.0 新增部分方法；公式: ajax()；公式: getCell(row,col)；公式: getRow(index)；公式: getColumn(index)
- **FR11版本要点**：版本功能变动 11.0.10报表块对象接口、报表块行列对象接口、报表块单元格对象接口 支持普通报表；11.0.10报表块对象接口、报表块行列对象接口、报表块单元格对象接口 支持普通报表 11.0.7「FVS大屏编辑模式」插件 V1.8.0** 及之后版本，适配了部分接口，详情见 FVS大屏JS接口汇总；11.0.7「FVS大屏编辑模式」插件 V1.8.0** 及之后版本，适配了部分接口，详情见 FVS大屏JS接口汇总 11.0.7决策报表新增多个报表块接口，详情见： 报表块对象接口、报表块行列对象接口、报表块单元格对象接口
### doc-view-4533｜Web API
- **doc-view ID**：4533
- **核心概念**：WebAPI 是网络应用程序接口，包含了广泛的功能。 网络应用通过 API 接口，可以实现存储服务、消息服务、计算服务等能力，利用这些能力可以开发出强大功能的 Web 应用。 比如通过 WebAPI 访问到数据库里的内容，通过 GET 方式展示出来，给其他终端调用。
### doc-view-4837｜触发V8远程代码执行漏洞
- **doc-view ID**：4837
- **核心概念**：针对 2022-08-01 网上反馈的帆软报表触发V8远程代码执行漏洞，受影响的帆软产品版本如下： FineReport10.0系列，11.0系列 FineBI5.X系列
### doc-view-4896｜JS?API兼容说明
- **doc-view ID**：4896
- **核心概念**：本文将介绍 Finereport 10.0 升级至 11.0 时官方 JavaScript 接口的变化，用户模板中如果使用了 javaScript 代码，版本升级时，需要仔细阅读本篇文档。 注：11.0 所有新增接口 10.0 下不支持，详情可查看 API接口汇总 中接口支持的范围
- **关键API/代码**：JS: _g() 获取的报表对象上。废弃的 contentPane 对象及其上的方法在 11.0 中可以使用，但后续不会随版本迭代更新，即在 11.0 上使用会存在兼容风险，建
### doc-view-4932｜开放平台API接口调用示例
- **doc-view ID**：4932
- **核心概念**：在完成开放平台API、应用和权限配置后，就可以调用API接口，实现相应的功能。 本文档将提供多种调用示例Demo，帮助大家理解开放平台的使用。 注：本文档的示例，均直接调用基础数据接口下的内置服务，在决策系统重启后，服务中用户已配置好的数据，会重置为默认数据。
- **关键API/代码**：SQL: SELECT * FROM `销量` where 地区 = '华东'
### doc-view-4993｜Word报告设置定时调度任务
- **doc-view ID**：4993
- **核心概念**：11.0.6 及之后版本2.0.2-Windows注：暂不支持MAC WPS 2019及以上 专业版/个人版支持定时调度任务，勾选后附件存档仅支持 word 与 pdf 格式，处理方式仅支持邮件消息与短信消息，支持 FTP 与 SFTP 上传 在日常应用中，除了生成报告更加便捷外，经常需要将报告与结合定时调度任务结合，自动生成报告内容，通过邮件等方式发送给业务人员或领导等报告的最终查看方。
- **FR11版本要点**：报表服务器版本插件版本自定义加载项版本系统要求office要求功能变动 11.0.6 及之后版本2.0.2-Windows注：暂不支持MAC
### doc-view-5023｜定时调度程序模板
- **doc-view ID**：5023
- **核心概念**：数据决策管理系统中的定时调度，在“调度对象”设置的步骤，可以选择程序报表执行。 设计器插件安装方法请参见：设计器插件管理 服务器安装插件方法请参见：服务器插件管理
- **关键API/代码**：SQL: select * from 销量")；Java: com.fr.form.main.Form；Java: com.fr.web.core.Reportlet；Java: com.fr.main.impl.WorkBook三个系统类；Java: com.fr.main.impl.WorkBook；Java: com.fr.form.ui.Label
- **FR11版本要点**：报表服务器版本插件版本 11.0.5V1.0.1
### doc-view-5076｜关于钉钉企业内部应用API调用量和频次限制的调整说明
- **doc-view ID**：5076
- **核心概念**：钉钉最近发布公告，对API调用做了限频处理。对于API调用总次数较多、每秒调用次数较多的企业，需要在钉钉那边购买对应版本来解决限频问题。 详情见：关于企业内部应用API调用量和频次限制的调整说明 影响范围针对标准版钉钉组织，情况如下：

> 本页收录 doc-view ID（18 条）：597、632、744、911、1023、1175、2523、3894、4204、4285、4327、4533、4837、4896、4932、4993、5023、5076
