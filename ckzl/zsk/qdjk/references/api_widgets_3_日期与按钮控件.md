<!--
KB_INDEX: {
  "title": "FR控件JS API：日期与按钮控件（DatePicker/DateTimeEditor/FreeButton/FormSubmitButton）+ 继承总览",
  "stage": "frontend",
  "tags": [
    "JS API",
    "控件",
    "日期",
    "按钮"
  ],
  "keywords": [
    "FR.DatePicker",
    "FR.DateTimeEditor",
    "FR.FreeButton",
    "FR.FormSubmitButton",
    "日期选择器",
    "自由按钮",
    "查询按钮",
    "继承关系"
  ],
  "summary": "FR 10.0 控件 JS API 第 3/3 页：日期选择器 DatePicker（22 方法）、日期时间 DateTimeEditor（44 方法）、自由按钮 FreeButton（36 方法/8 配置项）、查询提交按钮 FormSubmitButton；附继承关系总览图与核心通用方法速查（所有控件可用）"
}
-->

> 数据来源：http://dev.fanruan.com/jsdoc/
> 抓取日期：2026-08-04
> 说明：方法清单包含继承自父类的方法，"来源"列标注了方法定义所在的类（对应 Jsdoc 的 "Defined By"）。
> 🧪 **2026-09-04 实测标注说明**：文中的 `> [2026-09-04 实测]` 批注块是 L6 泳道在 FR10 真实页面（localhost:8075，Playwright 实测）逐条验证的结论（✅与文档一致 / ⚠有差异 / ❌不可用 / ⏭未实调），119 条断言汇总与替代写法见 [verified_20260904.md](verified_20260904.md)；原 JSDoc 内容未作任何删改。

> 本页为原 api_widgets.md（1083 行）第 3/3 页（2026-09-29 拆分）；基类与文本编辑器见 [api_widgets_1_基类与文本数字编辑器.md](api_widgets_1_基类与文本数字编辑器.md)，下拉/复选控件见 [api_widgets_2_下拉框与复选控件.md](api_widgets_2_下拉框与复选控件.md)，总导航见 [api_widgets.md](api_widgets.md)。

---

## 9. FR.DatePicker（日期选择器）

直接展示的日期控件（注意：这个类直接继承自 Widget，不走 BaseEditor/TriggerEditor 链）。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.DatePicker
```

### FILES
`widget.datepicker.js`

### 示例
```javascript
var $anchor = $('<div>').css({
    position:'absolute', top:5, left:5, width:300, height:300
}).appendTo('body');
var picker = new FR.DatePicker({
    renderEl : $anchor,
    format : 'yyyy-MM-dd',
    viewMode : 0
});
```
> [2026-09-04 实测] ✅ `new FR.DatePicker` 文档示例实测可实例化（详见 verified_20260904.md，WD14）

### Config options（共 1 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `options` | `JSON` | FR.DatePicker | 配置属性 |

### Properties（共 1 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |

### Methods（共 22 个）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `couldUsedAsEditor` | `()` | `Boolean` | 控件能否在填报中用做编辑器 | FR.Widget |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 | FR.Widget |
| `doResize` | `([give])` | — | 重新设置控件的大小和位置 | FR.Widget |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getText` | `()` | `String` | 获取控件的显示值 | FR.Widget |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `Object` | 获取控件的实际值 | FR.Widget |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `reset` | `()` | — | 恢复控件到初始状态 | FR.Widget |
| `setEnable` | `(enable)` | — | 设置控件的可用性 | FR.Widget |
| `setSource` | `(source)` | — | 设置控件的初始值 | FR.Widget |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.Widget |
| `setValue` | `(value, shouldFireEvent)` | — | 设置控件的值 | FR.Widget |
| `setVisible` | `(visible)` | — | 设置控件的可见性 | FR.Widget |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |

---

## 10. FR.DateTimeEditor（日期时间控件）

日期（时间）控件，带下拉触发按钮。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.BaseEditor
            └─ FR.TriggerEditor
                 └─ FR.BaseDateTimeEditor
                      └─ FR.DateTimeEditor
```

### FILES
`widget.datetime.js`

### 示例
```javascript
var $div = $('<div style="position:absolute;left:20px;top:20px;width:400px;height:400px">').appendTo('body');
var editor = new FR.DateTimeEditor({
    renderEl : $div,
    format : 'yyyy-MM-dd',       // 日期格式
    startDate : "2010-08-08",    // 起始日期
    endDate : "2010-10-10",      // 结束日期
    editable : true,             // 是否允许手动输入日期
    value : "2010-10-01"
});
```

### Config options（共 3 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `width` | `Number` | FR.TriggerEditor | 控件的宽度 |
| `height` | `Number` | FR.TriggerEditor | 控件的高度 |
| `options` | `JSON` | FR.DateTimeEditor | 属性配置 |

### Properties（共 2 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `PluginRegex` | `Array` | FR.BaseEditor | 正则表达式控件插件接口 |
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |

### Methods（共 44 个）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `addContent2Element` | `()` | — | 添加内容 | FR.TriggerEditor |
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 | FR.BaseEditor |
| `collapse` | `()` | — | 收起下拉列表 | FR.TriggerEditor |
| `collapseIf` | `(e)` | — | 鼠标下拉框外点击，收起下拉框 | FR.TriggerEditor |
| `couldUsedAsEditor` | `()` | `Boolean` | 控件能否在填报中用做编辑器 | FR.Widget |
| `createDependencePara4Data` | `()` | `Object` | 数据联动，生成参数依赖 | FR.BaseEditor |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 | FR.Widget |
| `doResize` | `(give)` | — | 重新设置控件的大小和位置 | FR.TriggerEditor |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `getArrowIconHeight` | `()` | `number` | 获取下拉箭头图标的高度 | FR.DateTimeEditor |
| `getDefaultSupportFormat` | `()` | `Array` | 获取默认支持的显示格式（手动输入时识别这几种并转化成设定格式） | FR.BaseDateTimeEditor |
| `getDependenceObj` | `()` | `Object` | 数据联动，获取联动数据 | FR.BaseEditor |
| `getErrorMsg` | `()` | `String` | 获取错误提示内容 | FR.BaseEditor |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getText` | `()` | `String` | 获取控件的显示值 | FR.Widget |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `Object` | 获取控件的实际值 | FR.DateTimeEditor |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isExpanded` | `()` | `Boolean` | 下拉列表是否展开 | FR.TriggerEditor |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isSupportDatabinding` | `()` | `Boolean` | 判断是否支持数据绑定 | FR.BaseEditor |
| `isValidate` | `(cValue)` | `boolean` | 校验值是否符合控件的值规范 | FR.BaseDateTimeEditor |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `loadData` | `()` | — | 加载数据 | FR.BaseEditor |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `onTriggerClick` | `(e)` ⚑抽象 | — | 下拉按钮触发事件，抽象方法，具体控件需实现 | FR.DateTimeEditor |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `recoveryValue` | `()` | — | 还原到之前的值 | FR.BaseDateTimeEditor |
| `reset` | `()` | — | 恢复控件到初始状态 | FR.DateTimeEditor |
| `setEnable` | `(arg)` | — | 设置控件的可用性 | FR.TriggerEditor |
| `setEndDate` | `(ed)` | — | 设置结束日期 | FR.BaseDateTimeEditor |
| `setIcon` | `(cls)` | — | 仅支持通过 class 来设置图标 | FR.TriggerEditor |
| `setSource` | `(source)` | — | 设置控件的初始值 | FR.Widget |
| `setStartDate` | `(sd)` | — | 设置起始日期 | FR.BaseDateTimeEditor |
| `setStartOrEndDate` | `(s, date)` | — | 设置起始和结束日期 | FR.BaseDateTimeEditor |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.BaseDateTimeEditor |
| `setValue` | `(value, shouldFireEvent)` | — | 设置控件的值 | FR.Widget |
| `setVisible` | `(visible)` | — | 设置控件的可见性 | FR.Widget |
| `startEditing` | `()` | — | 开始编辑 | FR.TriggerEditor |
| `stopEditing` | `()` | — | 结束编辑 | FR.TriggerEditor |
| `store` | `()` | — | 保存数据绑定的数据 | FR.BaseEditor |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
> [2026-09-04 实测] ✅ `setStartDate` 实测可用（详见 verified_20260904.md，WD15）
> [2026-09-04 实测] ✅ `setEndDate` 实测可用（详见 verified_20260904.md，WD15）
> [2026-09-04 实测] ✅ `setStartOrEndDate` 返回 true（详见 verified_20260904.md，WD15）
> [2026-09-04 实测] ✅ `getDefaultSupportFormat` 实测返回 12 种支持格式（yyyy-MM-dd 系 + 时间戳系）（详见 verified_20260904.md，WD15）

---

## 11. FR.FreeButton（自由按钮）

自定义按钮，分别使用不同的图片表示按钮的各种状态。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.BaseEditor
            └─ FR.FreeButton
```

### FILES
`widget.button.js`

### 示例
```javascript
var btn = new FR.FreeButton({
    renderEl : 'body',
    width : 200,
    height : 100,
    icon : {
        background : ""
    }
});
```

### Config options（共 8 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `color` | `String` | FR.FreeButton | 文字颜色 |
| `decoration` | `String` | FR.FreeButton | 文字的修饰 |
| `fontfamily` | `String` | FR.FreeButton | 字体类型 |
| `fontsize` | `Number` | FR.FreeButton | 字体大小 |
| `fontstyle` | `String` | FR.FreeButton | 字体的样式 |
| `fontweight` | `Number` | FR.FreeButton | 字体的粗细 |
| `hotkeys` | `String` | FR.FreeButton | 快捷键 |
| `options` | `JSON` | FR.Widget | 配置属性 |

### Properties（共 4 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `$img` | `jQuery` | FR.FreeButton | 用于显示按钮图标的 dom 元素 |
| `PluginRegex` | `Array` | FR.BaseEditor | 正则表达式控件插件接口 |
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |
| `text` | `jQuery` | FR.FreeButton | 用于显示按钮文字的 dom 元素 |

### Methods（共 36 个）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 | FR.BaseEditor |
| `couldUsedAsEditor` | `()` | `Boolean` | 控件能否在填报中用做编辑器 | FR.Widget |
| `createDependencePara4Data` | `()` | `Object` | 数据联动，生成参数依赖 | FR.BaseEditor |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 | FR.Widget |
| `doResize` | `(give)` | — | 重新设置控件的大小和位置 | FR.FreeButton |
| `fireDown` | `()` | — | 鼠标按下事件 | FR.FreeButton |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `fireOut` | `()` | — | 鼠标离开事件 | FR.FreeButton |
| `fireOver` | `()` | — | 鼠标悬浮事件 | FR.FreeButton |
| `fireUp` | `()` | — | 鼠标松开事件 | FR.FreeButton |
| `getDependenceObj` | `()` | `Object` | 数据联动，获取联动数据 | FR.BaseEditor |
| `getErrorMsg` | `()` | `String` | 获取错误提示内容 | FR.BaseEditor |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getText` | `()` | `String` | 获取控件的显示值 | FR.Widget |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `Object` | 获取控件的实际值 | FR.FreeButton |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isSupportDatabinding` | `()` | `Boolean` | 判断是否支持数据绑定 | FR.BaseEditor |
| `isValidate` | `(cValue)` | `boolean` | 校验值是否符合控件的值规范 | FR.BaseEditor |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `loadData` | `()` | — | 加载数据 | FR.BaseEditor |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `reset` | `()` | — | 恢复控件到初始状态 | FR.Widget |
| `setBackground` | `(img)` | — | 设置按钮的背景图片 | FR.FreeButton |
| `setEnable` | `(arg)` | — | 设置控件的可用性 | FR.FreeButton |
| `setSource` | `(source)` | — | 设置控件的初始值 | FR.Widget |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.Widget |
| `setValue` | `(value)` | — | 设置控件的值 | FR.FreeButton |
| `setVisible` | `(visible)` | — | 设置控件的可见性 | FR.Widget |
| `store` | `()` | — | 保存数据绑定的数据 | FR.BaseEditor |
| `switchDown` | `()` | — | 开关事件 | FR.FreeButton |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
> [2026-09-04 实测] ✅ `fireOver` 触发无异常（详见 verified_20260904.md，WD16）
> [2026-09-04 实测] ✅ `fireOut` 触发无异常（详见 verified_20260904.md，WD16）
> [2026-09-04 实测] ✅ `fireDown` 触发无异常（详见 verified_20260904.md，WD16）
> [2026-09-04 实测] ✅ `fireUp` 触发无异常（详见 verified_20260904.md，WD16）
> [2026-09-04 实测] ✅ `setBackground` 实测可用（详见 verified_20260904.md，WD16）
> [2026-09-04 实测] ✅ `switchDown` 触发无异常（getValue 返回 ' '）（详见 verified_20260904.md，WD16）

---

## 12. FR.FormSubmitButton（查询/提交按钮）

参数查询控件。

### HIERARCHY（继承链）
（文档未显示继承关系）

### FILES
`widget.button.js`

### 说明
此页面对应的 Jsdoc 条目非常简略，**没有列出任何 Config options、Properties 或 Methods**。它仅作为"参数查询控件"的占位说明存在。实际功能通常通过其父类 FR.Button / FR.Widget 的事件机制（`on('click', fn)`）实现。
> [2026-09-04 实测] ✅ `FR.FormSubmitButton` typeof 实测 'function' 存在；文档自认无方法表，实际用 on('click') 事件机制（详见 verified_20260904.md，WD17）

---

## 附：继承关系总览图

```
FR.OB  (事件系统: on/once/un/fireEvent/purgeListeners)
  │
  └─ FR.Widget  (控件基类: getValue/setValue/setText/getText/setEnabled/setVisible/reset/destroy...)
       │
       ├─ FR.DatePicker                    (日期选择器, 直接展示)
       │
       └─ FR.BaseEditor  (编辑器基类: checkValid/getErrorMsg/isValidate/loadData/store/isSupportDatabinding)
            │
            ├─ FR.EditComp  (文本编辑: selectText)
            │    └─ FR.TextEditor  → FR.Password, FR.TextArea
            │    └─ FR.NumberEditor
            │
            ├─ FR.FreeButton  (自由按钮: fireOver/fireOut/fireDown/fireUp/setBackground/switchDown)
            │
            ├─ FR.SynchronBaseEditor  (getTreeTrace, parseTo2DArray)
            │    └─ FR.ToggleButtonGroup  (doResize, setEnable, setSource, reset)
            │         └─ FR.CheckBoxGroup  → FS.FSCheckBoxGroup
            │
            └─ FR.TriggerEditor  (触发器基类: collapse/expand/isExpanded/startEditing/stopEditing/setIcon/onTriggerClick[抽象])
                 │
                 ├─ FR.BaseComboBoxEditor  (clearText, getSelectedIndex, setSource, recoveryValue, shouldReBuildList...)
                 │    └─ FR.ComboBoxEditor  (getData, rebuild, addData2View, expand, isFiltering...)
                 │         └─ FR.CheckBoxEditor  (doSelectAll, deSelectAll, modifyPosition...)
                 │
                 └─ FR.BaseDateTimeEditor  (setStartDate, setEndDate, setStartOrEndDate, getDefaultSupportFormat...)
                      └─ FR.DateTimeEditor
```

---

## 附：核心通用方法速查（所有控件都可用）

以下方法来自 FR.OB / FR.Widget，几乎所有控件都继承可用：

| 方法 | 用途 |
|------|------|
| `on(eventName, fn)` | 绑定事件 |
| `once(eventName, fn)` | 绑定一次性事件 |
| `un(eventName, fn)` | 解绑事件 |
| `fireEvent(eventName)` | 触发事件 |
| `purgeListeners()` | 清除所有事件 |
| `getValue()` | 获取实际值 |
| `setValue(value)` | 设置实际值 |
| `getText()` | 获取显示值 |
| `setText(text)` | 设置显示值 |
| `getName()` | 获取控件名 |
| `getType()` | 获取控件类型 |
| `getWidgetByName(name)` | 获取子控件 |
| `isEnabled()` | 是否可用 |
| `setEnable(bool)` | 设置可用性 |
| `isVisible()` | 是否可见 |
| `setVisible(bool)` | 设置可见性 |
| `reset()` | 重置到初始状态 |
| `destroy()` | 销毁控件 |
| `doResize([give])` | 重新设置大小位置 |
| `setSource(source)` | 设置初始值（数据绑定场景） |

---

*文档结束。共覆盖 12 个类，合计记录约 350+ 方法条目（含继承方法）。*
