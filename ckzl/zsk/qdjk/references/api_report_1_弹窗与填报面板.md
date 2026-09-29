<!--
KB_INDEX: {
  "title": "FR填报JS API：消息弹窗/对话框/填报面板（FR.Msg/Dialog/Window/WritePane）",
  "stage": "frontend",
  "tags": [
    "JS API",
    "填报",
    "弹窗",
    "WritePane"
  ],
  "keywords": [
    "FR.Msg",
    "FR.Dialog",
    "FR.Window",
    "FR.WritePane",
    "confirm",
    "showDialog",
    "verifyReport"
  ],
  "summary": "FR 10.0 填报核心 JS API 第 1/2 页：FR.Msg（confirm/alert/prompt/toast 4 静态方法）、FR.Dialog 与 FR.Window（对话框属性/方法）、FR.WritePane 填报面板（1 属性 + 41 方法：提交/校验/单元格取值赋值等）——原 api_report.md §1-§3"
}
-->

> 抓取自 http://dev.fanruan.com/jsdoc/ (JsDuck 生成)，覆盖 FR 报表填报开发最常用的 8 个类。
> 每个类按"继承关系 → Config/Properties → Methods"组织，方法表包含方法名、参数、返回值与中文描述。
> 🧪 **2026-09-04 实测标注说明**：文中的 `> [2026-09-04 实测]` 批注块是 L6 泳道在 FR10 真实页面（localhost:8075，Playwright 实测）逐条验证的结论（✅与文档一致 / ⚠有差异 / ❌不可用 / ⏭未实调），119 条断言汇总与替代写法见 [verified_20260904.md](verified_20260904.md)；原 JSDoc 内容未作任何删改。

> 本页为原 api_report.md（653 行）第 1/2 页（2026-09-29 拆分），对应原 §1-§3；报表面板与填报接口（§4-§8+附录）见 [api_report_2_报表面板与填报接口.md](api_report_2_报表面板与填报接口.md)，总导航见 [api_report.md](api_report.md)。

---

## 1. FR.Msg（消息弹窗 confirm/alert/prompt/toast）

**HIERARCHY**: 无（独立静态类）
**FILES**: `jquery.message.js`
**说明**: 自定义用于消息传递的模态对话框类，用于替代浏览器原生（比较丑的）`alert`、`prompt`、`confirm`。
**Since**: 6.5.3

### Static Methods（4 个，均为静态方法 STATIC）

| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `alert` | `(title, message, callback)` | — | 弹出消息提示对话框 |
| `confirm` | `(title, message, callback)` | — | 弹出确认对话框，`callback` 在用户点击确定时执行。⚠️ **只传 3 个参数**，`min_width` 是文档误标（传第 4 参数会 `SyntaxError: missing ) after argument list`，2026-08-07 实测） |
| `prompt` | `(title, message, value, callback, min_width)` | — | 弹出输入对话框，`value` 为输入框默认值 |
| `toast` | `(message)` | — | 在页面左侧出现并在 5 秒后消失的提示 |
> [2026-09-04 实测] ✅ `FR.Msg.toast` 已调用且 DOM 出现 3 个 toast 类节点、5 秒自动消失（详见 verified_20260904.md，MSG01/MSG02）
> [2026-09-04 实测] ❌ `FR.Msg.alert` 本构建静默无效：无头+有头双验均 0 个 .fr-core-window、回调不触发、无 JS 异常；用 new FR.Dialog 自绘（DLG01 已验证）或 toast 替代（详见 verified_20260904.md，MSG03R2）
> [2026-09-04 实测] ❌ `FR.Msg.confirm` 同 alert 静默无效（双验 0 窗口、回调不触发）；替代同上（详见 verified_20260904.md，MSG05R2）
> [2026-09-04 实测] ❌ `FR.Msg.prompt` 同 alert 静默无效（双验 0 窗口、回调不触发）；替代同上（详见 verified_20260904.md，MSG07R2）

**示例**:
```js
FR.Msg.toast("Hello");
FR.Msg.confirm("Confirm", "Content", showToast);
FR.Msg.prompt("Prompt", "Message", "Value", showConfirm);
FR.Msg.alert("Alert", "Content", showPrompt);
```

---

## 2. FR.Dialog（对话框）/ FR.Window（窗体）

### 2.1 FR.Dialog

**HIERARCHY**:
```
FR.OB
└─ FR.Widget
   └─ FR.Window
      └─ FR.Dialog
```
**FILES**: `widget.container.js`
**说明**: 对话框。可以同时显示多个对话框，但只有最上层的处于活跃状态。
**Since**: 6.5.3

#### Config options (1)
| 选项 | 类型 | 定义于 | 描述 |
|---|---|---|---|
| `options` | JSON | FR.Window | 配置属性 |

#### Properties (1)
| 属性 | 类型 | 定义于 | 描述 |
|---|---|---|---|
| `element` | jQuery | FR.Widget | 控件的根节点元素 |

#### Methods (25)
| 方法 | 参数 | 返回值 | 定义于 | 描述 |
|---|---|---|---|---|
| `couldUsedAsEditor` | `()` | Boolean | FR.Widget | 控件能否在填报中用做编辑器 |
| `destroy` | `()` | — | FR.Widget | 销毁整个控件的 dom 结构 |
| `doClose` | `()` | — | FR.Window | 关闭窗体 |
| `doResize` | `([give])` | — | FR.Widget | 重新设置控件的大小和位置 |
| `fireEvent` | `(eventName)` | Boolean | FR.OB | 触发绑定过的事件 |
| `getName` | `()` | Object | FR.Widget | 获取控件名字 |
| `getText` | `()` | String | FR.Widget | 获取控件的显示值 |
| `getType` | `()` | — | FR.Widget | 获取控件类型 |
| `getValue` | `()` | Object | FR.Widget | 获取控件的实际值 |
| `getWidgetByName` | `(name)` | FR.Widget | FR.Widget | 获取该控件中所添加的子控件 |
| `isEnabled` | `()` | Boolean | FR.Widget | 判断控件是否可用 |
| `isStringTypeNumber` | `(o)` | Boolean | FR.Widget | 判断 "24" 这种字符串形式的数字 |
| `isVisible` | `()` | Boolean | FR.Widget | 判断控件是否可见 |
| `on` | `(eventName, fn)` | — | FR.OB | 给观察者绑定一个事件 |
| `once` | `(eventName, fn)` | — | FR.OB | 给观察者绑定一个只执行一次的事件 |
| `purgeListeners` | `()` | — | FR.OB | 清除观察者的所有事件绑定 |
| `reset` | `()` | — | FR.Widget | 恢复控件到初始状态，一般用于重新取值 |
| `setContent` | `(c)` | — | FR.Window | 设置窗体的显示内容 |
| `setEnable` | `(enable)` | — | FR.Widget | 设置控件的可用性 |
| `setSource` | `(source)` | — | FR.Widget | 设置控件的初始值（数据绑定时动态加载） |
| `setText` | `(text)` | — | FR.Widget | 设置控件的显示值 |
| `setTitle` | `(title)` | — | FR.Window | 设置窗体的标题文本 |
| `setValue` | `(value, shouldFireEvent)` | — | FR.Widget | 设置控件的值 |
| `setVisible` | `(visible)` | — | FR.Widget | 设置控件的可见性 |
| `un` | `(eventName, fn)` | — | FR.OB | 解除观察者绑定的指定事件 |
> [2026-09-04 实测] ✅ `setTitle` 实测改题 L6Dialog-2 生效（详见 verified_20260904.md，DLG02）
> [2026-09-04 实测] ❌ `setContent` 构造后调用不生效（首次与重新 setVisible 后均 false）；用构造参数 contentHtml 一次性给内容（已验证）（详见 verified_20260904.md，DLG03R2）
> [2026-09-04 实测] ❌ `doClose` 语义与文档不符：调用后根节点仍 display=block 可见（DOM 留存）；用 setVisible(false) 关显示或 element.remove() 移节点（详见 verified_20260904.md，DLG04R2）
> [2026-09-04 实测] ✅ `setVisible` 与构造配合实测可用（window=1、内容挂载成功）（详见 verified_20260904.md，DLG01）

**示例**:
```js
var dlg = new FR.Dialog({
    title: 'Dialog',
    height: 100,
    contentHtml: '<p>Hello Dialog!</p>'
});
dlg.setVisible(true);
```
> [2026-09-04 实测] ✅ `new FR.Dialog` 文档示例构造（title/contentHtml + setVisible(true)）实测可用（详见 verified_20260904.md，DLG01）

### 2.2 FR.Window（Dialog 的父类）

**HIERARCHY**:
```
FR.OB
└─ FR.Widget
   └─ FR.Window
```
**SUBCLASSES**: `FR.Dialog`
**FILES**: `widget.container.js`
**说明**: 窗体控件。
**Since**: 6.5.3

#### Config options (1)
| 选项 | 类型 | 描述 |
|---|---|---|
| `options` | JSON | 配置属性 |

#### Properties (1)
| 属性 | 类型 | 描述 |
|---|---|---|
| `element` | jQuery | 控件的根节点元素 |

#### Methods (25)
（与 FR.Dialog 完全一致，因为 Dialog 的方法全部继承自 Window/Widget/OB，本身无新增方法。）

Window/Dialog 自身方法（非继承自 Widget/OB）：
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `doClose` | `()` | — | 关闭窗体 |
| `setContent` | `(c)` | — | 设置窗体的显示内容 |
| `setTitle` | `(title)` | — | 设置窗体的标题文本 |

其余 22 个方法继承自 FR.Widget / FR.OB（详见上表）。

---

## 3. FR.WritePane（填报面板）

**HIERARCHY**: 无明确继承声明（直接定义）
**FILES**: `write.js`
**说明**: 填报表页面内容容器，即填报预览中的 `contentPane` 对象。
> [2026-09-04 实测] ✅ `window.contentPane` op=write 填报页实测存在（详见 verified_20260904.md，WR01）

### Properties (1)
| 属性 | 类型 | 描述 |
|---|---|---|
| `onbeforeunload` | Object | 页面转向时提示（不支持 opera） |
> [2026-09-04 实测] ⚠ `onbeforeunload` dirty=true 时 beforeUnloadCheck 函数存在，但页面未挂 onbeforeunload（hasOnbu=false）——需要离开提示的模板须在模板里开启 UnloadCheck（详见 verified_20260904.md，WR27R2）

### Methods (41)

**填报入库 / 校验类**

| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `writeReport` | `(reportIndex, submitButton, successFn, failFn)` | Boolean | 填报入库。`reportIndex`=sheet 序号；成功/失败回调 |
| `verifyAndWriteReport` | `(isAllSheet, submitButton, successFn, failFn)` | Boolean | 校验并提交修改数据（服务器端写死调用） |
| `verifyReport` | `(btn, reportIndex)` | — | 数据校验 |
| `writeAndVerifyReport` | `(isAllSheet)` | — | **@Deprecated** 名字太差，不再推荐；请用 `writeReportIgnoreVerify` |
| `writeReportIgnoreVerify` | `(isAllSheet)` | — | 忽略校验出错信息直接提交（705 前只提交当前 sheet，后改为提交全部 sheet） |
| `isDirtyPage` | `()` | Boolean | 判断是否有未提交数据 |
| `beforeUnloadCheck` | `()` | String | 离开页面时，若有 dirty 数据，提示用户是否离开 |
> [2026-09-04 实测] ✅ `verifyReport` 已调用（只读校验，不落库）（详见 verified_20260904.md，WR22）
> [2026-09-04 实测] ✅ `isDirtyPage` 编辑格写入后实测 true（详见 verified_20260904.md，WR06R2）
> [2026-09-04 实测] ⏭ `writeReport` 会真实提交入库，本夜未实调（落库风险）（详见 verified_20260904.md，WR29）
> [2026-09-04 实测] ⏭ `verifyAndWriteReport` 同 writeReport 真实提交，未实调；验证场景用 verifyReport 替代（详见 verified_20260904.md，WR30）
> [2026-09-04 实测] ⏭ `writeReportIgnoreVerify` 同 writeReport 真实提交，未实调（详见 verified_20260904.md，WR30）
> [2026-09-04 实测] ⚠ `beforeUnloadCheck` 函数存在，但生效前提是模板开启 UnloadCheck（见上方 Properties 批注）（详见 verified_20260904.md，WR27R2）

**单元格取值/赋值类**

| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `getCellValue` | `(o)` | `*` | 获取单元格的值。`o` 可为 `{reportIndex, columnIndex, rowIndex}` 或多参数形式 ⚠仅填报预览（`op=write`）生效；不支持移动端（App/H5 白屏）；坐标列号从 0 开始（来源 doc-1207） |
| `setCellValue` | `(o)` | — | 给单元格赋值。`o` 可为 `{reportIndex, rowIndex, columnIndex, value}` 或多参数形式 ⚠仅填报预览（`op=write`）生效；不支持移动端（来源 doc-1207） |
| `getWidgetByCell` | `(cell)` | FR.Widget | 根据单元格编号获取控件 |
| `getWidgetByName` | `(name)` | FR.Widget | 根据名字获取单个控件（同名取最后一个） |
| `getWidgetsByName` | `(name)` | Array | 根据名字获取控件数组 |
| `writeCellValue` | `(tdCell)` | — | 写入 tdCell 的值 |
> [2026-09-04 实测] ✅ `getCellValue` 三种形式全通：对象 {reportIndex,columnIndex,rowIndex}、两参 (col,row)、三参 (r,i,row)；坐标 0 基（详见 verified_20260904.md，WR02/03/04）
> [2026-09-04 实测] ⚠ `setCellValue` 编辑格（控件所在格）写入生效且 isDirtyPage→true；静态格两轮结论不一致（WR05 FAIL vs WR05R2 PASS），保守按仅可编辑格可靠使用；写入仅内存不提交不落库（详见 verified_20260904.md，WR05/WR05R2）
> [2026-09-04 实测] ⚠ `getWidgetByCell` 真实签名只收 'C6' 形式字符串（列字母+1基行号），传数字抛 str.match is not a function；返回控件本体支持 setValue/getValue/setEnable/setVisible/isDirty 全套（WR10/11/12 电池通过）（详见 verified_20260904.md，WR07R2/32）
> [2026-09-04 实测] ⚠ `getWidgetByName` 匿名控件查不到；替代 getWidgetByCell('C6')，参数面板有名控件用 parameterEl.getWidgetByName（详见 verified_20260904.md，WR08R2）
> [2026-09-04 实测] ✅ `getWidgetsByName` 方法存在（详见 verified_20260904.md，WR09R2）

**插入/删除行类**

| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `appendReportRC` | `(count, cell)` | — | 工具栏增加记录（行）。`count`=行数，`cell`=格子位置（一般不传，用当前焦点格） |
| `appendReportRow` | `(location, reportIndex, count)` | — | 插入行按钮使用的插入行方法（依赖插入行按钮）。`location`=按钮位置，`reportIndex`=sheet 序号，`count`=行数 |
| `appendRows` | `()` | — | 增加记录 |
| `deleteReportRC` | `(cell)` | — | 工具栏删除记录。`cell`=删除位置（一般不传，用当前焦点格） |
| `deleteReportRow` | `(location, reportIndex, count)` | — | 删除行按钮使用的删除行方法。`location`=按钮位置，`reportIndex`=sheet 序号，`count`=行数（传不传都是删 1 行） |
| `deleteRows` | `()` | — | 删除记录 |
> [2026-09-04 实测] ⚠ `appendReportRC` 非行式模板实测行数不变（9→9）；行式填报模板待补测（详见 verified_20260904.md，WR28R2）
> [2026-09-04 实测] ⚠ `deleteReportRC` 同上，非行式模板无效（9→9）（详见 verified_20260904.md，WR28R2）

**编辑控制类**

| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `stopEditing` | `()` | — | 停止编辑当前单元格 |
| `setEditOnClick` | `(editOnClick)` | — | 提供接口实现单击就进入编辑 |
| `setEditOnMove` | `(editOnMove)` | — | 提供接口实现按键切换格子立即进入编辑 |
| `setFireStopEditOnChange` | `(fireOnChange)` | — | 编辑结束事件是否需要控件值改变才触发 |
> [2026-09-04 实测] ✅ `stopEditing` 实测无异常（详见 verified_20260904.md，WR20）
> [2026-09-04 实测] ✅ `setEditOnClick` 实测无异常（保持默认语义）（详见 verified_20260904.md，WR21）
> [2026-09-04 实测] ✅ `setEditOnMove` 实测无异常（保持默认语义）（详见 verified_20260904.md，WR21）
> [2026-09-04 实测] ✅ `setFireStopEditOnChange` 实测无异常（保持默认语义）（详见 verified_20260904.md，WR21）

**打印类**

| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `flashPrint` | `()` | — | flash 打印 |
| `appletPrint` | `()` | — | applet 打印 |
| `printReportServer` | `()` | — | 服务器端打印 |
| `SetPrinterOffset` | `()` | — | 设置打印偏移 |
> [2026-09-04 实测] ✅ `flashPrint` 方法存在；实调会开打印对话框/装插件故未实调（详见 verified_20260904.md，WR25）
> [2026-09-04 实测] ✅ `appletPrint` 方法存在（未实调，同上）（详见 verified_20260904.md，WR25）
> [2026-09-04 实测] ✅ `printReportServer` 方法存在（未实调，同上）（详见 verified_20260904.md，WR25）
> [2026-09-04 实测] ✅ `SetPrinterOffset` 方法存在（未实调，同上）（详见 verified_20260904.md，WR25）

**导出类**

| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `exportReportToExcel` | `(extype, sheets)` | — | 导出 Excel。`extype`='simple'(原样)/'page'(分页)；`sheets`=导出 sheet 序号数组 |
| `exportReportToPDF` | `(extype)` | — | 导出 PDF |
| `exportReportToWord` | `()` | — | 导出 Word |
| `exportReportToImage` | `(extype)` | — | 导出图片。`extype`='png' 等 |
| `exportReportToHtml` | `()` | — | 导出 HTML |
| `exportReportToOffineHtml` | `()` | — | 将报表导出为离线 HTML |
| `exportReportToWriteOfflineHtml` | `()` | — | 导出离线填报报表 |
| `emailReport` | `()` | — | 发送邮件 |
> [2026-09-04 实测] ✅ `exportReportToExcel` 'simple' 原样导出实触发下载成功（suggested=FS_Comments填报.xlsx）（详见 verified_20260904.md，WR24/WR31）
> [2026-09-04 实测] ✅ `exportReportToPDF` 方法存在（详见 verified_20260904.md，WR24）
> [2026-09-04 实测] ✅ `exportReportToWord` 方法存在（详见 verified_20260904.md，WR24）
> [2026-09-04 实测] ✅ `exportReportToImage` 方法存在（详见 verified_20260904.md，WR24）
> [2026-09-04 实测] ✅ `exportReportToHtml` 方法存在（详见 verified_20260904.md，WR24）
> [2026-09-04 实测] ✅ `exportReportToOffineHtml` 方法存在（详见 verified_20260904.md，WR24）
> [2026-09-04 实测] ❌ `exportReportToWriteOfflineHtml` 文档声称存在，FR10 实例实测 typeof=false 不存在——文档与实际不符（详见 verified_20260904.md，WR24）
> [2026-09-04 实测] ✅ `emailReport` 方法存在（详见 verified_20260904.md，WR24）

**Excel 导入 / 刷新类**

| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `importExcel` | `()` | — | Excel 导入 |
| `initExcelButton` | `(button)` | — | 初始化 Excel 导入按钮 |
| `refreshAllSheets` | `()` | — | 更新所有 sheet |
| `refreshWidgets` | `()` | — | （私有方法）刷新控件 |
| `reCalCurLGPPane` | `()` | — | 当前 sheet 重新计算 |
| `reloadCurLGPPane` | `(fec)` | — | 单 sheet 的 reload；`fec`=reload 后一开始 select 的格子 |
> [2026-09-04 实测] ✅ `importExcel` 方法存在；实调会开文件选择框故未实调（详见 verified_20260904.md，WR26）
> [2026-09-04 实测] ✅ `initExcelButton` 方法存在（未实调，同上）（详见 verified_20260904.md，WR26）
> [2026-09-04 实测] ✅ `refreshAllSheets` 存在（详见 verified_20260904.md，WR23）
> [2026-09-04 实测] ✅ `reCalCurLGPPane` 存在（详见 verified_20260904.md，WR23）

**示例**:
```js
// 填报入库第一个 sheet
contentPane.writeReport(0, null, function(){alert("成功");}, function(){alert("失败");});

// 获取第一个 sheet 第二行第三列的值
contentPane.getCellValue({reportIndex:0, columnIndex: 2, rowIndex: 1});
contentPane.getCellValue(2, 1);
contentPane.getCellValue(0, 2, 1);

// 给第一个 sheet 第二行第三列赋值 'aa'
contentPane.setCellValue(2, 1, "aa");
contentPane.setCellValue({reportIndex:0, rowIndex:1, columnIndex:2, value:"aa"});

// 插入/删除行
contentPane.appendReportRow("B1", 0, 2);   // B1 插入 2 行
contentPane.deleteReportRow("C2", 0, 1);   // C2 删除 1 行

// 导出
contentPane.exportReportToExcel('simple');          // 原样导出
contentPane.exportReportToExcel('page', [1]);       // 分页导出第二个 sheet
contentPane.exportReportToImage('png');             // 导出 PNG
```

---

