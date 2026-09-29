#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""req_workbook.py — 需求确认清单生成器（需求分析流水线核心, pipeline Stage 0）

从既有 cpt/frm 逆向生成 Excel 需求确认清单 —— 用户确认后即为开发的"单一事实源"。

结构规范(与 ckzl/lc/00_需求分析流水线.md 同源):
  Sheet 1  物料信息     项目概览 / 报表清单 / 数据库表资源(从SQL解析) / 业务背景(待用户填)
  Sheet 2+ <数据集简写>  实体示例数据(真执行取数, ≤--rows 行; 表样用 数据集名.字段 引用)
  Sheet n  SQL_<核心集>  数据集逻辑 SQL 原文(含 ${参数} 占位符)
  Sheet n  表样_<报表名> Excel 版表样: 顶部 5 行=参数面板示例, 下方=cpt 网格
                        (cpt 可直接导入设计器; 明细表≈定稿; DB格=数据集.字段)
  frm      表样_<报表名> 画布式: 合并单元格=组件分布(图表=区域占位)

用法: python req_workbook.py <cpt|frm> [out.xlsx] [--rows 10]
数据源: fr-agent(数据集元数据+真取数) + 模板 XML(DSColumn/静态格) + 注入渲染(图表格/frm组件)
"""
import argparse
import glob
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "kfgj/xlyl"))

PARAM_ROWS = 5          # 表样顶部参数面板约定行数
PX_PER_COL = 24         # frm 画布: 每格像素
PX_PER_ROW = 20

META_JS = """
var ths=java.lang.Thread.getAllStackTraces().keySet().toArray();
var chosen=null;
for(var i=0;i<ths.length;i++){try{var l=ths[i].getContextClassLoader(); if(l!=null){l.loadClass('com.fr.main.impl.WorkBook'); chosen=l; break}}catch(e){}}
function C(n){return java.lang.Class.forName(n,true,chosen)}
var W=C('com.fr.main.impl.WorkBook');
var wb=W.newInstance();
var fis=new java.io.FileInputStream('__TPL__');
W.getMethod('readStream',C('java.io.InputStream')).invoke(wb,fis);
fis.close();
var res=[];
var it=W.getMethod('getTableDataNameIterator').invoke(wb);
while(it.hasNext()){
  var nm=String(it.next());
  var td=W.getMethod('getTableData',C('java.lang.String')).invoke(wb,new java.lang.String(nm));
  var r={name:nm,cls:String(td.getClass().getSimpleName())};
  try{var am=td.getClass().getMethods();
    for(var z=0;z<am.length;z++){var mn=am[z].getName();
      if((mn==='getQuery'||mn==='getSQL')&&am[z].getParameterTypes().length===0){r.sql=String(am[z].invoke(td));break}}}
  catch(e){}
  // 数据连接名(DBTableData): getDatabase/getConnectionName 择一存在
  try{var amc=td.getClass().getMethods();
    for(var zc=0;zc<amc.length;zc++){var mc=amc[zc].getName();
      if((mc==='getDatabase'||mc==='getConnectionName')&&amc[zc].getParameterTypes().length===0){
        var cv=amc[zc].invoke(td); if(cv!=null){r.conn=String(cv);break}}}}
  catch(ec){}
  try{
    var cdm=null;var am2=td.getClass().getMethods();
    for(var z2=0;z2<am2.length;z2++){if(am2[z2].getName()==='createDataModel'&&am2[z2].getParameterTypes().length===1){cdm=am2[z2];break}}
    var CC=cdm.getParameterTypes()[0];
    var cins=null;try{cins=CC.getMethod('createCalculator').invoke(null)}catch(eA){cins=CC.newInstance()}
    var dm=cdm.invoke(td,cins);
    if(dm!=null){
      var rc=dm.getClass().getMethod('getRowCount').invoke(dm);
      var cc2=dm.getClass().getMethod('getColumnCount').invoke(dm);
      r.cols=[];r.rows=[];
      var gcn=dm.getClass().getMethod('getColumnName',java.lang.Integer.TYPE);
      var gvat=dm.getClass().getMethod('getValueAt',java.lang.Integer.TYPE,java.lang.Integer.TYPE);
      for(var ci=0;ci<cc2;ci++)r.cols.push(String(gcn.invoke(dm,java.lang.Integer.valueOf(ci))));
      var nr=Math.min(rc,__ROWS__);
      for(var ri=0;ri<nr;ri++){var row=[];
        for(var ci2=0;ci2<cc2;ci2++){var v=gvat.invoke(dm,java.lang.Integer.valueOf(ri),java.lang.Integer.valueOf(ci2));row.push(v==null?null:String(v))}
        r.rows.push(row)}
      r.totalRows=rc;
    }
  }catch(e3){r.sampleErr=String(e3).substring(0,80)}
  res.push(r);
}
JSON.stringify(res)
"""


def agent_exec(js, timeout=300):
    req = urllib.request.Request("http://localhost:19000/exec",
                                 data=json.dumps({"script": js}).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        res = json.loads(r.read().decode("utf-8"))
    if res.get("error") or not res.get("result"):
        raise RuntimeError("agent exec 失败: %s" % str(res.get("error"))[:200])
    return res["result"]


# 实体表结构+行数+样例 — SQL 代理式: 改写模板首个 DBTableData 的 query 再 createDataModel
# (实证 2026-08-23: ConnectionConfig 在设计器 JVM 不可达; DBTableData 代理执行 information_schema 成功)
DB_JS = """
var ths=java.lang.Thread.getAllStackTraces().keySet().toArray();
var chosen=null;
for(var i=0;i<ths.length&&!chosen;i++){try{var l=ths[i].getContextClassLoader();if(l!=null){l.loadClass('com.fr.main.impl.WorkBook');chosen=l}}catch(e){}}
function C(n){return java.lang.Class.forName(n,true,chosen)}
var W=C('com.fr.main.impl.WorkBook');
var wb=W.newInstance();
var fis=new java.io.FileInputStream('__TPL__');
W.getMethod('readStream',C('java.io.InputStream')).invoke(wb,fis);
fis.close();
var proxy=null;
var it=W.getMethod('getTableDataNameIterator').invoke(wb);
while(it.hasNext()){var n=String(it.next());
  var td=W.getMethod('getTableData',C('java.lang.String')).invoke(wb,new java.lang.String(n));
  if(String(td.getClass().getName())==='com.fr.data.impl.DBTableData'){proxy=td;break}}
if(proxy==null)throw new Error('模板无 DBTableData 可作 SQL 代理');
var am=proxy.getClass().getMethods();var setQ=null,cdm=null;
for(var z=0;z<am.length;z++){
  if(am[z].getName()==='setQuery'&&am[z].getParameterTypes().length===1)setQ=am[z];
  if(am[z].getName()==='createDataModel'&&am[z].getParameterTypes().length===1)cdm=am[z]}
var CalcCls=cdm.getParameterTypes()[0];
var calc=null;try{calc=CalcCls.getMethod('createCalculator').invoke(null)}catch(eA){calc=CalcCls.newInstance()}
function q(sql){
  setQ.invoke(proxy,new java.lang.String(sql));
  var dm=cdm.invoke(proxy,calc);
  var rc=dm.getClass().getMethod('getRowCount').invoke(dm);
  var cc=dm.getClass().getMethod('getColumnCount').invoke(dm);
  var gcn=dm.getClass().getMethod('getColumnName',java.lang.Integer.TYPE);
  var gvat=dm.getClass().getMethod('getValueAt',java.lang.Integer.TYPE,java.lang.Integer.TYPE);
  var cols=[];for(var c=0;c<cc;c++)cols.push(String(gcn.invoke(dm,java.lang.Integer.valueOf(c))));
  var rows=[];for(var r=0;r<rc;r++){var row=[];for(var c2=0;c2<cc;c2++){var v=gvat.invoke(dm,java.lang.Integer.valueOf(r),java.lang.Integer.valueOf(c2));row.push(v==null?null:String(v))}rows.push(row)}
  return {cols:cols,rows:rows};
}
var tables=__TABLES__;
var out=[];
for(var t=0;t<tables.length;t++){
  var parts=tables[t].split('.');
  var sch=parts.length>1?parts[0]:'public';
  var tbl=parts[parts.length-1];
  var r={table:tables[t],err:null};
  try{
    var c1=q("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='"+sch+"' AND table_name='"+tbl+"' ORDER BY ordinal_position");
    r.cols=c1.rows;
    var c2=q("SELECT reltuples::bigint AS n FROM pg_class WHERE oid='"+sch+"."+tbl+"'::regclass");
    r.approxRows=c2.rows.length?parseInt(c2.rows[0][0]):-1;
    var c3=q("SELECT * FROM "+sch+"."+tbl+" LIMIT __ROWS__");
    r.sampleCols=c3.cols;r.sample=c3.rows;
  }catch(e){r.err=String(e).substring(0,100)}
  out.push(r);
}
JSON.stringify(out)
"""


def fetch_table_info(tpl, tables, rows, timeout=300):
    """实体表: 字段/类型/估算行数/样例 — SQL 代理一次拿(需模板含 DBTableData)"""
    js = (DB_JS.replace("__TPL__", tpl.replace("\\", "/"))
          .replace("__TABLES__", json.dumps(tables))
          .replace("__ROWS__", str(rows)))
    return json.loads(agent_exec(js, timeout=timeout))


def sheet_safe(name, used):
    """Excel sheet 名: ≤31 字符, 禁 []:*?/\\, 去重"""
    s = re.sub(r"[\[\]:*?/\\]", "_", str(name))[:28] or "sheet"
    base, k = s, 1
    while s in used:
        k += 1
        s = "%s~%d" % (base[:26], k)
    used.add(s)
    return s


def parse_tables_from_sql(sqls):
    """SQL → 实体表名清单(FROM/JOIN 后的 schema.table; 排除 pg 函数/子查询)"""
    tables = set()
    for sql in sqls:
        if not sql:
            continue
        for m in re.finditer(r"\b(?:FROM|JOIN)\s+([A-Za-z_][\w.]*)", sql, re.I):
            t = m.group(1).strip('"').rstrip(")")
            if t.startswith("("):
                continue
            if t.split(".")[-1].lower() in ("generate_series", "unnest", "values"):
                continue
            tables.add(t)
    return sorted(tables)


def parse_ds_columns(tpl_path):
    """模板 XML → {(c,r): 数据引用文本}
    两种形态都收(时点实证: 示例预算表 08-23 上午=0 DSColumn+3112 公式, §47-49 改造后=927 DSColumn+0 select;
    双态是设计要求, 任一单态都会漏):
      DSColumn: ds.field
      Formula:  公式原文(=ds.select(字段, 条件) — 比 ds.field 更精确, 含过滤逻辑)
    """
    src = open(tpl_path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'<C c="(\d+)" r="(\d+)"[^>]*>.*?</C>', src, re.S):
        seg = m.group(0)
        key = (int(m.group(1)), int(m.group(2)))
        dm = re.search(r'<Attributes dsName="([^"]+)"\s+columnName="([^"]+)"', seg)
        if dm:
            out[key] = "%s.%s" % (dm.group(1), dm.group(2))
            continue
        # 公式: CDATA 以=开头且含 ds 引用(排除纯算术公式)
        fm = re.search(r'<!\[CDATA\[(=[^\]]*?\b(?:ds_\w+|dict_\w+)\.[^\]]*)\]\]>', seg)
        if fm:
            out[key] = fm.group(1)
    return out


# ── 交付反推三提取器(对应 frdoc 运维交档 sec5/6/7/9, 纯 XML 零引擎依赖) ──

def extract_write(tpl_path):
    """sec5 填报属性: 回写表/主键/提交器(无 ReportWriteAttr → None=纯分析模板)"""
    src = open(tpl_path, encoding="utf-8").read()
    m = re.search(r"<ReportWriteAttr>(.+?)</ReportWriteAttr>", src, re.S)
    if not m:
        return None
    seg = m.group(1)
    tables = ["%s.%s" % (s, n) for s, n in
              re.findall(r'<Table[^>]*schema="([^"]*)"[^>]*name="([^"]+)"', seg)]
    tables += re.findall(r'<Table[^>]*(?!schema)[^>]*name="([^"]+)"[^>]*>', seg) if not tables else []
    pairs = re.findall(r'<ColumnConfig[^>]*name="([^"]+)"[^>]*isKey="([^"]+)"', seg)
    cols = re.findall(r'<ColumnConfig[^>]*name="([^"]+)"', seg)
    subm = re.search(r'class="(com\.fr[\w.]*Submit[\w.]*)"', seg)
    return {"tables": tables, "keys": [c for c, k in pairs if k == "true"],
            "nCols": len(cols), "submiter": subm.group(1).rsplit(".", 1)[-1] if subm else "?"}


def extract_jumps(tpl_path):
    """sec6 超链/跳转: viewlet 目标模板清单(frdoc JumpTracker 同款正则)"""
    src = open(tpl_path, encoding="utf-8").read()
    return sorted(set(re.findall(r'viewlet=([\w/.%()+\u4e00-\u9fff-]+)', src)))


def extract_scripts(tpl_path):
    """sec9 自定义脚本量: 事件监听/JS 类引用计数(交付文档'自定义脚本'章的物料)"""
    src = open(tpl_path, encoding="utf-8").read()
    return {"listeners": src.count("<ListenerEvent"),
            "js": len(re.findall(r'class="com\.fr\.js\.\w+"', src))}


def render_json(tpl_path, timeout):
    """注入渲染 → JSON dict(cpt cells+colW/rowH 或 frm widgets); 老模板引擎不可提格时 XML 兜底"""
    from render_check import backend_injected
    out_dir = os.path.join(HERE, "_req_tmp")
    os.makedirs(out_dir, exist_ok=True)
    r = backend_injected(tpl_path, out_dir, timeout)
    if not r.get("ok"):
        import xml.etree.ElementTree as ET
        try:
            return xml_fallback_rj(tpl_path, r.get("reason"))
        except Exception:
            raise RuntimeError("渲染失败: %s" % str(r.get("reason"))[:200])
    return json.load(open(r["html"], encoding="utf-8"))


def _local(tag):
    return tag.rsplit("}", 1)[-1] if "}" in str(tag) else str(tag)


def xml_fallback_rj(tpl_path, reason):
    """引擎提取失败(实证: 老模板混淆 sheet 类 cellIterator 抛 UOE) → 纯 XML 兜底构造渲染等价结构。
    格子布局/静态值/公式/图表位全保真(模板 XML 即事实源); 计算值与字体直方图缺席。"""
    import xml.etree.ElementTree as ET
    root = ET.parse(tpl_path).getroot()
    cells = []
    for ce in root.iter():
        if _local(ce.tag) != "C":
            continue
        c = int(ce.get("c", "0")); r = int(ce.get("r", "0"))
        cs = int(ce.get("cs", "1")); rs = int(ce.get("rs", "1"))
        v, t = None, "str"
        for ch in ce:
            ln = _local(ch.tag)
            if ln == "O":
                cls = ch.get("class", "")
                if "Chart" in cls:
                    t, v = "chart", cls.rsplit(".", 1)[-1]
                else:
                    txt = (ch.text or "").strip()
                    m_ = re.search(r"<!\[CDATA\[(.*)\]\]>", ET.tostring(ch, encoding="unicode"))
                    v = (m_.group(1) if m_ else txt) or txt
            elif ln == "RichText" and v is None:
                strs = [x.text or "" for x in ch.iter() if _local(x.tag) == "Text"]
                v = "".join(strs)
        if v not in (None, ""):
            cells.append({"c": c, "r": r, "cs": cs, "rs": rs, "v": v, "t": t})
    params = []
    for w in root.iter():
        lw = _local(w.tag)
        if lw == "Widget" or lw.endswith("Editor") or "Widget" in lw:
            cls, nm = w.get("class", ""), w.get("widgetName", "")
            if cls and nm and "container" not in cls.lower():
                params.append({"name": nm, "cls": cls})
    return {"kind": "cpt" if tpl_path.lower().endswith(".cpt") else "frm",
            "sheets": [{"name": "", "cells": cells}], "params": params,
            "fallback": True, "fallback_reason": str(reason)[:120]}


def is_dict_ds(name):
    """字典类数据集(dict_xxx / ds_dict_xxx): 逻辑简单, 不建示例/SQL 页, 取值并入参数区"""
    return bool(re.search(r"(?:^|_)dict(?:_|$)", name))


def dict_lookup(meta, pname):
    """参数名 → 字典数据集: para_year→dict_year(剥前缀匹配); 返回 (数据集名, 枚举值列表, 总行数)"""
    key = re.sub(r"^(para_|p_|filter_)", "", pname or "")
    for d in meta:
        dn = d["name"]
        if is_dict_ds(dn) and dn.split("dict")[-1].strip("_") == key:
            vs = [str(r[0]) for r in (d.get("rows") or []) if r and r[0] is not None]
            return dn, vs, d.get("totalRows")
    return None, None, None


def fmt_enum(vs, total=None):
    """枚举压缩: ≤6 全列; >6 首尾+计数"""
    if not vs:
        return ""
    if len(vs) <= 6:
        return " | ".join(vs)
    return "%s … %s (共%s)" % (vs[0], vs[-1], total or len(vs))


def build_cpt(wb, tpl, meta, rj, used, title):
    from openpyxl.utils import get_column_letter
    dsc = parse_ds_columns(tpl)
    charts = {(c["c"], c["r"]): c for s in rj.get("sheets", []) for c in s.get("cells", []) if c.get("t") == "chart"}
    for si, s in enumerate(rj.get("sheets", [])):
        sname = sheet_safe("表样_%s%s" % (title, "" if len(rj["sheets"]) == 1 else "_s%d" % si), used)
        ws = wb.create_sheet(sname)
        # ── 顶部 5 行: 参数面板示例(字典类数据集取值并入此处 — 核心逻辑即取值枚举) ──
        if rj.get("fallback"):
            # XML 兜底模式: params 无坐标, 只排容器类
            plist = [p for p in (rj.get("params") or [])
                     if "container" not in (p.get("cls") or "").lower()]
        else:
            plist = [p for p in (rj.get("params") or [])
                     if p.get("x") is not None and "BoundsWidget" not in (p.get("cls") or "")
                     and "Layout" not in (p.get("cls") or "").rsplit(".", 1)[-1]]
        from openpyxl.styles import Font
        for i, p in enumerate(plist[:16]):
            col = i + 1
            c1 = ws.cell(row=1, column=col, value="[参数] %s" % (p.get("name") or "?"))
            c1.font = Font(bold=True)
            dn, vs, total = dict_lookup(meta, p.get("name"))
            if dn:
                # 字典参数: 枚举压缩展示 + 来源标注
                ws.cell(row=2, column=col, value=fmt_enum(vs, total) or "示例值")
                src = ws.cell(row=3, column=col, value="← %s" % dn)
                src.font = Font(size=8, color="FF888888")
            else:
                ws.cell(row=2, column=col, value="示例值")
        ws.cell(row=4, column=1, value="↑ 参数面板区(约定 5 行; 字典取值见上; 导入设计器后可删)")
        # ── 网格: r=0 → Excel 行 PARAM_ROWS+1 ──
        colw, rowh = s.get("colW") or [], s.get("rowH") or []
        for ci, w in enumerate(colw[:80]):
            ws.column_dimensions[get_column_letter(ci + 1)].width = max(round(w / 7, 1), 3)
        cells = s.get("cells", [])
        maxc = max((c["c"] + c.get("cs", 1) for c in cells), default=1)
        maxr = max((c["r"] + c.get("rs", 1) for c in cells), default=1)
        for ri in range(maxr):
            if ri < len(rowh):
                ws.row_dimensions[PARAM_ROWS + 1 + ri].height = max(round(rowh[ri] * 0.75, 1), 12)
        for c in cells:
            r0, c0 = c["r"] + PARAM_ROWS + 1, c["c"] + 1
            is_ref = (c["c"], c["r"]) in dsc
            if is_ref:
                val = dsc[(c["c"], c["r"])]        # ds.field / 公式原文
            elif (c["c"], c["r"]) in charts:
                val = "[图表 %s]" % charts[(c["c"], c["r"])].get("v", "")
            else:
                val = c.get("v")
            if val in (None, ""):
                continue
            try:
                cell = ws.cell(row=r0, column=c0, value=val)
            except AttributeError:
                continue  # 落进已合并区的格(老模板重叠声明) — 跳过
            if isinstance(val, str) and val.startswith("="):
                cell.data_type = "s"               # 防止 Excel 当公式解析(需求清单要显示原文)
            if c.get("cs", 1) > 1 or c.get("rs", 1) > 1:
                ws.merge_cells(start_row=r0, start_column=c0,
                               end_row=r0 + c.get("rs", 1) - 1, end_column=c0 + c.get("cs", 1) - 1)
            from openpyxl.styles import Alignment, PatternFill, Font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            if is_ref:
                cell.font = Font(color="FF1F5FBF", size=9)   # DB 引用蓝字
                cell.fill = PatternFill("solid", fgColor="FFF2F7FD")
            elif str(val).startswith("[图表"):
                cell.font = Font(color="FF8A5100")
                cell.fill = PatternFill("solid", fgColor="FFFDF3E7")


def build_frm(wb, tpl, rj, used, title):
    from openpyxl.utils import get_column_letter
    ws = wb.create_sheet(sheet_safe("表样_%s" % title, used))
    from openpyxl.styles import Font
    ws.cell(row=1, column=1, value="↓ frm 画布式表样(合并格=组件分布; 坐标=px÷%d/%d)" % (PX_PER_COL, PX_PER_ROW)).font = \
        Font(bold=True)
    leaves = []
    for w in rj.get("widgets", []):
        cls = (w.get("cls") or "").rsplit(".", 1)[-1]
        if "BoundsWidget" in cls or "Layout" in cls:
            continue
        if w.get("x") is None:
            continue
        leaves.append(w)
    grid_c = max((w["x"] + w.get("w", 0) for w in leaves), default=1020) // PX_PER_COL + 2
    grid_r = max((w["y"] + w.get("h", 0) for w in leaves), default=720) // PX_PER_ROW + 3
    for ci in range(grid_c):
        ws.column_dimensions[get_column_letter(ci + 1)].width = 4.5
    seen = {}
    canvas_w = max((w["x"] + w.get("w", 0) for w in leaves), default=1020)
    canvas_h = max((w["y"] + w.get("h", 0) for w in leaves), default=720)
    canvas_area = canvas_w * canvas_h
    # 全画布背景层(面积≥70%画布)不占位 — 否则 merge 吞掉整个画布, 其余控件无处安放
    placed = [w for w in leaves if w.get("w", 0) * w.get("h", 0) < canvas_area * 0.7]
    backgrounds = [w for w in leaves if w not in placed]
    if backgrounds:
        ws.cell(row=2, column=1, value="[背景层] %s(全画布, 不占格)" % ", ".join(
            (b.get("name") or "?") for b in backgrounds))
    # 关键: 按面积降序 — openpyxl merge 会抹掉区域内已写值, 大区域必须先占位
    for w in sorted(placed, key=lambda t: -(t.get("w", 0) * t.get("h", 0))):
        cls = (w.get("cls") or "").rsplit(".", 1)[-1]
        name = w.get("name") or cls
        c0 = w["x"] // PX_PER_COL + 1
        r0 = w["y"] // PX_PER_ROW + 3
        cc = max(w.get("w", 0) // PX_PER_COL, 1)
        rr = max(w.get("h", 0) // PX_PER_ROW, 1)
        key = (c0, r0)
        seen[key] = seen.get(key, 0) + 1
        tag = "⧉%s " % seen[key] if seen[key] > 1 else ""
        if "Chart" in cls:
            label, fill = "%s[图表] %s" % (tag, name), "FFFDF3E7"
        elif "ElementCase" in cls:
            label, fill = "%s[报表块] %s" % (tag, name), "FFEEF7EE"
        else:
            label, fill = "%s[%s] %s" % (tag, cls, name), "FFF2F2F2"
        # 写值位: 跳过已有值格 与 merge 覆盖格(repro 实证: merge 左上格是普通 Cell,
        # 不能只看 MergedCell 类型 — 否则层叠卡片互相覆盖, 最后写的赢)
        write_col = c0
        while True:
            probe = ws.cell(row=r0, column=write_col)
            if type(probe).__name__ != "MergedCell" and probe.value in (None, ""):
                break
            write_col += 1
        cell = ws.cell(row=r0, column=write_col, value=label)
        cell.font = Font(size=9)
        from openpyxl.styles import PatternFill, Border, Side
        cell.fill = PatternFill("solid", fgColor=fill)
        bd = Border(*[Side(style="thin", color="FF999999")] * 4)
        if write_col == c0:
            # 该位第一张: 占位 merge(重叠=层叠组后续张, 吞异常即可)
            try:
                ws.merge_cells(start_row=r0, start_column=c0, end_row=r0 + rr - 1, end_column=c0 + cc - 1)
                for rx in range(r0, r0 + rr):
                    for cx in range(c0, c0 + cc):
                        ws.cell(row=rx, column=cx).border = bd
            except Exception:
                pass


def collect_report(tpl, rows, timeout):
    """单报表采集: 元数据+取数 / 渲染 / 填报超链脚本 — 返回 report dict"""
    title = os.path.splitext(os.path.basename(tpl))[0]
    meta = json.loads(agent_exec(META_JS.replace("__TPL__", tpl.replace("\\", "/"))
                                 .replace("__ROWS__", str(rows)), timeout=timeout))
    rj = render_json(tpl, timeout)
    return {"title": title, "path": tpl, "meta": meta, "rj": rj,
            "is_frm": tpl.lower().endswith(".frm"),
            "winfo": extract_write(tpl), "jumps": extract_jumps(tpl),
            "sinfo": extract_scripts(tpl),
            "tables": parse_tables_from_sql([d.get("sql") for d in meta if d.get("sql")])}


def main():
    ap = argparse.ArgumentParser(description="需求确认清单生成器(逆向; 支持目录=项目级聚合)")
    ap.add_argument("tpl", help="cpt/frm 路径或项目目录")
    ap.add_argument("out", nargs="?", help="输出 xlsx(默认 <名>_需求确认清单.xlsx)")
    ap.add_argument("--rows", type=int, default=10, help="每数据集示例行数(默认10)")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--limit", type=int, default=0, help="项目模式仅处理前 N 个模板(测试用)")
    a = ap.parse_args()
    target = os.path.abspath(a.tpl)

    # ── 目标解析: 目录 → 项目模式(排除 _backup*); 文件 → 单报表模式 ──
    if os.path.isdir(target):
        files = sorted(glob.glob(os.path.join(target, "**", "*.cpt"), recursive=True)
                       + glob.glob(os.path.join(target, "**", "*.frm"), recursive=True))
        files = [f for f in files if not re.search(r"_backup|(^|[\\/])out[\\/]", f)]
        if a.limit:
            files = files[:a.limit]
        proj_name = os.path.basename(target)
        out = os.path.abspath(a.out or os.path.join(HERE, proj_name + "_项目需求确认清单.xlsx"))
    elif os.path.isfile(target):
        files = [target]
        proj_name = os.path.splitext(os.path.basename(target))[0]
        out = os.path.abspath(a.out or os.path.join(HERE, proj_name + "_需求确认清单.xlsx"))
    else:
        print("❌ 路径不存在: %s" % target)
        return 2
    if not files:
        print("❌ 未找到模板文件")
        return 2

    # ── 采集(逐报表: 元数据+真取数 / 渲染 / 交付提取) ──
    reports, failed = [], []
    for i, f in enumerate(files):
        print("[%d/%d] 采集 %s ..." % (i + 1, len(files), os.path.basename(f)))
        try:
            reports.append(collect_report(f, a.rows, a.timeout))
        except Exception as e:
            failed.append((os.path.basename(f), str(e)[:100]))
            print("    ⚠ 失败(跳过): %s" % str(e)[:100])
    if not reports:
        print("❌ 全部采集失败")
        return 2
    print("采集完成: %d 成功 / %d 失败" % (len(reports), len(failed)))

    # ── 项目级聚合 ──
    # 实体表并集(表 → 引用报表)
    table_refs = {}
    for rp in reports:
        for t in rp["tables"]:
            table_refs.setdefault(t, set()).add(rp["title"])
    tables = sorted(table_refs)
    # 数据集去重(同名合并, 记来源报表; 保留行数最多的一份)
    ds_map = {}
    for rp in reports:
        for d in rp["meta"]:
            if is_dict_ds(d["name"]):
                continue
            e = ds_map.setdefault(d["name"], {"d": d, "src": set()})
            e["src"].add(rp["title"])
            if len(d.get("rows") or []) > len(e["d"].get("rows") or []):
                e["d"] = d
    # 参数并集(同名合并, 字典取值在所属报表 meta 内找)
    param_rows = []
    seen_p = {}
    for rp in reports:
        for p in (rp["rj"].get("params") or []):
            nm, cls = p.get("name") or "", (p.get("cls") or "").rsplit(".", 1)[-1]
            if not nm or "BoundsWidget" in cls or "Layout" in cls:
                continue
            if nm in seen_p:
                seen_p[nm]["src"].add(rp["title"])
                continue
            dn, vs, total = dict_lookup(rp["meta"], nm)
            seen_p[nm] = {"cls": cls, "dn": dn, "vs": vs, "total": total, "src": {rp["title"]}}
    param_rows = sorted(seen_p.items(), key=lambda kv: kv[0])
    # 连接名(任一报表)
    conn_name = ""
    for rp in reports:
        raw = next((d.get("conn") for d in rp["meta"] if d.get("conn")), "") or ""
        m_ = re.search(r"\[([^\]\s]+)", raw)
        conn_name = m_.group(1) if m_ else raw.strip()
        if conn_name:
            break

    # 实体表结构探查(SQL 代理: 任一含 DBTableData 的模板)
    tinfo = []
    if tables:
        proxy_tpl = next((rp["path"] for rp in reports
                          if any(d.get("cls") == "DBTableData" for d in rp["meta"])), None)
        if proxy_tpl:
            print("[*] agent: 实体表结构+样例(SQL 代理, %d 表) ..." % len(tables))
            try:
                tinfo = fetch_table_info(proxy_tpl, tables, a.rows, a.timeout)
            except Exception as e:
                print("    ⚠ 表结构探查失败(不阻断): %s" % str(e)[:120])

    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    used = set()
    wb = Workbook()
    ws = wb.active
    ws.title = "物料信息"

    YEL = PatternFill("solid", fgColor="FFFFF9DB")
    SEC = PatternFill("solid", fgColor="FFE8F0FE")

    def section(row, label):
        c = ws.cell(row=row, column=1, value=label)
        c.font = Font(bold=True, size=12)
        for col in range(1, 7):
            ws.cell(row=row, column=col).fill = SEC
        return row + 1

    def kv(row, key, val="", yellow=False):
        ws.cell(row=row, column=1, value=key).font = Font(bold=True)
        c = ws.cell(row=row, column=2, value=val)
        if yellow:
            c.fill = YEL
        return row + 1

    n_frm = sum(1 for rp in reports if rp["is_frm"])
    # 预计算表样 sheet 真实名(同名报表 ~2/~3 去重; 总览二区索引与建页共用同一确定性序列)
    tpl_sheet = {}
    _tu = set()
    for rp in reports:
        tpl_sheet[rp["path"]] = sheet_safe("表样_%s" % rp["title"], _tu)
    # ════ Sheet1 需求总览(物料信息) — 项目级九区(交付反推) ════
    ws["A1"] = "需求确认清单 — 需求总览(物料信息)"
    ws["A1"].font = Font(bold=True, size=14)
    row = 3

    # 一、项目与责任
    row = section(row, "一、项目与责任")
    row = kv(row, "项目名称", proj_name, True)
    row = kv(row, "需求编号", "", True)
    row = kv(row, "业务负责人(需求方)", "", True)
    row = kv(row, "开发负责人", "", True)
    row = kv(row, "运维负责人(交付接收方)", "", True)
    row = kv(row, "需求日期", "", True)
    row = kv(row, "交付日期(目标)", "", True)
    row = kv(row, "确认日期(签字)", "", True)
    row = kv(row, "报表范围", "%d 张(cpt %d / frm %d)%s" % (
        len(reports), len(reports) - n_frm, n_frm,
        "; 采集失败 %d 张" % len(failed) if failed else ""))
    row = kv(row, "清单版本", "V1.0(逆向生成 %s)" % __import__("datetime").date.today().isoformat())
    row = kv(row, "生成方式", "req_workbook.py 项目级逆向(真引擎渲染+真取数+表结构实测)")
    if failed:
        row = kv(row, "⚠ 采集失败清单", "; ".join(f for f, _ in failed)[:200])
    row += 1

    # 二、报表清单(项目索引)
    row = section(row, "二、报表清单")
    for i, h in enumerate(["报表名称", "类型", "数据集", "填报", "用途说明(待填)", "表样sheet"]):
        ws.cell(row=row, column=i + 1, value=h).font = Font(bold=True)
    row += 1
    for rp in reports:
        ws.cell(row=row, column=1, value=rp["title"])
        ws.cell(row=row, column=2, value="frm" if rp["is_frm"] else "cpt")
        ws.cell(row=row, column=3, value=len(rp["meta"]))
        ws.cell(row=row, column=4, value="✔" if rp["winfo"] else "")
        ws.cell(row=row, column=5, value="").fill = YEL
        ws.cell(row=row, column=6, value=tpl_sheet[rp["path"]])
        row += 1
    row += 1

    # 三、数据库表资源与表结构
    row = section(row, "三、数据库表资源与表结构(字段明细见 T_ 实体页)")
    if tables:
        for i, h in enumerate(["表名", "数据连接", "引用报表数", "字段数", "估算行数"]):
            ws.cell(row=row, column=i + 1, value=h).font = Font(bold=True)
        row += 1
        for t in tables:
            ti = next((x for x in tinfo if x["table"] == t), {})
            ws.cell(row=row, column=1, value=t)
            ws.cell(row=row, column=2, value=conn_name)
            ws.cell(row=row, column=3, value=len(table_refs[t]))
            ws.cell(row=row, column=4, value=len(ti.get("cols") or []) or "?")
            ws.cell(row=row, column=5, value=ti.get("approxRows", "?"))
            row += 1
    else:
        ws.cell(row=row, column=1, value="(无 DB 实体表 — 数据为内嵌/无数据集)")
        row += 1
    row += 1

    # 四、数据集清单(项目去重)
    row = section(row, "四、数据集清单(项目去重; SQL+示例见'数据集逻辑'页; 字典类并入参数区)")
    for i, h in enumerate(["数据集", "类型", "总行数", "列数", "来源报表数", "参数依赖"]):
        ws.cell(row=row, column=i + 1, value=h).font = Font(bold=True)
    row += 1
    for nm in sorted(ds_map):
        e = ds_map[nm]
        d = e["d"]
        deps = sorted(set(re.findall(r"\b(para_\w+)\b", d.get("sql") or "")))
        ws.cell(row=row, column=1, value=nm)
        ws.cell(row=row, column=2, value=d.get("cls", "?"))
        ws.cell(row=row, column=3, value=d.get("totalRows", "?"))
        ws.cell(row=row, column=4, value=len(d.get("cols") or []))
        ws.cell(row=row, column=5, value=len(e["src"]))
        ws.cell(row=row, column=6, value=",".join(deps) if deps else "")
        row += 1
    row += 1

    # 五、参数清单(项目并集)
    row = section(row, "五、参数清单(项目并集; 字典取值枚举)")
    for i, h in enumerate(["参数名", "控件类型", "取值来源", "取值枚举", "出现报表数"]):
        ws.cell(row=row, column=i + 1, value=h).font = Font(bold=True)
    row += 1
    for nm, p in param_rows:
        ws.cell(row=row, column=1, value=nm)
        ws.cell(row=row, column=2, value=p["cls"])
        ws.cell(row=row, column=3, value=p["dn"] or "")
        ws.cell(row=row, column=4, value=fmt_enum(p["vs"], p["total"]) if p["dn"] else "")
        ws.cell(row=row, column=5, value=len(p["src"]))
        row += 1
    row += 1

    # 六、填报·交互·权限(项目级表格式: 每报表一行)
    row = section(row, "六、填报·交互·权限(运维排障关键; 仅列有填报/超链的报表)")
    for i, h in enumerate(["报表", "填报回写表", "主键", "超链跳转→", "脚本(监听/JS)"]):
        ws.cell(row=row, column=i + 1, value=h).font = Font(bold=True)
    row += 1
    n_w = 0
    for rp in reports:
        w, j, s = rp["winfo"], rp["jumps"], rp["sinfo"]
        if not (w or j):
            continue
        n_w += 1
        ws.cell(row=row, column=1, value=rp["title"])
        if w:
            ws.cell(row=row, column=2, value=", ".join(w["tables"]) or "?")
            ws.cell(row=row, column=3, value=",".join(w["keys"])[:40] or "(未标)")
        ws.cell(row=row, column=4, value=" | ".join(j[:3]) + (" …" if len(j) > 3 else ""))
        ws.cell(row=row, column=5, value="%d/%d" % (s["listeners"], s["js"]))
        row += 1
    if n_w == 0:
        ws.cell(row=row, column=1, value="(全项目无填报/无超链)")
        row += 1
    row = kv(row, "目录挂载路径(待填)", "", True)
    row = kv(row, "可访问角色/部门(待填)", "", True)
    row = kv(row, "数据行级权限口径(待填)", "", True)
    row += 1

    # 七、业务背景与口径
    row = section(row, "七、业务背景与口径(待用户填写)")
    for k in ["业务背景与目标", "指标口径定义", "数据范围(组织/期间)", "使用受众与场景",
              "刷新频率/时效要求", "验收标准"]:
        ws.cell(row=row, column=1, value=k).font = Font(bold=True)
        ws.cell(row=row, column=2).fill = YEL
        ws.cell(row=row, column=3).fill = YEL
        row += 1
    row += 1

    # 八、运行与运维要素
    row = section(row, "八、运行与运维要素(交付运维关键)")
    row = kv(row, "调度要求(频率/时刻)", "", True)
    row = kv(row, "数据刷新窗口/SLA", "", True)
    row = kv(row, "停机影响面(谁在用/何时不可停)", "", True)
    row = kv(row, "下游使用方(报表/人员/流程)", "", True)
    ds_base = "; ".join("%s=%s行" % (nm, e["d"].get("totalRows", "?"))
                        for nm, e in sorted(ds_map.items())
                        if e["d"].get("totalRows") is not None)
    row = kv(row, "数据质量基线(当前实测)", ds_base[:250] or "(见数据集逻辑页)")
    row = kv(row, "行数正常范围/空值率阈值", "", True)
    row = kv(row, "故障第一联系人", "", True)
    row += 1

    # 九、确认与变更记录
    row = section(row, "九、确认与变更记录")
    for i, h in enumerate(["版本", "日期", "确认人", "变更说明"]):
        ws.cell(row=row, column=i + 1, value=h).font = Font(bold=True)
    row += 1
    ws.cell(row=row, column=1, value="V1.0")
    ws.cell(row=row, column=2, value=__import__("datetime").date.today().isoformat())
    ws.cell(row=row, column=3, value="").fill = YEL
    ws.cell(row=row, column=4, value="逆向生成底稿(待业务确认)").fill = YEL
    row += 1

    for cw, w in zip("ABCDEF", [30, 34, 30, 16, 18, 40]):
        ws.column_dimensions[cw].width = w

    # ════ 实体表样例页 T_(全项目去重) ════
    n_ent = 0
    for ti in tinfo:
        if ti.get("err") or not ti.get("cols"):
            continue
        short = ti["table"].split(".")[-1]
        sname = sheet_safe("T_%s" % short[:24], used)
        we = wb.create_sheet(sname)
        we["A1"] = "实体表 %s | %d 字段 | 估算 %s 行 | 引用报表 %s" % (
            ti["table"], len(ti["cols"]), ti.get("approxRows", "?"),
            len(table_refs.get(ti["table"], ())))
        we["A1"].font = Font(bold=True)
        we["A2"] = "字段: " + "; ".join("%s %s" % (c[0], c[1]) for c in ti["cols"])
        we["A2"].font = Font(size=9, color="FF666666")
        we.append([])
        we.append(ti.get("sampleCols") or [c[0] for c in ti["cols"]])
        for c in we[4]:
            c.font = Font(bold=True)
        for r_ in ti.get("sample") or []:
            we.append(r_)
        we.append(["… 样例截取前 %d 行" % len(ti.get("sample") or [])])
        n_ent += 1
    print("[*] 实体页 T_: %d 个(项目去重)" % n_ent)

    # ════ 数据集逻辑页(单页分节: SQL + 示例数据同屏; 项目去重) ════
    if ds_map:
        wsl = wb.create_sheet("数据集逻辑")
        wsl.column_dimensions["A"].width = 26
        wsl.column_dimensions["B"].width = 96
        rr = 1
        for nm in sorted(ds_map):
            e = ds_map[nm]
            d = e["d"]
            h = wsl.cell(row=rr, column=1, value="◆ %s" % nm)
            h.font = Font(bold=True, size=12)
            wsl.cell(row=rr, column=2,
                     value="%s | %s 行 | 来源报表(%d): %s" % (
                         d.get("cls", "?"), d.get("totalRows", "?"), len(e["src"]),
                         ", ".join(sorted(e["src"]))[:70])).font = Font(size=9, color="FF666666")
            rr += 1
            if d.get("sql"):
                for ln in d["sql"].split("\n"):
                    wsl.cell(row=rr, column=1, value=ln).font = Font(name="Consolas", size=9)
                    rr += 1
            if d.get("cols"):
                wsl.cell(row=rr, column=1, value="示例(%d列):" % len(d["cols"])).font = Font(bold=True, size=9)
                wsl.cell(row=rr, column=2, value=" | ".join(str(c) for c in d["cols"])[:200])
                rr += 1
                for rowd in (d.get("rows") or [])[:a.rows]:
                    wsl.cell(row=rr, column=2,
                             value=" | ".join("" if v is None else str(v) for v in rowd)[:200])
                    rr += 1
            rr += 2  # 节间空行
        print("[*] 数据集逻辑页: 1 页(%d 数据集)" % len(ds_map))

    # ════ 表样(每报表一页) ════
    for k, rp in enumerate(reports):
        if rp["is_frm"]:
            build_frm(wb, rp["path"], rp["rj"], used, rp["title"])
        else:
            build_cpt(wb, rp["path"], rp["meta"], rp["rj"], used, rp["title"])
        if (k + 1) % 10 == 0:
            print("[*] 表样 %d/%d ..." % (k + 1, len(reports)))
    print("[*] 表样页: %d 个" % len(reports))

    try:
        wb.save(out)
    except PermissionError:
        out = out.replace(".xlsx", "_v2.xlsx")
        wb.save(out)
        print("⚠ 原文件被 Excel 占用, 已另存: %s" % out)
    print("✅ 生成: %s (%d sheets)" % (out, len(wb.sheetnames)))
    print("   结构: 物料信息 + %d 实体页 + %s + %d 表样页" % (
        n_ent, "1 数据集逻辑页" if ds_map else "-", len(reports)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
