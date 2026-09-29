<!--
KB_INDEX: {
  "title": "Stage 6 · 参数面板 CSS 注入",
  "stage": "pipeline",
  "tags": [
    "CSS",
    "Web",
    "工具栏",
    "注入"
  ],
  "keywords": [
    "CSS注入",
    "CSSImport",
    "afterinit",
    "参数面板样式"
  ],
  "summary": "CSSImport 注入位置、afterinit 事件、参数面板样式覆盖"
}
-->

# Stage 6 · 参数面板 CSS 注入

> 本页为 [06_Web呈现层.md](06_Web呈现层.md) 拆分分篇 2/4（2026-09-29 断链治理，单篇 ≤400 行）；返回 [导航页](06_Web呈现层.md)。

---

## 22. 参数面板 CSS 注入（Ver0.4 新增）
> 问法入口（2026-09-13 收官补，S-014）：「页面引入自定义css」「自定义样式表怎么加进报表」→ 本节 CSSImport/afterinit 注入（铁律 I）。

### 22.1 初始化事件位置

参数面板 CSS 注入通过 `<Listener event="afterinit">` 实现，**必须放在 `<Layout>` 内部、`<WidgetName name="para"/>` 之前**：

```xml
<ParameterUI class="com.fr.form.main.parameter.FormParameterUI">
  <Parameters/>
  <Layout class="com.fr.form.ui.container.WParameterLayout">
    <Listener event="afterinit" name="初始化后1">
      <JavaScript class="com.fr.js.JavaScriptImpl">
        <Parameters/>
        <Content><![CDATA[
$(function() {
    var css = "...";
    $("<style>").prop("type", "text/css").html(css).appendTo("head");
});
        ]]></Content>
      </JavaScript>
    </Listener>
    <WidgetName name="para"/>
    ...
  </Layout>
  <DesignAttr .../>
</ParameterUI>
```

> ⚠️ **不要放在 `</Layout>` 之后**——那是 Layout 外部，事件不会绑定到参数面板。

### 22.2 CSS 注入脚本

> 📁 `kfgj/tygs/CPT模板/默认格式/2.参数面板控件布局/` 目录下：
> - `css样式.txt` — 完整 CSS 注入代码（57 行，55 条规则）
> - `add_para_init_event.py` — 一键注入脚本，将 CSS 写入 cpt 的 afterinit 事件

### 22.3 FR 自定义按钮 CSS 选择器

FR 10.0 中自定义按钮的固定 ID 选择器，可在 CSS 注入中按需使用：

| 选择器 | 按钮 |
|--------|------|
| `#fr-btn-SEARCH` | 查询 (Search) |
| `#fr-btn-FORMSUBMIT0` | 提交 0 |
| `#fr-btn-FORMSUBMIT1` | 提交 1 |
| `#fr-btn-FORMSUBMIT2` | 提交 2 |
| `#fr-btn-FORMSUBMIT3` | 提交 3 |
| `#fr-btn-BACK` | 返回 |
| `#fr-btn-EXCEL` | 导出 Excel |
| `#fr-btn-COMPLETE` | 完成 |
| `#fr-btn-SUBMIT` | 提交 |
| `#fr-btn-CHECK` | 校验 |
| `#fr-btn-CONFIRM` | 确认 |
| `#fr-btn-CORRECT` | 修正 |
| `#fr-btn-UPLOAD_ATTACHMENT` | 上传附件 |
| `#fr-btn-DELETE_ATTACHMENT` | 删除附件 |
| `#fr-btn-CORRECT_CHECK` | 修正校验 |
| `#fr-btn-CANCLE` | 取消 |
| `#fr-btn-INSERT` | 插入行 |
| `#fr-btn-DELETE` | 删除行 |

```css
/* 示例：蓝色主题按钮 */
#fr-btn-SEARCH, #fr-btn-FORMSUBMIT0, #fr-btn-SUBMIT, #fr-btn-EXCEL {
    background: #3676C5 !important;
}
#fr-btn-CANCLE {
    background: #e9e9e9 !important;
}
#fr-btn-CANCLE button {
    color: #585858 !important;
}
```

### 22.4 一键注入命令

```powershell
python "kfgj/tygs/CPT模板/默认格式/2.参数面板控件布局/add_para_init_event.py" <cpt路径> [css文件路径]
```

- 自动创建 `_backup_YYYYMMDD_HHMMSS/` 备份
- 检测已有 `afterinit` 事件则跳过（不重复注入）
- 默认 CSS 文件：同目录下的 `css样式.txt`

### 22.5 参数面板样式模板（param_panel_style.py，Ver0.7 推荐）

> 📄 `kfgj/tygs/CPT模板/默认格式/param_panel_style.py`（2026-08-05 用户定稿全套样式）

项目报表目录系列标准样式模板（下拉滚动条 6px / 下拉选中蓝 / 填报边框 #3296f5 / 控件圆角 4px / 按钮蓝色主题 #3676C5 / 灰色 CANCLE / sheet 页 / 弹窗 / verify 提示 / 复选框组 等）。

**自定义按钮"变量化"**（不同报表按钮名不同 → 改三个列表即可）：
```python
CUSTOM_BTN_W = [('CHECK',120,'0 auto'), ('COMPLETE',120,'0 auto'), ('BACK',120,'right'),
                ('SUBMIT',120,'right'), ('CORRECT',120,'right'), ('SEARCH',70,None)]
BLUE_BTN_IDS = ['FORMSUBMIT0..3','BACK','EXCEL','COMPLETE','SUBMIT','CHECK','CONFIRM','CORRECT',
                'UPLOAD_ATTACHMENT','DELETE_ATTACHMENT','CORRECT_CHECK']
GRAY_BTN_IDS = ['CANCLE']
```

**注入方式**（para 初始化事件 afterinit 里 jQuery 追加 `<style>`）：
```python
from param_panel_style import build_style_css, afterinit_js
js = afterinit_js(build_style_css())   # 原 margin-left 逻辑 + 样式注入
```
> 注入脚本：`工作区/inject_panel_style.py`（只替换 afterinit JS，保留设计器属性/CONCATENATE/布局；备份+XML 校验）。
> ⚠️ 样式模板 CSS 无单引号/反斜杠/`]]>`，可直接拼进 jQuery 字符串；若自定义 CSS 含这些字符需转义。

---
