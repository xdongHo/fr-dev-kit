<!--
KB_INDEX: {
  "title": "FR前端交互指南 1/3：JavaScript API 速查（contentPane/Msg/Dialog/Widget/WritePane/PagePane/Elementcase/Chart/AJAX/工具类）",
  "stage": "frontend",
  "tags": [
    "指南",
    "JS API",
    "contentPane",
    "控件"
  ],
  "keywords": [
    "contentPane",
    "FR.Msg",
    "FR.Dialog",
    "FR.Widget",
    "FR.WritePane",
    "FR.PagePane",
    "FR.Chart",
    "AJAX"
  ],
  "summary": "FineReport 前端交互高级实现指南第 1/3 页：JavaScript API 速查——核心对象层次、contentPane 核心方法、FR.Msg 消息弹窗、FR.Dialog/FR.Window 对话框、FR.Widget 控件基类、FR.WritePane 填报面板、FR.PagePane 分页预览、FR.Elementcase 报表块、FR.Chart 图表 API、AJAX 请求、工具类扩展——原指南一章"
}
-->


> 整理自：FR10学习笔记、插件逆向笔记、ckzl/zsk/qdjk
> 整理日期：2026-08-24
> 覆盖范围：JavaScript API速查表、交互设计模式、样式定制、填报优化、常见问题

---

## 一、JavaScript API 速查表

### 1.1 核心对象层次

```
contentPane (FR.WritePane / FR.PagePane)
├── getWidgetByName(name)    → 控件对象 (FR.Widget)
├── getCellValue(col, row)   → 单元格值
├── getWidgetByCell(cell)    → 单元格内控件
├── getWidgetsByName(name)   → 同名控件数组
├── curLGP (FR.WLGP)        → 当前填报逻辑页面
│   ├── getCell(col, row)    → 单元格DOM
│   ├── getTDCell(col, row)  → 单元格jQuery对象
│   └── moveTDCell(direction)→ 移动选中框
├── contentEl                → 报表内容区域DOM
├── parameterEl              → 参数面板
└── currentBTTag             → 当前Tab页签
```

### 1.2 contentPane 核心方法

#### 报表导航与刷新
| 方法 | 参数 | 说明 |
|------|------|------|
| `gotoPage(pn)` | 页码(从1开始) | 跳转到指定页 |
| `gotoFirstPage()` | — | 第一页 |
| `gotoLastPage()` | — | 最后一页 |
| `gotoNextPage()` | — | 下一页 |
| `gotoPreviousPage()` | — | 上一页 |
| `refreshAllSheets()` | — | 刷新所有sheet |
| `reloadCurLGPPane(fec)` | 可选：重载后选中格子 | 当前sheet重载 |
| `reCalCurLGPPane()` | — | 当前sheet重新计算 |
| `parameterCommit(reloadOthers)` | Boolean | **提交参数并刷新报表**（最常用） |

> ⚠ `.frm`(决策报表)用 `_g().parameterCommit()`；`.cpt`(普通报表)用 `contentPane.parameterCommit()`

#### 单元格读写
| 方法 | 参数 | 说明 |
|------|------|------|
| `getCellValue(col, row)` | 列号,行号(从0开始) | 获取单元格值 |
| `getCellValue({reportIndex, columnIndex, rowIndex})` | 对象形式 | 多sheet时指定sheet |
| `setCellValue(col, row, value)` | 列号,行号,值 | 设置单元格值 |
| `getWidgetByCell(cell)` | 单元格编号 | 获取单元格中的控件 |

#### 列/行控制
| 方法 | 参数 | 说明 |
|------|------|------|
| `setColVisible(col, visible)` | 列号, Boolean | 显示/隐藏列 |
| `setRowVisible(row, visible)` | 行号, Boolean | 显示/隐藏行 |

#### 样式与缩放
| 方法 | 参数 | 说明 |
|------|------|------|
| `scale(factor)` | `'+'`/`'-'`/数字(如1.5) | 缩放报表 |
| `autoScale()` | — | 自适应缩放 |
| `setBorderVisible(isVisible)` | Boolean | 显示/隐藏边框(需在加载起始事件中) |
| `makeHighlight(color, op, deep)` | 颜色, `'click'`/`'mouseover'`, Boolean | 行高亮 |

#### 导出
| 方法 | 参数 | 说明 |
|------|------|------|
| `exportReportToExcel(extype, sheets)` | `'simple'`(原样)/`'page'`(分页), sheet序号数组 | 导出Excel |
| `exportReportToPDF(extype)` | — | 导出PDF |
| `exportReportToWord()` | — | 导出Word |
| `exportReportToImage(extype)` | `'png'`等 | 导出图片 |
| `exportReportToHtml()` | — | 导出HTML |
| `exportReportToOffineHtml()` | — | 离线HTML |
| `emailReport()` | — | 发送邮件 |

#### 打印
| 方法 | 说明 |
|------|------|
| `flashPrint()` | Flash打印 |
| `appletPrint()` | Applet打印 |
| `printReportServer()` | 服务器端打印 |

#### 填报入库与校验
| 方法 | 参数 | 说明 |
|------|------|------|
| `writeReport(reportIndex, submitButton, successFn, failFn)` | sheet序号, 按钮, 成功回调, 失败回调 | 填报入库 |
| `verifyAndWriteReport(isAllSheet, submitButton, successFn, failFn)` | Boolean | 校验并提交 |
| `writeReportIgnoreVerify(isAllSheet)` | Boolean | 忽略校验直接提交 |
| `isDirtyPage()` | — | 是否有未提交数据 |
| `stopEditing()` | — | 停止编辑当前单元格 |
| `setEditOnClick(editOnClick)` | Boolean | 单击进入编辑 |
| `setEditOnMove(editOnMove)` | Boolean | 按键切换格子立即编辑 |

#### 行操作
| 方法 | 参数 | 说明 |
|------|------|------|
| `appendReportRC(count, cell)` | 行数, 格子位置 | 工具栏增加行 |
| `appendReportRow(location, reportIndex, count)` | 位置, sheet序号, 行数 | 插入行按钮方法 |
| `deleteReportRC(cell)` | 格子位置 | 工具栏删除行 |
| `deleteReportRow(location, reportIndex, count)` | 位置, sheet序号, 行数 | 删除行按钮方法 |

#### Excel导入
| 方法 | 说明 |
|------|------|
| `importExcel()` | Excel导入 |

### 1.3 FR.Msg 消息弹窗

| 方法 | 参数 | 说明 |
|------|------|------|
| `FR.Msg.alert(title, message, callback)` | 标题, 内容, 回调 | 提示框 |
| `FR.Msg.confirm(title, message, callback)` | 标题, 内容, 回调 | **确认框（只传3个参数！）** |
| `FR.Msg.prompt(title, message, value, callback, min_width)` | 标题, 内容, 默认值, 回调 | 输入框 |
| `FR.Msg.toast(message)` | 消息 | 轻提示(5秒消失) |

> ⚠ `FR.Msg.confirm` **只传3个参数**，第4个参数`min_width`是文档误标（传4参数会SyntaxError）

### 1.4 FR.Dialog / FR.Window 对话框

```javascript
var dlg = new FR.Dialog({
    title: 'Dialog',
    height: 100,
    width: 400,
    contentHtml: '<p>Hello Dialog!</p>'
});
dlg.setVisible(true);
```

| 方法 | 说明 |
|------|------|
| `doClose()` | 关闭窗体 |
| `setContent(c)` | 设置窗体内容 |
| `setTitle(title)` | 设置标题 |
| `setVisible(visible)` | 显示/隐藏 |

### 1.5 FR.Widget 控件基类通用方法

所有控件（TextEditor、ComboBox、DatePicker等）都继承这些方法：

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `getValue()` | — | Object | 获取实际值 |
| `setValue(value, shouldFireEvent)` | 值, Boolean | — | 设置值 |
| `getText()` | — | String | 获取显示值 |
| `setText(text)` | 文本 | — | 设置显示值 |
| `setVisible(visible)` | Boolean | — | 显示/隐藏 |
| `setEnable(enable)` | Boolean | — | 启用/禁用 |
| `reset()` | — | — | 恢复初始状态 |
| `getName()` | — | Object | 控件名 |
| `destroy()` | — | — | 销毁DOM |
| `isEnabled()` | — | Boolean | 是否可用 |
| `isVisible()` | — | Boolean | 是否可见 |
| `on(eventName, fn)` | 事件名, 函数 | — | 绑定事件 |
| `once(eventName, fn)` | 事件名, 函数 | — | 绑定一次性事件 |
| `un(eventName, fn)` | 事件名, 函数 | — | 解绑事件 |
| `fireEvent(eventName)` | 事件名 | Boolean | 触发事件 |
| `purgeListeners()` | — | — | 清除所有事件绑定 |

### 1.6 FR.WritePane 填报面板特有方法

填报预览(`op=write`)时的 `contentPane` 额外方法：

| 方法 | 说明 |
|------|------|
| `getCellValue({reportIndex, columnIndex, rowIndex})` | 获取单元格值(多参数形式) |
| `setCellValue({reportIndex, rowIndex, columnIndex, value})` | 设置单元格值 |
| `writeCellValue(tdCell)` | 写入tdCell的值 |
| `stopEditing()` | 停止编辑 |
| `setEditOnClick(true)` | 单击进入编辑 |
| `beforeUnloadCheck()` | 离开页面时检查dirty数据 |

### 1.7 FR.PagePane 分页预览特有方法

| 方法 | 说明 |
|------|------|
| `gotoPage(pn)` | 跳转指定页(从1开始) |
| `currentPageIndex` | 当前页序号(属性) |
| `reportTotalPage` | 总页数(属性) |
| `autoScale()` | 自适应缩放 |
| `makeHighlight(color, op, deep)` | 行高亮 |

### 1.8 FR.Elementcase 报表块组件(决策报表)

| 方法 | 说明 |
|------|------|
| `gotoPage(pn, para, noCache)` | 跳转到指定页(可用于刷新当前报表块) |
| `currentPage` | 当前页索引(属性) |
| `totalPage` | 总页数(属性) |

### 1.9 FR.Chart 图表API

```javascript
// 获取图表实例
var chart = FR.Chart.WebUtils.getChart("chart0");

// 获取数据
var data = chart.data;
var options = chart.options;
var series = chart.getSeries();
var seriesData = chart.getSeriesData(0);

// 操作
chart.setChartTitle("新标题");
chart.dataRefresh();
chart.exportToImage();
```

### 1.10 AJAX请求

```javascript
FR.ajax({
    url: "/webroot/decision/view/report",
    type: "GET",  // GET/POST
    data: { viewlet: "test.cpt", param1: "value1" },
    dataType: "json",
    async: true,
    timeout: 30000,
    success: function(data) { /* 处理数据 */ },
    error: function(xhr, status, error) { /* 错误处理 */ },
    complete: function() { /* 无论成功失败 */ }
});
```

### 1.11 工具类扩展

#### String扩展
| 方法 | 说明 | 示例 |
|------|------|------|
| `startWith(s)` | 前缀判断 | `"hello".startWith("he")` → true |
| `endWith(s)` | 后缀判断 | `"hello".endWith("lo")` → true |
| `replaceAll(s1, s2)` | 全部替换 | `"aabb".replaceAll("a","x")` → `"xxbb"` |
| `appendQuery(paras)` | URL加参数 | `"url".appendQuery({k:"v"})` → `"url?k=v"` |
| `getQuery(name)` | 获取URL参数 | |
| `allIndexOf(sub)` | 所有出现位置 | |
| `String.format(fmt, ...)` | 格式化 | `String.format("{0}+{1}",1,2)` → `"1+2"` |
| `String.leftPad(val, size, ch)` | 左补齐 | `String.leftPad("5",3,"0")` → `"005"` |

#### FR.Keys 全局按键
| 方法 | 说明 |
|------|------|
| `FR.Keys.reg(fn)` | 注册全局按键处理 |
| `FR.Keys.unreg(fn)` | 移除全局按键处理 |
| `FR.Keys.enable(state)` | 启用/禁用全局按键 |

---

