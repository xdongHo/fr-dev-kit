# -*- coding: utf-8 -*-
"""重建后重填 cn_name（类级 + 方法级 i18n 映射）
集成进 build_bom_methods.py 类似流程: build_kb.py rebuild 后自动调用
"""
import json, sqlite3, os
import os
BASE = os.path.dirname(os.path.abspath(__file__))

DB = os.path.join(BASE, "api_kb.sqlite")
I18N = json.load(open(os.path.join(BASE, "i18n_zh.json"), encoding="utf-8"))

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 类级映射（控件面板名 → Java 类）
WIDGET_CN = {
    "文本框控件": "com.fr.form.ui.TextEditor", "数字框控件": "com.fr.form.ui.NumberEditor",
    "日期框控件": "com.fr.form.ui.DateEditor", "时间框控件": "com.fr.form.ui.TimeEditor",
    "下拉框控件": "com.fr.form.ui.ComboBox", "下拉复选框控件": "com.fr.form.ui.ComboCheckBox",
    "复选按钮控件": "com.fr.form.ui.CheckBox", "复选框组控件": "com.fr.form.ui.CheckBoxGroup",
    "单选按钮控件": "com.fr.form.ui.Radio", "单选按钮组控件": "com.fr.form.ui.RadioGroup",
    "文本域控件": "com.fr.form.ui.TextArea", "密码框控件": "com.fr.form.ui.Password",
    "文件控件": "com.fr.form.ui.FileControl", "列表控件": "com.fr.form.ui.ListEditor",
    "树控件": "com.fr.form.ui.TreeComboBox", "下拉树控件": "com.fr.form.ui.TreeComboBoxEditor",
    "滑块控件": "com.fr.form.ui.Slider", "评分控件": "com.fr.form.ui.Score",
    "标签控件": "com.fr.form.ui.Label", "按钮控件": "com.fr.form.ui.Button",
    "自定义按钮": "com.fr.form.ui.FreeButton", "查询按钮": "com.fr.form.parameter.FormSubmitButton",
    "提交按钮": "com.fr.form.parameter.FormSubmitButton", "报表块": "com.fr.form.ui.ReportBlock",
    "图表块": "com.fr.form.ui.ChartEditor", "表格": "com.fr.form.ui.ElementCaseEditor",
    "绝对布局": "com.fr.form.ui.container.WAbsoluteLayout", "自适应布局": "com.fr.form.ui.container.WFitLayout",
    "栅格布局": "com.fr.form.ui.container.WGridLayout", "卡片布局": "com.fr.form.ui.container.WCardMainBorderLayout",
    "折叠面板": "com.fr.form.ui.container.WFoldLayout", "Tab布局": "com.fr.form.ui.container.WTabLayout",
    "标题布局": "com.fr.form.ui.container.WTitleLayout", "分栏布局": "com.fr.form.ui.container.WTitleLayout",
}
n_cls = 0
for cn, cls in WIDGET_CN.items():
    short = cls.split(".")[-1] if "." in cls else cls
    row = cur.execute("SELECT part_id FROM parts WHERE class_name=? AND name=? LIMIT 1", (cls, short)).fetchone()
    if not row:
        row = cur.execute("SELECT part_id FROM parts WHERE class_name=? LIMIT 1", (cls,)).fetchone()
    if row:
        cur.execute("UPDATE parts SET cn_name=? WHERE part_id=?", (cn, row[0]))
        n_cls += 1

# 方法级映射（i18n 属性词 → setter 方法）
SETTER_CN = {}
for k, v in I18N.items():
    low = k.lower()
    for kw in ["Watermark", "Water_Mark"]:
        if kw.lower() in low: SETTER_CN.setdefault("setWatermark", set()).add(v)
    for kw in ["Multiple_Selection", "Mutiple_Selection"]:
        if kw.lower() in low: SETTER_CN.setdefault("setMultipleSelection", set()).add(v)
    for kw in ["Return_Full_Path"]:
        if kw.lower() in low: SETTER_CN.setdefault("setReturnFullPath", set()).add(v)
    for kw in ["Select_Leaf_Only", "Leaf_Only"]:
        if kw.lower() in low: SETTER_CN.setdefault("setReturnLeafNodeOnly", set()).add(v)
    for kw in ["Allow_Blank", "AllowBlank"]:
        if kw.lower() in low: SETTER_CN.setdefault("setAllowBlank", set()).add(v)
    for kw in ["Allow_Edit", "AllowEdit"]:
        if kw.lower() in low: SETTER_CN.setdefault("setAllowEdit", set()).add(v)
    for kw in ["Visible", "Visibility"]:
        if kw.lower() in low and len(v) < 10: SETTER_CN.setdefault("setVisible", set()).add(v)

n_method = 0
for method, cns in SETTER_CN.items():
    rows = cur.execute("SELECT part_id FROM parts WHERE name=?", (method,)).fetchall()
    for (pid,) in rows:
        old = cur.execute("SELECT cn_name FROM parts WHERE part_id=?", (pid,)).fetchone()[0] or ""
        names = sorted(cns)
        new = old + (";" + ";".join(names) if old else ";".join(names))
        cur.execute("UPDATE parts SET cn_name=? WHERE part_id=?", (new, pid))
        n_method += 1

conn.commit()
print(f"类级 cn_name: {n_cls}, 方法级 cn_name: {n_method}")
conn.close()
