# -*- coding: utf-8 -*-
"""cpt_facts.py — 从 .cpt XML 解析「声明态事实」，供运行期体检(运行期 vs 声明)对照。

产出 facts dict 键:
  path                 模板绝对路径
  params               [str]  模板声明参数名(ReportParameterAttr/ParameterUI/Parameters)
  widgets              [dict] 面板控件: name/class/label/x/y/w/h(声明坐标,px)
  panel_size           dict|None 面板声明尺寸 {x,y,w,h}
  row_height_default   int|None 行高默认值(EMU)
  row_heights          [int]  声明行高列表(EMU, 1 行 1 项; CDATA 逗号串或 <fr height=/> 两种存法)
  col_widths           [int]  声明列宽列表(EMU)
  datasets             [str]  TableDataMap 数据集名(去重保序)
  js_link_defs         int    NameJavaScript 超链定义数
  js_link_cells        int    挂 NameJavaScriptGroup 的单元格数
  first_link_cell      dict|None {col,row} 第一个超链格模板坐标(0起)
  first_link_target    str|None 第一个超链 ReportletName
  first_link_frame     str|None 第一个超链 TargetFrame(如 _dialog)

单位换算: FR XML 长度 = EMU, px = emu / 914400 * 96。文件可达 1.8MB, 只用正则, 不打印内容。
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji/符号不再 UnicodeEncodeError) ---
try:
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        if _s is not None and hasattr(_s, "reconfigure"):
            try:
                _s.reconfigure(errors="replace")
            except Exception:
                pass
except Exception:
    pass
# --- end guard ---

import re

EMU_PER_INCH = 914400
REF_DPI = 96


def emu_to_px(emu):
    """EMU → 96dpi 像素(取整到 0.1)。"""
    try:
        return round(float(emu) * REF_DPI / EMU_PER_INCH, 1)
    except (TypeError, ValueError):
        return None


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# <Widget class="...BoundsWidget"><InnerWidget class="..."> ...<WidgetName name="X"/>[<LabelName name="L"/>]... </InnerWidget><BoundsAttr .../>
# 注: InnerWidget 内部无嵌套; WidgetName 前可能先出现 <Listener> 等块, 故对块内再搜。
_WIDGET_RE = re.compile(
    r'<InnerWidget\s+class="([^"]+)">(.*?)</InnerWidget>\s*'
    r'<BoundsAttr\s+x="(-?[\d.]+)"\s+y="(-?[\d.]+)"'
    r'\s+width="(-?[\d.]+)"\s+height="(-?[\d.]+)"/>',
    re.S,
)
_WIDGET_NAME_RE = re.compile(r'<WidgetName\s+name="([^"]+)"/>')
_WIDGET_LABEL_RE = re.compile(r'<LabelName\s+name="([^"]*)"/>')

_PARAM_RE = re.compile(r'<Parameter>\s*<Attributes\s+name="([^"]+)"')
_DATASET_RE = re.compile(r'<TableData\s+name="([^"]+)"')
_ROWHEIGHT_DEFAULT_RE = re.compile(r'<RowHeight\s+defaultValue="(-?\d+)"')
_ROWHEIGHT_CDATA_RE = re.compile(r'<RowHeight[^>]*>\s*<!\[CDATA\[([0-9.,]+)\]\]>', re.S)
_ROWHEIGHT_LIST_RE = re.compile(r'<fr\s+height="(-?\d+)"')
_COLWIDTH_CDATA_RE = re.compile(r'<ColumnWidth[^>]*>\s*<!\[CDATA\[([0-9.,]+)\]\]>', re.S)
_COLWIDTH_LIST_RE = re.compile(r'<fr\s+width="(-?\d+)"')
_PANEL_SIZE_RE = re.compile(
    r'<Layout\s+class="[^"]*WParameterLayout">.*?</Layout>\s*'
    r'<DesignAttr\s+width="(-?[\d.]+)"\s+height="(-?[\d.]+)"/>',
    re.S,
)
_PANEL_SIZE_BOUNDS_RE = re.compile(
    r'<Layout\s+class="[^"]*WParameterLayout">.*?</Layout>\s*'
    r'<BoundsAttr\s+x="(-?[\d.]+)"\s+y="(-?[\d.]+)"\s+width="(-?[\d.]+)"\s+height="(-?[\d.]+)"/>',
    re.S,
)
_LINK_CELL_RE = re.compile(r'<C\s+c="(\d+)"\s+r="(\d+)"[^>]*>(?:(?!</C>).)*?<NameJavaScriptGroup>', re.S)
_REPORTLET_RE = re.compile(r'<ReportletName[^>]*>\s*<!\[CDATA\[([^\]]*)\]\]>', re.S)
_TARGETFRAME_RE = re.compile(r'<TargetFrame>\s*<!\[CDATA\[([^\]]*)\]\]>', re.S)



def _frm_widgets(path):
    """frm 全控件树遍历(2026-09-12 web_kit 扩容): 参数面板正则只覆盖面板区,
    决策报表 body 的表格块/图表/嵌套布局容器需要完整遍历。
    收集全部 InnerWidget(带 WidgetName): name/class/class_full/label/xywh + wrap 标记。"""
    import xml.etree.ElementTree as _ET
    out = []
    root = _ET.parse(path).getroot()
    for w in root.iter("Widget"):
        iw = w.find("InnerWidget")
        if iw is None:
            continue
        nm = iw.find("WidgetName")
        name = nm.get("name") if nm is not None else None
        if not name:
            continue
        cls = iw.get("class", "")
        ba = w.find("BoundsAttr")
        try:
            b = (float(ba.get("x", 0)), float(ba.get("y", 0)),
                 float(ba.get("width", 0)), float(ba.get("height", 0))) if ba is not None else (0.0, 0.0, 0.0, 0.0)
        except (TypeError, ValueError):
            b = (0.0, 0.0, 0.0, 0.0)
        label = ""
        wrap = ""
        has_chart = False
        for sub in iw.iter():
            c = (sub.get("class") or "")
            if "Chart" in c:
                has_chart = True
            if sub.tag == "O" and sub.text and not label:
                label = sub.text.strip()[:40]
        if has_chart:
            wrap = "chart"
        out.append({"name": name, "class": cls.split(".")[-1], "class_full": cls,
                    "label": label, "x": b[0], "y": b[1], "w": b[2], "h": b[3],
                    "wrap": wrap})
    return out


def parse_cpt(path):
    """解析 cpt, 返回 facts dict。任何一段解析失败只降级该键(空值), 不抛异常。"""
    xml = _read(path)
    facts = {
        "path": str(path),
        "params": [],
        "widgets": [],
        "panel_size": None,
        "row_height_default": None,
        "row_heights": [],
        "col_widths": [],
        "datasets": [],
        "js_link_defs": 0,
        "js_link_cells": 0,
        "first_link_cell": None,
        "first_link_target": None,
        "first_link_frame": None,
    }

    # ── 模板声明参数(限定 ReportParameterAttr 块, 避免混入数据集 SQL 参数) ──
    rpa = re.search(r"<ReportParameterAttr>.*?</ReportParameterAttr>", xml, re.S)
    scope = rpa.group(0) if rpa else xml
    try:
        facts["params"] = list(dict.fromkeys(_PARAM_RE.findall(scope)))
    except Exception:
        pass

    # ── 面板控件(InnerWidget+WidgetName[+LabelName]+BoundsAttr) ──
    try:
        for m in _WIDGET_RE.finditer(scope):
            cls, body, x, y, w, h = m.groups()
            nm = _WIDGET_NAME_RE.search(body)
            if not nm:
                continue
            lb = _WIDGET_LABEL_RE.search(body)
            facts["widgets"].append({
                "name": nm.group(1),
                "class": cls.split(".")[-1],
                "class_full": cls,
                "label": lb.group(1) if lb else None,
                "x": float(x), "y": float(y),
                "w": float(w), "h": float(h),
            })
    except Exception:
        pass

    # ── 面板声明尺寸(优先 DesignAttr, 兼容 Layout 自带 BoundsAttr) ──
    try:
        m = _PANEL_SIZE_RE.search(scope)
        if m:
            w, h = (float(v) for v in m.groups())
            facts["panel_size"] = {"x": 0.0, "y": 0.0, "w": w, "h": h}
        else:
            m = _PANEL_SIZE_BOUNDS_RE.search(scope)
            if m:
                x, y, w, h = (float(v) for v in m.groups())
                facts["panel_size"] = {"x": x, "y": y, "w": w, "h": h}
    except Exception:
        pass

    # ── 行高/列宽(优先 CDATA 逗号串, 兼容 <fr height=/> 列表) ──
    try:
        m = _ROWHEIGHT_DEFAULT_RE.search(xml)
        if m:
            facts["row_height_default"] = int(m.group(1))
        blocks = _ROWHEIGHT_CDATA_RE.findall(xml)
        if blocks:
            best = max(blocks, key=lambda s: s.count(",") + 1)
            facts["row_heights"] = [int(v) for v in best.split(",") if v]
        else:
            facts["row_heights"] = [int(v) for v in _ROWHEIGHT_LIST_RE.findall(xml)]
    except Exception:
        pass
    try:
        blocks = _COLWIDTH_CDATA_RE.findall(xml)
        if blocks:
            best = max(blocks, key=lambda s: s.count(",") + 1)
            facts["col_widths"] = [int(v) for v in best.split(",") if v]
        else:
            facts["col_widths"] = [int(v) for v in _COLWIDTH_LIST_RE.findall(xml)]
    except Exception:
        pass

    # ── 数据集 ──
    try:
        facts["datasets"] = list(dict.fromkeys(_DATASET_RE.findall(xml)))
    except Exception:
        pass

    # ── JS/网络报表超链 ──
    try:
        facts["js_link_defs"] = len(re.findall(r"<NameJavaScript[\s>]", xml))
        cells = _LINK_CELL_RE.findall(xml)
        facts["js_link_cells"] = len(cells)
        if cells:
            facts["first_link_cell"] = {"col": int(cells[0][0]), "row": int(cells[0][1])}
        m = _REPORTLET_RE.search(xml)
        if m:
            facts["first_link_target"] = m.group(1).strip()
        m = _TARGETFRAME_RE.search(xml)
        if m:
            facts["first_link_frame"] = m.group(1).strip()
    except Exception:
        pass

    # ── frm: 全控件树遍历(2026-09-12 web_kit 扩容) —— 参数面板正则只覆盖面板区,
    # 决策报表 body 的表格块/图表/嵌套布局容器需要完整遍历 ──
    if str(path).lower().endswith(".frm"):
        try:
            facts["widgets"] = _frm_widgets(path)
        except Exception:
            pass
    return facts


if __name__ == "__main__":  # 独立自检: python cpt_facts.py <cpt路径> ...
    import json
    import sys

    for p in sys.argv[1:]:
        f = parse_cpt(p)
        slim = {k: v for k, v in f.items() if k not in ("widgets",) }
        slim["widget_count"] = len(f["widgets"])
        slim["widget_names"] = [w["name"] for w in f["widgets"]]
        print(json.dumps(slim, ensure_ascii=False, indent=1))
