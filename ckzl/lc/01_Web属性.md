<!--
KB_INDEX: {
  "title": "Stage 6 · Web 属性",
  "stage": "pipeline",
  "tags": [
    "CSS",
    "Web",
    "工具栏",
    "注入"
  ],
  "keywords": [
    "Web属性",
    "ReportWebAttr",
    "工具栏",
    "分页预览",
    "页面框架"
  ],
  "summary": "Web 属性配置（ReportWebAttr）：分页预览/填报页面/数据分析三态设置、工具栏按钮、页面框架"
}
-->

# Stage 6 · Web 属性

> 本页为 [06_Web呈现层.md](06_Web呈现层.md) 拆分分篇 1/4（2026-09-29 断链治理，单篇 ≤400 行）；返回 [导航页](06_Web呈现层.md)。

---

## 11. Web 属性

### 11.1 工具栏

> **预览方式归属(重要)**:`<ReportWebAttr>` 是 Web 属性的根节点,其下有四个**并列**分区,互不继承:
>
> ```
> <ReportWebAttr>
>   ├─ <ServerPrinter/>            ← 服务器打印
>   ├─ <WebPageContent>            ← 分页预览(普通查看)配置区
>   ├─ <WebWriteContent>           ← 填报预览配置区
>   └─ <CSSImport>                 ← 对所有预览方式生效,必须是 ReportWebAttr 直接子节点
> ```
>
> ⚠️ **`WebPageContent` 与 `WebWriteContent` 互不继承**:在 `WebPageContent` 里配的工具栏只对分页预览生效,对填报预览无效,反之亦然。下方示例属于**分页预览**配置;填报侧请参照 `gen_fill_v2.py:127` 的 `<WebWriteContent>` 写法(内含 `<ToolBars/>`、`<RptLocation isShowAtLeft>`、`<ShowWidgets show>`、`<WebWrite SheetPosition>`、`writesuccess` 监听)。
>
> 来源:帆软官方帮助 doc-135

```xml
<WebPageContent>
  <ToolBars>
    <ToolBarManager>
      <Location><Embed position="3"/></Location>
      <ToolBar>
        <ShortCut name="First"/><ShortCut name="Previous"/>
        <ShortCut name="PageNavi"/><ShortCut name="Next"/><ShortCut name="Last"/>
        <Separator name="Separator"/>
        <ShortCut name="ExcelO"/><ShortCut name="Print"/>
      </ToolBar>
    </ToolBarManager>
  </ToolBars>
</WebPageContent>
```

#### 11.1.1 导出按钮与无头 URL 对照

`<ShortCut name="..."/>` 是工具栏快捷按钮的序列化通道,`name` 取值与无头导出 URL 的对应关系:

| ShortCut name | 导出方式 | 无头 URL 等价 |
|------|---------|--------------|
| `ExcelP` | 分页导出 | `format=excel&extype=page` |
| `ExcelO` | 原样导出 | `format=excel&extype=simple` |
| `ExcelS` | 分页分Sheet | `format=excel&extype=sheet` |
| `Word` | Word 导出 | `format=word` |
| `PDF` | PDF 导出 | `format=pdf` |
| `Image` | 图片导出 | `format=image` |

> ⚠️ 插件类导出按钮(如「导出 Excel 方式选择控件」插件提供的 Excel03 系列)也走同一个 `<ShortCut>` 序列化通道:插件在工具栏配置里多出按钮,勾选后被序列化进 `<ToolBar>` 的 `<ShortCut name="..."/>` 列表,无头生成器可以直接控制。
> ⚠️ `ShortCut@name` 拼错或臆造名字**不会报错,只是按钮静默不渲染**;且带插件按钮的 .cpt 迁到未装插件的服务器时按钮同样静默消失。kit 已验证的取值:First/Previous/PageNavi/Next/Last/ExcelO/Print。
> ⚠️ 插件双按钮(Excel03 系列)不支持移动端。
> 来源:帆软官方帮助 doc-786、doc-135

#### 11.1.2 工具栏的 Java API 装配链

```java
ToolBarManager tbm = ToolBarManager.createDefaultToolBar();
tbm.setToolBarLocation(Location.createTopEmbedLocation());
tbm.getToolBar().addWidget(btn);
WebPage p = new WebPage();
p.setToolBarManagers(new ToolBarManager[]{tbm});
attr.setWebPage(p);
```

三处易错:
- `setToolBarManagers` 在父类 `com.fr.report.web.WebContent` 上(非 WebPage);
- `getToolBar()` 返回的是 `com.fr.form.ui.ToolBar`(不在 com.fr.report.web 包);
- `ToolBarButton.clickAction` 抽象,只能 new 子类。

> 来源:帆软官方帮助 doc-2188

#### 11.1.3 自定义工具栏按钮 = 第三条 JS 挂载路径

`new CustomToolBarButton()` + `setText/setIconName/setShowText/setShowIcon` + **`setJSImpl(new JavaScriptImpl(js))`**:
- 它**不用 Listener、无事件名**,与①模板级 `ReportWebAttr→WebPage/WebWrite/WebView + Listener(afterload…)`、②控件级 `Widget.addListener(Listener(afterinit…))` 并列,是第三条 JS 挂载路径;
- ⚠️ 同类的 `setJs(String)` 是旧版 `<CustomButton>` 文本节点路径(字段 OLD_XMLTAG),10.0 设计器不产出;`setJs` 与 `setJSImpl` 同名近似,选错即静默失效。

> 来源:帆软官方帮助 doc-2188

#### 11.1.5 跨域 iframe 调用 FR JS(来源 doc-1241)

外部页面在 iframe 内跨域调用报表 JS(如 `_g().writeReport()`):模板侧须在「模板Web属性 → 填报页面设置 → 事件设置」挂「加载结束(afterload)」事件,脚本内暴露 `sendMessage()` 收发 `postMessage`/`window.name`(老 IE 用 window.name + setInterval 轮询)。Listener 写法同 §11.2:`WebWrite.addListener(new Listener("afterload", new JavaScriptImpl(js)))`;跨域调用本质是把 FR JS 表达式字符串发给 iframe 内执行,任何 FR JS 都可被这样调用。

#### 11.1.4 「嵌入友好模板」标准装配件(Java 落点)

- 隐藏内置工具栏 = `WebPage/WebWrite/WebView.setToolBarManagers(new ToolBarManager[0])` —— **三分区互不继承,必须各设一次**;传 `null`/不设 = 回落服务器全局工具栏,不等于隐藏;
- iframe 自适应 = `WebPage.setAutoScaleWhenEmbeddedInIframe(true)`;
- 恢复默认 = `ToolBarManager.createDefaultToolBar()/createDefaultWriteToolBar()/createDefaultViewToolBar()`;
- ⚠️ .frm 报表块是另一套:`ElementCaseEditor.setToolBars(FormToolBarManager[])`。

> 来源:帆软官方帮助 doc-4624

### 11.2 CSS
```xml
<CSSImport><![CDATA[help/purchase/css/purchase_v1.css]]></CSSImport>
```

### 11.3 数据分析设置(Web 属性第三分支)

数据分析预览区与 WebPageContent / WebWriteContent 并列,是 Web 属性的第三分支:
- 「加载结束」事件的 XML 节点名**待核**(疑似 `WebAnalyzeContent` 根节点 + 事件名,Listener 写法沿用 §11 afterinit 同款),需抓真实设计器保存产物回填;
- 标准 payload 示例:选区框 hide/remove/recolor 三种 JS;
- ⚠️ 官方示例 left 边颜色 `'gleen'` 为笔误(应为 green),引用时随条目修正注记。

> 来源:帆软官方帮助 doc-3195

### 11.4 Web 事件的 Java API 注入路径

统一注入器骨架:

```java
ReportWebAttr attr = new ReportWebAttr();
WebWrite w = new WebWrite();
w.addListener(new Listener("afterload", new JavaScriptImpl(js)));
attr.setWebWrite(w);
wb.setReportWebAttr(attr);
```

- `addListener` 来自 `com.fr.form.event.Observer`(`WebWrite`→`WebContent`→`Observer`);
- `setWebPage/setWebView` 同构(对应分页/数据分析区)。

> 来源:帆软官方帮助 doc-1213

### 11.5 Web 事件名全集

三预览区共有(`com.fr.report.web.WebContent` 常量池):`startload`、`afterload`、`beforetopdf`/`aftertopdf`、`beforetoexcel`/`aftertoexcel`、`beforetoword`/`aftertoword`、`beforetoimage`/`aftertoimage`、`beforepdfprint`/`afterpdfprint`、`beforeflashprint`/`afterflashprint`、`beforeappletprint`/`afterappletprint`、`beforeprint`/`afterprint`、`beforeimportexcel`/`afterimportexcel`、`beforeemail`/`afteremail`;

填报独有(`WebWrite` 常量池):`beforewrite`、`writesuccess`、`writefailure`、`afterverify`、`beforeverifywrite`/`afterverifywrite`、`afterwrite`、`beforeappend`/`afterappend`、`beforedelete`/`afterdelete`。

> 事件名写错与挂错分区一样是**静默失效**(不报错、JS 永不触发);本清单直接读自 jar 字节码常量池,可作为 fr_check 白名单。

> 来源:帆软官方帮助 doc-1213

### 11.6 模板 Web 属性的 Java API 构建路径

载体 `com.fr.web.attr.ReportWebAttr`(挂点 `AbstractFineBook#setReportWebAttr`,模板级必须 new 而非 getInstance):

| 方法 | 对应 XML |
|------|---------|
| `setTitle(String)` | `<Title>` |
| `setCacheValidateTime(long ms)` | 缓存 |
| `addCSSImport(String)` | `<CSSImport>` |
| `addJSImport(String)` | JS 引用 |
| `setBackground(com.fr.general.Background)` | `<BackgroundAttr>` |
| `setWebPage/setWebWrite/setWebView` | `<WebPageContent>/<WebWriteContent>/<WebViewContent>` |

**补充（doc-615，字节码实读）**：`addJSImport/addCSSImport` 落盘为 `<ReportWebAttr>` 下的**文本元素** `<CSSImport>/<JSImport>`（不是属性）；`writeXML` 顺序 **CSS 在 JS 之前**（与 GUI 菜单顺序相反），节点位于 `<WebWriteContent>` 之后、`<CacheValidateTime>` 之前；配套 `clearJSImportList()/clearCSSImportList()/getJSImport()`，挂载点是 `AbstractTemplateWorkBook#setReportWebAttr(...)`（声明在 `com.fr.main.AbstractFineBook`）。手拼时若写成属性或把 JS 排在 CSS 前，XML 仍合法、fr_check 仍过，只是被 `readXML` 忽略或与设计器另存产物 diff 不齐。

> 来源:帆软官方帮助 doc-1228（上表）/ doc-615（补充）

### 11.7 引用 CSS/JS 的两种机制

1. 设计器「引用 CSS/JavaScript」菜单 = `addCSSImport/addJSImport` 引用**工程目录外部文件**(产出 `<CSSImport>`/JS 节点,相对路径、不可 WEB-INF)——无头生成优先用此表达「引用外部文件」,更轻量;
2. afterinit 事件 `$('<link>').appendTo('head')` 内联注入(§22 现行做法)——仅内联样式走此路。
3. ⚠ **H5 端引用路径必须带前导 `/`（`/test.js`），PC 端可不带**；`addJSImport` 只原样存串、零规范化——工具函数应拆 `forH5(path)`/`forPC(path)` 两个入口，避免同一模板双端踩前缀坑（doc-3475 §8.1）。XML 节点顺序（CSS 在 JS 前）见 §11.6 补充。

> 来源:帆软官方帮助 doc-1228（1-2 点）/ doc-3475（第 3 点）

### 11.8 模板 Web 属性硬约束校验(生成期规则)

1. CSS 仅相对路径、CSS/JS 不可放 WEB-INF;
2. 填报/实时模板设缓存>0 → 静默看到旧数据;
3. 决策报表(.frm)无「引用 CSS/JS」入口(只能 afterinit JS 注入);
4. 移动端不支持引用 CSS/JS、浏览器背景无意义;
5. 标题 `${p}` 公式参数须闭合。

> 共同特征:「写进模板合法、PC 预览正常、但运行环境忽略或换机/换端失效却无报错」,应在生成期防住。

> 来源:帆软官方帮助 doc-1228

### 11.9 事件挂载宿主总表

| 宿主 | 挂载写法 | 事件名字典 |
|------|---------|-----------|
| 单元格控件 | `DefaultTemplateCellElement.setWidget(w)` + `w.addListener(...)` | afterinit/beforeedit/afteredit/stopedit |
| 参数面板控件 | `WParameterLayout` 内的 Widget(同上) | 同上字典 |
| 模板级 | `ReportWebAttr` → `setWebPage(WebPage)/setWebWrite(WebWrite)/setWebView(WebView)` **三选一** | afterload/startload/… 共 34 个 |
| 决策报表组件 | `FormIO.readForm` → `Form.getWidgetByName(name).addListener(new Listener(Widget.AFTERINIT, js))` → `FormIO.writeForm(IOFile,String)`(**落 .frm,写盘入口与 .cpt 的 TemplateWorkBookIO 不同**) | 控件事件字典 |
| 决策报表 body（表单级） | `Form.getContainer().addListener(...)`——**真实根 body WLayout**；**严禁 `Form#getBodyContainer()`**（返回 clone+removeWidget 的只读克隆，改动落盘即丢） | `{afterinit, click}`（doc-2372 实证 click，如「点击 body 全屏」；XML=`<Form><Body><Events>`） |

> 注：body 级与控件级挂错=静默失效，白名单与回读断言见 07 §12.13。

> ⚠️ 三个 WebPage/WebWrite/WebView 对象互不继承、事件不共享:只挂 WebPage 却用填报预览打开会静默无效。

> 来源:帆软官方帮助 doc-4195

### 11.10 事件名校验反例:不要用 `supportedEvents()` 做白名单

字节码实读 `com.fr.form.ui.ElementCaseEditor#supportedEvents()` 只返回 `{"click"}`,但官方文档(doc-920)推荐的报表块「初始化」事件 `afterinit` 确实生效(form.js 对所有组件统一分发 afterinit)。据此做硬校验会把官方推荐写法判成错误——校验只能做 WARN,不能做 ERROR。

> 来源:帆软官方帮助 doc-4195

### 11.11 资源部署：HTML 富内容 / 图片文件是部署动作，不是模板构建

GIF/图片等静态资源需拷贝到 `%FR_HOME%\webroot\help` 等工程目录——**该步骤无法用 Java API 表达，属部署动作**，与模板构建（值 + `setShowAsHTML(true)` + 合并）分离（doc-987 的 `<embed src>` 路径依赖服务器文件存在；移动端不支持、导出/打印不带动画，仅 PC 分页/填报预览生效）。无头交付清单应把「资源文件落位」单列为部署步骤，而不是塞进模板构建链。

> 来源: 帆软官方帮助 doc-615（资源部署定位；佐证 doc-987）

### 11.12 加载动画与 .frm 全局 JS 注入边界

- `FR.HtmlLoader` 定义在 `fine-report-engine-10.0.jar!/com/fr/web/core/js/jquery.tools.js`；`loadingEffect` 被 8 个内置 js 消费（form / widget.elementcase / chart.report.widget / chart.form.widget / VanChartWrapper / ExtendedChart / AbstractChart / jquery.tools），置空即**全局关闭**，故「分页/分析/决策报表通用」；
- ⚠ **副作用（官方未提）**：导出进度条 `#progressBar` + `FR.i18nText("Fine-Engine_Exporting_Recommend")` 也走 `FR.HtmlLoader.loadingEffect.call(this, config)`——置空后大文件导出**无任何进度反馈**；
- 要「换动画」而非「去掉」：走插件 `com.fr.plugin.loadingEffect.v10`（`com/fr/report/plugins.csv` 登记，对应 JS 钩子 `useCustomLoadingAnimation()`，基类恒 `false`），不要覆写 `loadingEffect`；
- .frm **没有模板级 JS 引入**：全 jar 扫 `ImportJsCssProvider` 实现者命中全在 WorkBook 侧，`com.fr.form.main.Form` 不在其中 → 决策报表注入全局 JS 的唯一挂点就是容器 Listener（白名单见 07 §12.13）。

> 来源: 帆软官方帮助 doc-1086（实证 doc-1629）

### 11.13 全站级前端资源注入（WebResourceProvider，第二条路）

在模板级 `ReportWebAttr#addJSImport`（§11.6/11.7）之外补第二条路：`com.fr.decision.fun.impl.AbstractWebResourceProvider`（实现 `attach()`+`client()`，plugin.xml 挂 `<extra-decision><WebResourceProvider class=".."/>`），**宿主 key 决定作用范围**：
- `com.fr.decision.web.MainComponent.KEY` → 决策平台（平台自身页面）；
- `com.fr.report.web.ReportMainComponent.KEY` → 全部 .cpt 预览页；
- `com.fr.form.web.FormMainComponent.KEY` → 全部 .frm。

选型规则：**改单模板走 ReportWebAttr；改全站或改平台入口行为走 WebResourceProvider**。三个宿主 key 的 `children()` 一律 `Registry.getChildren(自身.class)`（已字节码实读）。

> 来源: 帆软官方帮助 doc-2365

### 11.14 引入的 JS 不生效怎么查（CSS 探针法）

**先调 `WebUtils.getImportedCSS(attr)` 当探针，再调 `getImportedJS(attr)`**。exception_table 实读（fine-core `com.fr.web.utils.WebUtils`）：`getImportedJS` code_len=113 / exc=3（`[8,52)→66 catch java.lang.Exception`，handler 里 `logger.error` 后**返回已累积集合**）；`getImportedCSS` code_len=66 / **exc=0**。同一个 `getGlobalWebAttr()` 故障，JS 侧静默降级成空/半集、CSS 侧直接抛——只看 JS 版会拿到假的空结果。

> 来源: 帆软官方帮助 doc-3475（同根因另见 doc-615：EngineModule 未注册时吞掉模板级 JS 引用）

### 11.15 JS 挂载点速查 + 前端锚点

① 四个挂载点固化：单元格 = `JavaScriptImpl` → `NameJavaScript(name, js)` → `NameJavaScriptGroup(NameJavaScript[])` → `AbstractCellElement#setNameHyperlinkGroup(..)`（声明在 `AbstractCellElement`、不在 `TemplateCellElement`/`CellElement` 接口；`NameJavaScriptGroup` 只有 `addNameHyperlink(NameJavaScript)`，无 `add(JavaScript)`）；模板级引入 = `ReportWebAttr#addJSImport/addCSSImport`；超链级引入 = `JavaScriptImpl#addJSImort(String)`（**官方拼写错误，少一个 p，不可「纠正」**，见 §28.3）；工具栏 = `com.fr.form.ui.CustomToolBarButton`（`setJs(String)`/`setJSImpl(JavaScript)`）。
② 前端唯一稳定 DOM 锚点是 `div[widgetname='<大写>']`（`Widget#createJSONConfig` 把 widgetName `toUpperCase()` 后下发，XML 里保留原样；写小写恒 null），报表单元格**无稳定 id**。
③ 用户 JS 里的 `this` 不是 window（`createContentFunction` 末尾 `.createDelegate(this, [...], 0).apply(this, arguments)`，this 是 FR 控件上下文），操作文档须写 `document.`/`window.document.`。

> 来源: 帆软官方帮助 doc-1191

#### 11.16 权限细粒度-按角色定制工具栏（doc-861）
> 🔗 互链：GUI 取消勾选 + JS 加载结束两法总览 → ckzl/lc/fr11_knowledge/js-api二次开发/references/js_api_summary.md doc-view-4359；隐藏=三分区 setToolBarManagers 空数组细节 → 本文件 §11.1.4。问法别名：模板 web 属性 取消勾选 使用工具栏。

「模板>模板Web属性>为该模板单独设置」= 模板级 `ReportWebAttr`（**必须 new，非 getInstance**，挂点 `AbstractFineBook#setReportWebAttr`）；`setToolBarManagers` 空数组=隐藏该模板该预览区工具栏、传 null/不设=回落服务器全局、三分区互不继承（见 §11.1.4，不赘述）。本节补两块新内容：

1. **按角色定制按钮的 Java 装配链**（细粒度权限「进入权限编辑」GUI 方案之外的无头唯一落点，实践示例 `practice/topic_861_hermes/SetReportToolbarByRole.java`）：

```java
// 角色由运行期 Session 注入 $fine_role；按角色裁剪工具栏
String role = "..."; // 模板内公式引用 $fine_role 判定（如 $fine_role="超级管理员"）
ToolBarManager tbm = ToolBarManager.createDefaultToolBar();
tbm.setToolBarLocation(Location.createTopEmbedLocation());
tbm.getToolBar().addWidget(btn); // 按 role 分支 add 不同按钮集
WebPage p = new WebPage();
p.setToolBarManagers(new ToolBarManager[]{tbm});
ReportWebAttr attr = new ReportWebAttr();
attr.setWebPage(p);
wb.setReportWebAttr(attr); // AbstractFineBook 挂点
```

2. **内置权限参数**（认证后自动写入 Session 的运行时参数，无头模板中直接引用即可，**无需注册为模板参数**）：`$fine_username`（用户名）、`$fine_role`（角色，超级管理员=superusers，**无角色时为空串**——条件须写 `$fine_role!=""` 等空值加固写法）、`$fine_position`（部门+职位数组 `{"departments":"...","jobTitle":"..."}`）；配套公式 `GETUSERDEPARTMENTS()` / `GETUSERJOBTITLES()` 取部门/职位。⚠️ 大小写必须与文档一致、**不支持模拟计算**（设计器取不到值，只能登录后取）；可在数据集 SQL/单元格公式中直接引用实现「不同角色看不同数据」。

> 来源:帆软官方帮助 doc-861

---

---
---
