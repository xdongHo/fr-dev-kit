# -*- coding: utf-8 -*-
"""导出 i18n 词汇表（分类组织，供用户审阅）"""
import json, re, collections
import os
BASE = os.path.dirname(os.path.abspath(__file__))

I18N = json.load(open(os.path.join(BASE, "i18n_zh.json"), encoding="utf-8"))

# 按 key 前缀分类
cats = collections.defaultdict(list)
for k, v in I18N.items():
    # 提取主分类: key 的前几段
    parts = k.split("_")
    # 常见前缀模式: Fine-Design_Basic_Action_Copy_Name, Fine-Core_Vertical...
    if k.startswith("Fine-Design_Basic_Action"): cat = "Action菜单动作"
    elif "Widget_Type" in k: cat = "控件类型(Widget_Type)"
    elif "Widget" in k: cat = "控件(Widget)"
    elif k.startswith("Fine-Design_Form"): cat = "表单(Form)"
    elif "Chart" in k or k.startswith("Fine-Design_Chart"): cat = "图表(Chart)"
    elif "Button" in k: cat = "按钮(Button)"
    elif "Style" in k: cat = "样式(Style)"
    elif "Cell" in k: cat = "单元格(Cell)"
    elif "Data" in k or "TableData" in k or "Dataset" in k: cat = "数据/数据集(Data)"
    elif "Editor" in k: cat = "编辑器(Editor)"
    elif "Layout" in k: cat = "布局(Layout)"
    elif "Parameter" in k: cat = "参数(Parameter)"
    elif "Toolbar" in k: cat = "工具栏(Toolbar)"
    elif "Menu" in k: cat = "菜单(Menu)"
    elif "Preview" in k or "Preview" in k: cat = "预览(Preview)"
    elif "Export" in k or "Print" in k: cat = "导出打印(Export/Print)"
    elif "Hyperlink" in k: cat = "超链接(Hyperlink)"
    elif "Font" in k: cat = "字体(Font)"
    elif "Border" in k: cat = "边框(Border)"
    elif "BackGround" in k or "Background" in k: cat = "背景(Background)"
    elif "Report" in k: cat = "报表(Report)"
    elif "Mobile" in k: cat = "移动端(Mobile)"
    elif k.startswith("Fine-Design_Basic"): cat = "基础通用(Basic)"
    elif k.startswith("Fine-Core"): cat = "核心(Core)"
    else: cat = "其他(Other)"
    cats[cat].append((k, v))

# 输出 Markdown
out = ["# FR 设计器 i18n 词汇表（3776 条）", ""]
out.append(f"> 来源: main_zh(3028) + chart_zh(755) + dimension_zh(14) = **3776 条**")
out.append("")
out.append("## 分类统计")
out.append("")
out.append("| 分类 | 数量 |")
out.append("|------|------|")
for cat in sorted(cats, key=lambda c: -len(cats[c])):
    out.append(f"| {cat} | {len(cats[cat])} |")
out.append("")

for cat in sorted(cats, key=lambda c: -len(cats[c])):
    out.append(f"## {cat} ({len(cats[cat])} 条)")
    out.append("")
    out.append("| key | 中文名 |")
    out.append("|-----|--------|")
    for k, v in sorted(cats[cat])[:120]:
        out.append(f"| `{k}` | {v} |")
    if len(cats[cat]) > 120:
        out.append(f"| ... | 其余 {len(cats[cat])-120} 条略 |")
    out.append("")

path = os.path.join(BASE, "i18n_词汇表.md")
open(path, "w", encoding="utf-8").write("\n".join(out))
print(f"已导出 {path}")

# 控制台显示分类统计
print("\n分类统计:")
for cat in sorted(cats, key=lambda c: -len(cats[c])):
    print(f"  {cat}: {len(cats[cat])}")
