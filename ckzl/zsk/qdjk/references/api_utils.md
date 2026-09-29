<!--
KB_INDEX: {
  "title": "帆软 FR 10.0 JS API — 通用类方法清单",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["实测", "String", "verified_20260904", "详见", "jQuery", "true"],
  "summary": "> 数据来源：http://dev.fanruan.com/jsdoc/ > 抓取范围：jQuery、String、Array、Function、FR.Keys 五个通用类的全部公开 Methods。 > 🧪 **2026-09-04 实测"
}
-->

# 帆软 FR 10.0 JS API — 通用类方法清单

> 数据来源：http://dev.fanruan.com/jsdoc/
> 抓取范围：jQuery、String、Array、Function、FR.Keys 五个通用类的全部公开 Methods。
> 🧪 **2026-09-04 实测标注说明**：文中的 `> [2026-09-04 实测]` 批注块是 L6 泳道在 FR10 真实页面（localhost:8075，Playwright 实测）逐条验证的结论（✅与文档一致 / ⚠有差异 / ❌不可用 / ⏭未实调），119 条断言汇总与替代写法见 [verified_20260904.md](verified_20260904.md)；原 JSDoc 内容未作任何删改。

---

## jQuery

> **定义文件：** `jquery.base.js`
> **类描述：** 对 jQuery 对象方法的补充
> **公开方法数：** 4

| 方法签名 | 参数 | 返回值 | 描述 |
| --- | --- | --- | --- |
| `isChildAndSelfOf( b )` | `b : jQuery` — 需要比较的元素 | `Boolean` — 是则返回 true，否则返回 false | 判断指定元素是否为当前元素或当前元素的子元素 |
| `isChildOf( b )` | `b : jQuery` — 需要比较的元素 | `Boolean` — 如果当前元素为指定元素的子元素返回 true，否则返回 false | 判断当前元素是否为指定元素的子元素 |
| `swapClass( c1, c2 )` | `c1 : jQuery` — 原始的 class；`c2 : jQuery` — 新的 class | `jQuery` — jQuery 对象 | 使用指定的 class 替代 jQuery 对象的原始 class |
| `switchClass( c1, c2 )` | `c1 : jQuery` — 第一个 class；`c2 : jQuery` — 第二个 class | `jQuery` — jQuery 对象 | 让 jQuery 对象的 class 在两个指定的 class 中交换。如果当前是 c1，调用后则将 class 变为 c2；如果当前是 c2，调用后则将 class 变为 c1 |
> [2026-09-04 实测] ✅ `isChildAndSelfOf` DOM 自身/子元素判断实测 child=true self=true，与文档一致（详见 verified_20260904.md，UT15）
> [2026-09-04 实测] ⚠ `isChildOf` 可用，但参数必须是 jQuery 对象——传原生 DOM 返回 false（jq=true dom=false）（详见 verified_20260904.md，UT16R2）
> [2026-09-04 实测] ✅ `swapClass` class 替换后 hasClass('b')=true，行为符合文档（详见 verified_20260904.md，UT17）
> [2026-09-04 实测] ✅ `switchClass` 双向交换实测 step1/step2 均成立（详见 verified_20260904.md，UT18）

---

## String

> **定义文件：** `jquery.base.js`
> **类描述：** 对字符串对象的扩展
> **公开方法数：** 10（7 个实例方法 + 3 个静态方法）

### 实例方法（Instance methods）

| 方法签名 | 参数 | 返回值 | 描述 |
| --- | --- | --- | --- |
| `allIndexOf( sub )` | `sub : String` — 子字符串 | `Number[]` — 子字符串在父字符串中出现的所有位置组成的数组 | 获取字符串中某字符串的所有项位置数组 |
| `appendQuery( paras )` | `paras : Object` — 参数对象，是一个键值对对象 | `String` — 添加了给定参数的 url | 给 url 加上给定的参数 |
| `endWith( endTag )` | `endTag : String` — 指定的字符串 | `Boolean` — 如果字符串以指定字符串结束则返回 true，否则返回 false | 判断字符串是否以指定的字符串结束 |
| `getQuery( name )` | `name : String` — 参数的名字 | `String` — 参数的值 | 获取 url 中指定名字的参数 |
| `perfectStart( start )` | `start : String` — 指定的字符 | `String` — 以指定字符开头的字符串 | 总是让字符串以指定的字符开头 |
| `replaceAll( s1, s2 )` | `s1 : String` — 要替换的字符串的正则表达式；`s2 : String` — 替换的结果字符串 | `String` — 替换后的字符串 | 将所有符合第一个字符串所表示的字符串替换成为第二个字符串 |
| `startWith( startTag )` | `startTag : String` — 指定的开始字符串 | `Boolean` — 如果字符串以指定字符串开始则返回 true，否则返回 false | 判断字符串是否以指定的字符串开始 |
> [2026-09-04 实测] ✅ `allIndexOf` 实测返回 [1,3]，与文档一致（详见 verified_20260904.md，UT01）
> [2026-09-04 实测] ✅ `appendQuery` 实测拼出 http://a/b?x=1&y=z（详见 verified_20260904.md，UT02）
> [2026-09-04 实测] ✅ `endWith` 实测 true（详见 verified_20260904.md，UT03）
> [2026-09-04 实测] ✅ `getQuery` 实测取到 a.cpt（详见 verified_20260904.md，UT04）
> [2026-09-04 实测] ✅ `perfectStart` 实测 a→/abc(47=/)、b→/abc，总是补齐指定开头（详见 verified_20260904.md，UT05R2）
> [2026-09-04 实测] ⚠ `replaceAll` 可用，但首参按【正则】解析（文档已注明正则、极易被当字面串误用）：未转义时得到 -----|a-b- 类结果；字面替换先转义（详见 verified_20260904.md，UT06R2）
> [2026-09-04 实测] ✅ `startWith` 实测 true（详见 verified_20260904.md，UT07）

### 静态方法（Static methods）

| 方法签名 | 参数 | 返回值 | 描述 |
| --- | --- | --- | --- |
| `String.escape( string )` 🔒STATIC | `string : String` — 要做编码处理的字符串 | `String` — 编码后的字符串 | 对字符串中的 `'` 和 `\` 做编码处理 |
| `String.format( format )` 🔒STATIC | `format : String` — 要做替换的字符串，替换字符串 1，替换字符串 2... | `String` — 做了替换后的字符串 | 对字符串做替换的函数。示例：`String.format('<div class="{0}>{1}</div>"', cls, text)` |
| `String.leftPad( val, size, ch )` 🔒STATIC | `val : String` — 原始值；`size : Number` — 总共需要的位数；`ch : String` — 用于补齐的字符 | `String` — 补齐后的字符串 | 让字符串通过指定字符做补齐的函数。示例：`String.leftPad('123', 5, '0')` → `'00123'` |
> [2026-09-04 实测] ✅ `String.escape` 实测 it\'s a \\ test 编码生效（详见 verified_20260904.md，UT08）
> [2026-09-04 实测] ✅ `String.format` 实测输出 <div class="cls">t</div>（详见 verified_20260904.md，UT09）
> [2026-09-04 实测] ✅ `String.leftPad` 实测 '00123'，与文档示例一致（详见 verified_20260904.md，UT10）

---

## Array

> **定义文件：** `jquery.base.js`
> **类描述：** 对数组对象的扩展
> **公开方法数：** 4

| 方法签名 | 参数 | 返回值 | 描述 |
| --- | --- | --- | --- |
| `clear( )` | 无 | 无 | 移除数组中的所有元素 |
| `indexOf( o )` | `o : Object` — 要检查的值 | `Number` — o 在数组中的索引（如果不在数组中则返回 -1） | 检查指定的值是否在数组中 |
| `lastIndexOf( o )` | `o : Object` — 要检查的值 | `Number` — o 在数组中的索引（如果不在数组中则返回 -1） | 检查指定的值是否在数组中（ie6/7 不支持数组的这个方法） |
| `remove( o )` 🔗CHAINABLE | `o : Object` — 要移除的值 | `Array` — 移除指定值后的数组 | 从数组中移除指定的值，如果值不在数组中，则不产生任何效果 |
> [2026-09-04 实测] ✅ `clear` 实测 len=0（详见 verified_20260904.md，UT11）
> [2026-09-04 实测] ✅ `indexOf` 实测 1（详见 verified_20260904.md，UT12）
> [2026-09-04 实测] ✅ `lastIndexOf` 实测 3（详见 verified_20260904.md，UT13）
> [2026-09-04 实测] ✅ `remove` 实测 arr=1,3 且返回 [1,3]（详见 verified_20260904.md，UT14）

---

## Function

> **定义文件：** `jquery.base.js`
> **类描述：** 对函数对象的扩展
> **公开方法数：** 6

| 方法签名 | 参数 | 返回值 | 描述 |
| --- | --- | --- | --- |
| `createCallback( )` | 无 | `Function` | 将函数绑定到全局域上。示例：`var x = t.createCallback("abc"); window.x();` |
| `createDelegate( obj, args, appendArgs )` | `obj : Object` — 函数内部 this 作用域的范围；`args : Array` — 参数数组；`appendArgs : Array` — 如果是 Boolean 型且值为 true，args 参数将跟在调用代理方法时传入的参数后面组成数组一起传入当前方法，否则只传入 args；如果为 Number 型，args 将插入到指定位置 | `Function` | 函数的代理，更改原函数的参数和 this 作用域 |
| `createInterceptor( fcn, scope )` | `fcn : Function` — 阻断函数；`scope : Object` — 作用域 | `*` | 创建阻断方法，如果 fcn 返回 false，原方法将不会被执行 |
| `createSequence( fcn, scope )` | `fcn : Function` — 组合添加的 fcn 函数；`scope : Object` — 函数作用域 | `*` | 创建组合函数，将执行原函数以及 fcn 函数 |
| `defer( millis, obj, args, appendArgs )` | `millis : Number` — 延迟的毫秒数；`obj : Object` — 函数的 this 作用域；`args : Array` — 参数；`appendArgs : Array` — 同 createDelegate 函数的最后一个参数说明 | `Number` | 让函数延迟执行 |
| `getNameArguments( )` | 无 | `String[]` — 函数的参数列表组成的数组 | 通过函数名获取函数的参数列表 |
> [2026-09-04 实测] ✅ `createCallback` 实测输出 AB（详见 verified_20260904.md，UT19）
> [2026-09-04 实测] ✅ `createDelegate` 实测 this 代理返回 42（详见 verified_20260904.md，UT20）
> [2026-09-04 实测] ✅ `createInterceptor` 阻断时 called=false 返回 undefined；放行时 called=true 返回原结果（详见 verified_20260904.md，UT21）
> [2026-09-04 实测] ✅ `createSequence` 实测按序执行 a,b（详见 verified_20260904.md，UT22）
> [2026-09-04 实测] ✅ `defer` 延迟执行生效（返回句柄，实际延迟 60ms＞50ms 设定值，属正常调度误差）（详见 verified_20260904.md，UT23R2）
> [2026-09-04 实测] ✅ `getNameArguments` 实测返回 ["a","b","c"]；若个别原型无此方法属文档口径偏差，用 fn.toString() 正则解析替代（详见 verified_20260904.md，UT24）

---

## FR.Keys

> **定义文件：** `jquery.tools.js`
> **类描述：** 处理全局按键事件的类
> **公开方法数：** 3

| 方法签名 | 参数 | 返回值 | 描述 |
| --- | --- | --- | --- |
| `enable( state )` | `state : Boolean` — 事件是否有效 | `boolean` — 有效返回 true，无效返回 false | 控制给全局的 document 注册的事件是否起作用 |
| `reg( fn )` | `fn : Function` — 事件函数 | 无 | 给全局的 document 注册一个指定的函数 |
| `unreg( fn )` | `fn : Function` — 事件函数 | 无 | 从全局的 document 中移除指定的函数 |
> [2026-09-04 实测] ⚠ `enable` 功能可用，但实测返回 undefined 而非文档声称的 boolean——依赖返回值的代码须改造（详见 verified_20260904.md，UT25R2）
> [2026-09-04 实测] ✅ `reg/unreg` 注册/移除全程无异常（详见 verified_20260904.md，UT26）

---

### 备注 / 图例

- 🔒STATIC — 静态方法，通过类名直接调用（如 `String.format(...)`）。
- 🔗CHAINABLE — 链式方法，返回对象本身，可继续链式调用。
- 私有方法（如 Function 的 `arguments2Json`）已排除，仅保留公开方法。
- jQuery 原生方法（选择器、DOM 操作、AJAX、事件等）由 FR 内置的 jQuery 库提供，本表仅列出 FR 对 jQuery 对象的**补充方法**（定义于 `jquery.base.js`）。
