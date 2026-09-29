#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""page2tpl.py — 页面→模板逆向器 + round-trip 一一核对

A方向(逆向): 页面URL / viewlet路径 / 模板文件
  → 真引擎渲染(agent 服务端, 免登录免等待)
  → 逆向生成 .cpt(内嵌数据集=页面展示数据, 布局/跨度/值逐格还原, 图表→占位标记)
  → 逆向模板再渲染 → 与原渲染逐格比对(一一匹配核对)

用法:
  python kfgj/xlyl/page2tpl.py "http://localhost:8075/webroot/decision/view/report?viewlet=示例报表工程/.../示例预算表.cpt"
  python kfgj/xlyl/page2tpl.py "示例报表工程/.../示例预算表.cpt"        # viewlet 相对路径
  python kfgj/xlyl/page2tpl.py "C:\\...\\示例预算表.cpt"               # 直接文件
输出(out 目录): <名>_reverse.cpt(逆向模板) <名>_orig.json/<名>_reverse.json(两侧渲染产物)
               <名>_roundtrip.md(核对报告)

round-trip 断言(一一匹配):
  T1 网格规模  T2 坐标+跨度逐格  T3 值逐一(静态文本精确相等)
  T4 图表格(图表→占位标记互认)  T5 sheet 数  —— 未匹配差异=原模板问题或逆向器缺陷
"""
import argparse
import json
import os
import re
import sys
import uuid
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from expect_manifest import extract_manifest  # noqa: E402
from render_check import backend_injected     # noqa: E402

DEFAULT_REPORTLETS = r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF\reportlets"

# ══ 内嵌数据集编码器(与FR逐字节验证一致 — 源自 皮肤管理/skinstudio/gen_skeletons.py) ══

def _a85(raw):
    out = []
    for i in range(0, len(raw), 4):
        blk = raw[i:i + 4]
        v = int.from_bytes(blk.ljust(4, b"\0"), "big")
        digits = []
        for _ in range(5):
            digits.append(v % 85)
            v //= 85
        chars = "".join(chr(33 + d) for d in reversed(digits))
        out.append(chars[:len(blk) + 1] if len(blk) < 4 else chars)
    return "".join(out)


def encode_rows(rows, classes):
    lines = []
    for row in rows:
        cells = []
        for v, cls in zip(row, classes):
            if v is None:
                cells.append("")
            elif cls == "java.lang.Double":
                cells.append(str(int(v)) if float(v).is_integer() else repr(float(v)))
            else:
                cells.append(str(v).replace("\t", "&t;").replace("\n", "&n;"))
        lines.append("\t".join(cells))
    plain = "\n".join(lines).encode("utf-8")
    co = zlib.compressobj(6, zlib.DEFLATED, -15)
    return _a85(co.compress(plain) + co.flush()) + "~"


def embedded_ds(name, cols, types, rows):
    ct = ",".join(types)
    return ('<TableData name="%s" class="com.fr.data.impl.EmbeddedTableData">\n'
            '<Parameters xmlVersion="20211223" releaseVersion="10.0.0"/>\n'
            '<DSName>\n<![CDATA[]]></DSName>\n'
            '<ColumnNames>\n<![CDATA[%s]]></ColumnNames>\n'
            '<ColumnTypes>\n<![CDATA[%s]]></ColumnTypes>\n'
            '<RowData ColumnTypes="%s">\n<![CDATA[%s\n]]></RowData>\n'
            "</TableData>\n") % (name, ",,.,,".join(cols), ct, ct, encode_rows(rows, types))


# ══ 输入解析: URL / viewlet / 文件 → 模板绝对路径 ══

def resolve_input(src, reportlets):
    """页面地址/相对路径/文件路径 → (绝对模板路径, 来源说明)"""
    if re.match(r"^https?://", src, re.I):
        import urllib.parse
        q = urllib.parse.urlparse(src).query
        viewlet = None
        for kv in urllib.parse.parse_qsl(q):
            if kv[0] in ("viewlet", "reportlet", "formlet"):
                viewlet = kv[1]
                break
        if not viewlet:
            raise SystemExit(f"URL 中无 viewlet/reportlet/formlet 参数: {src}")
        viewlet = viewlet.lstrip("/")
        cand = os.path.normpath(os.path.join(reportlets, viewlet.replace("/", os.sep)))
        if not os.path.exists(cand):
            raise SystemExit(f"viewlet 在本机 reportlets 不存在(仅支持本机可及的页面):\n  {cand}\n"
                             f"远端服务器页面需先拷贝模板到本机,或在该服务器上运行本工具。")
        return cand, f"URL→viewlet: {viewlet}"
    if os.path.isabs(src) and os.path.exists(src):
        return src, "直接文件路径"
    cand = os.path.normpath(os.path.join(reportlets, src.replace("/", os.sep)))
    if os.path.exists(cand):
        return cand, f"viewlet 相对路径(reportlets/{src})"
    raise SystemExit(f"输入无法定位: {src}\n(既不是存在的文件,也不在 reportlets 下)")


# ══ 逆向构建: 渲染JSON → cpt XML ══

def _esc_cdata(s):
    return str(s).replace("]]>", "]]]]><![CDATA[>")


def build_reverse_cpt(rjson, manifest, base_cpt):
    """渲染产物 JSON → 逆向 cpt XML 字符串。
    - 每个非空格 → 静态文本单元格(坐标/跨度逐格还原, 值=页面展示值)
    - 图表格 → '[图表 原类名]' 占位标记(结构保留; 图表内部配置不在渲染产物中,不逆向)
    - 每个sheet的内嵌数据集 page_data_N = 该sheet的页面数据(宽表)
    - 参数面板: manifest 参数名 → TextEditor(逐个)"""
    sheets = rjson.get("sheets", [])
    if rjson.get("kind") == "frm" or not sheets:
        raise SystemExit("frm 页面逆向(组件树→frm XML)属 v2 范围; 当前版本支持 cpt 页面。\n"
                         "frm 可用验证: python kfgj/xlyl\\render_check.py <frm> --backend injected (J6-J8 组件树断言)")
    x = open(base_cpt, encoding="utf-8").read()

    # 网格尺寸
    maxc = max((c["c"] + (c.get("cs") or 1) for s in sheets for c in s.get("cells", [])), default=1)
    maxr = max((c["r"] + (c.get("rs") or 1) for s in sheets for c in s.get("cells", [])), default=1)

    ds_parts, report_blocks = [], []
    m_sheet_names = [s for s in (manifest or {}).get("sheet_names", []) if s]
    for si, s in enumerate(sheets):
        cells = [c for c in s.get("cells", []) if c.get("v") is not None]
        cells.sort(key=lambda c: (c["r"], c["c"]))
        cell_xml = []
        grid_rows = {}
        for c in cells:
            cs, rs = c.get("cs") or 1, c.get("rs") or 1
            if c.get("t") == "chart":
                text = f"[图表 {c.get('v', 'Chart')}]"
            else:
                text = str(c["v"])
            cell_xml.append('<C c="%d" r="%d" cs="%d" rs="%d" s="1">\n<O>\n<![CDATA[%s]]></O>\n'
                            "<PrivilegeControl/>\n<Expand/>\n</C>\n"
                            % (c["c"], c["r"], cs, rs, _esc_cdata(text)))
            grid_rows.setdefault(c["r"], {})[c["c"]] = str(c["v"]) if c.get("t") != "chart" else f"[图表 {c.get('v')}]"
        # 内嵌数据集: 页面展示数据(宽表, 全 String)
        cols = [f"col_{i}" for i in range(maxc)]
        types = ["java.lang.String"] * maxc
        rows = [[grid_rows.get(r, {}).get(i) for i in range(maxc)] for r in sorted(grid_rows)]
        ds_parts.append(embedded_ds(f"page_data_{si}", cols, types, rows))
        # Report 块
        name = (m_sheet_names[si] if si < len(m_sheet_names) and m_sheet_names[si]
                else s.get("name") or f"sheet{si}")
        one = ('<Report class="com.fr.report.worksheet.WorkSheet" name="%s">\n'
               "<ReportPageAttr>\n<HR F=\"0\" T=\"0\"/>\n<FR/>\n<HC/>\n<FC/>\n"
               '<UPFCR COLUMN="false" ROW="true"/>\n</ReportPageAttr>\n'
               "<ColumnPrivilegeControl/>\n<RowPrivilegeControl/>\n"
               '<RowHeight defaultValue="1153643">\n<![CDATA[%s]]></RowHeight>\n'
               '<ColumnWidth defaultValue="2743200">\n<![CDATA[%s]]></ColumnWidth>\n'
               "<CellElementList>\n%s</CellElementList>\n"
               "<ReportAttrSet>\n"
               '<ReportSettings headerHeight="0" footerHeight="0">\n<FrozenColumnRow columnrow="0,0"/>'
               "<PaperSetting/>\n"
               '<Background name=\"ColorBackground\" color=\"-1\"/>\n</ReportSettings>\n'
               "</ReportAttrSet>\n</Report>\n"
               % (name, ",".join(["1153643"] * maxr), ",".join(["2743200"] * maxc), "".join(cell_xml)))
        report_blocks.append(one)

    # 基准手术: WorkBook34 只有一个 Report 块 → 整体替换为我们的 N 块
    x = re.sub(r'<Report class="com\.fr\.report\.worksheet\.WorkSheet"[^>]*>.*?</Report>\s*',
               "".join(report_blocks), x, count=1, flags=re.S)
    # TableDataMap 注入(在 Report 前)
    dsmap = "<TableDataMap>\n%s</TableDataMap>\n" % "".join(ds_parts)
    if "<TableDataMap>" in x:
        x = re.sub(r"<TableDataMap>.*?</TableDataMap>", dsmap, x, count=1, flags=re.S)
    else:
        x = x.replace("<Report class=", dsmap + "<Report class=", 1)
    # 样式表: s0 标题 s1 正文
    styles = ('<StyleList>\n'
              '<Style imageLayout="1">\n<FRFont name="微软雅黑" style="1" size="80" foreground="-1"/>\n'
              '<Background name="ColorBackground" color="-3570555"/>\n<Border/>\n</Style>\n'
              '<Style imageLayout="1">\n<FRFont name="微软雅黑" style="0" size="72"/>\n'
              '<Background name="ColorBackground" color="-1"/>\n<Border/>\n</Style>\n'
              "</StyleList>")
    x = x.replace("<StyleList/>", styles, 1)
    # 参数面板: 优先按渲染控件树原类原坐标重建; 无渲染数据时降级 manifest 参数名→TextEditor
    pane = _param_pane_from_render(rjson)
    if pane is None:
        params = ((manifest or {}).get("params") or {}).get("parameters") or []
        if params:
            pane = _param_pane(params)
    if pane is not None:
        x = x.replace("</Report>\n<StyleList>", "</Report>\n" + pane + "<StyleList>", 1)
        x = x.replace("</Report>\n<StyleList/>", "</Report>\n" + pane + "<StyleList/>", 1)
    # 新模板身份
    x = re.sub(r'TemplateIdAttMark TemplateId="[^"]*"',
               'TemplateIdAttMark TemplateId="%s"' % uuid.uuid4(), x)
    return x


def _param_pane(params):
    ed = []
    for k, p in enumerate(params):
        nm = re.sub(r"\W+", "_", str(p)) or f"param{k}"
        ed.append(
            '<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">'
            '<InnerWidget class="com.fr.form.ui.TextEditor">'
            f'<WidgetName name="{nm}"/>'
            f'<WidgetID widgetID="{uuid.uuid4()}"/>'
            '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">'
            f'<MobileBookMark useBookMark="false" bookMarkName="{nm}" frozen="false" index="-1" oldWidgetName=""/>'
            "<PrivilegeControl/>\n</WidgetAttr>\n<TextAttr/>\n<widgetValue/>\n"
            '<MobileScanCodeAttr scanCode="true" textInputMode="0"/>\n</InnerWidget>\n'
            f'<BoundsAttr x="{16 + k * 200}" y="16" width="160" height="21"/>\n</Widget>\n')
    return _param_pane_wrap("".join(ed))


def _param_leaves(rjson):
    """渲染 params → 叶子控件清单[(cls,name,bounds)](取 inner 真实类, 剔除包装器/布局)"""
    out = []
    for w in rjson.get("params", []):
        cls = w.get("cls", "")
        if cls.endswith("BoundsWidget") or "Layout" in cls.rsplit(".", 1)[-1]:
            continue
        if w.get("x") is None:
            continue
        out.append((cls, w.get("name") or f"p{len(out)}",
                    {"x": w["x"], "y": w["y"], "w": w["w"], "h": w["h"]}))
    return out


def _param_pane_from_render(rjson):
    """参数面板逆向: 渲染控件树 → 原类保真(已知)/Label占位(未知) + 原坐标 BoundsAttr 重建"""
    leaves = _param_leaves(rjson)
    if not leaves:
        return None
    parts = []
    for cls, name, b in leaves:
        ph = f"[占位 {cls.rsplit('.', 1)[-1]}]" if cls not in KNOWN_WIDGETS else None
        parts.append(_widget_xml(cls, name, b, ph))
    return _param_pane_wrap("".join(parts))


def _param_pane_wrap(inner_xml):
    return ('<ReportParameterAttr>\n'
            '<Attributes showWindow="true" delayPlaying="false" windowPosition="1" align="0" '
            'useParamsTemplate="false" currentIndex="0"/>\n'
            "<PWTitle>\n<![CDATA[参数]]></PWTitle>\n"
            '<ParameterUI class="com.fr.form.main.parameter.FormParameterUI">\n<Parameters/>\n'
            '<Layout class="com.fr.form.ui.container.WParameterLayout">\n'
            '<WidgetName name="para"/>\n'
            '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">\n'
            '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>\n'
            "<PrivilegeControl/>\n</WidgetAttr>\n"
            '<Margin top="0" left="0" bottom="0" right="0"/>\n'
            "<Border>\n<border style=\"0\" color=\"-723724\" borderRadius=\"0\" type=\"0\" borderStyle=\"0\"/>\n"
            "<WidgetTitle>\n<O>\n<![CDATA[参数]]></O>\n"
            '<FRFont name="SimSun" style="0" size="72"/>\n<Position pos="0"/>\n</WidgetTitle>\n'
            "<Alpha alpha=\"1.0\"/>\n</Border>\n"
            '<Background name="ColorBackground" color="-1"/>\n'
            '<LCAttr vgap="0" hgap="0" compInterval="0"/>\n'
            + inner_xml +
            "</Layout>\n</ParameterUI>\n</ReportParameterAttr>\n")


# ══ frm 逆向: 组件树JSON → frm XML ══

# 已知参数/基础控件类(逆向保真: 原类重建); 其余(插件/图表/降级标记)→Label 占位
KNOWN_WIDGETS = {"com.fr.form.ui.TextEditor", "com.fr.form.ui.ComboBox",
                 "com.fr.form.ui.DateEditor", "com.fr.form.ui.NumberEditor",
                 "com.fr.form.ui.ComboCheckBox", "com.fr.form.ui.TreeComboBoxEditor",
                 "com.fr.form.ui.FreeButton", "com.fr.form.ui.Label"}


def _is_layout(cls):
    s = cls.rsplit(".", 1)[-1]
    return "Layout" in s or cls.endswith("BoundsWidget")


def _widget_xml(cls_full, name, b, placeholder=None):
    """BoundsWidget XML: 已知类→原类最小形态; 未知→Label 占位(文本标注原类)"""
    inner_cls = cls_full if (not placeholder and cls_full in KNOWN_WIDGETS) else "com.fr.form.ui.Label"
    x = (f'<InnerWidget class="{inner_cls}">\n'
         f'<WidgetName name="{name}"/>\n'
         f'<WidgetID widgetID="{uuid.uuid4()}"/>\n'
         '<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">\n'
         f'<MobileBookMark useBookMark="false" bookMarkName="{name}" frozen="false" index="-1" oldWidgetName=""/>\n'
         '<PrivilegeControl/>\n</WidgetAttr>\n')
    if inner_cls == "com.fr.form.ui.Label":
        text = placeholder or f"[占位 {cls_full.rsplit('.', 1)[-1]}]"
        x += (f"<widgetValue>\n<O>\n<![CDATA[{_esc_cdata(text)}]]></O>\n</widgetValue>\n"
              '<LabelAttr verticalcenter="true" textalign="0" autoline="true"/>\n'
              '<FRFont name="SimSun" style="0" size="72"/>\n<border style="0" color="-723724"/>\n')
    else:
        x += "<widgetValue/>\n"
    x += f"</InnerWidget>\n<BoundsAttr x=\"{b['x']}\" y=\"{b['y']}\" width=\"{b['w']}\" height=\"{b['h']}\"/>\n"
    return f'<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">\n{x}</Widget>\n'


def _leaf_widgets(rjson):
    """渲染组件树 → 叶子控件清单[(cls,name,bounds)]: 布局容器剔除, 坐标缺失则合成(纵排)"""
    leaves = []
    for w in rjson.get("widgets", []):
        cls = w.get("cls", "")
        if _is_layout(cls) or cls.endswith("WidgetErrorMarker") and False:
            continue
        if w.get("x") is None:
            continue  # 无坐标的容器内件(自适应) — 合成见下
        leaves.append((cls, w.get("name") or f"widget{len(leaves)}",
                       {"x": w["x"], "y": w["y"], "w": w["w"], "h": w["h"]}))
    # 自适应形态: 全无坐标 → 纵排合成(诚实标注: 合成坐标非原始布局)
    if not leaves:
        k = 0
        for w in rjson.get("widgets", []):
            cls = w.get("cls", "")
            if _is_layout(cls):
                continue
            leaves.append((cls, w.get("name") or f"widget{k}",
                           {"x": 16, "y": 16 + k * 30, "w": 160, "h": 21}))
            k += 1
    return leaves


def build_reverse_frm(rjson, base_frm):
    """frm 渲染JSON → 逆向 frm XML。
    - 每个叶子控件 → BoundsWidget 原坐标重建(已知编辑器类保真, 未知→Label占位)
    - 布局容器不重建(几何扁平化到一个绝对画布; 结构简化, 坐标保真)
    - 画布尺寸 = 控件包围盒"""
    leaves = _leaf_widgets(rjson)
    if not leaves:
        raise SystemExit("渲染产物无叶子控件")
    x = open(base_frm, encoding="utf-8").read()
    parts = []
    for cls, name, b in leaves:
        ph = None
        if cls.endswith("WidgetErrorMarker"):
            ph = "[降级 控件加载失败]"
        elif cls not in KNOWN_WIDGETS:
            ph = f"[占位 {cls.rsplit('.', 1)[-1]}]"
        parts.append(_widget_xml(cls, name, b, ph))
    # 手术: Center 内 ShowBookmarks 前插入; Center→绝对布局; 画布尺寸
    i_center = x.find("<Center")
    i_sb = x.find("<ShowBookmarks", i_center)
    x = x[:i_sb] + "".join(parts) + x[i_sb:]
    x = x.replace('<Center class="com.fr.form.ui.container.WFitLayout">',
                  '<Center class="com.fr.form.ui.container.WAbsoluteLayout">', 1)
    x = x.replace('<BodyLayoutType type="0"/>', '<BodyLayoutType type="1"/>', 1)
    W = max(b["x"] + b["w"] for _, _, b in leaves) + 16
    H = max(b["y"] + b["h"] for _, _, b in leaves) + 16
    x = re.sub(r'<Size width="\d+" height="\d+"/>', '<Size width="%d" height="%d"/>' % (W, H), x)
    # MobileWidgetList 登记
    names = "".join(f'<Widget widgetName="{n}"/>\n' for _, n, _ in leaves)
    i_mwl = x.find("<MobileWidgetList", i_center)
    end_mwl = x.find("</MobileWidgetList>", i_mwl)
    if end_mwl >= 0:
        x = x[:end_mwl] + names + x[end_mwl:]
    else:
        j = x.find("/>", i_mwl)
        x = x[:i_mwl] + "<MobileWidgetList>\n" + names + "</MobileWidgetList>\n" + x[j + 2:]
    x = re.sub(r'TemplateIdAttMark TemplateId="[^"]*"',
               'TemplateIdAttMark TemplateId="%s"' % uuid.uuid4(), x)
    return x


def frm_roundtrip_compare(j1, j2):
    """frm 一一核对: 按控件名逐一比对坐标(T6) + 数量(T7) + 类保真率(T8)"""
    P, F, W = [], [], []
    g1 = {n: (c, b) for c, n, b in _leaf_widgets(j1)}
    g2 = {n: (c, b) for c, n, b in _leaf_widgets(j2)}
    if len(g1) == len(g2):
        P.append(f"T7 叶子控件数一致: {len(g1)}")
    else:
        F.append(f"T7 控件数不一致: 原 {len(g1)} vs 逆向 {len(g2)}")
    miss, geom = [], []
    for n, (c1, b1) in g1.items():
        if n not in g2:
            miss.append(n)
            continue
        c2, b2 = g2[n]
        if (b1["x"], b1["y"], b1["w"], b1["h"]) != (b2["x"], b2["y"], b2["w"], b2["h"]):
            geom.append((n, b1, b2))
    if not miss and not geom:
        P.append(f"T6 坐标一一命中: {len(g1)} 件(x,y,w,h 逐件相等)")
    else:
        if miss:
            F.append(f"T6 控件缺失 {len(miss)}: {miss[:8]}")
        if geom:
            F.append(f"T6 坐标偏移 {len(geom)}: {[(n, b2) for n, _, b2 in geom[:5]]}")
    same = sum(1 for n, (c1, _) in g1.items() if n in g2 and g2[n][0] == c1)
    known = sum(1 for n, (c1, _) in g1.items() if c1 in KNOWN_WIDGETS)
    if known:
        P.append(f"T8 类保真: 已知控件 {known} 件全保真, 未知 {len(g1) - known} 件→Label占位(结构简化)")
    elif g1:
        W.append("T8 全部为占位重建(未知控件类型), 仅核对几何")
    return P, F, W


# ══ round-trip 一一核对 ══

def roundtrip_compare(j1, j2):
    """原渲染 vs 逆向再渲染 → (pass, fail, warn, 摘要)"""
    P, F, W = [], [], []

    def cells_of(j, kind_normal):
        out = {}
        for s in j.get("sheets", []):
            for c in s.get("cells", []):
                v = c.get("v")
                if v is None:
                    continue
                key = (c["c"], c["r"])
                if c.get("t") == "chart":
                    out[key] = ("chart", f"[图表 {v}]")
                else:
                    out[key] = ("str", str(v))
        return out

    c1, c2 = cells_of(j1, True), cells_of(j2, True)
    # T1 规模
    if len(c1) == len(c2):
        P.append(f"T1 非空格规模一致: {len(c1)} 格")
    else:
        F.append(f"T1 非空格规模不一致: 原 {len(c1)} vs 逆向 {len(c2)}")
    # T2/T3 坐标+跨度+值 逐一
    miss_pos, miss_val = [], []
    chart_pair = 0
    for key, (t1, v1) in c1.items():
        if key not in c2:
            miss_pos.append(key)
            continue
        t2, v2 = c2[key]
        if t1 == "chart":
            if t2 == "str" and v2.startswith("[图表"):
                chart_pair += 1
            else:
                miss_val.append((key, v1[:20], v2[:20]))
        else:
            if v2 != v1:
                miss_val.append((key, v1[:20], v2[:20]))
    if not miss_pos:
        P.append(f"T2 坐标一一命中: {len(c1)} 格全部存在(含跨行列位置)")
    else:
        F.append(f"T2 坐标缺失 {len(miss_pos)} 格: {miss_pos[:8]}")
    if not miss_val:
        P.append("T3 值逐一相等(静态文本精确匹配)")
    else:
        F.append(f"T3 值不匹配 {len(miss_val)} 格(前8): {miss_val[:8]}")
    # T4 图表
    n_chart1 = sum(1 for t, _ in c1.values() if t == "chart")
    if n_chart1 == 0:
        P.append("T4 双方均无图表")
    elif chart_pair == n_chart1:
        P.append(f"T4 图表格一一互认: {n_chart1} 格(图表→占位标记)")
    else:
        F.append(f"T4 图表格互认不全: {chart_pair}/{n_chart1}")
    # T5 sheet 数
    n1, n2 = len(j1.get("sheets", [])), len(j2.get("sheets", []))
    if n1 == n2:
        P.append(f"T5 sheet 数一致: {n1}")
    else:
        F.append(f"T5 sheet 数不一致: {n1} vs {n2}")
    # T9 参数面板布局(控件名→坐标/类; 仅原渲染有 params 时核对)
    g1 = {n: (c, b) for c, n, b in _param_leaves(j1)}
    if g1:
        g2 = {n: (c, b) for c, n, b in _param_leaves(j2)}
        if len(g1) == len(g2):
            P.append(f"T9 参数控件数一致: {len(g1)}")
        else:
            F.append(f"T9 参数控件数不一致: 原 {len(g1)} vs 逆向 {len(g2)}")
        pmiss, pgeom = [], []
        for n, (c1, b1) in g1.items():
            if n not in g2:
                pmiss.append(n)
            else:
                c2, b2 = g2[n]
                if (b1["x"], b1["y"], b1["w"], b1["h"]) != (b2["x"], b2["y"], b2["w"], b2["h"]):
                    pgeom.append((n, b2))
        if not pmiss and not pgeom:
            P.append(f"T9 参数面板布局一一命中: {len(g1)} 件(x,y,w,h 逐件相等) — 问题清单『参数面板布局』核对")
        else:
            if pmiss:
                F.append(f"T9 参数控件缺失 {len(pmiss)}: {pmiss[:6]}")
            if pgeom:
                F.append(f"T9 参数坐标偏移 {len(pgeom)}: {pgeom[:4]}")
    return P, F, W


# ══ 主流程 ══

def main():
    ap = argparse.ArgumentParser(description="页面→模板逆向 + round-trip 核对")
    ap.add_argument("src", help="页面URL / viewlet相对路径 / 模板文件绝对路径")
    ap.add_argument("--out", default=os.path.join(HERE, "out"), help="输出目录")
    ap.add_argument("--reportlets", default=DEFAULT_REPORTLETS, help="reportlets 根目录")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--skip-orig-render", action="store_true",
                    help="跳过原模板渲染(已有 <名>_orig.json 时复用)")
    args = ap.parse_args()

    tpl, how = resolve_input(args.src, args.reportlets)
    print(f"[输入] {how}\n  → {tpl}")
    base_cpt = os.path.join(args.reportlets, "WorkBook34.cpt")
    if not os.path.exists(base_cpt):
        raise SystemExit(f"缺设计器基准模板: {base_cpt}")
    os.makedirs(args.out, exist_ok=True)
    stem = os.path.splitext(os.path.basename(tpl))[0]

    # 1) 期望侧 manifest(参数/图表声明/sheet名)
    try:
        manifest = extract_manifest(tpl)
        print(f"[1] manifest: {len(manifest.get('datasets', []))} 数据集, "
              f"参数 {manifest.get('params', {}).get('parameters', [])}, "
              f"图表 {manifest.get('charts', {}).get('chart_total', 0)}")
    except Exception as e:
        print(f"[1] manifest 提取失败(继续, 无参数面板): {e}")
        manifest = {}

    # 2) 原模板真引擎渲染
    orig_json_path = os.path.join(args.out, f"{stem}_orig.json")
    if args.skip_orig_render and os.path.exists(orig_json_path):
        print(f"[2] 复用原渲染产物: {orig_json_path}")
    else:
        r = backend_injected(tpl, args.out, args.timeout)
        if not r.get("ok"):
            print(f"[2] ❌ 原模板渲染失败: {r.get('reason')}")
            print("    (模板不可用/损坏猎物命中! 这是问题清单第一类问题的直接证据)")
            raise SystemExit(2)
        os.replace(r["html"], orig_json_path)
        print(f"[2] 原模板已渲染 → {orig_json_path}")
    j1 = json.load(open(orig_json_path, encoding="utf-8"))
    is_frm = j1.get("kind") == "frm"
    n_cells = (sum(w.get("name") is not None for w in j1.get("widgets", [])) if is_frm
               else sum(s.get("cellCount", 0) for s in j1.get("sheets", [])))
    print(f"    {'组件树' if is_frm else 'sheet/cell'}: {n_cells}")

    # 3) 逆向构建
    rev_path = os.path.join(args.out, f"{stem}_reverse{'.frm' if is_frm else '.cpt'}")
    if is_frm:
        base_frm = os.path.join(args.reportlets, "Form7.frm")
        if not os.path.exists(base_frm):
            raise SystemExit(f"缺设计器基准模板: {base_frm}")
        xml = build_reverse_frm(j1, base_frm)
    else:
        base_cpt = os.path.join(args.reportlets, "WorkBook34.cpt")
        if not os.path.exists(base_cpt):
            raise SystemExit(f"缺设计器基准模板: {base_cpt}")
        xml = build_reverse_cpt(j1, manifest, base_cpt)
    with open(rev_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(xml)
    import xml.dom.minidom as MD
    MD.parseString(xml)  # 良构校验
    print(f"[3] 逆向模板已生成(良构): {rev_path}  ({len(xml)} 字符)")

    # 4) 逆向模板再渲染
    r2 = backend_injected(rev_path, args.out, args.timeout)
    if not r2.get("ok"):
        print(f"[4] ❌ 逆向模板渲染失败(逆向器缺陷): {r2.get('reason')}")
        raise SystemExit(3)
    rev_json_path = os.path.join(args.out, f"{stem}_reverse.json")
    os.replace(r2["html"], rev_json_path)
    j2 = json.load(open(rev_json_path, encoding="utf-8"))
    print(f"[4] 逆向模板已再渲染 → {rev_json_path}")

    # 5) 一一核对 (T1-T9 roundtrip + L1-L4 原模板布局合理性)
    P, F, W = frm_roundtrip_compare(j1, j2) if is_frm else roundtrip_compare(j1, j2)
    try:
        from layout_check import check_layout
        lp, lf, lw = check_layout(j1)  # 布局断言在原模板渲染产物上跑
        P = lp + P
        F = F + lf
        W = W + lw
    except ImportError:
        pass
    print(f"[5] round-trip 核对: PASS={len(P)} FAIL={len(F)}")
    for p in P:
        print(f"    ✅ {p}")
    for f_ in F:
        print(f"    ❌ {f_}")
    # 报告落盘
    rpt = os.path.join(args.out, f"{stem}_roundtrip.md")
    with open(rpt, "w", encoding="utf-8") as f:
        f.write(f"# round-trip 核对报告: {stem}\n\n"
                f"- 原模板: `{tpl}`\n- 逆向模板: `{rev_path}`\n"
                f"- 产物: `{orig_json_path}` / `{rev_json_path}`\n\n"
                "## 结果\n\n" + "".join(f"- ✅ {p}\n" for p in P)
                + "".join(f"- ❌ {x}\n" for x in F) + "".join(f"- ⚠ {x}\n" for x in W))
    print(f"    报告: {rpt}")
    print("DONE" if not F else "DONE_WITH_FAIL")


if __name__ == "__main__":
    main()
