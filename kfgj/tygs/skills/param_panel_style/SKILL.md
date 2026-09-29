<!--
KB_INDEX: {
  "title": "param_panel_style.py — 参数面板样式模板",
  "stage": "tool",
  "tags": ["补头20260929"],
  "keywords": ["CSS", "build_style_css", "param_panel_style", "style", "afterinit", "import"],
  "summary": "--- name: param-panel-style description: 参数面板按钮/CSS 样式定制时使用：生成参数面板 afterinit jQuery 注入的 style 内容、按钮蓝/灰主题与宽度、换报表复用面板样式时触发"
}
-->

---
name: param-panel-style
description: 参数面板按钮/CSS 样式定制时使用：生成参数面板 afterinit jQuery 注入的 style 内容、按钮蓝/灰主题与宽度、换报表复用面板样式时触发。关键词：param_panel_style、build_style_css、参数面板 CSS、按钮样式、afterinit、BLUE_BTN_IDS。
---

# param_panel_style.py — 参数面板样式模板

一句话：生成「参数面板 para 初始化事件(afterinit) 里用 jQuery 注入的 `<style>` 内容」；不同报表只改按钮三个变量，其余样式静态复用（示例项目系列 2026-08-05 用户定稿）。

## 用法（逐字，import 型脚本，无 CLI）

```python
from param_panel_style import build_style_css
css = build_style_css()               # 默认按钮变量
css = build_style_css(blue_ids=[...], custom_btns=[...])  # 换报表时覆盖
```

自定义按钮"变量化"（改列表即可）：
- `CUSTOM_BTN_W` : [widgetname=X] 自定义按钮宽度/margin/float 规则
- `BLUE_BTN_IDS` : #fr-btn-XXX 蓝色主题按钮（背景 #3676C5）
- `GRAY_BTN_IDS` : #fr-btn-XXX 灰色按钮（CANCLE）

⚠ AGENTS.md 铁律：涉及参数面板样式的任务必须先查本脚本 `build_style_css()` 复用，禁止手写 CSS。

## 典型调用

- fmt_wildcard.py 内置复用本脚本 CSS（通配规则 A-①）
- 新报表: import build_style_css 传 custom_btns/blue_ids 覆盖，勿复制粘贴改 CSS 正文

## references（细节指路）

- 脚本本体: `kfgj/tygs/CPT模板/默认格式/param_panel_style.py`（STATIC_CSS 全文/默认按钮清单见源码）
- 知识背景: `ckzl/lc/06_Web呈现层.md` §22 CSS 注入
