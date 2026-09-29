# -*- coding: utf-8 -*-
"""
param_panel_style.py — 参数面板样式模板（示例报表工程系列，2026-08-05 用户定稿）

用途：生成「参数面板 para 初始化事件(afterinit) 里用 jQuery 注入的 <style> 内容」。
用法：
    from param_panel_style import build_style_css
    css = build_style_css()               # 默认按钮变量
    css = build_style_css(blue_ids=[...], custom_btns=[...])  # 换报表时覆盖

自定义按钮"变量化"（用户要求）：
  - CUSTOM_BTN_W : [widgetname=X] 自定义按钮宽度/margin/float 规则
  - BLUE_BTN_IDS : #fr-btn-XXX 蓝色主题按钮（背景 #3676C5）
  - GRAY_BTN_IDS : #fr-btn-XXX 灰色按钮（CANCLE）
不同报表按钮名不同 → 改这三个列表即可，其余样式静态复用。
"""

# 自定义按钮变量（widgetname → (宽, margin/float 规则)）
CUSTOM_BTN_W = [
    ('CHECK',    120, '0 auto !important'),
    ('COMPLETE', 120, '0 auto !important'),
    ('BACK',     120, 'right !important'),
    ('SUBMIT',   120, 'right !important'),
    ('CORRECT',  120, 'right !important'),
    ('SEARCH',    70, None),
    ('Import',   112, None),
]

# 蓝色主题按钮 ID（背景 #3676C5）
BLUE_BTN_IDS = [
    'FORMSUBMIT0', 'FORMSUBMIT1', 'FORMSUBMIT2', 'FORMSUBMIT3',
    'SEARCH', 'BACK', 'EXCEL', 'COMPLETE', 'SUBMIT', 'CHECK', 'CONFIRM', 'CORRECT',
    'UPLOAD_ATTACHMENT', 'DELETE_ATTACHMENT', 'CORRECT_CHECK', 'Import',
]

# 灰色按钮 ID（背景 #e9e9e9，文字 #585858）
GRAY_BTN_IDS = ['CANCLE']

# ============ 静态样式（通用，不随报表变） ============
STATIC_CSS = r"""
/*cpt模板*/
.fr-combo-list {
	overflow: hidden !important;
}

.fr-combo-list:hover {
	overflow: auto !important;
}

.fr-combo-list::-webkit-scrollbar {
	width: 6px;
	height: 6px;
}

.fr-combo-list::-webkit-scrollbar {
	width: 6px;
	height: 6px;
}

/* 滚动条的外层滑轨背景颜色 */
.fr-combo-list::-webkit-scrollbar-track-piece {
	background-color: transparent;
}

/* 滚动条的内层滑轨背景颜色 */
.fr-combo-list::-webkit-scrollbar-track-piece {
	background-color: #ebebed;
}

.fr-combo-list::-webkit-scrollbar-track-piece:no-button {
}

/*滚动条鼠标默认样式*/
.fr-combo-list::-webkit-scrollbar-thumb {
	background-color: #c7c7c7;
	border-radius: 2px;
}

/*滚动条鼠标悬浮样式*/
.fr-combo-list::-webkit-scrollbar-thumb:hover {
	background-color: #888888;
}

/*滚动条激活样式*/
.fr-combo-list::-webkit-scrollbar-thumb:active {
	background-color: #888888;
}

/*上下按钮样式*/
.fr-combo-list::-webkit-scrollbar-button {
	background-color: #ebebed;
}

/** 下拉框样式***/
.fr-combo-list-item {
	font-family: Microsoft YaHei !important;
}

.fr-combo-list-item.fr-combo-selected {
	color: #0f82ef !important;
	background-color: #c3def9 !important;
}

/*****mask层样式**************************************************************************************/
#popup_overlay {
	background-color: #333333 !important;
	opacity: 0.3 !important;
}

/*****CPT页面展示右下偏移*******************************************************************************/
#content-container {
	left: 20px !important;
}

.parameter-container .fr-horizontalboxlayout.ui-state-enabled {
	background: white;
}
.parameter-container [widgetname=__layout4align__] {
	background: transparent !important;
}

/*冻结滚动条不偏移*/
#content-container .slimScrollBarY {
	right: 21px !important;
}
#frozen-center ~ .slimScrollBarX{
	height: 22px !important;
}

/***收缩小三角****************************************************************************************/
.parameter-container-collapseimg-up {
	display: none !important;
}

/****插入/删除***************************************************************************************/
#fr-btn-INSERT {
	background: none !important;
}

#fr-btn-DELETE {
	background: none !important;
}

/***填报边框****************************************************************************************/
#fDtop {
	background-color: #3296f5 !important;
}

#fDleft {
	background-color: #3296f5 !important;
}

#fDbottom {
	background-color: #3296f5 !important;
}

#fDright {
	background-color: #3296f5 !important;
}

/****控件样式***************************************************************************************/
.fr-trigger-text {
	border-radius: 4px 0 0 4px;
	border-right: 0px;
}

.fr-texteditor {
	border-radius: 4px;
}

.ui-state-enabled.fr-form-imgboard {
	border-radius: 4px;
}

.ui-state-enabled.fr-form-imgboard div {
	border-radius: inherit;
}

.fr-trigger-btn-up {
	border-radius: 0 4px 4px 0;
	background-color: rgba(255, 255, 255, 1);
	background: rgba(255, 255, 255, 1);
}

.fr-trigger-btn-over {
	border-radius: 0 4px 4px 0;
	background-color: rgba(255, 255, 255, 1);
	background: rgba(255, 255, 255, 1);
}

.fr-trigger-btn-down {
	border-radius: 0 4px 4px 0;
	background-color: rgba(255, 255, 255, 1);
	background: rgba(255, 255, 255, 1);
}

.fr-trigger-center {
	background: url(data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%2712%27%20height=%2712%27%20viewBox=%270%200%2012%2012%27%3E%3Cpath%20d=%27M2%204l4%204%204-4z%27%20fill=%27%238a8a8a%27/%3E%3C/svg%3E) no-repeat 0 0;
	margin-top: 25% !important;
	height: 100%;
}

.fr-date-trigger-center {
	background: url(data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20width=%2712%27%20height=%2712%27%20viewBox=%270%200%2012%2012%27%3E%3Crect%20x=%272%27%20y=%272%27%20width=%278%27%20height=%278%27%20fill=%27none%27%20stroke=%27%238a8a8a%27/%3E%3Cpath%20d=%27M2%205h8M4%200v3M8%200v3%27/%3E%3C/svg%3E) no-repeat 0 0;
	margin-top: 20% !important;
	height: 100%;
}

.fr-tree ul,
.fr-tree li {
	font-family: Microsoft YaHei !important;
}

.fr-label {
	font-family: Microsoft YaHei !important;
}

/******按钮********************************************************************************************/
.fr-btn-text {
	font-size: 12px !important;
}

.fr-btn-up.fr-btn-noicon .fr-btn-text {
	height: 20px !important;
}

/**** 确认框 ***************************************************************************************************/
#popup_message {
	text-align: left !important;
}

#popup_content {
	background-position: left !important;
}

/*****弹出框******************************************************************************************************/
#popup_message {
	font-family: Microsoft YaHei !important;
	color: #333333 !important;
	font-weight: normal !important;
	font-size: 15px !important;
}

#popup_title {
	font-family: Microsoft YaHei !important;
	font-weight: normal !important;
	font-size: 15px !important;
}

#popup_header {
	background-color: #3676C5 !important;
}

div.fr-core-btn-style-blue {
	background: #3676C5 !important;
}

.fr-core-btn-inner .fr-core-btn-text {
	font-size: 13px !important;
}

/*toolbar********************************************************************************************************/
.x-toolbar.ui-state-enabled.fs-tab-content-top-toolbar>table {
	margin-left: 20px;
}

.fr-core-panel-body.fr-core-panel-body-border.fr-core-window-body {
	border: none !important;
}

.fr-core-panel-header.fr-core-panel-style-blue.fr-core-window-header {
	background-color: #3676C5 !important;
}

.fr-core-panel-title {
	font-family: Microsoft YaHei !important;
	font-weight: normal !important;
	font-size: 14px !important;
}

/******* sheet页样式**********************************************************************************************/
.fr-sheetbutton-middlepart-top {
	font-size: 13.33px !important;
}

.fr-tabpane-controlbuttons.ui-state-enabled {
	width: 14px !important;
}

.ui-state-enabled.fr-edit-sheetcontrol-icon-box,.parameter-container-collapseimg-up {
	display: none !important;
}

textarea,span,button,input,pre,.fr-combo-list-item {
	font-family: Microsoft YaHei !important;
}

.x-toolbar.ui-state-enabled.fs-tab-content-top-toolbar>table {
	margin-left: 20px !important;
}

.fr-tabpane-tabscontent-bg {
	left: 0px !important;
	width: 100% !important;
	background: white !important;
}

.fr-tabpane-tabscontent.fr-tabpane-tabscontent-top,.fr-tabpane-controlbuttons.ui-state-enabled {
	background: white !important;
}

.fr-sheetbutton-firstpart-top,.fr-sheetbutton-middlepart-top,.fr-sheetbutton-thirdpart-top,.fr-sheetbutton-endpart-top {
	background: none !important;
}

.fr-sheetbutton-firstpart-top-invalidate,.fr-sheetbutton-middlepart-top-invalidate,.fr-sheetbutton-thirdpart-top-invalidate,.fr-sheetbutton-endpart-top-invalidate {
	background: none !important;
}

.fr-sheetbutton-firstpart-top-invalidate-style2,.fr-sheetbutton-middlepart-top-invalidate-style2,.fr-sheetbutton-thirdpart-top-invalidate-style2,.fr-sheetbutton-endpart-top-invalidate-style2 {
	background: none !important;
}

.fr-sheetbutton-firstpart-top-invalidate-style3,.fr-sheetbutton-middlepart-top-invalidate-style3,.fr-sheetbutton-thirdpart-top-invalidate-style3,.fr-sheetbutton-endpart-top-invalidate-style3 {
	background: none !important;
}

.fr-sheetbutton-firstpart-top-invalidate-style4,.fr-sheetbutton-middlepart-top-invalidate-style4,.fr-sheetbutton-thirdpart-top-invalidate-style4,.fr-sheetbutton-endpart-top-invalidate-style4 {
	background: none !important;
}

.fr-sheetbutton-firstpart-top-invalidate {
	width: 0px !important;
}

.fr-sheetbutton-thirdpart-top-invalidate,.fr-sheetbutton-endpart-top-invalidate {
	width: 10px !important;
}

.fr-sheetbutton-thirdpart-top-invalidate-style2,.fr-sheetbutton-endpart-top-invalidate-style2 {
	width: 10px !important;
}

.fr-sheetbutton-thirdpart-top-invalidate-style3,.fr-sheetbutton-endpart-top-invalidate-style3 {
	width: 10px !important;
}

.fr-sheetbutton-thirdpart-top-invalidate-style4,.fr-sheetbutton-endpart-top-invalidate-style4 {
	width: 10px !important;
}

.fr-sheetbutton-middlepart-top-invalidate {
	margin-left: 10px !important;
}

.fr-sheetbutton-firstpart-top {
	display: none !important;
}

.fr-sheetbutton-middlepart-top {
	margin-left: 10px !important;
	margin-top: 1px !important;
}

.fr-sheetbutton-thirdpart-top {
	width: 10px !important;
}

.fr-sheetbutton-endpart-top {
	width: 10px !important;
}

.ui-state-enabled.fr-sheetbutton-container.fr-sheetbutton-container-active {
	color: white !important;
	background: #3676C5 !important;
}

.fr-tabpane-tabscontent.fr-tabpane-tabscontent-top {
	top: 0px !important;
}

.fr-tabpane-tabswrap {
	top: 0px !important;
	height: 25px !important;
}

.fr-tabpane-tabscontent.fr-tabpane-tabscontent-top {
	top: 0px !important;
	height: 30px !important;
}

#content-container .fr-quick-border-layout.ui-state-enabled {
	height: 40px !important;
}

.ui-state-enabled.fr-sheetbutton-container {
	height: 25px !important;
	background: #EDEDED !important;
	color: #555555 !important;
	border: 1px #ffffff solid !important;
}
/************ verify error tips ***********************************************************************************************/
.view-container {
	top: 6px !important;
}

.verify-error-s {
	top: -15px !important;
}

.verify-error-messages {
	left: 40px  !important;
}

.verify-error-info {
	display: none  !important;
}

/************复选框按钮组样式*************/
.x-text.fr-widget-click {
	font-size: 13.33px !important;
	color: #333 !important;
}
"""


def build_style_css(custom_btns=None, blue_ids=None, gray_ids=None):
    """拼接完整 <style> 内容（变量化按钮段 + 静态段）。
    custom_btns: [(widgetname, width, rule)]  rule=None 则不输出 margin/float 行
    blue_ids / gray_ids: 按钮 ID 列表

    选择器统一「大写 + 原样 + 小写」三写：FR 前端渲染 widgetname/id 时把
    WidgetName **统一转大写**（cpt 里 `WidgetName name="Import"` 渲染成
    `widgetname="IMPORT"` / `id="fr-btn-IMPORT"`，实测 2026-08-06），CSS 属性/ID
    选择器大小写敏感 → 三写保证任意命名习惯都命中。
    """
    def variants(name):
        """去重保序输出: 大写、原样、小写"""
        return list(dict.fromkeys([name.upper(), name, name.lower()]))

    def w_sel(name):
        """[widgetname=X] 属性选择器（大写/原样/小写）"""
        return ', '.join(f'[widgetname="{v}"]' for v in variants(name))

    def id_sel(name):
        """#fr-btn-X ID 选择器（大写/原样/小写）"""
        return ', '.join(f'#fr-btn-{v}' for v in variants(name))

    cbtns = custom_btns if custom_btns is not None else CUSTOM_BTN_W
    blues = blue_ids if blue_ids is not None else BLUE_BTN_IDS
    grays = gray_ids if gray_ids is not None else GRAY_BTN_IDS

    parts = []
    parts.append("/******自定义按钮（变量化，选择器大小写双写）******/")
    for name, w, rule in cbtns:
        parts.append(f"{w_sel(name)} {{")
        parts.append(f"\twidth: {w}px !important;")
        if rule:
            key = 'float' if rule.startswith(('right', 'left')) else 'margin'
            parts.append(f"\t{key}: {rule};")
        parts.append("}")
        parts.append(f"{id_sel(name)} .fr-btn-text {{")
        parts.append("\tfont-size: 12px !important;")
        parts.append("}")
        parts.append("")
    # 蓝色主题按钮（含自定义按钮的 ID 版背景）
    for bid in blues:
        parts.append(f"{id_sel(bid)} {{")
        parts.append("\tbackground: #3676C5 !important;")
        parts.append("}")
    parts.append("")
    # 灰色按钮
    for gid in grays:
        parts.append(f"{id_sel(gid)} {{")
        parts.append("\tbackground: #e9e9e9 !important;")
        parts.append("}")
        parts.append(f"{id_sel(gid)} button {{")
        parts.append("\tcolor: #585858 !important;")
        parts.append("}")
        parts.append("")
    parts.append(STATIC_CSS)
    return "\n".join(parts)


def afterinit_js(css):
    """构造 para 初始化事件(afterinit) 的完整 JS：保留原逻辑 + jQuery 注入 <style>。

    必须把 CSS 里的换行/回车/反斜杠/单引号全部转义成 JS 字符串内的合法序列——
    否则多行 CSS 直接嵌入单引号字符串会报 `SyntaxError: Invalid or unexpected token`
    （实测 2026-08-05：示例模块 注入后设计器报错，根因就是原始 \\n 未转义）。

    末尾的 /* param_panel_style */ 注释是幂等标记：inject_panel_style.py 检测到
    该标记即跳过，避免重复注入。"""
    esc = (css.replace('\\', '\\\\')
              .replace("'", "\\'")
              .replace('\r', '\\r')
              .replace('\n', '\\n'))
    return (
        '$("body .x-toolbar.ui-state-enabled table").eq(0).css("margin-left", "15px");\n'
        '$("<style>" + \'' + esc + '\' + "</style>").appendTo("head");\n'
        '/* param_panel_style */'
    )
