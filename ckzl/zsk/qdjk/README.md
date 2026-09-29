---
keywords: [FR, FS, Widget, Msg, Dialog, WritePane, jQuery, 获取单元格, 单元格, getCellValue, setCellValue, JSAPI]
---
<!--
KB_INDEX: {
  "title": "帆软ckzl/zsk/qdjk总览",
  "stage": "frontend",
  "tags": ["JavaScript", "前端接口", "JS API", "jQuery", "控件"],
  "keywords": ["FR", "FS", "Widget", "Msg", "Dialog", "WritePane", "jQuery"],
  "summary": "帆软 FR 10.0 前端 JS API 文档总览：90+ 类的命名空间分类、控件/报表/窗口/布局 API 速查"
}
-->

# 帆软ckzl/zsk/qdjk总览

← [返回主路由](../AGENTS.md)

> **来源**: http://dev.fanruan.com/jsdoc/
> **适用**: 所有报表中的 JavaScript 脚本（填报事件、参数面板交互、工具栏自定义按钮、CSS 注入回调）

---

## 命名空间总览

```
FR          ← 核心命名空间（控件/报表/窗口/布局/消息）
FS          ← 决策平台命名空间（Tab/插件/系统配置）
jQuery      ← FR 内置 jQuery 库（可直接使用 $ 或 jQuery）
String      ← 字符串扩展
Array       ← 数组扩展
Function    ← 函数扩展
```

---

## FR 命名空间分类（开发常用）

### 控件类（填报/参数面板）

| 类名 | 说明 | 开发频率 |
|------|------|---------|
| **FR.Widget** | 控件基类（getValue/setValue/getName/getWidgetByName/setVisible/setEnable/reset/destroy） | ⭐⭐⭐⭐⭐ |
| **FR.OB** | 观察者基类（on/once/un/fireEvent/purgeListeners）— 事件绑定 | ⭐⭐⭐⭐⭐ |
| **FR.TextEditor** | 文本输入框 | ⭐⭐⭐⭐ |
| **FR.NumberEditor** | 数字输入框 | ⭐⭐⭐⭐ |
| **FR.ComboBoxEditor** | 下拉框（含 ComboCheckBox） | ⭐⭐⭐⭐ |
| **FR.CheckBoxEditor** | 复选框 | ⭐⭐⭐ |
| **FR.CheckBoxGroup** | 复选框组 | ⭐⭐⭐ |
| **FR.DatePicker** | 日期选择器 | ⭐⭐⭐ |
| **FR.DateTimeEditor** | 日期时间选择器 | ⭐⭐⭐ |
| **FR.FreeButton** | 自由按钮（导出/提交/导入按钮） | ⭐⭐⭐⭐⭐ |
| **FR.FormSubmitButton** | 查询按钮（带 enter 快捷键） | ⭐⭐⭐⭐⭐ |
| **FR.TextArea** | 多行文本框 | ⭐⭐ |
| **FR.Label** | 标签 | ⭐⭐ |
| **FR.Password** | 密码框 | ⭐ |
| **FR.RadioButton** / **FR.RadioGroup** | 单选按钮/组 | ⭐⭐ |
| **FR.TriggerEditor** | 触发编辑器 | ⭐⭐ |
| **FR.ListEditor** | 列表编辑器 | ⭐ |

### 报表类（内容操作）

| 类名 | 说明 | 开发频率 |
|------|------|---------|
| **FR.Elementcase** | 报表内容基类 | ⭐⭐⭐⭐ |
| **FR.WritePane** | 填报面板（提交/校验/数据操作） | ⭐⭐⭐⭐⭐ |
| **FR.PagePane** | 分页预览面板 | ⭐⭐⭐ |
| **FR.WLGP** | 填报相关全局属性 | ⭐⭐⭐ |
| **FR.Write** | 填报操作 | ⭐⭐⭐⭐ |
| **FR.WriteEditor** | 填报编辑器 | ⭐⭐⭐ |

### 窗口/弹窗类

| 类名 | 说明 | 开发频率 |
|------|------|---------|
| **FR.Msg** | 消息弹窗（confirm/alert/in prompt） | ⭐⭐⭐⭐⭐ |
| **FR.Dialog** | 对话框（showDialog/closeDialog/destroyDialog） | ⭐⭐⭐⭐⭐ |
| **FR.Window** | 窗口 | ⭐⭐⭐ |

### 布局类（参数面板/表单布局）

| 类名 | 说明 |
|------|------|
| FR.AbsoluteLayout | 绝对定位布局（参数面板默认） |
| FR.BorderLayout | 边框布局 |
| FR.CardLayout | 卡片布局 |
| FR.CenterLayout | 居中布局 |
| FR.FlowLayout | 流式布局 |
| FR.GridLayout | 网格布局 |
| FR.TableLayout | 表格布局 |

### 工具类

| 类名 | 说明 |
|------|------|
| **FR.Keys** | 按键常量（enter/esc/ctrl 等） |
| FR.BigDecimal | 大数字处理 |
| FR.Browser | 浏览器检测 |

---

### 常见问法：前端 JS 怎么拿到/改某个单元格的内容？（前端js取单元格值的接口是哪个）

| 症状/口语问题 | 动作 | 出处（本文件§+行号） |
|---|---|---|
| 想在前端用 js 读某个单元格的值 | `_g().getCellValue("A2")` | L114 |
| 想用 js 改单元格值 | `_g().setCellValue("A2", "test")` | L113 |
| _g() 到底是什么 | 全局函数，返回当前报表实例（ContentPane 对象）；`_g()` 系列全家福见下节表 | L101-114 |
| 提交前要停掉编辑状态 | `_g().stopEditing(); _g().verifyAndWriteReport(true)` | L109-110 |
| 提交成功后怎么刷新数据 | `_g().parameterCommit()`，挂 writesuccess | L108、L240 |
| 要更全的填报/报表类 API 去哪查 | `references/api_report.md`（Msg/Dialog/WritePane/Elementcase 等）；FR10/FR11 差异→`ckzl/lc/fr11_knowledge/js-api二次开发/SKILL.md` | L249-255（两入口 ls 实测存在） |
| 问法「前端js取单元格值和参数控件值的接口是哪个」 | 单元格值=本表 `_g().getCellValue/setCellValue`；**参数控件值**=下方「JS 怎么取参数面板控件的值、给控件赋值/隐藏/禁用？」卡（两卡合起来即完整答案） | L101/L175 |

## 核心全局函数（`_g()` 系列）

> 这些是 FR 报表预览环境中的全局函数，不属于类方法，但在开发中最常用。

| 函数 | 说明 | 示例 |
|------|------|------|
| `_g()` | 获取当前报表实例（返回 ContentPane 对象） | `_g().parameterCommit()` |
| `_g().parameterCommit()` | 重新查询（参数提交触发查询） | 填报提交成功后刷新数据 |
| `_g().verifyAndWriteReport(isShow)` | 校验并提交填报 | `_g().verifyAndWriteReport(true)` |
| `_g().stopEditing()` | 停止当前编辑状态（提交前必调） | `_g().stopEditing(); _g().verifyAndWriteReport(true);` |
| `_g().exportReportToExcel(type)` | 导出 Excel | `_g().exportReportToExcel('simple')` |
| `_g().getWidgetByName(name)` | 获取参数面板控件 | `_g().getWidgetByName("para_bu").getValue()` |
| `_g().setCellValue(cell, value)` | 设置单元格值 | `_g().setCellValue("A2", "test")` |
| `_g().getCellValue(cell)` | 获取单元格值 | `_g().getCellValue("A2")` |

---

### 常见问法：JS 弹确认框/提示框怎么写？confirm 取消就不提交怎么做？

| 症状/口语问题 | 动作 | 出处（本文件§+行号） |
|---|---|---|
| 提交前弹确认框，点取消就不提交 | `FR.Msg.confirm("提示","确认提交？",function(v){if(v){_g().stopEditing();_g().verifyAndWriteReport(true);}})` 挂提交按钮 click | L123、L237 |
| confirm 加了宽度参数就报语法错 | ⚠ confirm 只有 3 个参数，追加第 4 个（如 `,100`）会 `SyntaxError: missing ) after argument list`（2026-08-07 实测踩坑） | L239 |
| 只要个提示框/要用户输入 | `FR.Msg.alert(title, message, callback, width)` / `FR.Msg.in(prompt, message, callback)` | L122、L124 |
| 点按钮弹导入弹窗（iframe） | `FR.showDialog("导入",1200,600,$iframe,{resizeable:false})`；iframe src 拼 `${servletURL}` + 控件筛选参数，完整代码见导入弹窗标准模式 | L128-150 |
| 弹窗里操作完怎么关闭并刷新父页 | `window.parent._g().parameterCommit(); window.parent.FR.closeDialog(); window.parent.FR.destroyDialog();` | L133-134、L241 |

## FR.Msg — 消息弹窗（最常用）

| 方法 | 说明 | 示例 |
|------|------|------|
| `FR.Msg.alert(title, message, callback, width)` | 警告框 | `FR.Msg.alert("提示", "操作成功")` |
| `FR.Msg.confirm(title, message, callback)` | 确认框 | `FR.Msg.confirm("提示", "确认提交？", function(v){ if(v){...} })` |
| `FR.Msg.in(prompt, message, callback)` | 输入框 | `FR.Msg.in("输入", "请输入值", function(v){...})` |

---

## FR.Dialog / FR.showDialog — 弹窗（导入按钮常用）

| 方法 | 说明 | 示例 |
|------|------|------|
| `FR.showDialog(title, width, height, content, config)` | 显示弹窗 | `FR.showDialog("导入", 1200, 600, $iframe, {resizeable:false})` |
| `FR.closeDialog()` | 关闭弹窗（在弹窗内部调用） | `window.parent.FR.closeDialog()` |
| `FR.destroyDialog()` | 销毁弹窗 | `window.parent.FR.destroyDialog()` |

### 导入弹窗标准模式

```javascript
var form = this.options.form;
var url = "${servletURL}?viewlet=path/import.cpt&op=write";
// 传递参数面板筛选条件到导入页面
var ps = ["para_year_start", "para_bu"];
for (var i = 0; i < ps.length; i++) {
    var w = form.getWidgetByName(ps[i]);
    if (w) { var v = w.getValue(); if (v) url += "&" + ps[i] + "=" + encodeURIComponent(v); }
}
var $iframe = $("<iframe id='inp' width='100%' height='100%' scrolling='no' frameborder='0'>");
$iframe.attr("src", encodeURI(url));
FR.showDialog("Import", 1200, 600, $iframe, {resizeable:false, draggable:false});
```

---

### 常见问法：JS 怎么取参数面板控件的值、给控件赋值/隐藏/禁用？

| 症状/口语问题 | 动作 | 出处（本文件§+行号） |
|---|---|---|
| 想拿参数面板某个控件的值 | `_g().getWidgetByName("para_bu").getValue()` | L112、L158 |
| 参数面板自己的 JS 里取控件 | `this.options.form.getWidgetByName("para_bu").getValue()` | L244 |
| 给控件赋值/设显示值 | `w.setValue("ALL")`（实际值）/ `w.setText("全部")`（显示值）；getValue vs getText 区别见方法表前两行 | L158-161 |
| 隐藏/禁用/重置控件 | `w.setVisible(false)` / `w.setEnabled(false)` / `w.reset()` | L164-166 |
| 想知道控件叫什么/是什么类型 | `w.getName()` / `w.getType()` | L162-163 |
| 接口用法拿不准想看实测样例 | 对照 `references/verified_20260904.md`（FR10 前端 JS API 实测验证报告，附 Console 最小样例） | references 实测存在 |

## FR.Widget — 控件通用方法（通过 getWidgetByName 获取后调用）

| 方法 | 说明 | 示例 |
|------|------|------|
| `getValue()` | 获取控件实际值 | `var v = _g().getWidgetByName("para_bu").getValue()` |
| `setText(text)` | 设置显示值 | `w.setText("全部")` |
| `getText()` | 获取显示值 | `var t = w.getText()` |
| `setValue(value)` | 设置实际值 | `w.setValue("ALL")` |
| `getName()` | 获取控件名 | `w.getName()` → `"para_bu"` |
| `getType()` | 获取控件类型 | `w.getType()` → `"ComboBox"` |
| `setEnabled(bool)` | 启用/禁用 | `w.setEnabled(false)` |
| `setVisible(bool)` | 显示/隐藏 | `w.setVisible(false)` |
| `reset()` | 重置到初始值 | `w.reset()` |
| `isEnabled()` | 是否可用 | `w.isEnabled()` → `true` |
| `isVisible()` | 是否可见 | `w.isVisible()` → `true` |
| `getWidgetByName(name)` | 获取子控件 | `w.getWidgetByName("child")` |
| `fireEvent(eventName)` | 触发事件 | `w.fireEvent("afterinit")` |
| `on(event, fn)` | 绑定事件 | `w.on("click", function(){...})` |
| `destroy()` | 销毁控件 | `w.destroy()` |

---

## 事件系统（FR.OB 基类）

所有 FR 控件都继承自 FR.OB，支持事件绑定：

| 方法 | 说明 |
|------|------|
| `on(eventName, fn)` | 绑定事件 |
| `once(eventName, fn)` | 绑定一次性事件 |
| `un(eventName, fn)` | 解绑事件 |
| `fireEvent(eventName)` | 手动触发事件 |
| `purgeListeners()` | 清除所有事件绑定 |

### 常见事件名

| 事件 | 触发时机 | 使用场景 |
|------|---------|---------|
| `click` | 按钮点击 | 自定义按钮操作 |
| `afterinit` | 控件初始化完成 | 参数面板加载后注入 CSS/JS |
| `writesuccess` | 填报提交成功 | 刷新数据 / 关闭弹窗 |
| `change` / `valuechange` | 控件值改变 | 级联联动 |
| `afterload` | 页面加载完成 | 页面初始化 |
| `beforeunload` | 页面卸载前 | 离开提醒 |

### 常见问法：事件 JS 里怎么拿 sessionID/用户名？为什么写 ${sessionID} 报错？

| 症状/口语问题 | 动作 | 出处（本文件§+行号） |
|---|---|---|
| 事件 JS 里直接写 ${sessionID} 报错 | 公式只在「事件面板声明的参数」里展开：面板声明 `a = ${sessionID}`，JS 体裸变量 `var sid = a`，不要写 ${a} | L199-208 |
| cpt XML 的 CDATA JS 里能直接写吗 | 可以：`_g("${sessionID}")` **必须双引号**；单引号会 SyntaxError、裸写会被当模板字符串插值报错（2026-08-07 实测） | L206 |
| 声明的参数名有什么要求 | 必须是合法 ASCII 标识符（注入为 JS 作用域裸变量） | L210 |

### 事件 JS 两段式传参（来源 doc-4104）

FR 事件 JS 内**不能**直接写 `${sessionID}` 之类的服务端公式——公式只在「事件面板声明的参数」里展开，JS 体里按裸变量引用：

```
事件面板声明:   a = ${sessionID}  b = ${fine_username}

> ⚠️ **例外**：cpt XML 里的 JS（`<Content><![CDATA[...]]></Content>`）**可以**直接写 `"${sessionID}"`（**双引号**）——FR 服务端渲染时替换为真实值（示例项目报表 示例映射A/LTA分月明细表等实测）。**必须用双引号**：`_g("${sessionID}")`；单引号 `_g('${sessionID}')` 在部分 FR 封装脚本下会 `SyntaxError: missing ) after argument list`（2026-08-07 实测踩坑）；裸写 `_g(${sessionID})` 会被浏览器当模板字符串插值直接报错。
JS 体内引用:   var sid = a; var user = b;   // 裸变量,不要写 ${a}
```

规则：① 需要服务端值 → 先在事件面板声明参数并赋值公式；② JS 体只引用声明过的参数名；③ 参数名必须是合法 ASCII 标识符（会被注入为 JS 作用域裸变量）。

---

## jQuery 支持

FR 内置 jQuery，可直接使用 `$` 或 `jQuery`：

```javascript
// DOM 操作
$(".fr-btn-up").css("background", "#47a8ea");
$("#popup_container").children().eq(2).css("width", "120px");

// AJAX
$.ajax({ url: "...", success: function(data){...} });

// iframe 创建（导入弹窗）
var $iframe = $("<iframe id='inp'>");
$iframe.attr("src", url);
```

---

## 实际使用场景速查

| 场景 | JS 代码 | 用于哪个事件 |
|------|--------|-------------|
| **提交确认弹窗** | `FR.Msg.confirm("提示","确认提交？",function(v){if(v){_g().stopEditing();_g("${sessionID}").verifyAndWriteReport(true);}})` | 提交按钮 click |

> ⚠️ **易错**：`FR.Msg.confirm(title, message, callback)` **只有 3 个参数**，不要追加第 4 个参数（如 `,100`）——会导致 `SyntaxError: missing ) after argument list`（2026-08-07 实测踩坑）。
| **填报成功后刷新** | `_g().parameterCommit()` | writesuccess listener |
| **导入成功后关闭弹窗** | `window.parent._g().parameterCommit(); window.parent.FR.closeDialog(); window.parent.FR.destroyDialog();` | writesuccess listener (导入模板) |
| **导出 Excel** | `_g().exportReportToExcel('simple')` | 导出按钮 click |
| **打开导入弹窗** | `FR.showDialog(...)` | 导入按钮 click |
| **获取参数值** | `this.options.form.getWidgetByName("para_bu").getValue()` | 参数面板 JS |
| **设置单元格值** | `_g().setCellValue("A2", "test")` | 报表 JS |

---

## 详细 API 参考

| 文档 | 内容 |
|------|------|
| `references/api_report.md` | 报表/填报核心类 API（Msg/Dialog/WritePane/Elementcase/PagePane/WLGP/Write/WriteEditor） |
| `references/api_widgets.md` | 控件类 API（Widget/TextEditor/NumberEditor/ComboBox/CheckBox/DatePicker/FreeButton/FormSubmitButton/OB/TriggerEditor） |
| `references/api_utils.md` | 通用类 API（jQuery/String/Array/Function/Keys） |

---

## FS 命名空间（决策平台）

> 一般报表开发不常用，仅在做决策平台插件或自定义导航时使用。

| 类 | 说明 |
|----|------|
| FS.QuickTab | 快速切换 Tab |
| FS.SwitchButton | 开关按钮 |
| FS.LTabPane / FS.InsideTabPane | Tab 面板 |
| FS.FloatPane | 浮动面板 |
| FS.Accordion | 手风琴 |
| FS.TablePane | 表格面板 |
| FS.ParameterGrid | 参数网格 |
| FS.ColorPicker | 颜色选择器 |
| FS.Plugin.* | 插件接口 |

---

*来源: http://dev.fanruan.com/jsdoc/ | 最后更新: 2026-08-05*
