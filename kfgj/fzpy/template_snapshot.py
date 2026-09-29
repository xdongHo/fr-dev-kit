#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
template_snapshot.py — 模板结构快照提取器（借鉴 FR AI 助手 DesignerLLMContext/FineAIEnvProvider）

AI 助手做法：实时把「当前模板结构信息、数据库表字段信息」注入 LLM 上下文，避免幻觉。
我们落地：开发/修改模板前先跑本脚本，拿到当前模板的结构 JSON 作为上下文，再动手。

用法：
    python template_snapshot.py               # 自动取设计器当前打开模板（需 FR10 + fr-agent 注入，/exec 19000）
    python template_snapshot.py <file.cpt>    # 直接解析指定模板文件
    python template_snapshot.py <file.frm> --json   # 输出 JSON（默认也打印 JSON）
    python template_snapshot.py <file.cpt> --save    # 存档到用户目录 ~/.fr_dev_kit/snapshot/<时间戳>_<模板名>.json

输出结构：
{
  "path": "...",
  "type": "CPT|FORM",
  "datasets": [{"name","type","sql","fields"(可选)}],
  "params":   [{"name","widget","dict"}],
  "charts":   [{"widget","ds","cat","series","values","title"}],
  "kpi":      [{"name","html片段"}](FRM ElementCase 摘要)
}
"""

# --- console-safe guard (2026-09-11 SOP 提速: GBK 控制台打印 emoji 不再 UnicodeEncodeError) ---
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
import argparse
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

EXEC_URL = "http://localhost:19000/exec"

# FR 工作区根（JTemplate.getPath() 相对此目录）
def _detect_fr_workroot():
    for home in (r"C:\Program Files\FineReport_10.0", r"D:\FineReport_10.0", r"C:\FineReport_11.0"):
        root = os.path.join(home, "webapps", "webroot", "WEB-INF")
        if os.path.isdir(root):
            return root
    return r"C:\Program Files\FineReport_10.0\webapps\webroot\WEB-INF"

# FR 工作区根（JTemplate.getPath() 相对此目录）——自动探测，C 盘优先（本机无 D 盘）
FR_WORKROOT = _detect_fr_workroot()

# ---------- fr-agent 取当前模板路径 ----------

def get_current_template_path():
    script = """
var HistoryTemplateListCache = Java.type("com.fr.design.file.HistoryTemplateListCache");
var jt = HistoryTemplateListCache.getInstance().getCurrentEditingTemplate();
if (jt == null) { "NONE"; } else { jt.getPath(); }
"""
    try:
        req = urllib.request.Request(EXEC_URL, data=json.dumps({"script": script}).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            r = json.loads(resp.read().decode("utf-8"))
        if "error" in r:
            return None, r["error"]
        return r.get("result", ""), None
    except Exception as e:
        return None, f"无法连接 fr-agent /exec (19000): {e}"

# ---------- XML 解析 ----------

NS = "{http://www.w3.org/XML/1998/namespace}"  # 某些 XML 带 xml: 属性


def local(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def parse_datasets(root):
    """数据集列表：<TableData> 节点。CPT/FRM 通用结构：name 属性 + <Query> 内 SQL + <Connection> 连接。"""
    out = []
    for ds in root.iter():
        if local(ds.tag) not in ("TableData", "DBTableData"):
            continue
        # name: 优先属性，其次 <Name> 子元素
        name = ds.attrib.get("name")
        if not name:
            name_el = ds.find(".//Name")
            name = name_el.text if name_el is not None else None
        # SQL: <Query> 优先，其次 <SQL>
        sql = None
        for q in ds.iter():
            if local(q.tag) in ("Query", "SQL"):
                sql = q.text
                break
        # 连接名
        conn = None
        dbn = ds.find(".//Connection/DatabaseName")
        if dbn is not None and dbn.text:
            conn = dbn.text.strip()
        cls = ds.attrib.get("class", "")
        if name:
            out.append({"name": name.strip(), "type": cls.split(".")[-1],
                        "sql": (sql or "").strip(), "conn": conn})
    return out


def widget_name(w):
    """组件名：优先 <WidgetName>CDATA</WidgetName>，其次 <WidgetName name=""/> 属性式，再 widgetName/name 属性。"""
    for wn in w.iter():
        if local(wn.tag) == "WidgetName":
            txt = "".join(wn.itertext()).strip()
            if txt:
                return txt
            attr = wn.attrib.get("name")
            if attr:
                return attr
    return w.attrib.get("widgetName") or w.attrib.get("name")


def parse_params(root):
    """FRM 参数控件：遍历 <Widget>（含 BoundsWidget 包装），兼容属性式 WidgetName。"""
    PARAM_CLASSES = ("ComboBox", "ComboCheckBox", "DateEditor", "NumberEditor", "TextEditor",
                     "RadioGroup", "CheckBox", "CheckBoxGroup", "FreeButton", "FormSubmitButton")
    out = []
    for el in root.iter():
        t = local(el.tag)
        cls = el.attrib.get("class", "")
        if t != "Widget" or not cls:
            continue
        base = cls.split(".")[-1]
        # BoundsWidget 包装：看 InnerWidget 的 class
        if base == "WAbsoluteLayout$BoundsWidget":
            inner = el.find("InnerWidget")
            if inner is None:
                continue
            base = inner.attrib.get("class", "").split(".")[-1]
        if base in PARAM_CLASSES:
            nm = widget_name(el)
            if nm:
                out.append({"name": nm, "widget": base})
    seen, uniq = set(), []
    for p in out:
        k = (p["name"], p["widget"])
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


def parse_chart_def(el):
    """解析单个 ChartDefinition 段，返回 {ds, cat, series[], values[]}。"""
    info = {}
    td = el.find(".//TableData/Name")
    if td is not None and td.text:
        info["ds"] = td.text.strip()
    cat = el.find(".//CategoryName")
    if cat is not None:
        info["cat"] = cat.attrib.get("value", "")
    # OneValueCDDefinition: seriesName/valueName
    ser = el.find(".//seriesName")
    if ser is not None:
        info["series"] = [ser.attrib.get("value", "")]
    val = el.find(".//valueName")
    if val is not None:
        info["values"] = [val.attrib.get("value", "")]
    # MoreNameCDDefinition: ChartSummaryColumn name
    cols = el.findall(".//ChartSummaryColumn")
    if cols:
        info["series"] = [c.attrib.get("name", "") for c in cols]
    # 无 category/series 时尝试 (OneValueCDDefinition 里 value 属性)
    if "series" not in info and "values" not in info:
        for n in ("categoryName", "seriesName"):
            e = el.find(".//" + n)
            if e is not None:
                info[n] = e.attrib.get("value", "")
    return info


def parse_charts(root):
    """FRM 图表：直接遍历 ChartDefinition（兼容任意包装结构），widgetName 取区块内最近出现的 WidgetName。"""
    out = []
    last_wn = None
    for el in root.iter():
        t = local(el.tag)
        cls = el.attrib.get("class", "")
        # 更新最近组件名（WidgetName 子元素 或 widgetName 属性）
        if t == "WidgetName":
            txt = "".join(el.itertext()).strip()
            if txt:
                last_wn = txt
        elif t == "Widget" and (el.attrib.get("widgetName") or el.attrib.get("name")):
            last_wn = el.attrib.get("widgetName") or el.attrib.get("name")
        elif t in ("OneValueCDDefinition", "MoreNameCDDefinition"):
            chart = parse_chart_def(el)
            out.append({"widget": last_wn or ("chart_" + str(len(out) + 1)), **chart})
    return out


def parse_kpi(root):
    """FRM ElementCase 单元格摘要（HTML 块）：<Widget class="...ElementCaseEditor">。"""
    out = []
    for ec in root.iter():
        t = local(ec.tag)
        cls = ec.attrib.get("class", "")
        if not (t == "Widget" and cls.endswith(".ElementCaseEditor")) and t != "ElementCaseEditor":
            continue
        wname = widget_name(ec) if t == "Widget" else (ec.attrib.get("widgetName") or ec.attrib.get("name"))
        cells = []
        for cell in ec.iter():
            if local(cell.tag) in ("TCell", "Cell"):
                txt = "".join(cell.itertext()).strip()
                if txt:
                    cells.append(txt[:120])
        out.append({"name": wname, "cells": cells[:12]})
    return out


def parse_cpt_cells(root):
    """CPT 单元格摘要（可选，仅统计非空单元格数量和公式/文本样例）。"""
    cells = []
    for cell in root.iter():
        if local(cell.tag) in ("TCell", "Cell"):
            txt = "".join(cell.itertext()).strip()
            if txt:
                cells.append(txt[:80])
    return {"nonEmptyCells": len(cells), "samples": cells[:10]}


def snapshot(path, fields=False, max_fields=5):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # 剥掉 DOCTYPE（ET 不支持外部实体）
    content = re.sub(r"<!DOCTYPE[^>]*>", "", content)
    root = ET.fromstring(content)

    typ = "FORM" if root.tag.lower() == "form" else ("CPT" if root.tag.lower() == "report" else root.tag)
    snap = {"path": path, "type": typ,
            "datasets": parse_datasets(root),
            "params": parse_params(root),
            "charts": parse_charts(root)}
    if fields:
        # 借鉴 AI 助手 getColumnsFromDataset/getDataSetData：数据集字段+样例数据
        import db_schema
        checked = 0
        for ds in snap["datasets"]:
            if not ds.get("sql") or not ds.get("conn"):
                continue
            conn_l = (ds.get("conn") or "").lower()
            if "dws" not in conn_l and "pg" not in conn_l:
                continue
            if checked >= max_fields:
                ds["fields"] = "(已达 max_fields 上限)"
                continue
            checked += 1
            try:
                info = db_schema.sql_schema(ds["sql"], sample=True, limit=2)
                ds["fields"] = [c["name"] for c in info["columns"]]
                ds["sample"] = info.get("sample", [])
            except Exception as e:
                ds["fields"] = f"(探查失败: {e})"
    if typ == "FORM":
        snap["kpi"] = parse_kpi(root)
    else:
        snap["cells"] = parse_cpt_cells(root)
    return snap


def main():
    ap = argparse.ArgumentParser(description="模板结构快照（上下文注入）")
    ap.add_argument("file", nargs="?", help="模板文件；缺省取设计器当前打开")
    ap.add_argument("--json", action="store_true", help="纯 JSON 输出")
    ap.add_argument("--out", help="另存快照 JSON（指定路径）")
    ap.add_argument("--save", action="store_true",
                    help="自动存档到用户目录 ~/.fr_dev_kit/snapshot/<时间戳>_<模板名>.json")
    ap.add_argument("--fields", action="store_true", help="增强：探查数据集字段+样例数据(DWS)")
    ap.add_argument("--max-fields", type=int, default=5, help="--fields 最多探查数据集数(默认5)")
    args = ap.parse_args()

    path = args.file
    if not path:
        p, err = get_current_template_path()
        if err:
            print(f"❌ {err}\n   请先启动 FR10 Designer 并注入 fr-agent，或直接传入模板文件路径")
            sys.exit(1)
        if p in (None, "", "NONE"):
            print("❌ 设计器没有打开模板")
            sys.exit(1)
        if not os.path.exists(p):
            # JTemplate.getPath() 可能是工作区相对路径（reportlets/...），按 FR 工作区解析
            alt = os.path.join(FR_WORKROOT, p)
            if os.path.exists(alt):
                p = alt
            else:
                print(f"❌ 当前模板未保存到磁盘（{p}），无法解析 XML——请先保存模板，或直接传入文件路径")
                sys.exit(1)
        path = p

    snap = snapshot(path, fields=args.fields, max_fields=args.max_fields)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=2)
        print(f"✅ 快照已保存: {args.out}")
    if args.save:
        import userdir
        userdir.ensure()
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = userdir.SNAPSHOT_DIR / f"{stamp}_{Path(path).stem}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=2)
        print(f"✅ 快照已存档: {out}")
    if not args.json and not args.out:
        print(json.dumps(snap, ensure_ascii=False, indent=2))
    elif args.json:
        print(json.dumps(snap, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
