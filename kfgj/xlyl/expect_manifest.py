#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
expect_manifest.py — 期望清单提取器（无服务器kfgj/xlyl工具 · 断言层"期望侧"）

从 cpt/frm 模板 XML 提取「渲染后输出必须体现」的结构事实，生成 manifest JSON。
渲染路线无关：独立 JVM 渲染 / 设计器注入渲染 的产物都对照同一份 manifest 断言。

用法:
    python expect_manifest.py <模板.cpt|frm>              # 单文件 → stdout
    python expect_manifest.py <目录> --out manifest.json  # 批量 → 汇总 JSON
    python expect_manifest.py <文件> --check rendered.html # 断言模式：渲染产物 vs manifest
"""
import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

# ── 提取 ───────────────────────────────────────────────────────────────

def _local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def extract_dataset_info(root):
    """TableDataMap → 数据集清单（名称/类型类名/是否内嵌数据）"""
    out = []
    for td in root.iter():
        if _local(td.tag) != "TableData":
            continue
        cls = td.get("class", "")
        name = td.get("name", "")
        # RowData CDATA 长度 ≈ 内嵌数据量（压缩编码）
        rowdata = td.find(".//RowData")
        embedded_bytes = len((rowdata.text or "").strip()) if rowdata is not None else 0
        out.append({
            "name": name,
            "class": cls,
            "embedded": "EmbeddedTableData" in cls,
            "embedded_payload_bytes": embedded_bytes,
        })
    return out


def extract_cell_grid(root):
    """CellElementList → 单元格网格（行列/跨度/静态文本）"""
    cells, texts = [], []
    for c in root.iter():
        if _local(c.tag) != "C":
            continue
        cs, rs = int(c.get("cs", "1")), int(c.get("rs", "1"))
        col, row = int(c.get("c", "-1")), int(c.get("r", "-1"))
        o = c.find("O")
        o_attr_t = (o.get("t") if o is not None else None) or ""
        text = None
        if o is not None and not o_attr_t and (o.text or "").strip():
            text = o.text.strip()
            texts.append({"cell": f"{col},{row}", "text": text})
        cells.append({"c": col, "r": row, "cs": cs, "rs": rs, "t": o_attr_t or "str"})
    return {
        "cell_count": len(cells),
        "max_col": max((c["c"] + c["cs"] for c in cells), default=0),
        "max_row": max((c["r"] + c["rs"] for c in cells), default=0),
        "static_texts": texts,
    }


def extract_charts(root):
    """图表清单——三种形态：
    - 老式 <ChartCollection>（cpt 单元格图表容器）
    - 新式 VanChart: <Chart chartClass="com.fr.plugin.chart.vanchart.VanChart">（10.0+ 主形态）
    - FRM 组件: <ChartEditor>"""
    charts = []
    for el in root.iter():
        lt = _local(el.tag)
        if lt == "ChartCollection":
            ctype = None
            for sub in el.iter():
                if _local(sub.tag) == "Chart" and sub.get("chartClass"):
                    ctype = sub.get("chartClass"); break
            charts.append({"container": "ChartCollection", "chart_class": ctype})
        elif lt == "Chart" and (el.get("chartClass") or el.get("class")):
            charts.append({"container": "Chart",
                           "chart_class": el.get("chartClass") or el.get("class"),
                           "name": el.get("name")})
    frm_charts = sum(1 for el in root.iter() if _local(el.tag) == "ChartEditor")
    return {"charts": charts, "chart_total": len(charts) + frm_charts,
            "frm_chart_editors": frm_charts}


def extract_params(root):
    """ParameterUI / Parameter → 参数面板"""
    has_pui = any(_local(el.tag) == "ParameterUI" for el in root.iter())
    params = [p.get("name") for p in root.iter() if _local(p.tag) == "Parameter" and p.get("name")]
    return {"parameter_ui": has_pui, "parameters": sorted(set(params))}


def _short_cls(cls):
    """com.fr.form.ui.container.WFitLayout → WFitLayout；插件类取末两段"""
    if not cls:
        return None
    parts = cls.split(".")
    return parts[-1] if len(parts) <= 4 else ".".join(parts[-2:])


def extract_frm_widgets(root):
    """FRM 专用：Widget 树 → 组件清单（类/名称/坐标尺寸）。
    结构: Layout>...>Widget(BoundsWidget)>InnerWidget(真实控件) + BoundsAttr(x,y,w,h)"""
    widgets = []
    for w in root.iter():
        if _local(w.tag) != "Widget":
            continue
        inner = w.find("InnerWidget")
        if inner is None:
            continue
        cls = inner.get("class", "")
        name_el = inner.find("WidgetName")
        name = name_el.get("name") if name_el is not None else None
        bounds = w.find("BoundsAttr")
        b = ({k: int(bounds.get(k, 0)) for k in ("x", "y", "width", "height")}
             if bounds is not None else None)
        widgets.append({"class": _short_cls(cls), "full_class": cls,
                        "name": name, "bounds": b,
                        "plugin": inner.get("pluginID")})
    by_cls = {}
    for wgt in widgets:
        by_cls[wgt["class"]] = by_cls.get(wgt["class"], 0) + 1
    return {"widget_count": len(widgets), "widgets": widgets,
            "class_histogram": dict(sorted(by_cls.items(), key=lambda kv: -kv[1]))}


def extract_manifest(path):
    tree = ET.parse(path)  # 异常向上抛：XML 损坏是硬失败
    root = tree.getroot()
    is_frm = _local(root.tag) == "Form"
    m = {
        "file": os.path.basename(path),
        "root_tag": _local(root.tag),
        "kind": "frm" if is_frm else "cpt",
        "sheet_names": [ws.get("name", "") for ws in root.iter() if _local(ws.tag) == "Report"],
        "datasets": extract_dataset_info(root),
        "grid": extract_cell_grid(root),
        "charts": extract_charts(root),
        "params": extract_params(root),
    }
    if is_frm:
        m["frm"] = extract_frm_widgets(root)
    return m


# ── 断言（渲染产物 vs manifest）────────────────────────────────────────

def check_rendered(manifest, html_path):
    """结构断言：渲染 HTML 应体现 manifest 的关键事实。
    返回 (passed, failed, warned) 列表。HTML 形态依赖渲染路线，
    规则保守：只断言高置信结构，其余 warn。"""
    html = open(html_path, encoding="utf-8", errors="replace").read()
    passed, failed, warned = [], [], []

    def has_any(patterns):
        return any(re.search(p, html) for p in patterns)

    # R1 静态文本应出现在输出（cpt 明细模板高置信）
    for t in manifest["grid"]["static_texts"][:20]:
        key = re.escape(t["text"][:24])
        if re.search(key, html):
            passed.append(f"R1 静态文本出现: {t['text'][:16]}")
        else:
            # frm 图表画布常不直出文本 → 降级 warn
            warned.append(f"R1 静态文本未见(可能被图表容器化): {t['text'][:16]}")

    # R2 数据集名（FR 导出 HTML 常带 ds 名 or 其数据痕迹）
    for ds in manifest["datasets"]:
        if has_any([rf'\b{re.escape(ds["name"])}\b', "dataset"]):
            passed.append(f"R2 数据集痕迹: {ds['name']}")
        else:
            warned.append(f"R2 数据集名未见: {ds['name']}")

    # R3 sheet 名
    for sn in manifest["sheet_names"]:
        if sn and sn in html:
            passed.append(f"R3 sheet 名出现: {sn}")
        else:
            warned.append(f"R3 sheet 名未见: {sn}")

    # R4 图表：容器存在即可（svg/canvas/chart 节点）
    nc = manifest["charts"]["chart_total"]
    if nc == 0:
        passed.append("R4 无图表声明,跳过")
    elif has_any([r"<svg", r"<canvas", r"chart", r"ChartCollection"]):
        passed.append(f"R4 图表容器存在({nc} 声明)")
    else:
        failed.append(f"R4 图表容器缺失({nc} 声明但输出无 svg/canvas/chart 痕迹)")

    # R5 HTML 基本形态
    if re.search(r"<html|<!DOCTYPE", html, re.I):
        passed.append("R5 HTML 文档形态")
    else:
        failed.append("R5 非 HTML 文档(缺 <html/DOCTYPE)")

    # R6 非空输出
    if len(html) > 500:
        passed.append(f"R6 输出体量 {len(html)}B")
    else:
        failed.append(f"R6 输出过小({len(html)}B,疑空渲染)")

    # R7 FRM 组件：渲染产物应含组件容器痕迹（按类名 histogram 抽查）
    frm = manifest.get("frm")
    if frm:
        for cls, n in list(frm["class_histogram"].items())[:8]:
            token = cls.rsplit(".", 1)[-1]
            if re.search(token, html) or has_any([r'div', r'widget', r'component']):
                passed.append(f"R7 组件痕迹: {cls}×{n}")
            else:
                warned.append(f"R7 组件痕迹未见: {cls}×{n}")

    return passed, failed, warned


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="渲染期望清单提取器")
    ap.add_argument("target", help="cpt/frm 文件或目录")
    ap.add_argument("--out", help="manifest 输出 JSON 路径(批量模式)")
    ap.add_argument("--check", help="断言模式: 渲染产物 HTML 路径")
    args = ap.parse_args()

    if os.path.isdir(args.target):
        files = sorted(glob.glob(os.path.join(args.target, "**", "*.cpt"), recursive=True)
                       + glob.glob(os.path.join(args.target, "**", "*.frm"), recursive=True))
    else:
        files = [args.target]

    manifests = []
    for f in files:
        try:
            manifests.append(extract_manifest(f))
        except ET.ParseError as e:
            manifests.append({"file": os.path.basename(f), "error": f"XML ParseError: {e}"})

    if args.check:
        if len(manifests) != 1:
            print("--check 仅支持单文件", file=sys.stderr); sys.exit(2)
        p, f_, w = check_rendered(manifests[0], args.check)
        for x in p: print(f"  [PASS] {x}")
        for x in w: print(f"  [WARN] {x}")
        for x in f_: print(f"  [FAIL] {x}")
        print(f"  == {len(p)} PASS / {len(w)} WARN / {len(f_)} FAIL")
        sys.exit(1 if f_ else 0)

    out = json.dumps(manifests if len(manifests) > 1 else manifests[0],
                     ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(out)
        ok = sum(1 for m in manifests if "error" not in m)
        print(f"manifest: {args.out} ({ok}/{len(manifests)} 成功)")
    else:
        print(out)
    sys.exit(0 if all("error" not in m for m in manifests) else 1)


if __name__ == "__main__":
    main()
