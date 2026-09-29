<!--
KB_INDEX: {
  "title": "FR填报JS API：报表面板与填报接口（Elementcase/PagePane/WLGP/Write/WriteEditor）",
  "stage": "frontend",
  "tags": [
    "JS API",
    "填报",
    "PagePane",
    "WLGP"
  ],
  "keywords": [
    "FR.Elementcase",
    "FR.PagePane",
    "FR.WLGP",
    "FR.Write",
    "FR.WriteEditor",
    "getTDCell",
    "分页预览"
  ],
  "summary": "FR 10.0 填报核心 JS API 第 2/2 页：FR.Elementcase 报表内容基类（31 方法）、FR.PagePane 分页预览（33 方法）、FR.WLGP 填报逻辑页面（getTDCell 等 19 方法）、FR.Write 填报控件管理（21 方法）、FR.WriteEditor 填报编辑器接口（36 方法）+ 通用基类方法速查附录——原 api_report.md §4-§8+附录"
}
-->

> 抓取自 http://dev.fanruan.com/jsdoc/ (JsDuck 生成)，覆盖 FR 报表填报开发最常用的 8 个类。
> 每个类按"继承关系 → Config/Properties → Methods"组织，方法表包含方法名、参数、返回值与中文描述。
> 🧪 **2026-09-04 实测标注说明**：文中的 `> [2026-09-04 实测]` 批注块是 L6 泳道在 FR10 真实页面（localhost:8075，Playwright 实测）逐条验证的结论（✅与文档一致 / ⚠有差异 / ❌不可用 / ⏭未实调），119 条断言汇总与替代写法见 [verified_20260904.md](verified_20260904.md)；原 JSDoc 内容未作任何删改。

> 本页为原 api_report.md（653 行）第 2/2 页（2026-09-29 拆分），对应原 §4-§8+附录；弹窗与填报面板（§1-§3）见 [api_report_1_弹窗与填报面板.md](api_report_1_弹窗与填报面板.md)，总导航见 [api_report.md](api_report.md)。

---

## 4. FR.Elementcase（报表内容/报表块组件）

**HIERARCHY**:
```
FR.OB
└─ FR.Widget
   └─ FR.BaseEditor
      └─ FR.Elementcase
```
**FILES**: `widget.elementcase.js`
**说明**: 报表块组件，是组成表单（决策报表）的一种组件。

### Config options (1)
| 选项 | 类型 | 定义于 | 描述 |
|---|---|---|---|
| `options` | JSON | FR.Widget | 配置属性 |

### Properties (4)
| 属性 | 类型 | 定义于 | 描述 |
|---|---|---|---|
| `PluginRegex` | Array | FR.BaseEditor | 正则表达式控件插件接口（正则表达式类型数组） |
| `currentPage` | Number | FR.Elementcase | 当前页索引 |
| `element` | jQuery | FR.Widget | 控件的根节点元素 |
| `totalPage` | Number | FR.Elementcase | 总页数 |

### Methods (31)

**FR.Elementcase 自身方法**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `gotoPage` | `(pn, para, noCache)` | — | 跳转到指定页（可用于刷新当前报表块） |

**继承自 FR.BaseEditor**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 |
| `createDependencePara4Data` | `()` | Object | 数据联动，生成参数依赖 |
| `getDependenceObj` | `()` | Object | 数据联动，获取联动数据 |
| `getErrorMsg` | `()` | String | 获取错误提示内容 |
| `isSupportDatabinding` | `()` | Boolean | 判断是否支持数据绑定 |
| `isValidate` | `(cValue)` | Boolean | 校验值是否符合控件的值规范（不符合则设置 `this.errorMsg`） |
| `loadData` | `()` | — | 加载数据 |
| `store` | `()` | — | 保存数据绑定的数据 |

**继承自 FR.Widget**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `couldUsedAsEditor` | `()` | Boolean | 控件能否在填报中用做编辑器 |
| `destroy` | `()` | — | 销毁整个控件的 dom 结构 |
| `doResize` | `([give])` | — | 重新设置控件的大小和位置 |
| `getName` | `()` | Object | 获取控件名字 |
| `getText` | `()` | String | 获取控件的显示值 |
| `getType` | `()` | — | 获取控件类型 |
| `getValue` | `()` | Object | 获取控件的实际值 |
| `getWidgetByName` | `(name)` | FR.Widget | 获取该控件中所添加的子控件 |
| `isEnabled` | `()` | Boolean | 判断控件是否可用 |
| `isStringTypeNumber` | `(o)` | Boolean | 判断 "24" 这种字符串形式的数字 |
| `isVisible` | `()` | Boolean | 判断控件是否可见 |
| `reset` | `()` | — | 恢复控件到初始状态 |
| `setEnable` | `(enable)` | — | 设置控件的可用性 |
| `setSource` | `(source)` | — | 设置控件的初始值（数据绑定时动态加载） |
| `setText` | `(text)` | — | 设置控件的显示值 |
| `setValue` | `(value, shouldFireEvent)` | — | 设置控件的值 |
| `setVisible` | `(visible)` | — | 设置控件的可见性 |

**继承自 FR.OB**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `fireEvent` | `(eventName)` | Boolean | 触发绑定过的事件 |
| `on` | `(eventName, fn)` | — | 给观察者绑定一个事件 |
| `once` | `(eventName, fn)` | — | 给观察者绑定一个只执行一次的事件 |
| `purgeListeners` | `()` | — | 清除观察者的所有事件绑定 |
| `un` | `(eventName, fn)` | — | 解除观察者绑定的指定事件 |

---

## 5. FR.PagePane（分页预览面板）

**HIERARCHY**:
```
FR.OB
└─ FR.Widget
   └─ FR.BasePane
      └─ FR.PagePane
```
**FILES**: `page.js`
**说明**: 分页预览对象。
> [2026-09-04 实测] ✅ `window.contentPane(PagePane)` 查看页实测存在（详见 verified_20260904.md，CP01）
> [2026-09-04 实测] ✅ `_g()` cpt 查看页实测 _g()===contentPane；普通报表若无 _g 直接用 contentPane，_g 仅决策报表(.frm)语境必有（详见 verified_20260904.md，CP02）

### Config options (1)
| 选项 | 类型 | 定义于 | 描述 |
|---|---|---|---|
| `options` | JSON | FR.Widget | 配置属性 |

### Properties (5)
| 属性 | 类型 | 定义于 | 描述 |
|---|---|---|---|
| `currentPageIndex` | Number | FR.PagePane | 当前页所在总页数中的序号 |
| `element` | jQuery | FR.Widget | 控件的根节点元素 |
| `isLoadingPage` | Number | FR.PagePane | 正在加载的页的序号 |
| `pagesLoaded` | Number | FR.PagePane | 已经加载的页序号组成的数组 |
| `reportTotalPage` | Number | FR.PagePane | 总页数 |
> [2026-09-04 实测] ✅ `currentPageIndex` 属性实测=0（单页模板）（详见 verified_20260904.md，CP09）
> [2026-09-04 实测] ✅ `reportTotalPage` 属性实测=0（页面未加载完成时可能为 0）（详见 verified_20260904.md，CP10）

### Methods (33)

**FR.PagePane 自身方法**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `gotoFirstPage` | `()` | — | 转向报表的第一页 |
| `gotoLastPage` | `()` | — | 转向报表的最后一页 |
| `gotoNextPage` | `()` | — | 转向报表的下一页 |
| `gotoPreviousPage` | `()` | — | 转向报表的上一页 |
| `gotoPage` | `(pn)` | — | 转向报表的指定页。`pn`=页序号（从 1 开始） |
| `setBorderVisible` | `(isVisible)` | — | 是否显示分页预览时的边框（需加在页面"加载起始"事件中） |
> [2026-09-04 实测] ✅ `gotoFirstPage` 实测无异常（详见 verified_20260904.md，CP11）
> [2026-09-04 实测] ✅ `gotoLastPage` 实测无异常（详见 verified_20260904.md，CP11）
> [2026-09-04 实测] ✅ `gotoNextPage` 实测无异常（详见 verified_20260904.md，CP11）
> [2026-09-04 实测] ✅ `gotoPreviousPage` 实测无异常（详见 verified_20260904.md，CP11）
> [2026-09-04 实测] ✅ `gotoPage` gotoPage(1) 实测无异常（单页模板页序号均 0）（详见 verified_20260904.md，CP11）
> [2026-09-04 实测] ✅ `setBorderVisible` false/true 往返无异常（详见 verified_20260904.md，CP12）

**继承自 FR.BasePane**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `autoScale` | `()` | — | 根据报表所在窗体的宽度和高度自适应放大和缩小表内容 |
| `makeHighlight` | `(color, [op], deep)` | — | 改变鼠标经过/点击报表行时行的颜色。`color`=颜色；`op`='click'/'mouseover'（默认 'click'）；`deep`=是否加在 td 上 |
| `parameterCommit` | `(reloadOthers)` | — | 提交参数并加载报表主体内容。⚠两种语境：决策报表（.frm）用 `_g().parameterCommit()`；普通报表（.cpt）用 `contentPane.parameterCommit()`（来源 doc-1434） |
| `scale` | `()` | — | 缩放报表页面。`contentPane.scale('+')` 放大；`contentPane.scale(1.5)` 缩放到 150% |
| `showPageSetupDialog` | `(o)` | — | 展示页面设置的对话框。`o`=对话框配置 |
> [2026-09-04 实测] ✅ `makeHighlight` 'red'+'mouseover' 已调用（变色需人工移入行确认）（详见 verified_20260904.md，CP13）
> [2026-09-04 实测] ✅ `parameterCommit` 干净态可用；但对参数控件编程式 setText/setValue 后立刻调用会抛 TypeError ...replace——赋值后延迟一拍或统一走查询按钮事件（详见 verified_20260904.md，PM12R2/PM14）
> [2026-09-04 实测] ✅ `scale` '+' 放大与 1 复原无异常（详见 verified_20260904.md，CP14）

**继承自 FR.Widget / FR.OB**（22 个，同前述通用方法）
`couldUsedAsEditor`, `destroy`, `doResize`, `fireEvent`, `getName`, `getText`, `getType`, `getValue`, `getWidgetByName`, `isEnabled`, `isStringTypeNumber`, `isVisible`, `on`, `once`, `purgeListeners`, `reset`, `setEnable`, `setSource`, `setText`, `setValue`, `setVisible`, `un`
> [2026-09-04 实测] ✅ `getType` 查看面板实测返回 'page'（详见 verified_20260904.md，CP03）
> [2026-09-04 实测] ✅ `getName` 实测可调用（空值）（详见 verified_20260904.md，CP04）
> [2026-09-04 实测] ✅ `isVisible` 实测 true（详见 verified_20260904.md，CP05）
> [2026-09-04 实测] ✅ `isEnabled` 实测 true（详见 verified_20260904.md，CP06）
> [2026-09-04 实测] ✅ `couldUsedAsEditor` 查看页实测 false（详见 verified_20260904.md，CP07）
> [2026-09-04 实测] ⚠ `isStringTypeNumber` 校验比文档宽松：'24a' 亦返回 true，不能当严格数字格式校验用（详见 verified_20260904.md，CP08R2）

**示例**:
```js
contentPane.gotoFirstPage();           // 跳转到首页
contentPane.gotoPage(2);               // 跳转到第二页
contentPane.makeHighlight('red', 'click');   // 点击行变红
contentPane.scale('+');                // 放大
contentPane.scale(1.5);                // 缩放到 150%
contentPane.parameterCommit();         // 提交参数
```

---

## 6. FR.WLGP（填报逻辑页面 Write Logic Page）

**HIERARCHY**:
```
FR.OB
└─ FR.WLGP
```
**FILES**: `write.js`
**说明**: 填报的逻辑页面（Write Logic Page）。通常通过 `contentPane.curLGP` 访问。
> [2026-09-04 实测] ✅ `contentPane.curLGP` 填报页实测存在（详见 verified_20260904.md，WR14）

### Properties (3)
| 属性 | 类型 | 描述 |
|---|---|---|
| （匿名） | Object | 直接显示控件时的特殊处理统一放这里 |
| `$container` | Object | 实际被添加内容的 jQuery 对象（contentPane 或 TabPane 的选中 tab） |
| `writePane` | Object | 该 lgp 所属的 FR.WritePane |
> [2026-09-04 实测] ✅ `writePane/$container` 实测均存在（writePane=true、container=true）（详见 verified_20260904.md，WR33）

### Methods (19)

**FR.WLGP 自身方法**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `calCurrentPage` | `()` | — | 计算下当前页 |
| `displayTDCell` | `(tdCell, cv, presentValue)` | — | 把值显示在 TD 里。`cv` 可以是 `{text, value}`（直接显示 text）或字符串（根据 dict 有无判断是否要处理） |
| `formatContent` | `(dp, $tdCell)` | `*` | 格式化单元格值 |
| `getTDCell` | `(col, row)` | `*` | 获取某个单元格 td 的 jQuery 对象 |
| `getTDCol` | `(td)` | Number | 得到单元格的列号 |
| `getTDRow` | `(td)` | Number | 得到单元格的行号（**API 行列都从 1 开始**） |
| `hideSelectFrame` | `()` | — | 隐藏选中的黑框 |
| `isEditableWidget` | `(tdCell)` | Boolean | 直接显示控件时可编辑控件与不可编辑控件（如按钮）的区分 |
| `isFrozen` | `()` | Boolean | 检查当前页面是否冻结 |
| `isWeakSelectable` | `(tdCell)` | — | tdCell 是否可被选中（含直接显示控件场景下的可编辑控件） |
| `modifyRowHeightAfterContentChange` | `($tr, oriHeight)` | — | 调整对应行的行高（为冻结服务） |
| `moveTDCell` | `(direction)` | — | 移动选中格子的黑框。`contentPane.curLGP.moveTDCell(1)` 向上移动 |
| `present` | `($tdCell, cv)` | — | 作形态处理 |
| `saveCurrentPage` | `()` | — | 填报翻页时保存当前页面内容 |
> [2026-09-04 实测] ⚠ `getTDCell` 返回【原生 DOM TD】而非文档所称 jQuery 对象；需 jQuery 时手动 $(td)，读文本用 td.innerText（td.text() 报 not a function）（详见 verified_20260904.md，WR15R2）
> [2026-09-04 实测] ✅ `getTDCol` 实测 1 基（C6 格返回 3）；与 getCellValue 的 0 基差 1，混用注意（详见 verified_20260904.md，WR16R2）
> [2026-09-04 实测] ✅ `getTDRow` 实测 1 基（C6 格返回 6）——文档『行列都从 1 开始』属实（详见 verified_20260904.md，WR16R2）
> [2026-09-04 实测] ✅ `hideSelectFrame` 选格后实测 ok；坑：必须先点击选格（自动化先派发 mousedown/mouseup/click）再调，否则抛 ftop TypeError（详见 verified_20260904.md，WR17R2）
> [2026-09-04 实测] ✅ `moveTDCell` 选格后实测 ok（同上先选格）（详见 verified_20260904.md，WR17R2）
> [2026-09-04 实测] ✅ `displayTDCell` 选格后实测 ok（同上先选格）（详见 verified_20260904.md，WR17R2）
> [2026-09-04 实测] ✅ `isFrozen` 实测 false（详见 verified_20260904.md，WR18）
> [2026-09-04 实测] ✅ `isEditableWidget` 编辑格选格后实测 true（详见 verified_20260904.md，WR19R2）
> [2026-09-04 实测] ✅ `isWeakSelectable` 编辑格选格后实测 true（详见 verified_20260904.md，WR19R2）

**继承自 FR.OB**（5 个）
`fireEvent(eventName):Boolean`, `on(eventName, fn)`, `once(eventName, fn)`, `purgeListeners()`, `un(eventName, fn)`

**示例**:
```js
contentPane.curLGP.hideSelectFrame();      // 隐藏选中黑框
contentPane.curLGP.moveTDCell(1);          // 向上移动黑框
```

---

## 7. FR.Write（填报控件管理）

**HIERARCHY**:
```
FR.OB
└─ FR.Write
```
**FILES**: `write.js`
**说明**: 生成填报页面的所有控件，绑定事件，提供参数联动等。

### Properties (2)
| 属性 | 类型 | 描述 |
|---|---|---|
| `WidgetMgr` | Object | Widget 管理对象 |
| `location_widgets` | Map | 位置和控件组成的键值对集合 |

### Methods (21)

**FR.Write 自身方法**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `addDependenceRelation` | `(location, dependenceLocation)` | — | 添加依赖关系 |
| `addEditor` | `(editor)` | — | 将控件注册到控件位置集合（`location_widgets`）和控件名集合（`name_widgets`）中 |
| `addLocationWidget` | `($dom, editorConfig)` | — | 单元格初始化控件并绑定事件 |
| `addLocationWidgetWithoutWriteEvent` | `($dom, editorConfig)` | — | 单元格初始化控件，只在指定 DOM 里生成控件，不绑定事件 |
| `addWidget` | `($dom)` | — | 单元格初始化控件，绑定事件并标记已初始化 |
| `addWidgetShouldInitDependence` | `(location)` | — | 添加要初始化依赖关系的控件 |
| `getDependenceRelation` | `(location)` | `*` | 获取依赖关系 |
| `getWidgetByCell` | `(location, widgets)` | FR.Widget | 根据单元格位置获取单元格中的控件 |
| `getWidgetByName` | `(name)` | FR.Widget | 根据控件名字获取控件 |
| `getWidgetShouldInitDependence` | `()` | `*` | 获取要初始化依赖关系的控件 |
| `getWidgetsByName` | `(name)` | FR.Widget[] | 根据控件名获取同名控件数组的集合 |
| `isInited` | `(location)` | Boolean | 判断是否初始化 |
| `pushNameWidget` | `(widgetName, widget)` | — | 将控件添加进控件名集合中 |
| `resolveVariable` | `(variable)` | `*` | 处理联动的方法 |
| `setInited` | `(location)` | — | 标识已经初始化 |
| `widgetOnWriteEvent` | `(widget)` | — | 为控件绑定事件 |

**继承自 FR.OB**（5 个）
`fireEvent(eventName):Boolean`, `on(eventName, fn)`, `once(eventName, fn)`, `purgeListeners()`, `un(eventName, fn)`

---

## 8. FR.WriteEditor（填报编辑器接口）

**HIERARCHY**:
```
FR.OB
└─ FR.Widget
   └─ FR.BaseEditor
      └─ FR.WriteEditor
```
**FILES**: `write.js`
**说明**: 填报控件的接口，为填报中使用的控件添加公共函数。按钮、复选框之类的即时显示控件不需要继承此类。

### Config options (1)
| 选项 | 类型 | 定义于 | 描述 |
|---|---|---|---|
| `options` | JSON | FR.Widget | 配置属性 |

### Properties (3)
| 属性 | 类型 | 定义于 | 描述 |
|---|---|---|---|
| （匿名） | Object | FR.WriteEditor | 给填报控件增加 FR.WriteEditor 所具有的函数（类似继承接口） |
| `PluginRegex` | Array | FR.BaseEditor | 正则表达式控件插件接口 |
| `element` | jQuery | FR.Widget | 控件的根节点元素 |

### Methods (36)

**FR.WriteEditor 自身方法**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `cssFrom` | `(dom)` | — | 从 dom 复制部分样式给编辑器，保证编辑器样式与格子样式一致 |
| `isDirty` | `()` | Boolean | 判断控件所在的格子是否被编辑过 |
| `isWriteDataChanged` | `()` | Boolean | 让原值和新值比较，判断该控件是否进行了值的改动 |
| `reset` | `()` | — | 重置控件的值（用于填报联动）（**覆盖** FR.Widget.reset） |
| `setValue4Write` | `(value, shouldFireEvent)` | `*` | 设置控件的值并保存原值以做比较 |
| `startEditing` | `()` | — | 开始编辑 |
| `stopEditing` | `()` | — | 结束编辑 |
> [2026-09-04 实测] ✅ `cssFrom` 填报控件实例实测存在（详见 verified_20260904.md，WR13R2）
> [2026-09-04 实测] ✅ `isDirty` 实测 true（编辑后）（详见 verified_20260904.md，WR13R2）
> [2026-09-04 实测] ✅ `isWriteDataChanged` 实例实测存在（详见 verified_20260904.md，WR13R2）
> [2026-09-04 实测] ✅ `setValue4Write` 实例实测存在（详见 verified_20260904.md，WR13R2）
> [2026-09-04 实测] ✅ `startEditing` 实例实测存在（详见 verified_20260904.md，WR13R2）
> [2026-09-04 实测] ✅ `stopEditing` 无异常（详见 verified_20260904.md，WR20）

**继承自 FR.BaseEditor**
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `checkValid` | `(cValue)` | — | 校验并且设置状态标志 |
| `createDependencePara4Data` | `()` | Object | 数据联动，生成参数依赖 |
| `getDependenceObj` | `()` | Object | 数据联动，获取联动数据 |
| `getErrorMsg` | `()` | String | 获取错误提示内容 |
| `isSupportDatabinding` | `()` | Boolean | 判断是否支持数据绑定 |
| `isValidate` | `(cValue)` | Boolean | 校验值是否符合控件的值规范 |
| `loadData` | `()` | — | 加载数据 |
| `store` | `()` | — | 保存数据绑定的数据 |

**继承自 FR.Widget**（14 个）
`couldUsedAsEditor():Boolean`, `destroy()`, `doResize([give])`, `getName():Object`, `getText():String`, `getType()`, `getValue():Object`, `getWidgetByName(name):FR.Widget`, `isEnabled():Boolean`, `isStringTypeNumber(o):Boolean`, `isVisible():Boolean`, `setEnable(enable)`, `setSource(source)`, `setText(text)`, `setValue(value, shouldFireEvent)`, `setVisible(visible)`

**继承自 FR.OB**（5 个）
`fireEvent(eventName):Boolean`, `on(eventName, fn)`, `once(eventName, fn)`, `purgeListeners()`, `un(eventName, fn)`

---

## 附录：通用基类方法速查

以下方法在几乎所有 FR 类中可用（继承自 FR.OB / FR.Widget），下表为速查：

### FR.OB（观察者基类）
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `fireEvent` | `(eventName)` | Boolean | 触发绑定过的事件 |
| `on` | `(eventName, fn)` | — | 绑定事件 |
| `once` | `(eventName, fn)` | — | 绑定只执行一次的事件 |
| `purgeListeners` | `()` | — | 清除所有事件绑定 |
| `un` | `(eventName, fn)` | — | 解除指定事件绑定 |

### FR.Widget（控件基类）
| 方法 | 参数 | 返回值 | 描述 |
|---|---|---|---|
| `couldUsedAsEditor` | `()` | Boolean | 能否在填报中用作编辑器 |
| `destroy` | `()` | — | 销毁 dom |
| `doResize` | `([give])` | — | 重设大小位置 |
| `getName` | `()` | Object | 控件名 |
| `getText` | `()` | String | 显示值 |
| `getType` | `()` | — | 控件类型 |
| `getValue` | `()` | Object | 实际值 |
| `getWidgetByName` | `(name)` | FR.Widget | 子控件 |
| `isEnabled` | `()` | Boolean | 是否可用 |
| `isStringTypeNumber` | `(o)` | Boolean | "24" 形式判断 |
| `isVisible` | `()` | Boolean | 是否可见 |
| `reset` | `()` | — | 恢复初始状态 |
| `setEnable` | `(enable)` | — | 设置可用性 |
| `setSource` | `(source)` | — | 设置初始值（数据绑定） |
| `setText` | `(text)` | — | 设置显示值 |
| `setValue` | `(value, shouldFireEvent)` | — | 设置值 |
| `setVisible` | `(visible)` | — | 设置可见性 |

---

*文档来源: http://dev.fanruan.com/jsdoc/ · 帆软软件有限公司 · 文档生成于 Thu 03 Mar 2016*
