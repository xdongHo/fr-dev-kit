#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
json_page.py — FineReport 真引擎渲染 JSON → 自包含高保真 HTML 页面

将注入 JVM 渲染器产出的结构化 JSON 转为单文件、内联 CSS、无外部依赖的 HTML。
- CPT 模态：表格网格还原（colspan/rowspan/图表占位/空格）
- FRM 模态：绝对定位控件画布 + 自适应布局树

生成器: json_page.py
来源: https://github.com/ （内部工具）
"""

import json
import os
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# HTML 转义
# ---------------------------------------------------------------------------

def esc(s: str) -> str:
    """HTML 转义 < > & ' \"，确保安全嵌入。"""
    if s is None:
        return ""
    s = str(s)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _is_numeric(v) -> bool:
    """判断值是否为纯数字（整数或浮点数字符串）。"""
    if v is None:
        return False
    s = str(v).strip()
    if not s:
        return False
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# CSS 通用块
# ---------------------------------------------------------------------------

def _base_css(title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
/* json_page.py — 自动生成样式 */
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font:12px/1.5 "Microsoft YaHei","微软雅黑",sans-serif;background:#f5f6f8;color:#333;padding:16px}}
h1{{font-size:16px;margin-bottom:6px}}
h2{{font-size:14px;margin:12px 0 6px;color:#555;border-bottom:1px solid #ddd;padding-bottom:4px}}
.info-bar{{background:#e8f4fd;border:1px solid #b3d8f0;border-radius:4px;padding:8px 12px;margin-bottom:12px;font-size:12px;line-height:1.8}}
.info-bar span{{display:inline-block;margin-right:18px}}
.info-bar .label{{color:#666;font-weight:bold}}
.sheet-title{{background:#4a90d9;color:#fff;padding:6px 12px;font-size:13px;font-weight:bold;border-radius:4px 4px 0 0;margin-top:12px}}

/* CPT 表格 */
table.cpt{{border-collapse:collapse;table-layout:fixed;width:100%;background:#fff}}
table.cpt td{{border:1px solid #c8d4e0;padding:4px;vertical-align:top;font-size:12px;min-width:40px;word-break:break-all}}
table.cpt td.chart-cell{{background:#fdf0e9;color:#842;text-align:center;font-weight:bold;border-color:#e0a87c}}
table.cpt td.empty{{background:#fafafa}}
table.cpt td.num{{text-align:right}}
table.cpt td span.chart-icon{{font-size:16px;display:block;margin-bottom:2px}}

/* FRM 画布 */
.canvas-wrap{{position:relative;background:#fff;border:1px solid #ccc;border-radius:4px;box-shadow:0 1px 4px rgba(0,0,0,.1);overflow:auto;margin:8px 0}}
.canvas{{position:relative;min-height:200px;
  background-image:repeating-linear-gradient(0deg,#eee 0 1px,transparent 1px 20px),
                    repeating-linear-gradient(90deg,#eee 0 1px,transparent 1px 20px)}}
.wgt{{position:absolute;border:1px solid #4a90d9;background:#eaf3fc;overflow:hidden;
      display:flex;align-items:center;justify-content:center;text-align:center;
      font-size:11px;color:#246;word-break:break-all;padding:4px}}
.wgt.layout{{border-style:dashed;border-color:#aaa;background:#fafafa;color:#666}}
.wgt.chart{{border-color:#d97a4a;background:#fdf0e9;color:#842}}
.wgt.error-marker{{border:2px solid #e74c3c;background:#fdecea;color:#c0392b;font-weight:bold;z-index:10}}
.wgt.error-marker::before{{content:"⚠ ";font-size:14px}}

/* 自适应布局树 */
.tree{{background:#fff;border:1px solid #ddd;border-radius:4px;padding:8px;margin:8px 0;font-size:12px}}
.tree-node{{padding:3px 0 3px 0;border-left:2px solid #ccc;margin-left:8px;padding-left:12px}}
.tree-node.root{{border-left:none;margin-left:0;padding-left:0}}
.tree-node .cls-name{{color:#4a90d9;font-weight:bold}}
.tree-node .wgt-name{{color:#888;margin-left:6px}}
.tree-node .marker{{color:#e74c3c;font-weight:bold}}

/* 通用 */
.footer{{margin-top:16px;text-align:center;color:#aaa;font-size:11px}}
</style>
</head>
<body>
"""


# ---------------------------------------------------------------------------
# CPT 渲染
# ---------------------------------------------------------------------------

def _build_cpt_grid(sheet: dict) -> str:
    """
    将 sheet 的 cells 数组转成 HTML <table>。
    核心逻辑：
    1. 按 (r, c) 排序 cells
    2. 计算总行/列数
    3. 维护 occupied 集合，跳过被合并覆盖的格子
    """
    cells = sheet.get("cells", [])
    if not cells:
        return '<p class="info-bar">（无单元格数据）</p>'

    # 排序：先行后列
    cells_sorted = sorted(cells, key=lambda cell: (cell.get("r", 0), cell.get("c", 0)))

    # 计算网格尺寸
    max_r = 0
    max_c = 0
    for cell in cells_sorted:
        r = cell.get("r", 0)
        c = cell.get("c", 0)
        rs = cell.get("rs", 1)
        cs = cell.get("cs", 1)
        max_r = max(max_r, r + rs)
        max_c = max(max_c, c + cs)

    # 构建 occupied 快速查找集合
    occupied = set()
    for cell in cells_sorted:
        r0 = cell.get("r", 0)
        c0 = cell.get("c", 0)
        rs = cell.get("rs", 1)
        cs = cell.get("cs", 1)
        for dr in range(rs):
            for dc in range(cs):
                if dr == 0 and dc == 0:
                    continue  # 左上角是 td 本身
                occupied.add((r0 + dr, c0 + dc))

    # 构建快速查找 dict
    cell_map = {}
    for cell in cells_sorted:
        key = (cell.get("r", 0), cell.get("c", 0))
        cell_map[key] = cell

    # 生成 HTML
    colW = sheet.get("colW") or []
    rowH = sheet.get("rowH") or []
    has_size = bool(colW and len(colW) >= max_c)
    tbl_style = ' style="width:auto;min-width:100%"' if has_size else ""
    parts = [f'<div style="overflow-x:auto;margin-bottom:14px">', f'<table class="cpt"{tbl_style}>']
    # 真实尺寸渲染: 列宽/行高来自渲染器(FU→px, 见 单位换算实证.md) — 图表区按设计器真实比例显示
    if colW and len(colW) >= max_c:
        parts.append("<colgroup>")
        for w in colW[:max_c]:
            parts.append(f'<col style="width:{max(w, 1)}px">')
        parts.append("</colgroup>")
    row_h_map = {i: h for i, h in enumerate(rowH) if h and h > 0}
    for r in range(max_r):
        if row_h_map:
            parts.append(f'<tr style="height:{max(row_h_map.get(r, 12), 6)}px">')
        else:
            parts.append("<tr>")
        for c in range(max_c):
            if (r, c) in occupied:
                continue  # 被合并覆盖，跳过

            cell = cell_map.get((r, c))
            if cell is None:
                # 空格子
                parts.append('<td class="empty"></td>')
                continue

            rs = cell.get("rs", 1)
            cs = cell.get("cs", 1)
            t = cell.get("t", "")
            v = cell.get("v")

            # 构建属性
            attrs = ""
            if cs > 1:
                attrs += f' colspan="{cs}"'
            if rs > 1:
                attrs += f' rowspan="{rs}"'

            # 内容
            if t == "chart":
                chart_label = esc(v) if v and v != "ChartPainter" else "图表"
                parts.append(
                    f'<td class="chart-cell"{attrs}>'
                    f'<span class="chart-icon">📊</span>'
                    f'{esc(chart_label)}'
                    f'</td>'
                )
            elif v is None or (isinstance(v, str) and not v.strip()):
                parts.append(f'<td class="empty"{attrs}></td>')
            else:
                css_class = ' class="num"' if _is_numeric(v) else ""
                parts.append(f'<td{attrs}{css_class}>{esc(v)}</td>')

        parts.append("</tr>")
    parts.append("</table></div>")
    return "".join(parts)


def _render_cpt(data: dict) -> str:
    """渲染 CPT 类型 JSON 为 HTML 片段。"""
    parts = []
    template = data.get("template", "unknown")
    sheets = data.get("sheets", [])
    sheet_count = data.get("sheetCount", len(sheets))

    # 统计
    total_cells = sum(len(s.get("cells", [])) for s in sheets)
    chart_count = sum(
        1 for s in sheets for c in s.get("cells", []) if c.get("t") == "chart"
    )

    # 信息条
    parts.append('<div class="info-bar">')
    parts.append(f'<span><span class="label">模板:</span> {esc(os.path.basename(template))}</span>')
    parts.append(f'<span><span class="label">Sheet数:</span> {sheet_count}</span>')
    parts.append(f'<span><span class="label">单元格:</span> {total_cells}</span>')
    parts.append(f'<span><span class="label">图表:</span> {chart_count}</span>')
    parts.append(f'<span><span class="label">生成时间:</span> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>')
    parts.append('</div>')

    if not sheets:
        parts.append('<p>（无 sheet 数据）</p>')
        return "".join(parts)

    # 参数面板条(渲染器 params 字段: 控件原坐标/原类, 置于表格上方)
    params = data.get("params") or []
    pleaves = [p for p in params
               if p.get("x") is not None
               and "BoundsWidget" not in (p.get("cls") or "")
               and "Layout" not in _short_cls(p.get("cls") or "")]
    if pleaves:
        pw = max(p["x"] + (p.get("w") or 0) for p in pleaves) + 16
        ph = max(p["y"] + (p.get("h") or 0) for p in pleaves) + 12
        parts.append(f'<div class="sheet-title" style="margin-top:10px">🎛 参数面板 ({len(pleaves)} 控件)</div>')
        parts.append(f'<div style="position:relative;width:{pw}px;min-width:100%;height:{ph}px;'
                     'background:#fff;border:1px solid #d8dce4;border-radius:4px;margin-bottom:12px">')
        for p in pleaves:
            cls_s = _short_cls(p.get("cls") or "?")
            nm = p.get("name") or ""
            style = (f'position:absolute;left:{p["x"]}px;top:{p["y"]}px;'
                     f'width:{p.get("w") or 80}px;height:{p.get("h") or 21}px;')
            if cls_s == "WidgetErrorMarker":
                style += 'border:2px solid #d33;background:#fdeaea;color:#b00;'
                label = f"⚠ {esc(nm)} 控件加载失败(缺插件)"
            else:
                style += 'border:1px solid #aab3c0;background:#fafbfc;border-radius:2px;'
                label = f"{esc(cls_s)} · {esc(nm)}"
            parts.append(f'<div style="{style}font-size:11px;line-height:1.3;'
                         f'overflow:hidden;padding:1px 4px" title="{esc(p.get("cls") or "")}">{label}</div>')
        parts.append('</div>')

    for idx, sheet in enumerate(sheets):
        sname = sheet.get("name", f"sheet{idx}")
        scell_count = len(sheet.get("cells", []))
        if len(sheets) > 1:
            parts.append(f'<div class="sheet-title">📄 {esc(sname)} ({scell_count} cells)</div>')
        else:
            parts.append(f'<h2>📄 {esc(sname)} ({scell_count} cells)</h2>')
        parts.append(_build_cpt_grid(sheet))

    return "".join(parts)


# ---------------------------------------------------------------------------
# FRM 渲染
# ---------------------------------------------------------------------------

def _short_cls(cls: str) -> str:
    """取 Java 类名最后一段。"""
    if not cls:
        return "Unknown"
    return cls.rsplit(".", 1)[-1]


def _widget_label(cls: str, name: str) -> str:
    """生成 widget 显示标签。"""
    short = _short_cls(cls)

    # 特殊类型映射
    if "ErrorMarker" in short:
        return "控件加载失败(缺插件)"
    if "Chart" in short or "ChartEditor" in short:
        return f"图表:{name}" if name else "图表"
    if "Label" in short:
        return f"文本:{name}" if name else "文本"
    if "Button" in short:
        return f"按钮:{name}" if name else "按钮"
    if "Editor" in short:
        return f"编辑器:{name}" if name else "编辑器"
    if "Layout" in short:
        return f"布局:{name}" if name else "布局容器"
    if "ComboBox" in short or "CheckBox" in short:
        return f"下拉:{name}" if name else "下拉控件"
    if "Tree" in short:
        return f"树:{name}" if name else "树控件"
    if "Date" in short:
        return f"日期:{name}" if name else "日期控件"
    if "Number" in short:
        return f"数字:{name}" if name else "数字控件"
    if "Text" in short:
        return f"文本框:{name}" if name else "文本框"

    return f"{short}:{name}" if name else short


def _has_absolute_coords(widgets: list) -> bool:
    """检查是否有 widget 含 x/y/w/h 坐标。"""
    for w in widgets:
        if "x" in w and "y" in w and "w" in w and "h" in w:
            return True
    return False


def _render_frm_absolute(widgets: list, canvas_w: int = 1200, canvas_h: int = 800) -> str:
    """渲染有坐标的 widget 为绝对定位画布。"""
    # 计算画布实际尺寸
    for w in widgets:
        if "x" in w and "y" in w and "w" in w and "h" in w:
            canvas_w = max(canvas_w, w["x"] + w["w"])
            canvas_h = max(canvas_h, w["y"] + w["h"])

    parts = [
        f'<div class="canvas-wrap" style="max-width:{canvas_w + 40}px;max-height:{canvas_h + 40}px">',
        f'<div class="canvas" style="width:{canvas_w}px;height:{canvas_h}px">'
    ]

    for w in widgets:
        x = w.get("x")
        y = w.get("y")
        wpx = w.get("w")
        hpx = w.get("h")
        cls = w.get("cls", "")
        name = w.get("name", "")
        inner = w.get("inner", False)

        # 跳过 inner 容器（已由 BoundsWidget 表达）
        if inner:
            continue

        if x is None or y is None or wpx is None or hpx is None:
            continue

        label = _widget_label(cls, name)
        short = _short_cls(cls)

        # CSS 类
        css_cls = "wgt"
        if "ErrorMarker" in short:
            css_cls += " error-marker"
        elif "Chart" in short or "ChartEditor" in short:
            css_cls += " chart"
        elif "Layout" in short:
            css_cls += " layout"

        parts.append(
            f'<div class="{css_cls}" style="left:{x}px;top:{y}px;width:{wpx}px;height:{hpx}px">'
            f'{esc(label)}'
            f'</div>'
        )

    parts.append('</div></div>')
    return "".join(parts)


def _render_frm_tree(widgets: list, depth: int = 0) -> str:
    """渲染无坐标的 widget 为嵌套树结构。"""
    parts = []
    for w in widgets:
        cls = w.get("cls", "")
        name = w.get("name", "")
        inner = w.get("inner", False)
        short = _short_cls(cls)
        label = _widget_label(cls, name)

        # 根节点判断
        is_root = depth == 0 and "Layout" in short
        node_cls = "tree-node root" if is_root else "tree-node"

        # 标记
        extra = ""
        if "ErrorMarker" in short:
            extra = f' <span class="marker">⚠ {esc(label)}</span>'
        elif "Chart" in short:
            extra = f' <span style="color:#d97a4a">📊 {esc(label)}</span>'
        elif "Layout" in short:
            extra = f' <span class="cls-name">{esc(label)}</span>'
        else:
            extra = f' <span style="color:#555">{esc(label)}</span>'

        name_tag = f' <span class="wgt-name">[{esc(name)}]</span>' if name else ""

        parts.append(f'<div class="{node_cls}">{extra}{name_tag}')

    return "".join(parts)


def _render_frm(data: dict) -> str:
    """渲染 FRM 类型 JSON 为 HTML 片段。"""
    parts = []
    template = data.get("template", "unknown")
    widgets = data.get("widgets", [])
    widget_count = data.get("widgetCount", len(widgets))
    root_container = data.get("rootContainer", "")

    # 信息条
    parts.append('<div class="info-bar">')
    parts.append(f'<span><span class="label">模板:</span> {esc(os.path.basename(template))}</span>')
    parts.append(f'<span><span class="label">控件数:</span> {widget_count}</span>')
    parts.append(f'<span><span class="label">根容器:</span> {esc(_short_cls(root_container))}</span>')
    parts.append(f'<span><span class="label">生成时间:</span> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>')
    parts.append('</div>')

    if not widgets:
        parts.append('<p>（无控件数据）</p>')
        return "".join(parts)

    # 判断是否有绝对坐标
    has_coords = _has_absolute_coords(widgets)

    if has_coords:
        parts.append('<h2>📍 绝对定位画布</h2>')
        parts.append(_render_frm_absolute(widgets))
    else:
        parts.append('<h2>🌲 自适应布局树</h2>')
        parts.append('<div class="tree">')
        parts.append(_render_frm_tree(widgets))
        parts.append('</div>')

    # 统计 ErrorMarker
    error_count = sum(1 for w in widgets if "ErrorMarker" in w.get("cls", ""))
    if error_count > 0:
        parts.append(
            f'<div style="margin-top:8px;padding:6px 10px;background:#fdecea;border:1px solid #f5c6cb;'
            f'border-radius:4px;color:#c0392b;font-size:12px">'
            f'⚠ 检测到 <b>{error_count}</b> 个 WidgetErrorMarker — 控件加载失败（通常因缺少插件）。'
            f'</div>'
        )

    return "".join(parts)


# ---------------------------------------------------------------------------
# 主生成函数
# ---------------------------------------------------------------------------

def generate(json_path: str, out_html_path: str = None) -> str:
    """
    读取渲染 JSON，生成自包含 HTML 页面。

    Args:
        json_path: 输入 JSON 文件路径
        out_html_path: 输出 HTML 路径（None 则仅返回字符串）

    Returns:
        生成的 HTML 字符串
    """
    # 读取 JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 校验基本结构
    if not data.get("ok"):
        raise ValueError(f"JSON 标记 ok=false，数据异常: {json_path}")

    kind = data.get("kind", "")
    template = data.get("template", "")

    # 构建 HTML
    title = f"kfgj/xlyl — {os.path.basename(template)}"
    html_parts = [_base_css(title)]

    # 顶部标题
    html_parts.append(f'<h1>🖥️ {esc(title)}</h1>')
    html_parts.append(f'<p style="color:#888;font-size:11px;margin-bottom:10px">'
                      f'json_page.py 真引擎渲染产物预览 · 来源: {esc(os.path.basename(json_path))}</p>')

    # 按类型渲染
    if kind == "cpt":
        html_parts.append(_render_cpt(data))
    elif kind == "frm":
        html_parts.append(_render_frm(data))
    else:
        html_parts.append(f'<p>未知类型: {esc(kind)}</p>')

    # 页脚
    html_parts.append(
        '<div class="footer">'
        'Generated by json_page.py · FineReport 无服务器渲染验证工具'
        '</div>'
    )
    html_parts.append('</body></html>')

    html = "".join(html_parts)

    # 写出文件
    if out_html_path:
        out_dir = os.path.dirname(out_html_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(out_html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ 生成 HTML: {out_html_path} ({len(html):,} bytes)")

    return html


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("用法: python json_page.py <render.json> [out.html]")
        print()
        print("将 FineReport 真引擎渲染产物 JSON 转为自包含高保真 HTML 页面。")
        print("  render.json  — 输入 JSON 文件（ok/kind/sheets 或 widgets）")
        print("  out.html     — 输出 HTML 路径（省略则默认同名 .html）")
        sys.exit(2)

    json_path = sys.argv[1]

    # 确定输出路径
    if len(sys.argv) > 2:
        out_html = sys.argv[2]
    else:
        base = os.path.splitext(json_path)[0]
        out_html = base + ".html"

    # 校验输入
    if not os.path.isfile(json_path):
        print(f"❌ 文件不存在: {json_path}")
        sys.exit(1)

    try:
        generate(json_path, out_html)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ 数据校验失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
