# -*- coding: utf-8 -*-
"""checks/fr_api.py — FineReport 官方前端 JS API 探针片段库。

信条: 能用 FR 官方 API(contentPane/_g() 等, 见 ckzl/zsk/qdjk/references/api_*.md)拿到的信息,
绝不用裸 DOM 刮取; API 拿不到时 DOM 兜底; 再失败返回 None, 绝不抛异常打断体检。

依据文档(本地离线版 dev.fanruan.com/jsdoc):
  - contentPane.getWidgetByName / widget.getValue/setValue/isVisible/isEnabled/getType/getText
    → api_widgets.md FR.Widget 基类方法表 + api_report.md §3 FR.WritePane
  - contentPane.getCellValue(col,row) → api_report.md §3 (⚠仅 op=write 生效, 文档注明)
  - contentPane.curLGP.getTDCell(col,row) → api_report.md §6 FR.WLGP(getTDCell 返回 jQuery)
  - contentPane.parameterEl → 速查表 §1.1 核心对象层次(参数面板)
  - FR.Chart.WebUtils.getChart(name) → 速查表 §1.5

FR10 实测修正(2026-09-05, L6 泳道 119 条断言实测, 见 _runs/night/20260904/L6/REPORT.md §⑤-1):
  - getTDCell 返回原生 DOM TD(非 jQuery): 读文本用 innerText/textContent, td.text() 不存在
  - parameterEl 为参数容器对象(own keys: options/name_widgets/rootWidget), 非 jQuery: 无 width()
  - 参数容器无 getWidgetsAll(): 控件名册枚举用 Object.keys(pel.name_widgets||{})
  - getWidgetByCell 只收 '列字母+1基行号' 字符串(数字抛 str.match)
  - 图表探测按 DOM id 猜测命中率为 0: 图表 id 应从模板 facts 精确注入(chart_list chart_ids)
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

import json
import os


# ────────────────────────────────────────────────────────────
# frame 定位(兜底版; ctx.find_report_frame(page) 优先, 由调用方决定)
# ────────────────────────────────────────────────────────────

# 报告区 frame 标记: 有 contentPane(FR 报表 iframe)或已渲染的 .x-table/.sheet
FRAME_MARKER_JS = (
    "(function(){try{"
    "return !!(window.contentPane || document.querySelector('.x-table,.sheet-container,.fr-sheet-switch-container'));"
    "}catch(e){return false;}})()"
)


def find_report_frame(page):
    """兜底: 遍历 page.frames, 返回第一个含 contentPane 或报告表格的 frame; 找不到返回 None。"""
    try:
        frames = [page.main_frame] + [f for f in page.frames if f is not page.main_frame]
    except Exception:
        return None
    # 先找 contentPane(权威), 再退表格标记
    hit_table = None
    for fr in frames:
        try:
            if fr.evaluate(FRAME_MARKER_JS):
                has_cp = False
                try:
                    has_cp = bool(fr.evaluate("typeof window.contentPane!=='undefined' && !!window.contentPane"))
                except Exception:
                    pass
                if has_cp:
                    return fr
                if hit_table is None:
                    hit_table = fr
        except Exception:
            continue
    return hit_table


def eval_js(frame, js, arg=None):
    """frame.evaluate 的静默包装: 任何异常返回 None。"""
    try:
        return frame.evaluate(js, arg)
    except Exception:
        return None


def get_contentpane(page_or_frame):
    """返回持有 contentPane 的 frame(优先入参 frame, 其次遍历); 没有→None。"""
    frame = page_or_frame
    has_cp = lambda f: eval_js(f, "typeof window.contentPane!=='undefined' && !!window.contentPane")
    try:
        if has_cp(frame):
            return frame
    except Exception:
        pass
    try:
        for f in page_or_frame.page.frames:
            if has_cp(f):
                return f
    except Exception:
        pass
    return None


# ────────────────────────────────────────────────────────────
# 1. list_widgets — 枚举参数面板控件(FR API: getWidgetByName + FR.Widget 基类)
# ────────────────────────────────────────────────────────────

_LIST_WIDGETS_JS = (
    "(function(names){try{"
    "var cp = window.contentPane || (window._g ? _g() : null);"
    "if(!cp || !cp.getWidgetByName) return null;"
    "function str(v){try{if(v===null||v===undefined) return null;"
    "  if(typeof v==='object'){return JSON.stringify(v);} return String(v);}catch(e){return null;}}"
    "var out=[];"
    "for(var i=0;i<names.length;i++){"
    "  var n=names[i], w=null;"
    "  try{w=cp.getWidgetByName(n);}catch(e){w=null;}"
    "  if(!w){out.push({name:n, found:false}); continue;}"
    "  var o={name:n, found:true};"
    "  try{o.type = w.getType ? str(w.getType()) : null;}catch(e){o.type=null;}"
    "  try{o.value = w.getValue ? str(w.getValue()) : null;}catch(e){o.value=null;}"
    "  try{o.text  = w.getText  ? str(w.getText())  : null;}catch(e){o.text=null;}"
    "  try{o.visible = w.isVisible ? !!w.isVisible() : null;}catch(e){o.visible=null;}"
    "  try{o.enabled = w.isEnabled ? !!w.isEnabled() : null;}catch(e){o.enabled=null;}"
    "  o.rect=null;"
    "  try{var el=(w.element&&(w.element[0]||w.element))||null;"
    "    if(el&&el.getBoundingClientRect){var r=el.getBoundingClientRect();"
    "      o.rect={x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height)};}"
    "  }catch(e){}"
    "  out.push(o);"
    "}"
    # L6 修正(2026-09-05): FR10 parameterEl 是参数容器对象(own keys: options/name_widgets/rootWidget...)
    # 非 jQuery, width()/[0] 均不存在 → 面板矩形改 pel.element/options.element 探测,
    # 失败兜底 .parameter-container DOM(与 panel_rect 同源); width 取矩形宽
    "var panel={width:null, rect:null};"
    "try{var pel=cp.parameterEl||null, pe=null;"
    "  if(pel){pe=(pel.element&&(pel.element[0]||pel.element))"
    "    ||(pel.options&&pel.options.element&&(pel.options.element[0]||pel.options.element))||null;}"
    "  if(!pe){pe=document.querySelector('.parameter-container');}"
    "  if(pe&&pe.getBoundingClientRect){var pr=pe.getBoundingClientRect();"
    "    panel.width=Math.round(pr.width);"
    "    panel.rect={x:Math.round(pr.left),y:Math.round(pr.top),w:Math.round(pr.width),h:Math.round(pr.height)};}}catch(e){}"
    "return {widgets:out, panel:panel};"
    "}catch(e){return {error:String(e)};}})"
)


def list_widgets(frame, names):
    """用 FR API 枚举控件。names=cpt 声明名单。
    返回 dict {widgets:[{name,found,type,value,text,visible,enabled,rect}], panel:{width,rect}} 或 None。
    控件矩形用 widget.element 的 getBoundingClientRect(FR API 拿不到坐标, DOM 兜底属官方语义)。
    """
    if frame is None or not names:
        return None
    res = eval_js(frame, _LIST_WIDGETS_JS + "(" + json.dumps(list(names)) + ")")
    if isinstance(res, dict) and res.get("error"):
        return None
    return res if isinstance(res, dict) else None


# ────────────────────────────────────────────────────────────
# 1b. DOM 兜底枚举 — FR 渲染的每个控件根节点带 widgetname 属性(大小写不敏感匹配)
# ────────────────────────────────────────────────────────────

_DOM_WIDGETS_JS = (
    "(function(){try{"
    "var els=document.querySelectorAll('[widgetname]');var out=[];"
    "for(var i=0;i<els.length;i++){"
    "  var e=els[i],r=e.getBoundingClientRect();"
    "  if(r.width<=0&&r.height<=0){continue;}"
    "  out.push({name:e.getAttribute('widgetname'),"
    "            rect:{x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height)},"
    "            cls:e.className.toString().slice(0,60)});"
    "}"
    "return out;"
    "}catch(e){return null;}})"
)


def dom_widgets(frame):
    """DOM 兜底: 返回 [{name,rect,cls}] 或 None。FR 渲染控件根节点带 widgetname 属性。
    L6 边界(2026-09-05): 对匿名控件(XML 无 widgetName, 如填报页 TextArea)返回空——
    该场景走 anon_cell_widgets(getWidgetByCell('列字母+行号')) 路径。"""
    if frame is None:
        return None
    return eval_js(frame, _DOM_WIDGETS_JS + "()")


# L6 修正(2026-09-05): 填报页(op=write)单元格内嵌控件若 XML 无 widgetName, [widgetname] 枚举为空;
# 官方路径 contentPane.getWidgetByCell('C6')(列字母+1基行号, 数字坐标抛 str.match is not a function)
_ANON_CELL_WIDGETS_JS = (
    "(function(){try{"
    "var cp = window.contentPane || (window._g ? _g() : null);"
    "if(!cp || !cp.getWidgetByCell) return [];"
    "function colRef(c){var s='';c=c+1;"
    "  while(c>0){var m=(c-1)%26;s=String.fromCharCode(65+m)+s;c=Math.floor((c-1)/26);}"
    "  return s;}"
    "var tds=document.querySelectorAll('.x-table td, .sheet-container td');"
    "if(!tds.length){tds=document.querySelectorAll('table td');}"
    "var out=[], seen={};"
    "for(var i=0;i<tds.length&&out.length<50;i++){"
    "  var td=tds[i];"
    "  if(td.getAttribute('widgetname')){continue;}"   # 有名控件归 dom_widgets 管
    "  var ctl=td.querySelector('textarea,input,select,button,"
    "[class*=\"editor\"],[class*=\"combo\"],[class*=\"fr-trigger\"],[class*=\"fr-textbox\"]');"
    "  if(!ctl){continue;}"
    "  var tr=td.parentNode, row=-1;"
    "  try{row=Array.prototype.indexOf.call(tr.parentNode.children,tr);}catch(e){row=-1;}"
    "  if(row<0||td.cellIndex<0){continue;}"
    "  var ref=colRef(td.cellIndex)+(row+1);"
    "  if(seen[ref]){continue;} seen[ref]=1;"
    "  var w=null; try{w=cp.getWidgetByCell(ref);}catch(e){w=null;}"
    "  if(!w){continue;}"
    "  var r=td.getBoundingClientRect();"
    "  var o={name:null, ref:ref, found:true,"
    "         rect:{x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height)}};"
    "  try{o.type=w.getType?String(w.getType()):null;}catch(e){o.type=null;}"
    "  out.push(o);"
    "}"
    "return out;"
    "}catch(e){return null;}})"
)


def anon_cell_widgets(frame):
    """匿名单元格控件枚举(write 页)。返回 [{name:null,ref:'C6',type,rect}] 或 None。
    依据 L6 WR07R2: getWidgetByCell 只收 '列字母+1基行号' 字符串。"""
    if frame is None:
        return None
    return eval_js(frame, _ANON_CELL_WIDGETS_JS + "()")


_PANEL_RECT_JS = (
    "(function(){try{"
    "var pc=document.querySelector('.parameter-container');"
    "if(pc){var r=pc.getBoundingClientRect();"
    "  return {x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height)};}"
    "return null;"
    "}catch(e){return null;}})"
)


def panel_rect(frame):
    """面板可视矩形(DOM .parameter-container)。失败→None。"""
    if frame is None:
        return None
    return eval_js(frame, _PANEL_RECT_JS + "()")


# ────────────────────────────────────────────────────────────
# 2. get_cell_value — 单元格取值(contentPane.getCellValue → curLGP 兜底)
# ────────────────────────────────────────────────────────────

_GET_CELL_JS = (
    "(function(ar){try{"
    "var col=ar[0], row=ar[1];"
    "var cp = window.contentPane || (window._g ? _g() : null);"
    "if(!cp) return null;"
    "if(cp.getCellValue){try{var v=cp.getCellValue(col,row);"
    "  if(v!==undefined&&v!==null&&String(v)!=='') return {value:String(v), source:'api'};}catch(e){}}"
    # L6 修正(2026-09-05): FR10 getTDCell 返回原生 DOM TD 非 jQuery, td.text 不存在;
    # 读文本改 innerText/textContent, 并兼容旧版 jQuery 返回形态(td.jquery 时取 td[0])
    "if(cp.curLGP&&cp.curLGP.getTDCell){try{var td=cp.curLGP.getTDCell(col,row);"
    "  if(td){var el=td.jquery?td[0]:td;"
    "    var t=(el&&el.innerText&&el.innerText!=='')?el.innerText:((el&&el.textContent)||'');"
    "    if(t) return {value:String(t), source:'curLGP'};}}catch(e){}}"
    "return null;"
    "}catch(e){return null;}})"
)


def get_cell_value(frame, col, row):
    """取单元格显示值。返回 {value:str, source:'api'|'curLGP'} 或 None(不可得, 不报错)。"""
    if frame is None:
        return None
    return eval_js(frame, _GET_CELL_JS + "([" + str(int(col)) + "," + str(int(row)) + "])")


# ────────────────────────────────────────────────────────────
# 3. grid_metrics — 报告区表格指标(FR 无公开“行列/行高”API, DOM 兜底为文档允许路径)
# ────────────────────────────────────────────────────────────

_GRID_METRICS_JS = (
    "(function(maxRows){try{"
    "var xt=document.querySelector('.content-container .x-table, .sheet-container .x-table')"
    " || document.querySelector('.x-table');"
    "var trs=xt?xt.querySelectorAll('tr'):[];"
    "var rows=trs.length;"
    "var cols=0;"
    "if(rows){var cells0=trs[0].querySelectorAll('td,th'); cols=cells0.length;"
    "  for(var k=0;k<trs.length;k++){var c=trs[k].querySelectorAll('td,th').length;"
    "    if(c>cols){cols=c;}}}"
    "var heights=[];"
    "for(var i=0;i<Math.min(rows,maxRows);i++){"
    "  heights.push(Math.round(trs[i].getBoundingClientRect().height*10)/10);}"
    "var tds=xt?xt.querySelectorAll('td'):[];"
    "var ovf=0, samples=[];"
    "for(var j=0;j<tds.length;j++){"
    "  var td=tds[j];"
    "  if(td.scrollWidth>td.clientWidth+2 && td.clientWidth>0){"
    "    ovf++;"
    "    if(samples.length<3){"
    "      var trr=td.parentNode;"
    "      samples.push({row:Array.prototype.indexOf.call(trr.parentNode.children,trr),"
    "                   col:td.cellIndex, text:(td.innerText||'').slice(0,20)});}"
    "  }"
    "}"
    "return {rows:rows, cols:cols, row_heights:heights, td_total:tds.length,"
    "        overflow_count:ovf, overflow_samples:samples,"
    "        scoped:!!xt};"
    "}catch(e){return null;}})"
)


def grid_metrics(frame, max_rows=20):
    """报告区表格行/列数、行高采样(≤max_rows)、文本溢出计数+前3样例。失败→None。"""
    if frame is None:
        return None
    return eval_js(frame, _GRID_METRICS_JS + "(" + str(int(max_rows)) + ")")


# ────────────────────────────────────────────────────────────
# 4. chart_list — 页面图表实例数(FR.Chart API)
# ────────────────────────────────────────────────────────────

_CHART_LIST_JS = (
    "(function(ar){try{"
    "var res={fr_api:null, dom:0, names:[], matched:[]};"
    "var nodes=document.querySelectorAll('[id*=\"chart\" i], canvas');"
    "var ids={};"
    "for(var i=0;i<nodes.length;i++){"
    "  var id=nodes[i].id||nodes[i].getAttribute('id')||'';"
    "  if(id){ids[id]=1;}"
    "}"
    "res.dom=document.querySelectorAll('canvas').length;"
    "if(window.FR&&FR.Chart&&FR.Chart.WebUtils&&FR.Chart.WebUtils.getChart){"
    "  var ok=0;"
    "  var probe={};"
    "  var injected=ar&&ar.length;"
    "  if(injected){for(var a=0;a<ar.length;a++){probe[String(ar[a])]=1;}}"
    "  for(var id in ids){if(injected&&!probe[id]){continue;}"
    "    try{var c=FR.Chart.WebUtils.getChart(id);if(c){ok++;res.names.push(id);}}catch(e){}}"
    "  if(injected){for(var b=0;b<ar.length;b++){"
    "    try{var c2=FR.Chart.WebUtils.getChart(ar[b]);if(c2){res.matched.push(String(ar[b]));}}catch(e){}}}"
    "  res.fr_api=ok;"
    "}else{res.matched=null;}"
    "return res;"
    "}catch(e){return null;}})"
)


def chart_list(frame, chart_ids=None):
    """图表实例数。返回 {fr_api:int|null, dom:int, names:[...], matched:[...]} 或 None。
    chart_ids: cpt 模板声明的图表 id 列表(extract_chart_ids 提取)——精确探测,
    L6 实测按 DOM id 猜测在无/有图表页命中率均为 0; 未注入时保留旧猜测路径作兜底。"""
    if frame is None:
        return None
    arg_expr = json.dumps([str(x) for x in chart_ids]) if chart_ids else "null"
    return eval_js(frame, _CHART_LIST_JS + "(" + arg_expr + ")")


def extract_chart_ids(cpt_path):
    """从 cpt XML 提取图表 id 列表(给 chart_list 的 chart_ids 注入)。
    无图表/解析失败返回 []，不抛异常。"""
    ids = []
    if not cpt_path or not os.path.isfile(cpt_path):
        return ids
    try:
        import xml.etree.ElementTree as ET
        root = ET.parse(cpt_path).getroot()
        for el in root.iter():
            if "chart" in str(el.tag).lower():
                cid = el.attrib.get("id") or el.attrib.get("ID")
                if cid and cid not in ids:
                    ids.append(cid)
    except Exception:
        try:
            import re
            with open(cpt_path, "r", encoding="utf-8", errors="replace") as f:
                txt = f.read()
            for m in re.finditer(r"<[^>]*[Cc]hart[^>]*\bid=\"([^\"]+)\"", txt):
                if m.group(1) not in ids:
                    ids.append(m.group(1))
        except Exception:
            return []
    return ids


# ────────────────────────────────────────────────────────────
# 5. 超链弹窗探针(links.py 用)
# ────────────────────────────────────────────────────────────

# FR 渲染超链格的候选特征: td 内 a/span.fr-link / 内联下划线蓝色样式; 全部尝试, 不猜单一选择器
_LINK_CELL_CANDIDATES_JS = (
    "(function(limit){try{"
    "var tds=document.querySelectorAll('.x-table td, .sheet-container td');"
    "if(!tds.length){tds=document.querySelectorAll('table td');}"
    "var hits=[];"
    "for(var i=0;i<tds.length&&hits.length<limit;i++){"
    "  var td=tds[i], txt=(td.innerText||'').trim();"
    "  if(!txt) continue;"
    "  var marked=td.querySelector('a[href],.fr-link,[class*=\"link\"]');"
    "  var cs=getComputedStyle(td), inner=td.querySelector('span,div');"
    "  var cs2=inner?getComputedStyle(inner):null;"
    "  var deco=(cs.textDecorationLine||cs.textDecoration||'')+(cs2?(cs2.textDecorationLine||cs2.textDecoration||''):'');"
    "  var color=(cs2?cs2.color:cs.color)||'';"
    "  var blue=color.indexOf('0, 0, 238')>=0||color.indexOf('0, 0, 255')>=0||color.indexOf('17, 85, 204')>=0;"
    "  var underline=deco.indexOf('underline')>=0;"
    "  if(marked||blue||underline){"
    "    var tr=td.parentNode, r=td.getBoundingClientRect();"
    "    hits.push({row:Array.prototype.indexOf.call(tr.parentNode.children,tr),"
    "              col:td.cellIndex, text:txt.slice(0,30),"
    "              x:Math.round(r.left+r.width/2), y:Math.round(r.top+r.height/2)});}"
    "}"
    "return hits;"
    "}catch(e){return null;}})"
)

# 同页 DOM 弹窗探测: FR.Dialog/FR.Window 渲染的容器 + 内嵌 iframe
# 本机 FR10 build 弹窗根节点为 div.fr-core-window(带 fr-core-window-mask 遮罩), 兼容旧类名
_DIALOG_PROBE_JS = (
    "(function(){try{"
    "var sel='.fr-core-window,.fr-window-outer,.fr-dialog,.fr-window,[class*=\"fr-window\"],[class*=\"dialog-container\"]';"
    "var dlg=document.querySelectorAll(sel);"
    "var vis=[], srcs=[];"
    "for(var i=0;i<dlg.length;i++){"
    "  var d=dlg[i], cs=getComputedStyle(d);"
    "  if(cs.display!=='none'&&cs.visibility!=='hidden'&&d.getBoundingClientRect().height>50){"
    "    vis.push(d.className.toString().slice(0,60));"
    "    var ifs=d.querySelectorAll('iframe');"
    "    for(var j=0;j<ifs.length;j++){srcs.push(ifs[j].src);}"
    "  }"
    "}"
    "return {visible:vis, iframes:srcs};"
    "}catch(e){return null;}})"
)

# ---- 运行期校验状态(2026-09-04 迭代新增; 2026-09-05 L6 修正) ----
# L6 实测: FR10 参数容器无 getWidgetsAll()(undefined), 硬编码 ['para_legal',...] 兜底名单已废;
# 全量控件名册在 pel.name_widgets 映射(own keys), 外加调用方从 cpt facts 注入声明名(names 参数)
_JS_VALIDATION = """
(names) => {
  const out = [];
  try {
    const pel = (typeof contentPane !== 'undefined' && contentPane.parameterEl)
      ? contentPane.parameterEl : ((typeof _g === 'function' && _g()) ? _g().parameterEl : null);
    if (!pel) return out;
    const seen = {};
    const collect = (w) => {
      try {
        const n = w.getWidgetName ? w.getWidgetName() : (w.widgetName || (w.options && w.options.widgetName));
        // 去重必须落在 collect: name_widgets 主路径与 items 树兜底会命中同一控件(R27 实测 5×2 重复)
        if (!n || seen[String(n)]) return;
        seen[String(n)] = 1;
        let em = null;
        try { em = w.getErrorMsg && w.getErrorMsg(); } catch (e) { em = null; }
        if (em) out.push([String(n), String(em).slice(0, 60)]);
      } catch (e) {}
    };
    const scan = (n) => {
      if (!n || seen[String(n)]) return;
      try { const w = pel.getWidgetByName ? pel.getWidgetByName(n) : null; if (w) collect(w); } catch (e) {}
    };
    // 主路径: FR10 运行期名册(name_widgets keys, 实测返回 PARA/PARA_ENTITY/... 全部控件)
    try { Object.keys(pel.name_widgets || {}).forEach(scan); } catch (e) {}
    // 注入名补充扫描(cpt facts 声明名, 防运行期名册缺漏)
    if (Array.isArray(names)) { names.forEach(scan); }
    // 跨版本兜底: items 树遍历(部分版本存在 getWidgetsAll/getWidgets; FR10 下为 no-op 不报错)
    try {
      const all = (pel.items || (pel.widgets && pel.widgets.items) || []);
      const walk = (container) => {
        try {
          const arr = container.getWidgetsAll ? container.getWidgetsAll() : (container.getWidgets ? container.getWidgets() : null);
          if (arr && arr.length) { arr.forEach((w) => { collect(w); if (w.getWidgetsAll) walk(w); }); }
        } catch (e) {}
      };
      all.forEach((w) => { collect(w); walk(w); });
    } catch (e) {}
  } catch (e) {}
  return out;
};
"""


def widget_validation_errors(frame, names=None):
    """逐控件采集 getErrorMsg()（必填/字典校验）。frame=None 返回 None。
    names: cpt facts 声明控件名 list(由 widgets.py 注入), 作为运行期 name_widgets 名册的补充扫描。
    """
    if frame is None:
        return None
    try:
        return frame.evaluate(_JS_VALIDATION, list(names) if names else None)
    except Exception:
        return None
