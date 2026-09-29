# -*- coding: utf-8 -*-
"""fr-agent 反射枚举 FR API → 生成细粒度零件（api_reflect_parts.py）
用法: python reflect_api.py [--dry-run]
通过 fr-agent /exec 在设计器 JVM 内 Class.forName + getMethods 枚举真实方法
"""
import json, sys, os, urllib.request, sqlite3
BASE = os.path.dirname(os.path.abspath(__file__))

EXEC = "http://localhost:19000/exec"
OUT = os.path.join(BASE, "api_reflect_parts.py")
DRY = "--dry-run" in sys.argv

# 关注类（手动精选，覆盖所有控件的核心类）
CLASSES = [
    # 控件 form.ui
    "com.fr.form.ui.TextEditor","com.fr.form.ui.NumberEditor","com.fr.form.ui.DateEditor",
    "com.fr.form.ui.ComboBox","com.fr.form.ui.ComboCheckBox","com.fr.form.ui.CheckBox",
    "com.fr.form.ui.CheckBoxGroup","com.fr.form.ui.RadioGroup","com.fr.form.ui.TextArea",
    "com.fr.form.ui.Label","com.fr.form.ui.FreeButton","com.fr.form.ui.TreeComboBoxEditor",
    "com.fr.form.ui.TreeComboBox","com.fr.form.ui.WidgetValue","com.fr.form.ui.Widget",
    "com.fr.form.ui.ElementCaseEditor","com.fr.form.ui.TableDataDict","com.fr.form.ui.Dictionary",
    "com.fr.form.ui.TreeDictionary","com.fr.form.ui.MultiSelectComboBox","com.fr.form.ui.TimeEditor",
    "com.fr.form.ui.Password","com.fr.form.ui.FileControl","com.fr.form.ui.ListEditor",
    "com.fr.form.ui.Slider","com.fr.form.ui.Score","com.fr.form.ui.Button","com.fr.form.ui.Image",
    "com.fr.form.ui.Radio","com.fr.form.ui.ComboTree",
    # 参数
    "com.fr.form.parameter.FormSubmitButton","com.fr.form.parameter.ReportParameterUI",
    "com.fr.form.ui.parameter.ReportParameterUI",
    # 容器
    "com.fr.form.ui.container.WFitLayout","com.fr.form.ui.container.WBorderLayout",
    "com.fr.form.ui.container.WAbsoluteBodyLayout","com.fr.form.ui.container.WAbsoluteLayout",
    "com.fr.form.ui.container.WParameterLayout","com.fr.form.ui.container.WCardMainBorderLayout",
    "com.fr.form.ui.container.WGridLayout","com.fr.form.ui.container.WTitleLayout",
    "com.fr.form.ui.container.WTabLayout","com.fr.form.ui.container.WFoldLayout",
    # 表单/图表
    "com.fr.form.main.Form","com.fr.form.ui.ChartEditor","com.fr.report.worksheet.FormElementCase",
    "com.fr.report.cell.DefaultTemplateCellElement","com.fr.report.cell.cellattr.CellGUIAttr",
    "com.fr.report.cell.TemplateCellElement",
    # 样式/数据
    "com.fr.report.style.Style","com.fr.report.style.BorderAttr","com.fr.base.background.ColorBackground",
    "com.fr.data.impl.EmbeddedTableData","com.fr.data.impl.DBTableData","com.fr.data.TableDataDictionary",
    "com.fr.data.FormulaDictionary","com.fr.data.impl.NameDatabaseConnection",
    "com.fr.base.Formula","com.fr.stable.unit.FU","com.fr.form.event.Listener",
    # 图表
    "com.fr.chart.ChartTypeManager",
    "com.fr.plugin.chart.column.ColumnIndependentVanChart","com.fr.plugin.chart.bar.BarIndependentVanChart",
    "com.fr.plugin.chart.line.LineIndependentVanChart","com.fr.plugin.chart.pie.PieIndependentVanChart",
    "com.fr.plugin.chart.area.AreaIndependentVanChart","com.fr.plugin.chart.scatter.ScatterIndependentVanChart",
    "com.fr.plugin.chart.bubble.BubbleIndependentVanChart","com.fr.plugin.chart.radar.RadarIndependentVanChart",
    "com.fr.plugin.chart.funnel.FunnelIndependentVanChart","com.fr.plugin.chart.treemap.TreemapIndependentVanChart",
    "com.fr.plugin.chart.wordcloud.WordCloudIndependentVanChart","com.fr.plugin.chart.force.ForceIndependentVanChart",
    "com.fr.plugin.chart.multiLayerColumn.MultiLayerColumnIndependentVanChart",
    "com.fr.plugin.chart.column.VanChartColumnPlot","com.fr.plugin.chart.common.VanChartPlot",
]

def exec_js(js):
    body = json.dumps({"script": js}).encode("utf-8")
    req = urllib.request.Request(EXEC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def reflect(cls):
    """Nashorn 反射: 返回该类所有 public 方法名数组"""
    js = f"""
    var C = Java.type("{cls}");
    var out = [];
    var ms = C.class.getMethods();
    for (var i=0;i<ms.length;i++){{ var n = ms[i].getName(); if(out.indexOf(n)<0) out.push(n); }}
    JSON.stringify(out);
    """
    try:
        r = exec_js(js)
        if r.get("status") == "ok" and r.get("result"):
            return json.loads(r["result"])
        return []
    except Exception as e:
        return []

def main():
    cls_methods = {}
    total = len(CLASSES)
    for i, cls in enumerate(CLASSES):
        methods = reflect(cls)
        if methods:
            cls_methods[cls] = methods
        print(f"[{i+1}/{total}] {cls}: {len(methods)} 方法")
        if (i+1) % 20 == 0:
            import time; time.sleep(1)  # 温和限速

    print(f"\n共 {len(cls_methods)} 个类可反射")
    total_m = sum(len(v) for v in cls_methods.values())
    print(f"方法总数: {total_m}")

    conn = sqlite3.connect(os.path.join(BASE, "api_kb.sqlite"))
    existing = set((r[0], r[1]) for r in conn.execute("SELECT name, class_name FROM parts").fetchall())
    conn.close()
    new_count = 0
    for cls, methods in cls_methods.items():
        for m in methods:
            if (m, cls) not in existing:
                new_count += 1
    print(f"新增方法: {new_count}")
    if DRY:
        print("[dry-run] 未生成"); return

    def cat_of(cls):
        if cls.startswith("com.fr.form.ui"): return "WIDGET"
        if "parameter" in cls: return "PARAM"
        if "container" in cls: return "CONTAINER"
        if cls.startswith("com.fr.data"): return "DATASET"
        if cls.startswith("com.fr.report") or "Cell" in cls: return "CPT_BUILD"
        if "Style" in cls or "Border" in cls: return "STYLE"
        if "Chart" in cls or "chart" in cls: return "CHART"
        if cls.startswith("com.fr.io"): return "IO"
        if cls.startswith("com.fr.base") or "FU" in cls: return "UTIL"
        if "Listener" in cls or "event" in cls: return "EVENT"
        return "OTHER"

    lines = ['# -*- coding: utf-8 -*-',
             '"""fr-agent 反射枚举的 FR API 细粒度零件（自动生成自 reflect_api.py，勿手改）"""',
             '', 'EXTRA_PARTS = [']
    next_no = 205
    for cls in sorted(cls_methods):
        short = cls.split(".")[-1]
        for m in sorted(cls_methods[cls]):
            if (m, cls) in existing:
                continue
            cat = cat_of(cls)
            row = '    ("P-{:04d}", "{}", "{}", "{}(...)", "{}", "{} 的方法（fr-agent 反射枚举）", "-", "-", "反射枚举，未逐个实测，使用前核对", "fr-agent反射", 0),'.format(next_no, m, cls, m, cat, short)
            lines.append(row)
            next_no += 1
    lines.append(']')
    lines.append('')
    open(OUT, "w", encoding="utf-8").write("\n".join(lines))
    print(f"已生成 {OUT}，编号 P-0205..P-{next_no-1:04d}")

if __name__ == "__main__":
    main()
