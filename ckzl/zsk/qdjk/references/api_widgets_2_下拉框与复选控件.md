<!--
KB_INDEX: {
  "title": "FR控件JS API：下拉框与复选控件（ComboBoxEditor/CheckBoxEditor/CheckBoxGroup）",
  "stage": "frontend",
  "tags": [
    "JS API",
    "控件",
    "下拉框",
    "复选框"
  ],
  "keywords": [
    "FR.ComboBoxEditor",
    "FR.CheckBoxEditor",
    "FR.CheckBoxGroup",
    "下拉框",
    "下拉复选",
    "复选按钮组"
  ],
  "summary": "FR 10.0 控件 JS API 第 2/3 页：下拉框 ComboBoxEditor（55 方法/7 配置项）、下拉复选框 CheckBoxEditor（58 方法）、复选按钮组 CheckBoxGroup（32 方法）；含 HIERARCHY/SUBCLASSES/示例/继承方法表与 2026-09-04 实测标注"
}
-->

> 数据来源：http://dev.fanruan.com/jsdoc/
> 抓取日期：2026-08-04
> 说明：方法清单包含继承自父类的方法，"来源"列标注了方法定义所在的类（对应 Jsdoc 的 "Defined By"）。
> 🧪 **2026-09-04 实测标注说明**：文中的 `> [2026-09-04 实测]` 批注块是 L6 泳道在 FR10 真实页面（localhost:8075，Playwright 实测）逐条验证的结论（✅与文档一致 / ⚠有差异 / ❌不可用 / ⏭未实调），119 条断言汇总与替代写法见 [verified_20260904.md](verified_20260904.md)；原 JSDoc 内容未作任何删改。

> 本页为原 api_widgets.md（1083 行）第 2/3 页（2026-09-29 拆分）；基类与文本编辑器见 [api_widgets_1_基类与文本数字编辑器.md](api_widgets_1_基类与文本数字编辑器.md)，日期与按钮控件见 [api_widgets_3_日期与按钮控件.md](api_widgets_3_日期与按钮控件.md)，总导航见 [api_widgets.md](api_widgets.md)。

---

## 6. FR.ComboBoxEditor（下拉框）

下拉框控件。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.BaseEditor
            └─ FR.TriggerEditor
                 └─ FR.BaseComboBoxEditor
                      └─ FR.ComboBoxEditor
```

### SUBCLASSES（子类）
`FR.CheckBoxEditor`

### FILES
`widget.combo.js`

### 示例
```javascript
var $el = $('<div>').css({position:'absolute',top:5,left:40}).appendTo('body');
var editor = new FR.ComboBoxEditor({
    renderEl : $el,
    directEdit : true,        // 是否允许直接编辑
    allowBlank : false,       // 是否允许为空
    widgetUrl : null,         // 支持模糊搜索,异步取数请求url
    fontSize : 14,
    width : 120,
    height : 24,
    maxCount : 3,             // 一页显示的记录数
    sonHeight : 24,           // 子项元素高度
    items : [                 // 本地取数方式,优先于widgetUrl
        {text:"一一", value:"aa"},
        {text:"二二", value:"bb"},
        {text:"三三", value:"cc"},
        {text:"四四", value:"dd"}
    ]
});
```

### Config options（共 7 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `customData` | `Boolean` | FR.BaseComboBoxEditor | 允许自定义值 |
| `directEdit` | `Boolean` | FR.BaseComboBoxEditor | 允许直接编辑 |
| `height` | `Number` | FR.TriggerEditor | 控件的高度 |
| `name4Empty` | `String` | FR.BaseComboBoxEditor | 在允许为空的时候待选列表的第一项的值 |
| `options` | `JSON` | FR.ComboBoxEditor | 属性配置 |
| `searchTime` | `Number` | FR.BaseComboBoxEditor | 手动输入指定毫秒后开始到服务器查询符合条件的项 |
| `width` | `Number` | FR.TriggerEditor | 控件的宽度 |

### Properties（共 2 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `PluginRegex` | `Array` | FR.BaseEditor | 正则表达式控件插件接口 |
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |

### Methods（共 55 个）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `addContent2Element` | `()` | — | 添加内容 | FR.TriggerEditor |
| `addData2View` | `(data)` | — | 将数据生成为子项元素，添加到下拉列表中 | FR.ComboBoxEditor |
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 | FR.BaseEditor |
| `checkViewScroll` | `(data)` | — | 判断是否需要滚动加载 | FR.ComboBoxEditor |
| `clearText` | `()` | — | 清空文本编辑框 | FR.BaseComboBoxEditor |
| `collapse` | `()` | — | 收起下拉列表 | FR.TriggerEditor |
| `collapseIf` | `(e)` | — | 鼠标下拉框外点击，收起下拉框 | FR.TriggerEditor |
| `considerAllowBlankLength` | `()` | `number` | 返回加入允许为空一项的下拉列表的总元素个数 | FR.BaseComboBoxEditor |
| `couldUsedAsEditor` | `()` | `Boolean` | 控件能否在填报中用做编辑器 | FR.Widget |
| `createDependencePara4Data` | `()` | `Object` | 数据联动，生成参数依赖 | FR.BaseEditor |
| `data2Add` | `()` | `*` | 添加值 | FR.ComboBoxEditor |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 | FR.Widget |
| `doResize` | `(give)` | — | 重新设置控件的大小和位置 | FR.TriggerEditor |
| `expand` | `()` | — | 展开下拉列表 | FR.ComboBoxEditor |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `getArrowIconHeight` | `()` | `number` | 获取下拉箭头图标的高度 | FR.TriggerEditor |
| `getData` | `()` | `*` | 取数方法的实现 | FR.ComboBoxEditor |
| `getDependenceObj` | `()` | `Object` | 数据联动，获取联动数据 | FR.BaseEditor |
| `getErrorMsg` | `()` | `String` | 获取错误提示内容 | FR.BaseEditor |
| `getItemsLength` | `()` | `*` | 获取下拉列表内的元素数 | FR.BaseComboBoxEditor |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getSelectedIndex` | `()` | `Number` | 获取选中的元素 | FR.BaseComboBoxEditor |
| `getText` | `()` | `String` | 获取控件的显示值 | FR.BaseComboBoxEditor |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `*` | 取值（从后台或已加载数据中匹配） | FR.BaseComboBoxEditor |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `initContent` | `($dom, showValue, index)` | — | 初始化一个子项元素 | FR.ComboBoxEditor |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isExpanded` | `()` | `Boolean` | 下拉列表是否展开 | FR.TriggerEditor |
| `isFiltering` | `()` | `Boolean` | 判断是否正在过滤字段 | FR.ComboBoxEditor |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isSupportDatabinding` | `()` | `Boolean` | 判断是否支持数据绑定 | FR.BaseEditor |
| `isValidate` | `(cValue)` | `Boolean` | 校验是否符合规则 | FR.BaseComboBoxEditor |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `loadData` | `()` | — | 加载数据 | FR.BaseEditor |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `onTriggerClick` | `()` | — | 点击下拉框右侧小按钮时触发的函数 | FR.ComboBoxEditor |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `rebuild` | `(items)` | — | 重新构建下拉列表 | FR.ComboBoxEditor |
| `recoveryValue` | `()` | — | 还原到之前的值 | FR.BaseComboBoxEditor |
| `reset` | `()` | — | 恢复控件到初始状态 | FR.BaseComboBoxEditor |
| `setEnable` | `(arg)` | — | 设置控件的可用性 | FR.ComboBoxEditor |
| `setFocusWithIndex` | `(index)` | — | 选中下拉列表中指定位置的一项 | FR.ComboBoxEditor |
| `setIcon` | `(cls)` | — | 仅支持通过 class 来设置图标 | FR.TriggerEditor |
| `setSelectedIndex` | `(index)` | — | 设置当前被选中的一项 | FR.BaseComboBoxEditor |
| `setSource` | `(source)` | — | 设置数据联动源 | FR.BaseComboBoxEditor |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.BaseComboBoxEditor |
| `setValue` | `(value)` | — | 设置控件的值 | FR.BaseComboBoxEditor |
| `setVisible` | `(arg)` | — | 设置控件的可见性 | FR.ComboBoxEditor |
| `shouldReBuildList` | `()` | — | 需要重新生成下拉列表 | FR.BaseComboBoxEditor |
| `startEditing` | `()` | — | 开始编辑 | FR.TriggerEditor |
| `stopEditing` | `()` | — | 结束编辑 | FR.TriggerEditor |
| `store` | `()` | — | 保存数据绑定的数据 | FR.BaseEditor |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
> [2026-09-04 实测] ✅ `expand` expand 后 isExpanded=true（详见 verified_20260904.md，WD07）
> [2026-09-04 实测] ✅ `collapse` collapse 后 isExpanded=false（详见 verified_20260904.md，WD07）
> [2026-09-04 实测] ✅ `isExpanded` 状态翻转验证通过（详见 verified_20260904.md，WD07）
> [2026-09-04 实测] ✅ `setSelectedIndex` idx=1 → 值 'cc' 验证通过（详见 verified_20260904.md，WD08）
> [2026-09-04 实测] ✅ `getSelectedIndex` 与 setSelectedIndex 往返一致（详见 verified_20260904.md，WD08）
> [2026-09-04 实测] ✅ `rebuild` rebuild 后 items=2（详见 verified_20260904.md，WD09）
> [2026-09-04 实测] ✅ `addData2View` 配合 rebuild 验证通过（详见 verified_20260904.md，WD09）
> [2026-09-04 实测] ✅ `getItemsLength` 实测返回 2（详见 verified_20260904.md，WD09）
> [2026-09-04 实测] ✅ `clearText` clear 后文本为空（详见 verified_20260904.md，WD10）
> [2026-09-04 实测] ✅ `recoveryValue` 还原验证通过（详见 verified_20260904.md，WD10）
> [2026-09-04 实测] ✅ `getText` clear/recovery 后取值验证通过（详见 verified_20260904.md，WD10）
> [2026-09-04 实测] ✅ `destroy` 实例销毁无异常（详见 verified_20260904.md，WD11）

---

## 7. FR.CheckBoxEditor（下拉复选框）

下拉复选框控件（本质是 ComboBoxEditor 的多选版本）。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.BaseEditor
            └─ FR.TriggerEditor
                 └─ FR.BaseComboBoxEditor
                      └─ FR.ComboBoxEditor
                           └─ FR.CheckBoxEditor
```

### SUBCLASSES（子类）
`FR.TagCheckBoxEditor`

### FILES
`widget.check.js`

### 示例
```javascript
var $root = $('<div>').css({position:'absolute',top:5,left:40}).appendTo('body');
var editor = new FR.CheckBoxEditor({
    renderEl : $root,
    directEdit : true,
    allowBlank : true,
    widgetUrl : null,         // 同下拉框
    returnArray : true,       // 返回值是否以数组形式
    delimiter : ',',          // 字符串返回值的分隔符
    startSymbol : '',         // 起始符
    endSymbol : '',           // 结束符
    fontSize : 14,
    width : 120,
    height : 24,
    maxCount : 10,
    items : [
        {text:"111", value:"aaa"},
        {text:"222", value:"bbb"},
        {text:"333", value:"ccc"},
        {text:"444", value:"ddd"}
    ]
});
```

### Config options（共 7 个，同 ComboBoxEditor）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `customData` | `Boolean` | FR.BaseComboBoxEditor | 允许自定义值 |
| `directEdit` | `Boolean` | FR.BaseComboBoxEditor | 允许直接编辑 |
| `height` | `Number` | FR.TriggerEditor | 控件的高度 |
| `name4Empty` | `String` | FR.BaseComboBoxEditor | 允许为空时待选列表第一项的值 |
| `options` | `JSON` | FR.CheckBoxEditor | 属性配置 |
| `searchTime` | `Number` | FR.BaseComboBoxEditor | 手动输入指定毫秒后开始查询 |
| `width` | `Number` | FR.TriggerEditor | 控件的宽度 |

### Properties（共 2 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `PluginRegex` | `Array` | FR.BaseEditor | 正则表达式控件插件接口 |
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |

### Methods（共 58 个）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `addContent2Element` | `()` | — | 添加内容 | FR.TriggerEditor |
| `addData2View` | `(data)` | — | 将值添加到 DOM 中 | FR.CheckBoxEditor |
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 | FR.BaseEditor |
| `checkViewScroll` | `(data)` | — | 判断是否需要滚动加载 | FR.ComboBoxEditor |
| `clearText` | `()` | — | 清空文本编辑框 | FR.BaseComboBoxEditor |
| `collapse` | `()` | — | 收起下拉列表 | FR.TriggerEditor |
| `collapseIf` | `(e)` | — | 鼠标下拉框外点击，收起下拉框 | FR.TriggerEditor |
| `considerAllowBlankLength` | `()` | `number` | 返回加入允许为空一项的下拉列表总元素个数 | FR.BaseComboBoxEditor |
| `couldUsedAsEditor` | `()` | `Boolean` | 控件能否在填报中用做编辑器 | FR.Widget |
| `createDependencePara4Data` | `()` | `Object` | 数据联动，生成参数依赖 | FR.BaseEditor |
| `data2Add` | `()` | `*` | 添加数值，性能优化 | FR.CheckBoxEditor |
| `deSelectAll` | `()` | — | 反选操作 | FR.CheckBoxEditor |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 | FR.Widget |
| `doResize` | `(give)` | — | 重新设置控件的大小和位置 | FR.TriggerEditor |
| `doSelectAll` | `()` | — | 全选操作 | FR.CheckBoxEditor |
| `expand` | `()` | — | 展开下拉列表 | FR.ComboBoxEditor |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `getArrowIconHeight` | `()` | `number` | 获取下拉箭头图标的高度 | FR.TriggerEditor |
| `getData` | `()` | `*` | 取数方法的实现 | FR.ComboBoxEditor |
| `getDependenceObj` | `()` | `Object` | 数据联动，获取联动数据 | FR.BaseEditor |
| `getErrorMsg` | `()` | `String` | 获取错误提示内容 | FR.BaseEditor |
| `getItemsLength` | `()` | `*` | 获取下拉列表内的元素数 | FR.BaseComboBoxEditor |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getSelectedIndex` | `()` | `Number` | 获取选中的元素 | FR.BaseComboBoxEditor |
| `getText` | `()` | `*` | 获取显示值 | FR.CheckBoxEditor |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `*` | 取值函数 | FR.CheckBoxEditor |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `initContent` | `($dom, showValue, index)` | — | 初始化一个子项元素 | FR.ComboBoxEditor |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isExpanded` | `()` | `Boolean` | 下拉列表是否展开 | FR.TriggerEditor |
| `isFiltering` | `()` | `Boolean` | 判断是否正在过滤字段 | FR.ComboBoxEditor |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isSupportDatabinding` | `()` | `Boolean` | 判断是否支持数据绑定 | FR.BaseEditor |
| `isValidate` | `(cValue)` | `Boolean` | 校验是否符合规则 | FR.BaseComboBoxEditor |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `loadData` | `()` | — | 加载数据 | FR.BaseEditor |
| `modifyPosition` | `()` | — | 调整下拉表生成的位置 | FR.CheckBoxEditor |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `onTriggerClick` | `()` | — | 点击下拉框右侧小按钮时触发的函数 | FR.ComboBoxEditor |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `rebuild` | `(items)` | — | 重新构建下拉列表 | FR.CheckBoxEditor |
| `recoveryValue` | `()` | — | 还原到之前的值 | FR.BaseComboBoxEditor |
| `reset` | `()` | — | 重置控件 | FR.CheckBoxEditor |
| `setEnable` | `(arg)` | — | 设置控件的可用性 | FR.ComboBoxEditor |
| `setFocusWithIndex` | `(index)` | — | 选中下拉列表中指定位置的一项 | FR.ComboBoxEditor |
| `setIcon` | `(cls)` | — | 仅支持通过 class 来设置图标 | FR.TriggerEditor |
| `setSelectedIndex` | `(index)` | — | 设置当前被选中的一项 | FR.BaseComboBoxEditor |
| `setSource` | `(source)` | — | 设置数据联动源 | FR.BaseComboBoxEditor |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.BaseComboBoxEditor |
| `setValue` | `(value)` | — | 设置控件的值 | FR.BaseComboBoxEditor |
| `setVisible` | `(arg)` | — | 设置控件的可见性 | FR.ComboBoxEditor |
| `shouldReBuildList` | `()` | — | 需要重新生成下拉列表 | FR.BaseComboBoxEditor |
| `startEditing` | `()` | — | 开始编辑 | FR.TriggerEditor |
| `stopEditing` | `()` | — | 结束编辑 | FR.TriggerEditor |
| `store` | `()` | — | 保存数据绑定的数据 | FR.BaseEditor |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
> [2026-09-04 实测] ✅ `doSelectAll` 全选后值=['aaa','bbb','ccc']（详见 verified_20260904.md，WD12）
> [2026-09-04 实测] ⚠ `deSelectAll` 文档称『反选』，实测行为疑似【清空】（反选后=[]）——语义存疑，使用前先实测（详见 verified_20260904.md，WD12）

---

## 8. FR.CheckBoxGroup（复选按钮组）

复选按钮组。一系列的复选按钮组成的控件，可以选择其中的零个或者多个。

### HIERARCHY（继承链）
```
FR.OB
  └─ FR.Widget
       └─ FR.BaseEditor
            └─ FR.SynchronBaseEditor
                 └─ FR.ToggleButtonGroup
                      └─ FR.CheckBoxGroup
```

### SUBCLASSES（子类）
`FS.FSCheckBoxGroup`

### FILES
`widget.group.js`

### 示例
```javascript
var editor = new FR.CheckBoxGroup({
    renderEl : 'body',
    width : 200,
    height : 100,
    columnsInRow : 1,
    mode : 'local',
    items : [
        {text:'apple',  value:'1'},
        {text:'orange', value:'2'},
        {text:'banana', value:'3'}
    ]
});
```

### Config options（共 1 个）

| 配置项 | 类型 | 来源 | 描述 |
|--------|------|------|------|
| `options` | `JSON` | FR.CheckBoxGroup | 配置属性 |

### Properties（共 2 个）

| 属性 | 类型 | 来源 | 描述 |
|------|------|------|------|
| `PluginRegex` | `Array` | FR.BaseEditor | 正则表达式控件插件接口 |
| `element` | `jQuery` | FR.Widget | 控件的根节点元素 |

### Methods（共 32 个）

| 方法 | 参数 | 返回值 | 描述 | 来源 |
|------|------|--------|------|------|
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 | FR.BaseEditor |
| `couldUsedAsEditor` | `()` | `Boolean` | 控件能否在填报中用做编辑器 | FR.Widget |
| `createDependencePara4Data` | `()` | `Object` | 数据联动，生成参数依赖 | FR.BaseEditor |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 | FR.Widget |
| `doResize` | `(give)` | — | 重新设置控件的大小和位置 | FR.ToggleButtonGroup |
| `fireEvent` | `(eventName)` | `Boolean` | 触发绑定过的事件 | FR.OB |
| `getDependenceObj` | `()` | `Object` | 数据联动，获取联动数据 | FR.BaseEditor |
| `getErrorMsg` | `()` | `String` | 获取错误提示内容 | FR.BaseEditor |
| `getName` | `()` | `Object` | 获取控件名字 | FR.Widget |
| `getText` | `()` | `String` | 获取控件的显示值 | FR.Widget |
| `getTreeTrace` | `(str, node)` | — | 例如 "南京" → ["江苏","南京"] | FR.SynchronBaseEditor |
| `getType` | `()` | — | 获取控件类型 | FR.Widget |
| `getValue` | `()` | `Object` | 获取控件的实际值 | FR.Widget |
| `getWidgetByName` | `(name)` | `FR.Widget` | 获取该控件中所添加的子控件 | FR.Widget |
| `isEnabled` | `()` | `Boolean` | 判断控件是否可用 | FR.Widget |
| `isStringTypeNumber` | `(o)` | `boolean` | 判断 "24" 这种形式 | FR.Widget |
| `isSupportDatabinding` | `()` | `Boolean` | 判断是否支持数据绑定 | FR.BaseEditor |
| `isValidate` | `(cValue)` | `boolean` | 校验值是否符合控件的值规范 | FR.BaseEditor |
| `isVisible` | `()` | `Boolean` | 判断控件是否可见 | FR.Widget |
| `loadData` | `()` | — | 加载数据 | FR.BaseEditor |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 | FR.OB |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 | FR.OB |
| `parseTo2DArray` | `(arr)` | `*` | 一维数组转化成数组中的数组 | FR.SynchronBaseEditor |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 | FR.OB |
| `reset` | `()` | — | 恢复控件到初始状态 | FR.ToggleButtonGroup |
| `setEnable` | `(arg)` | — | 设置控件的可用性 | FR.ToggleButtonGroup |
| `setSource` | `(source)` | — | 设置控件的初始值 | FR.ToggleButtonGroup |
| `setText` | `(text)` | — | 设置控件的显示值 | FR.Widget |
| `setValue` | `(value, shouldFireEvent)` | — | 设置控件的值 | FR.Widget |
| `setVisible` | `(visible)` | — | 设置控件的可见性 | FR.Widget |
| `store` | `()` | — | 保存数据绑定的数据 | FR.BaseEditor |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 | FR.OB |
> [2026-09-04 实测] ❌ `getTreeTrace` 实例上不存在（typeof=function 为 false）——文档声称有但 FR10 实测无（详见 verified_20260904.md，WD13）
> [2026-09-04 实测] ❌ `parseTo2DArray` 同上不存在（详见 verified_20260904.md，WD13）
> [2026-09-04 实测] ✅ `setValue/getValue` 本身可用（value=1）；但树形轨迹两方法缺失，多选场景建议改用 FR.CheckBoxEditor(returnArray:true)（详见 verified_20260904.md，WD13）

---

