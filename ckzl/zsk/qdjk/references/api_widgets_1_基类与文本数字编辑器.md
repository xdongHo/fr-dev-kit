<!--
KB_INDEX: {
  "title": "FR控件JS API：基类与文本/数字/触发编辑器（FR.OB/Widget/TextEditor/NumberEditor/TriggerEditor）",
  "stage": "frontend",
  "tags": [
    "JS API",
    "控件",
    "FR.OB",
    "FR.Widget",
    "TextEditor"
  ],
  "keywords": [
    "FR.OB",
    "FR.Widget",
    "FR.TextEditor",
    "FR.NumberEditor",
    "FR.TriggerEditor",
    "控件基类",
    "事件系统"
  ],
  "summary": "FR 10.0 控件 JS API 第 1/3 页：观察者基类 FR.OB（事件系统 5 方法）、控件基类 FR.Widget（22 方法：getValue/setValue/setVisible/setEnabled/reset 等）、文本框 TextEditor（32 方法）、数字框 NumberEditor（31 方法）、触发编辑器 TriggerEditor（39 方法，抽象）；含 HIERARCHY/SUBCLASSES/继承方法表与 2026-09-04 实测标注"
}
-->

> 数据来源：http://dev.fanruan.com/jsdoc/
> 抓取日期：2026-08-04
> 说明：方法清单包含继承自父类的方法，"来源"列标注了方法定义所在的类（对应 Jsdoc 的 "Defined By"）。
> 🧪 **2026-09-04 实测标注说明**：文中的 `> [2026-09-04 实测]` 批注块是 L6 泳道在 FR10 真实页面（localhost:8075，Playwright 实测）逐条验证的结论（✅与文档一致 / ⚠有差异 / ❌不可用 / ⏭未实调），119 条断言汇总与替代写法见 [verified_20260904.md](verified_20260904.md)；原 JSDoc 内容未作任何删改。

> 本页为原 api_widgets.md（1083 行）第 1/3 页（2026-09-29 拆分）；下拉/复选控件见 [api_widgets_2_下拉框与复选控件.md](api_widgets_2_下拉框与复选控件.md)，日期与按钮控件见 [api_widgets_3_日期与按钮控件.md](api_widgets_3_日期与按钮控件.md)，总导航见 [api_widgets.md](api_widgets.md)。

---

## 1. FR.OB（观察者基类 — 事件系统）

**抽象类**。客户端观察者，主要处理事件的添加、删除、执行等。所有控件的事件系统根基。

### HIERARCHY（继承链）
```
FR.OB  （顶层）
```

### SUBCLASSES（子类）
`FR.WLGP`、`FR.Widget`、`FR.Write`

### FILES
`jquery.observer.js`

### Methods（共 5 个，全部由 FR.OB 定义）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
> [2026-09-04 实测] ✅ `on` contentPane 与独立控件实测均可绑定，事件命中（详见 verified_20260904.md，CP15/WD18）
> [2026-09-04 实测] ✅ `once` 只执行一次语义验证通过（重复 fire 不重复执行）（详见 verified_20260904.md，CP15/WD18）
> [2026-09-04 实测] ✅ `un` 解绑后不再触发（详见 verified_20260904.md，CP15/WD18）
> [2026-09-04 实测] ✅ `fireEvent` 返回 true，事件链正常（详见 verified_20260904.md，CP15/WD18）
> [2026-09-04 实测] ✅ `purgeListeners` 清绑后无残留触发（详见 verified_20260904.md，CP15/WD18）

---

## 2. FR.Widget（控件基类）

**抽象类**，是所有控件的父类，不能直接使用，只能使用其具体的子类。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
```

### SUBCLASSES（子类）
`FR.BaseEditor`、`FR.BasePane`、`FR.Button`、`FR.DatePicker`、`FR.IconButton`、`FR.Layout`、`FR.Panel`、`FR.QuickButton`、`FR.QuickGrid`、`FR.SheetButton`、`FR.TabPane`、`FR.Toolbar`、`FR.Window`、`FS.Accordion`、`FS.ColorPicker`、`FS.FloatPane`、`FS.LTabPane`、`FS.ParameterGrid`、`FS.QuickTab`、`FS.SwitchButton`、`FS.TablePane`

### FILES
`jquery.widget.js`

### Config options（共 1 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `options` | `JSON` | FR.Widget | 配置属性 |

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
| `getText` | `()` | `String` | 获取控件的显示值，所有表单控件都应该实现这个方法 | FR.Widget |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `Object` | 获取控件的实际值 | FR.Widget |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式的字符串 | FR.Widget |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `reset` | `()` | — | 恢复控件到初始状态，一般用于重新取值 | FR.Widget |
| `setEnable` | `(enable)` | — | 设置控件的可用性 | FR.Widget |
| `setSource` | `(source)` | — | 设置控件的初始值，一般情况和 setValue 一样，在初始值为数据绑定的时候需要动态加载数据 | FR.Widget |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.Widget |
| `setValue` | `(value, shouldFireEvent)` | — | 设置控件的值 | FR.Widget |
| `setVisible` | `(visible)` | — | 设置控件的可见性 | FR.Widget |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
> [2026-09-04 实测] ✅ `couldUsedAsEditor` 查看页 contentPane 实测 false（详见 verified_20260904.md，CP07）
> [2026-09-04 实测] ✅ `getValue` 参数控件取值正常（详见 verified_20260904.md，PM03）
> [2026-09-04 实测] ✅ `getText` 参数控件 setText/getText 往返成功（详见 verified_20260904.md，PM03/PM07）
> [2026-09-04 实测] ✅ `getName` 参数控件实测 name=PARA_LEGAL（详见 verified_20260904.md，PM04）
> [2026-09-04 实测] ✅ `getType` combo 控件实测 type=combo、查看面板 type=page（详见 verified_20260904.md，PM04/CP03）
> [2026-09-04 实测] ❌ `getWidgetByName` cpt 查看页经 contentPane 调用实测 found=false 不可用；改用 contentPane.parameterEl.getWidgetByName（PM02 已验证）或填报页 getWidgetByCell('C6')（详见 verified_20260904.md，PM11R2/WR08R2）
> [2026-09-04 实测] ✅ `isEnabled` 实测 true，setEnable 禁用/恢复往返 false→true（详见 verified_20260904.md，PM05/PM08/CP06）
> [2026-09-04 实测] ⚠ `isStringTypeNumber` 校验比文档宽松：'24a' 亦返回 true，不能当严格数字格式校验用（详见 verified_20260904.md，CP08R2）
> [2026-09-04 实测] ✅ `isVisible` 实测 true，setVisible 隐藏/恢复往返（详见 verified_20260904.md，PM05/PM09/CP05）
> [2026-09-04 实测] ✅ `reset` 参数控件 reset 无异常（详见 verified_20260904.md，PM10）
> [2026-09-04 实测] ✅ `setEnable` 禁用/恢复往返验证通过（详见 verified_20260904.md，PM08）
> [2026-09-04 实测] ⚠ `setText` 往返成功；坑：编程赋值后立刻 parameterCommit 会抛 TypeError——延迟一拍或走查询按钮事件（详见 verified_20260904.md，PM07/PM14）
> [2026-09-04 实测] ⚠ `setValue` 参数 ComboBox 传待选列表外的值不生效（old/afterSet=undefined）；自动化填参走 URL 传参或 setText+查询（详见 verified_20260904.md，PM06R2）
> [2026-09-04 实测] ✅ `setVisible` 隐藏/恢复往返验证通过（详见 verified_20260904.md，PM09）

---

## 3. FR.TextEditor（文本框）

文本控件。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.BaseEditor
            └─ FR.EditComp
                 └─ FR.TextEditor
```

### SUBCLASSES（子类）
`FR.Password`、`FR.TextArea`

### FILES
`widget.plaineditor.js`

### 示例
```javascript
var editor = new FR.TextEditor({
    renderEl : 'body',
    value : 'Hello'
});
```
> [2026-09-04 实测] ✅ `new FR.TextEditor` 文档示例实测可实例化；renderEl 缺省也不抛错（详见 verified_20260904.md，WD01/WD19）

### Config options（共 1 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `options` | `JSON` | FR.TextEditor | 属性配置 |

### Properties（共 2 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `PluginRegex` | `Array` | FR.BaseEditor | 正则表达式控件插件接口，正则表达式类型数组 |
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |

### Methods（共 32 个）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 | FR.BaseEditor |
| `couldUsedAsEditor` | `()` | `Boolean` | 控件能否在填报中用做编辑器 | FR.Widget |
| `createDependencePara4Data` | `()` | `Object` | 数据联动，生成参数依赖 | FR.BaseEditor |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 | FR.Widget |
| `doResize` | `(give)` | — | 重新设置控件的大小和位置 | FR.EditComp |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `getDependenceObj` | `()` | `Object` | 数据联动，获取联动数据 | FR.BaseEditor |
| `getErrorMsg` | `()` | `String` | 获取错误提示内容 | FR.BaseEditor |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getText` | `()` | `String` | 获取控件的显示值 | FR.Widget |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `Object` | 获取控件的实际值 | FR.Widget |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isSupportDatabinding` | `()` | `Boolean` | 判断是否支持数据绑定 | FR.BaseEditor |
| `isValidate` | `(cValue)` | `boolean` | 校验值是否符合控件的值规范（只判断+设置 errorMsg，不改 CSS） | FR.BaseEditor |
| `isValidateInput` | `(e)` | `boolean\|*` | 判断是否是不符合规则的输入 | FR.TextEditor |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `loadData` | `()` | — | 加载数据 | FR.BaseEditor |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `reset` | `()` | — | 恢复控件到初始状态 | FR.Widget |
| `selectText` | `(start, end)` | — | 选取控件中的文本内容 | FR.EditComp |
| `setEnable` | `(arg)` | — | 设置控件的可用性 | FR.EditComp |
| `setSource` | `(source)` | — | 设置控件的初始值 | FR.Widget |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.Widget |
| `setValue` | `(value, shouldFireEvent)` | — | 设置控件的值 | FR.Widget |
| `setVisible` | `(visible)` | — | 设置控件的可见性 | FR.Widget |
| `store` | `()` | — | 保存数据绑定的数据 | FR.BaseEditor |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
> [2026-09-04 实测] ✅ `checkValid` 与 isValidate/getErrorMsg 一组校验电池通过（详见 verified_20260904.md，WD04）
> [2026-09-04 实测] ✅ `isValidate` 实测 true（合法值）（详见 verified_20260904.md，WD04）
> [2026-09-04 实测] ✅ `getErrorMsg` 实测空（无错误）（详见 verified_20260904.md，WD04）
> [2026-09-04 实测] ✅ `destroy` 销毁后子节点清空=true（详见 verified_20260904.md，WD05）
> [2026-09-04 实测] ✅ `getValue` 初始 'Hello' 读取一致（详见 verified_20260904.md，WD02）
> [2026-09-04 实测] ✅ `setText` 改 'L6x' 后读取一致（往返成功）（详见 verified_20260904.md，WD02）
> [2026-09-04 实测] ✅ `getText` 与 getValue 同步验证通过（详见 verified_20260904.md，WD02）
> [2026-09-04 实测] ✅ `selectText` selectText(0,1) 无异常（详见 verified_20260904.md，WD03）

---

## 4. FR.NumberEditor（数字框）

数字控件。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.BaseEditor
            └─ FR.EditComp
                 └─ FR.NumberEditor
```

### FILES
`widget.number.js`

### 示例
```javascript
var editor = new FR.NumberEditor({
    renderEl : 'body',
    allowDecimals : true,
    allowNegative : true,
    decimalPrecision : -1,
    autoVerify : true,
    decimalSeparator : ".",
    value : -233.455
});
```
> [2026-09-04 实测] ✅ `new FR.NumberEditor` 文档示例（value=-233.455 等）实测可实例化，初始值读回 -233.455（详见 verified_20260904.md，WD06）

### Config options（共 1 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `options` | `JSON` | FR.NumberEditor | 属性配置 |

### Properties（共 2 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `PluginRegex` | `Array` | FR.BaseEditor | 正则表达式控件插件接口 |
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |

### Methods（共 31 个）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 | FR.BaseEditor |
| `couldUsedAsEditor` | `()` | `Boolean` | 控件能否在填报中用做编辑器 | FR.Widget |
| `createDependencePara4Data` | `()` | `Object` | 数据联动，生成参数依赖 | FR.BaseEditor |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 | FR.Widget |
| `doResize` | `(give)` | — | 重新设置控件的大小和位置 | FR.NumberEditor |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `getDependenceObj` | `()` | `Object` | 数据联动，获取联动数据 | FR.BaseEditor |
| `getErrorMsg` | `()` | `String` | 获取错误提示内容 | FR.BaseEditor |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getText` | `()` | `String` | 获取控件的显示值 | FR.Widget |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `Object` | 取值：无值返回 `''`，输入 0 返回 `0` | FR.NumberEditor |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isSupportDatabinding` | `()` | `Boolean` | 判断是否支持数据绑定 | FR.BaseEditor |
| `isValidate` | `(cValue)` | `boolean` | 校验值是否符合控件的值规范 | FR.NumberEditor |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `loadData` | `()` | — | 加载数据 | FR.BaseEditor |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `reset` | `()` | — | 恢复控件到初始状态 | FR.Widget |
| `selectText` | `(start, end)` | — | 选取控件中的文本内容 | FR.EditComp |
| `setEnable` | `(arg)` | — | 设置控件的可用性 | FR.EditComp |
| `setSource` | `(source)` | — | 设置控件的初始值 | FR.Widget |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.Widget |
| `setValue` | `(value, shouldFireEvent)` | — | 设置控件的值 | FR.Widget |
| `setVisible` | `(visible)` | — | 设置控件的可见性 | FR.Widget |
| `store` | `()` | — | 保存数据绑定的数据 | FR.BaseEditor |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
> [2026-09-04 实测] ✅ `getValue` 无值返回 ''、输入 0 返回 0 的文档语义实测相符（init=-233.455、zero=0）（详见 verified_20260904.md，WD06）

---

## 5. FR.TriggerEditor（触发编辑器，抽象）

**抽象类**。带额外点击按钮的控件，所有带有下拉按钮的控件的父类。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.BaseEditor
            └─ FR.TriggerEditor
```

### SUBCLASSES（子类）
`FR.BaseComboBoxEditor`、`FR.BaseDateTimeEditor`

### FILES
`widget.triggereditor.js`

### Config options（共 3 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `width` | `Number` | FR.TriggerEditor | 控件的宽度 |
| `height` | `Number` | FR.TriggerEditor | 控件的高度 |
| `options` | `JSON` | FR.Widget | 配置属性 |

### Properties（共 2 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `PluginRegex` | `Array` | FR.BaseEditor | 正则表达式控件插件接口 |
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |

### Methods（共 39 个）

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
| `getArrowIconHeight` | `()` | `number` | 获取下拉箭头图标的高度 | FR.TriggerEditor |
| `getDependenceObj` | `()` | `Object` | 数据联动，获取联动数据 | FR.BaseEditor |
| `getErrorMsg` | `()` | `String` | 获取错误提示内容 | FR.BaseEditor |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getText` | `()` | `String` | 获取控件的显示值 | FR.Widget |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `Object` | 获取控件的实际值 | FR.Widget |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isExpanded` | `()` | `Boolean` | 下拉列表是否展开 | FR.TriggerEditor |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isSupportDatabinding` | `()` | `Boolean` | 判断是否支持数据绑定 | FR.BaseEditor |
| `isValidate` | `(cValue)` | `boolean` | 校验值是否符合控件的值规范 | FR.BaseEditor |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `loadData` | `()` | — | 加载数据 | FR.BaseEditor |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `onTriggerClick` | `()` ⚑抽象 | — | 下拉按钮触发事件，抽象方法，具体控件需实现 | FR.TriggerEditor |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `reset` | `()` | — | 恢复控件到初始状态 | FR.Widget |
| `setEnable` | `(arg)` | — | 设置控件的可用性 | FR.TriggerEditor |
| `setIcon` | `(cls)` | — | 仅支持通过 class 来设置图标 | FR.TriggerEditor |
| `setSource` | `(source)` | — | 设置控件的初始值 | FR.Widget |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.Widget |
| `setValue` | `(value, shouldFireEvent)` | — | 设置控件的值 | FR.Widget |
| `setVisible` | `(visible)` | — | 设置控件的可见性 | FR.Widget |
| `startEditing` | `()` | — | 开始编辑 | FR.TriggerEditor |
| `stopEditing` | `()` | — | 结束编辑 | FR.TriggerEditor |
| `store` | `()` | — | 保存数据绑定的数据 | FR.BaseEditor |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |

---

