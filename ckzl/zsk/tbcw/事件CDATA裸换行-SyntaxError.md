<!--
KB_INDEX: {
    "title": "事件CDATA裸换行致页面SyntaxError分析",
    "stage": "error-analysis",
    "tags": [
      "错误案例",
      "🔥新沉淀",
      "JS注入",
      "程序化生成"
    ],
    "keywords": [
      "SyntaxError",
      "Invalid or unexpected token",
      "CDATA",
      "裸换行",
      "字符串未闭合",
      "node --check",
      "style注入",
      "事件JS",
      "fr_check盲区",
      "程序化生成cpt"
    ],
    "summary": "程序化往 cpt 事件 <Content> CDATA 写 JS 时把含 CSS 的多行文本拼进单引号字符串字面量、段间残留真实换行(0x0A/0x0D0A)→字符串未闭合，浏览器打开页面即 SyntaxError: Invalid or unexpected token 且整页不可用；XML 合法+fr_check 通过但上线即崩（两道校验都不查 JS 语法）；含 node --check 批量定位脚本、修复样板与预防三原则（2026-09-04 示例实际表/预算 实战）"
  }
-->

# 事件CDATA裸换行致页面SyntaxError分析

> 实战来源：2026-09-04 示例报表工程/明细报表 示例实际表.cpt / 示例预算表.cpt 程序化改写，按钮样式注入块（`$("<style>"+'…')` 模式）多段拼接时段间残留真实换行。
> 定位脚本源起 `%TEMP%\extract_check_js.py`（2026-09-04）；若 Temp 已清理，按本文 §3 重写。

---

## 1. 现象

浏览器打开报表页面**立即**抛：

```
SyntaxError: Invalid or unexpected token
```

页面整体不可用（JS 全挂）。而落盘前的两道常规校验全绿：`ET.parse` XML 合法、`fr_check.py` 通过（仅已知误报族）——**"XML 合法 + fr_check 通过"但"上线即崩"**。

## 2. 根因与盲区本质

程序化往 cpt 事件 `<Content>` CDATA 写 JS 时，把**含 CSS 的多行文本**（`xxx { width:...; }` 一段一段）拼进单引号字符串字面量，段间残留**真实换行**（0x0A / 0x0D0A）：

```js
// ❌ 坏形态：字面量内有裸换行 → Unterminated string literal
$("<style>" + '/******注释******/
[widgetname="CHECK"] {
	width: 120px;
}
' + "</style>").appendTo("head");
```

JS 字符串字面量不允许跨物理行，解析到行尾引号未闭合 → `SyntaxError: Invalid or unexpected token`。

**盲区本质**：`ET.parse` 只验 XML 合法（CDATA 内部对 XML 解析器是纯文本）；`fr_check` 只查模板级规则（参数闭合/连接名/调度标记等）；**没有任何一道静态校验检查 CDATA 里 JS 的语法**。三道全绿照样崩，这类错误只有浏览器执行时才暴露。

## 3. 定位方法：全模板 Content CDATA 逐块 node --check

把 cpt 内全部 `<Content>` CDATA 抽出来逐块落 `.js` 文件，用 `node --check` 做语法终判（需要本机有 node）。通用版脚本（源起 `%TEMP%\extract_check_js.py`，此处泛化为命令行传参）：

```python
# -*- coding: utf-8 -*-
# check_cpt_js.py — 抽取 cpt 全部 <Content> CDATA 逐块 node --check
# 用法: python check_cpt_js.py <a.cpt> [b.cpt ...]
import io, os, re, sys, subprocess, tempfile

def check_one(cpt):
    d = io.open(cpt, encoding='utf-8', newline='').read()
    tmp = tempfile.mkdtemp(prefix='cpt_js_')
    fail = 0; idx = 0
    for m in re.finditer(r'<Content>\s*<!\[CDATA\[(.*?)\]\]></Content>', d, re.S):
        idx += 1
        code = m.group(1)
        fp = os.path.join(tmp, '%02d.js' % idx)
        io.open(fp, 'w', encoding='utf-8').write(code)
        r = subprocess.run(['node', '--check', fp], capture_output=True, text=True)
        head = code.strip().splitlines()[0][:56] if code.strip() else '(empty)'
        if r.returncode == 0:
            print('  [%02d] ok   | %s' % (idx, head))
        else:
            fail += 1
            print('  [%02d] FAIL | %s' % (idx, head))
            for line in (r.stderr or '').strip().splitlines()[:6]:
                print('         ' + line)
    print('%s: %d 块, FAIL %d' % (os.path.basename(cpt), idx, fail))
    return fail

if __name__ == '__main__':
    total = sum(check_one(p) for p in sys.argv[1:])
    sys.exit(1 if total else 0)
```

要点：`node --check` 只查语法不执行，零副作用；FAILED 块的 stderr 会给出确切行列号。批量巡检多模板时按模板名给 `.js` 编号即可归位到具体 `<Content>`。

## 4. 修复：恢复单行字符串 + 转义形态

同工程已验证样板：`示例报表工程\填报报表\示例映射A.cpt` 注入块——

```js
// ✅ 正确形态：语句之间允许真实换行（语句分隔），字面量内部只有 \n \t 转义
$("body .x-toolbar.ui-state-enabled table").eq(0).css("margin-left", "15px");
$("<style>" + '/******注释******/\n[widgetname="CHECK"], [widgetname="check"] {\n\twidth: 120px !important;\n\tmargin: 0 auto !important;\n}\n…' + "</style>").appendTo("head");
```

即：整段 CSS 压进**单物理行**的字符串字面量里，换行/缩进一律 `\n`/`\t` 转义。程序化生成时等价于：拼接前把每段文本做 `text.replace('\\','\\\\').replace("'","\\'").replace('\r\n','\\n').replace('\n','\\n').replace('\t','\\t')` 再入字面量。

## 5. 预防三原则

1. **生成器/脚本硬门禁（落盘前）**：凡程序化写事件 JS，落盘前做两件事——拼接转义规整（§4 的 replace 链）+ 全模板 CDATA `node --check`（§3 脚本），**FAIL 即中止不落盘**（宁可不出文件，不可出坏文件）。
3. **拼接纪律**：多段拼 JS 禁止用真实换行做**字面量内部**的分隔；真实换行只允许出现在语句与语句之间（语句分隔符），字面量内的换行只允许转义形式存在。

## 6. 触发案例

FR 按钮样式注入：`$("<style>" + '<CSS文本>' + "</style>").appendTo("head")` 模式。CSS 天然多行多段，程序化把 N 段 CSS 文本拼接进单引号字面量时最易在段间引入裸换行（读入时 `newline=''` 保留 0x0D0A、列表 join 用 `'\n'`、或源文本本身就带换行）。示例实际表.cpt / 示例预算表.cpt（2026-09-04）即在此模式上踩雷；示例映射A.cpt 为同模式的正确参照。
