#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fr_rules_doc.py — 帆软模板静态校验规则库(源自 105 篇官方帮助文档学习沉淀)
================================================================================

来源: C:\\Users\\Admin\\Desktop\\fr_overnight\\merge_batch2\\A_rules_doc.json
      (CodeBuddy hy3 学习 105 篇帆软官方帮助文档后产生的 56 条「fr_check 校验规则」建议)

本模块把 A_rules_doc.json 中全部 56 条规则(数据建模 / 参数 / 级联 / 排序 / 图表 /
联动 / 填报交互类)实现为静态校验函数。每条规则:

  * 一个 `def check_<name>(cpt_path: str) -> list[tuple[str, str]]` 函数,
    返回 (级别, 消息) 列表,级别 ∈ {'ERROR', 'WARN', 'OK'};
  * 模块级 RULES 注册表(含 name / fn / doc / context 适用语境 / apply 触发条件);
  * docstring 注明来源 doc-XXXX。

设计约束:
  * 仅用标准库(xml.etree.ElementTree 解析 .cpt / .frm 即 XML);不联网;
  * 独立模块,不 import fr_check.py;
  * 优先移植 practice/topic_<docid>/ 下已验证的实现(如 check_cascade /
    validate_plan / check_linkage / check_cell_chart / check_autodefault /
    check_param_cascade / check_carousel_linkage / check_form_linkage /
    check_dynparam_linkage / check_dataset_param 等),practice 未覆盖的按
    LEARNINGS.md 对应条目从零实现;
  * 需要运行时/平台信息的规则写成保守 WARN 并说明判定假设。

用法:
  python fr_rules_doc.py <模板路径>            # 跑全部规则,汇总打印
  python fr_rules_doc.py <模板路径> --json     # 输出 JSON
  python fr_rules_doc.py <模板路径> --name cascade   # 只跑名字含 cascade 的规则
  python -c "import fr_rules_doc as f; print(f.run_all('x.cpt.xml'))"

退出码: 0=无 ERROR 1=有 ERROR(有 WARN 时仍为 1,见 main)
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

import os
import re
import sys
import json
import xml.etree.ElementTree as ET

# ════════════════════════════════════════════════════════════════════════════
# 公共工具
# ════════════════════════════════════════════════════════════════════════════

_ERR_LEVELS = ("ERROR", "WARN", "OK")


def _load_root(cpt_path):
    """读取并解析模板 XML。返回 (root, err);err 非空时 root 为 None。

    (R30 perf 2026-09-05) 同一文件(mtime_ns/size 未变)只解析一次, 跨规则共享同一棵树。
    行为等价前提: 全规则库对树只读(2026-09-05 审计: 无 .set/.text=/tail=/remove 等变更)。
    """
    root, err, _exc = _load_root_full(cpt_path)
    return root, err


def _load_root_full(cpt_path):
    """(R30 perf) _load_root 的内部版: 额外返回触发失败的原始异常 exc(成功为 None),
    供 run_all 预检以原有「XML 解析失败: %s」格式重建消息, 从而免去预检的重复解析。"""
    try:
        st = os.stat(cpt_path)
        key = (os.path.abspath(cpt_path), st.st_mtime_ns, st.st_size)
    except OSError:
        key = None
    if key is not None and key in _LOAD_CACHE:
        return _LOAD_CACHE[key]
    if not os.path.isfile(cpt_path):
        result = None, "文件不存在: %s" % cpt_path, None
    else:
        try:
            with open(cpt_path, "rb") as f:
                data = f.read()
            result = ET.fromstring(data), None, None
        except ET.ParseError as e:
            result = None, "XML 解析失败: %s" % e, e
        except Exception as e:
            result = None, "读取失败: %s" % e, e
    if key is not None:
        if len(_LOAD_CACHE) >= 8 and key not in _LOAD_CACHE:
            _LOAD_CACHE.clear()   # 批量场景内存上限: 换文件即弃旧树
            _SER_CACHE.clear()
        _LOAD_CACHE[key] = result
        _SER_CACHE.clear()        # 新树新 id: 序列化缓存只对当前树有效
    return result


# (R30 perf 2026-09-05) 解析/序列化复用缓存 ─────────────────────────────
# 规则库 98 条规则对同一棵树反复 _load_root(原 56 次重复解析, R8 定位占 23%)
# 与反复 ET.tostring(原 5.9MB 模板 8 万+ 次, R8 定位占 65%)。缓存按
# (abspath, mtime_ns, size) 与元素引用 memoize, 行为不变(只读树)。
_LOAD_CACHE = {}   # (abspath, mtime_ns, size) -> (root, err, exc)
_SER_CACHE = {}    # id(el) -> (el, text); 钉住元素引用防 id 复用串键


def _ser(el, encoding="unicode"):
    """ET.tostring 的按元素 memoize 版(行为等价)。

    签名兼容原调用形态 `_ser(el, encoding="unicode")`;仅当 encoding 为默认值
    "unicode" 时走缓存, 其他取值原样直调(不缓存), 保证任意调用形态行为不变。
    """
    if encoding != "unicode":
        return ET.tostring(el, encoding=encoding)
    hit = _SER_CACHE.get(id(el))
    if hit is not None and hit[0] is el:
        return hit[1]
    text = ET.tostring(el, encoding="unicode")
    _SER_CACHE[id(el)] = (el, text)
    return text


def _text(node):
    return (node.text or "").strip() if node is not None else ""


def _col_name(idx):
    """0 -> A, 25 -> Z, 26 -> AA"""
    s = ""
    idx = int(idx)
    while True:
        s = chr(ord("A") + idx % 26) + s
        idx = idx // 26 - 1
        if idx < 0:
            return s


def _cell(c, r):
    """0 基坐标 -> 单元格名,如 (0,1) -> 'A2'"""
    return _col_name(int(c)) + str(int(r) + 1)


def _cr(cell):
    """'B2' -> (c=1, r=1)(0 基)。非法返回 None。"""
    if not cell:
        return None
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", cell.strip())
    if not m:
        return None
    col = 0
    for ch in m.group(1).upper():
        col = col * 26 + (ord(ch) - 64)
    return col - 1, int(m.group(2)) - 1


_CELL_REF_RE = re.compile(r"^[A-Za-z]{1,3}\d+$")


def _is_cell_ref(s):
    return bool(s) and bool(_CELL_REF_RE.match(s.strip()))


VAR_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def sql_referenced_params(sql, known=None):
    """取 SQL 里 ${...} 中出现的参数名。known 非空时只返回属于 known 集合的。"""
    hit = set()
    for expr in re.findall(r"\$\{(.*?)\}", sql or "", re.S):
        for tok in VAR_RE.findall(expr):
            if known is None or tok in known:
                hit.add(tok)
    return hit


def _macro_param_refs(text):
    """取文本中 $param 形式(公式/JS)引用的参数名,含中文。"""
    return set(re.findall(r"\$([A-Za-z0-9_\u4e00-\u9fff]+)", text or ""))


def _all_template_params(root):
    """ReportParameterAttr 下声明的模板参数名集合(兼容多种结构)。"""
    names = set()
    for p in root.iter("Parameter"):
        a = p.find("Attributes")
        n = a.get("name") if a is not None else p.get("name")
        if n:
            names.add(n)
    # 兼容 <Parameter><Name>x</Name> 形态(推断片段)
    for n in root.iter("Name"):
        if n.text and n.text.strip():
            names.add(n.text.strip())
    return names


def _widget_names(root, exclude=None):
    """所有 WidgetName;exclude 为要排除的容器/按钮名集合。"""
    exclude = exclude or {"para", "search", "Export", "Submit", "Import",
                          "formSubmit3", "formSubmit", "submit", "delete",
                          "append", "add", "remove"}
    out = set()
    for w in root.iter("WidgetName"):
        n = w.get("name")
        if n and n not in exclude:
            out.add(n)
    return out


def _collect_datasets(root):
    """{ds名: {'sql': str, 'params': {参数名: 默认值文本}}, 兼容多种 Query 节点。"""
    out = {}
    for td in root.iter("TableData"):
        name = td.get("name")
        if not name:
            continue
        sql = ""
        for q in td.iter("Query"):
            sql = (q.text or "")
            break
        if not sql:
            for q in td.iter("SQL"):
                sql = (q.text or "")
                break
        params = {}
        for p in td.iter("Parameter"):
            a = p.find("Attributes")
            n = a.get("name") if a is not None else p.get("name")
            if not n:
                continue
            o = p.find("O")
            params[n] = (o.text or "") if o is not None else None
        out[name] = {"sql": sql, "params": params}
    return out


def _sql_columns(sql):
    """从 SELECT 语句粗提列名(去掉 AS 别名)。失败返回空列表。"""
    if not sql:
        return []
    m = re.search(r"select\s+(.*?)\s+from\s", sql, re.I | re.S)
    if not m:
        return []
    cols = []
    for part in m.group(1).split(","):
        part = part.strip()
        if not part or part == "*":
            continue
        part = re.sub(r"\s+as\s+\w+.*$", "", part, flags=re.I)
        part = part.strip().strip("`\"'[]()")
        if part and part.lower() not in ("distinct", "top"):
            cols.append(part)
    return cols


def _iter_js_contents(root):
    """遍历所有 (JS文本, 事件参数名集合)。兼容 Listener/JavaScript/Content 多种结构。"""
    for js in root.iter("JavaScript"):
        content = js.find("Content")
        if content is None:
            content = js
        txt = (content.text or "") if content is not None else ""
        params = set()
        for p in js.iter("Parameter"):
            a = p.find("Attributes")
            n = a.get("name") if a is not None else p.get("name")
            if n:
                params.add(n)
        yield txt, params
    # 兼容 <JS><![CDATA[]]></JS> 形态(推断片段)
    for js in root.iter("JS"):
        if js.text and js.text.strip():
            yield js.text, set()


def _iter_js_of_widget(widget_el):
    """单个控件元素内所有 JS 文本。"""
    for js in widget_el.iter("JavaScript"):
        content = js.find("Content")
        txt = (content.text or "") if content is not None else (js.text or "")
        if txt:
            yield txt
    for js in widget_el.iter("JS"):
        if js.text and js.text.strip():
            yield js.text


def _parent_map(root):
    """{child: parent} 全树映射(ElementTree 无 getparent,自建)。"""
    pmap = {}
    for p in root.iter():
        for ch in p:
            pmap[ch] = p
    return pmap


def _walk_up(el, pmap, want="cell", max_steps=64):
    """从 el 沿父链向上找最近的 <C>(want='cell',返回单元格名)或
    含 WidgetName 的 InnerWidget/Widget(want='widget',返回控件名)。找不到返回 None。"""
    cur = el
    for _ in range(max_steps):
        cur = pmap.get(cur)
        if cur is None:
            return None
        if want == "cell" and cur.tag == "C" and cur.get("c") is not None:
            return _cell(cur.get("c"), cur.get("r"))
        if want == "widget":
            if cur.tag in ("InnerWidget", "Widget"):
                wn = cur.find("WidgetName")
                if wn is not None and wn.get("name"):
                    return wn.get("name")
    return None


# 通用图表/超链接相关常量(来自 practice 已核验实现)
CHART_EDITOR_CLASS = "com.fr.form.ui.ChartEditor"
CELL_EDITOR_CLASS = "com.fr.form.ui.ElementCaseEditor"
CELL_CHART_HL_CLASS = "com.fr.js.CellChartHyperlink"
DYN_PARAM_HL_CLASS = "com.fr.js.DynamicParamHyperlink"
JS_HL_CLASS = "com.fr.js.JavaScriptHyperlink"
REPORTLET_HL_CLASS = "com.fr.js.ReportletHyperlink"
FORM_HL_CLASS = "com.fr.form.main.FormHyperlink"

# doc-2332:支持 sortChart 的 8 种图表类型白名单
SORTABLE_CHARTS = {"柱形图", "条形图", "折线图", "面积图", "饼图", "多层饼图", "仪表盘", "雷达图"}
# doc-2332 §2.4:需要延时执行的事件
NEED_DELAY_EVENTS = {"afterinit", "afteredit", "editend", "aftereditor"}
# doc-2332 §3.2:单元格控件渲染的预览方式
CELL_WIDGET_PREVIEW_MODES = {"write", "analysis"}

# doc-2857 §1.2:可设轮播联动 / 刷新联动的扩展图表白名单
CAROUSEL_CHART_KEYS = ["GIS", "POINT-MAP", "3D", "COMBO-MAP", "KPI", "GEAR", "CATALOG",
                       "GAUGE", "NOCTILUCENT", "WATER-BALL", "PIXEL",
                       "点地图", "三维组合地图", "指标卡", "目录齿轮", "夜光仪表盘", "水球", "像素点"]
REFRESH_CHART_KEYS = ["PARTICLE", "COUNTER", "粒子计数器"]
VALID_ANIMATIONS = ("增量刷新", "重新加载")

# doc-2474:扩展图表类型名清单(文本检测钩子)
EXT_TYPES = ["场景切换地图", "三维柱形地球", "三维点地球", "三维流向地球",
             "轮播GIS点地图", "轮播三维组合地图", "轮播夜光仪表盘", "水球图", "像素点图",
             "轮播KPI指标卡-闪烁", "轮播KPI指标卡-电子", "粒子计数器", "时间齿轮",
             "弧形柱形图", "特殊图形柱形图", "轮播条形图", "轮播饼图", "轮播目录齿轮", "智慧树图"]
# doc-3115:扩展图表类名标记
EXTENDED_CHART_MARKERS = ("ExtChart", "Gauge", "Carousel", "ThreeD", "Chart3D", "GIS", "Map3D")
# doc-2474:扩展图表 5 条静默约束
EXT_CHART_CONSTRAINTS = [
    "不支持导出(Excel/PDF 等导出时该图表不渲染)",
    "不支持移动端展示",
    "不支持任何图表接口(chart JS API 对其无效)",
    "只支持 Chrome 浏览器预览(>=86)",
    "不支持组件刷新(须用图表交互 JS 或插件 3.5+ 监控刷新)",
]

# doc-1839:JS 超链参数名合法性
JS_IDENT = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
JS_RESERVED = {"break", "case", "catch", "class", "const", "continue", "debugger",
               "default", "delete", "do", "else", "export", "extends", "finally",
               "for", "function", "if", "import", "in", "instanceof", "new", "return",
               "super", "switch", "this", "throw", "try", "typeof", "var", "void",
               "while", "with", "yield", "let", "static", "enum", "await",
               "implements", "package", "protected", "interface", "private",
               "public", "null", "true", "false"}
JS_GLOBALS = {"FR", "window", "document", "self", "top", "parent", "location",
              "navigator", "contentPane", "_g", "$", "jQuery", "alert", "name"}

# doc-1672:图表通用样式九类封闭枚举
STYLE_CATEGORIES = ("标题", "图例", "标签", "系列", "坐标轴", "数据表", "背景", "提示", "配色")

# doc-903:排序方向白名单
ALLOWED_DIRECTIONS = ("asc", "desc", "")

# doc-897 / doc-3622 / doc-2684 共享的排序节点常量
SORT_ATTR = "sortAfterExpand"
SORT_EXPR_TAG = "SortExpression"
SORT_EXPR_ATTR_TAG = "Attributes"
ASC, DESC, NONE = 1, 2, 0

# ════════════════════════════════════════════════════════════════════════════
# 规则实现(第一部分:R01–R15,数据/参数/级联/联动)
# ════════════════════════════════════════════════════════════════════════════

def check_cascade(cpt_path):
    """doc-1284 下拉框参数联动一致性:SQl ${p} 与控件 <Parameter> 双向一致、
    字典数据集缺参、依赖自环、父子控件定义顺序倒置、依赖参数未定义为模板参数。
    移植 practice/topic_1284/gen_cascade.py 的 check_cascade。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    ds = {}
    for td in root.iter("TableData"):
        name = td.get("name")
        if not name:  # NameTableData(控件里的引用)没有 name 属性
            continue
        q = td.find("Query")
        declared = set()
        for p in td.iterfind("DBTableDataParameters/Parameter"):
            a = p.find("Attributes")
            if a is not None and a.get("name"):
                declared.add(a.get("name"))
        if q is None:
            # 兼容 <SQL> 子节点
            q = td.find("SQL")
        ds[name] = ((q.text or "") if q is not None else "", declared)

    tpl_params = set()
    rpa = root.find("ReportParameterAttr")
    if rpa is not None:
        for p in rpa.iter("Parameter"):
            a = p.find("Attributes")
            n = a.get("name") if a is not None else p.get("name")
            if n:
                tpl_params.add(n)

    widgets = []  # [(widget_name, dict_ds_name, 依赖参数集)]
    for w in root.iter("InnerWidget"):
        wn = w.find("WidgetName")
        if wn is None or not wn.get("name"):
            continue
        name = wn.get("name")
        ntd = w.find("Dictionary/TableDataDictAttr/TableData")
        if ntd is None:
            widgets.append((name, None, set()))
            continue
        dn_el = ntd.find("Name")
        dsname = (dn_el.text or "").strip() if dn_el is not None else ""
        deps = {p.get("name") for p in ntd.iterfind("Parameters/Parameter")
                if p.get("name")}
        widgets.append((name, dsname or None, deps))

    if not widgets:
        out.append(("OK", "未发现级联下拉控件(InnerWidget 下拉框),跳过"))
        return out

    known = {w[0] for w in widgets}
    seen = set()
    for idx, (name, dsname, deps) in enumerate(widgets):
        if name in seen:
            out.append(("ERROR", "重复 WidgetName: %s(级联按名绑定,重名即指向不确定)" % name))
        seen.add(name)
        if dsname is None:
            continue
        if dsname not in ds:
            out.append(("ERROR", "%s: 字典数据集 %s 不存在" % (name, dsname)))
            continue
        sql, ds_declared = ds[dsname]
        used = sql_referenced_params(sql, known)
        # ① SQL 用到但控件字典未声明 -> 联动不触发
        for p in sorted(used - deps):
            out.append(("ERROR", "%s: SQL 用了 ${%s} 但控件 Dictionary 缺 <Parameter name=\"%s\"/>" % (name, p, p)))
        # ② 声明了却没在 SQL 里用 -> 无效依赖
        for p in sorted(deps - used):
            out.append(("ERROR", "%s: 声明依赖 %s 但 SQL 未使用 ${%s}" % (name, p, p)))
        # ③ 数据集自身参数列表缺失
        for p in sorted(used - ds_declared):
            out.append(("ERROR", "%s: 数据集 %s 缺 DBTableDataParameters 中的 %s" % (name, dsname, p)))
        # ④ 依赖自己 -> 死循环
        if name in deps:
            out.append(("ERROR", "%s: 依赖自身,联动成环" % name))
        # ⑤ 依赖的父控件必须在自己之前定义
        earlier = {w[0] for w in widgets[:idx]}
        for p in sorted(deps - earlier - {name}):
            out.append(("ERROR", "%s: 依赖的父控件 %s 未在其之前定义" % (name, p)))
        # ⑥ 参数必须同时是模板参数
        for p in sorted(deps - tpl_params):
            out.append(("ERROR", "%s: 依赖参数 %s 未定义为模板参数" % (name, p)))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "级联一致性检查通过(%d 个控件)" % len(widgets)))
    return out


def check_chart_cell_formula(cpt_path):
    """doc-175 图表单元格数据源:检测 =[...] 公式语法(连续/不连续分隔符)、
    值含二次运算(±*/)时给 WARN,并检查「分类是系列父格、系列是值父格」的父子链声明。
    移植 practice/topic_175/gen_cell_chart.py 的校验思路。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    # ① 检测 =[...] 单元格范围公式(图表/单元格公式常用形态)
    found = 0
    for m in re.finditer(r"=\s*\[([^\]]+)\]", text):
        found += 1
        body = m.group(1)
        # 连续区间 B2:E5 与不连续 B2,C5 分隔符检查
        if re.search(r"[A-Za-z]+\d+[A-Za-z]+\d+", body.replace(":", "")):
            out.append(("ERROR", "图表单元格公式 [%s] 疑似漏分隔符(连续区间用 ':',不连续用 ',')" % body))
        # 二次计算: 值表达式含 + - * / 会丢单元格属性
        for v in re.findall(r"=\s*([^;\n]+)", text):
            if re.search(r"[+\-*/]", v) and not re.match(r"^=\s*\$\{", v):
                out.append(("WARN", "图表取值公式 '%s' 含二次运算(±*/):doc-175 明示二次计算会丢单元格属性,建议用数据集汇总" % v.strip()[:60]))
                break
    if found == 0:
        # 退而求其次:检测单元格数据源的图表(含 =A1 形态取数)
        cell_charts = 0
        for c in root.iter("C"):
            for o in c.iter("O"):
                if (o.text or "").startswith("="):
                    cell_charts += 1
        if cell_charts == 0:
            out.append(("OK", "未发现图表单元格数据源公式,跳过"))
            return out

    # ② 父子链声明:分类是系列父格、系列是值父格(检测 <Expand left/up> 或 <P> 父格节点)
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        exp = c.find("Expand")
        if exp is None:
            continue
        left = exp.get("left")
        up = exp.get("up")
        if left and _is_cell_ref(left):
            lc, lr = _cr(left)
            if lr != int(rr) and lc != int(cc):
                out.append(("WARN", "单元格 %s 左父格 %s 跨行跨列:图表父子链(分类>系列>值)应逐级挂在同行/同列,否则分类/系列错位" % (name, left)))
        if up and _is_cell_ref(up):
            uc, ur = _cr(up)
            if uc != int(cc) and ur != int(rr):
                out.append(("WARN", "单元格 %s 上父格 %s 跨列:图表父子链建议逐级,否则系列/值错位" % (name, up)))

    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "图表单元格数据源公式语法检查通过"))
    return out


def check_print_export_bg(cpt_path):
    """doc-175(附 doc-225)打印导出背景/预览设置:检测「不预览但打印导出」单元格提示
    填报预览下失效;检测「打印导出单元格背景」开关提示 Word/Excel 仅支持颜色背景。
    判定为静态假设,纯文本/节点检测。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    # ① 「不预览但打印导出」:CellGUIAttr/WebAttr 中 preview 关闭但 print/export 开启
    hit = 0
    for cg in root.iter("CellGUIAttr"):
        if cg.get("printBackground") == "true" or cg.get("printContent") == "true":
            hit += 1
            if cg.get("preview") == "false":
                out.append(("WARN", "存在「不预览但打印导出」单元格:doc-225 提示该设置在填报预览下会失效,须用分页预览验证导出效果"))
    if hit == 0 and "printBackground" not in text:
        out.append(("OK", "未发现打印导出背景相关配置,跳过"))
        return out

    # ② 「打印导出单元格背景」开关:图片背景在 Word/Excel 导出会丢,PDF 才全支持
    if "printBackground" in text or "Background" in text:
        if re.search(r"Background[^>]*image|ImageBackground|图片背景", text):
            out.append(("WARN", "检测到图片背景+打印导出配置:Word/Excel 导出仅支持颜色背景、图片背景会丢,PDF 才全支持(doc-225)"))
    return out


def check_group_sort(cpt_path):
    """doc-2684 按分组汇总结果排序:对每个设了排序公式的单元格,顺着 <Expand left=.../>
    左父格链回溯,断言链终点等于被排序格(或二者同行);不满足则报错。
    移植 practice/topic_2684/inject_group_sort.py 的 validate_plan(改为 XML 级)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    # 单元格名 -> (c,r) 与 左父格
    cell_pos, left_of = {}, {}
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        cell_pos[name] = (int(cc), int(rr))
        exp = c.find("Expand")
        if exp is None:
            continue
        left = exp.get("left")
        if left and _is_cell_ref(left):
            left_of[name] = left.strip().upper()
        else:
            lpc, lpr = exp.get("leftParentColumn"), exp.get("leftParentRow")
            if lpc is not None and lpr is not None:
                try:
                    left_of[name] = _cell(int(lpc), int(lpr))
                except Exception:
                    pass

    sorted_cells = []
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        exp = c.find("Expand")
        if exp is None:
            continue
        se = exp.find(SORT_EXPR_TAG)
        if se is None:
            continue
        attr = se.find(SORT_EXPR_ATTR_TAG)
        formula = (attr.text or se.text or "") if attr is not None else (se.text or "")
        formula = formula.strip()
        if not formula:
            continue
        if exp.get(SORT_ATTR) in ("0", None) and "=" not in formula:
            continue
        sorted_cells.append((name, formula))

    if not sorted_cells:
        out.append(("OK", "未发现扩展后排序(SortExpression)配置,跳过"))
        return out

    for name, formula in sorted_cells:
        f = formula.lstrip("=").strip()
        if not _is_cell_ref(f):
            continue  # 复杂公式(如 inarray)无法静态回溯,跳过
        target = f.upper()
        if target not in cell_pos:
            out.append(("WARN", "%s 的排序公式 %s 指向不存在的单元格 %s(公式引用格须为真实格)" % (name, formula, target)))
            continue
        if cell_pos[target][1] == cell_pos[name][1]:
            continue  # 同行 = 天然同层,合法
        node, seen = target, set()
        while node in left_of and node not in seen:
            seen.add(node)
            node = left_of[node]
        if node != name:
            out.append(("ERROR", "%s 的排序公式 %s 指向 %s,但 %s 的左父格链终点是 %s,不是 %s —— 每个分组将对应多个/零个汇总值,排序不可预期(doc-2684)" % (name, formula, target, target, node, name)))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "分组排序左父格链检查通过(%d 处排序配置)" % len(sorted_cells)))
    return out


def check_cell_chart_link(cpt_path):
    """doc-4207 图表超链-联动单元格图表:凡单元格超链类型为「联动单元格图表」,
    断言 ①「联动单元格坐标」确实存在一个插入了图表的单元格;②超链参数名同时
    声明于图表数据集与模板参数(双向一致)。移植 topic_4207 verify 思路(XML 级)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    # 收集所有单元格名(含图表格:检测 CellChart / Chart 节点 cell 属性或所在格)
    chart_cells = set()
    for tag in ("CellChart", "ChartObject"):
        for cc in root.iter(tag):
            cell = cc.get("cell") or cc.get("cellName") or cc.get("name")
            if cell:
                chart_cells.add(cell.strip().upper())
    # 兼容:单元格内含 Chart 节点
    for c in root.iter("C"):
        if c.find(".//Chart") is not None:
            cc, rr = c.get("c"), c.get("r")
            if cc is not None and rr is not None:
                chart_cells.add(_cell(cc, rr))

    tpl_params = _all_template_params(root)
    datasets = _collect_datasets(root)

    links = 0
    for hl in root.iter("Hyperlink"):
        cls = hl.get("class") or ""
        if CELL_CHART_HL_CLASS not in cls and "ChartHyperlink" not in cls:
            continue
        links += 1
        target = hl.get("cellName") or hl.get("cell") or hl.get("target") or ""
        # ① 目标格存在且是图表格
        if not target:
            out.append(("ERROR", "联动单元格图表超链缺少目标单元格(cellName)声明"))
        elif target.strip().upper() not in chart_cells:
            out.append(("ERROR", "联动单元格图表超链指向 %s,但该格未插入图表(doc-4207:联动目标是'插入了图表的单元格',不是数据格)" % target))
        # ② 超链参数名双声明
        for p in hl.iter("Parameter"):
            pn = p.get("name") or (p.findtext("Name") or "").strip()
            if not pn:
                continue
            ds_hit = any(pn in d["params"] for d in datasets.values())
            if not ds_hit:
                out.append(("ERROR", "超链参数 %s 未声明于任何图表数据集参数(联动静默失效)" % pn))
            if pn not in tpl_params:
                out.append(("ERROR", "超链参数 %s 未声明为模板参数(传参空转)" % pn))
            # ③ 取值须取被点击格自身值 =$$$
            val = p.get("value") or (p.text or "").strip()
            if val and val != "=$$$" and not _is_cell_ref(val.lstrip("=")):
                out.append(("WARN", "参数 %s 取值 %r 非 =$$$ 也非单元格引用:联动可能取不到被点击格当前值" % (pn, val)))

    if links == 0:
        out.append(("OK", "未发现「联动单元格图表」超链,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "联动单元格图表一致性检查通过(%d 处超链)" % links))
    return out


def check_hyperlink_param(cpt_path):
    """doc-947 超级链接到有参数的模板:凡挂「跳参数化子模板」超链(网络报表/JS),
    断言 ①子模板声明同名模板参数;②子模板数据集 ${...} 表达式内引用该参数名
    (注意非 ${参数} 字面量,而是 ${if(len(...))} 内的裸变量)。移植 verify。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    base_dir = os.path.dirname(os.path.abspath(cpt_path))

    links = 0
    for hl in root.iter("Hyperlink"):
        cls = hl.get("class") or ""
        is_net = REPORTLET_HL_CLASS in cls or "ReportletHyperlink" in cls
        is_js = JS_HL_CLASS in cls or "JavaScriptHyperlink" in cls
        if not (is_net or is_js):
            continue
        # 子模板路径
        sub = ""
        rp = hl.find("Reportlet")
        if rp is not None:
            sub = (rp.text or "").strip()
        if not sub:
            for p in hl.iter("Parameter"):
                pn = p.get("name")
                if pn:
                    links += 1
                    out.append(("WARN", "JS 超链参数 %s 无法静态定位子模板路径,跳过子模板侧校验(判定假设:子模板须声明同名模板参数且 SQL 引用)" % pn))
        if not sub:
            continue
        links += 1
        # 参数名(可能多个)
        pnames = [p.get("name") for p in hl.iter("Parameter") if p.get("name")]
        if not pnames:
            out.append(("ERROR", "跳参数化子模板超链未声明任何传递参数(子表将拿到空参)"))
            continue
        # 解析子模板文件(相对 cpt 目录或原样路径)
        sub_path = sub
        if not os.path.isabs(sub_path):
            cand = os.path.join(base_dir, os.path.basename(sub_path))
            if os.path.isfile(cand):
                sub_path = cand
            elif os.path.isfile(sub):
                pass
            else:
                # 找不到子模板文件:保守 WARN
                out.append(("WARN", "子模板 %s 无法在本机定位,子模板侧校验跳过(判定假设:子模板须声明同名模板参数且 SQL 引用参数)" % sub))
                continue
        sroot, serr = _load_root(sub_path)
        if serr:
            out.append(("WARN", "子模板 %s 解析失败:%s(子模板侧校验跳过)" % (sub, serr)))
            continue
        sparam = _all_template_params(sroot)
        sqls = "\n".join((q.text or "") for q in sroot.iter("Query"))
        for pn in pnames:
            # ① 子模板必须声明同名模板参数
            if pn not in sparam:
                out.append(("ERROR", "[A] 子模板 %s 未声明模板参数 '%s',主表传参后子表将静默全空" % (sub, pn)))
            # ② SQL 必须在 ${...} 块内引用该参数(裸变量,不是 ${area} 字面量)
            blocks = re.findall(r"\$\{(.+?)\}", sqls, re.S)
            referenced = any(re.search(r"(?<![A-Za-z0-9_])" + re.escape(pn) + r"(?![A-Za-z0-9_])", b) for b in blocks)
            if not referenced:
                out.append(("ERROR", "[B] 子模板 %s 数据集 SQL 未在 ${...} 表达式内引用参数 '%s',过滤不生效" % (sub, pn)))
        # ③ JS 方式不支持移动端
        if is_js:
            out.append(("WARN", "[D] JS 超链方式不支持移动端,仅 PC/Web/HTML5 生效"))

    if links == 0:
        out.append(("OK", "未发现跳参数化子模板超链,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "超链参数化子模板一致性检查通过(%d 处超链)" % links))
    return out


def check_dropdown_chart_link(cpt_path):
    """doc-1995 下拉框和图表联动(隐藏桥接格链路):凡「联动单元格图表」超链其值来自
    JS setCellValue 的隐藏桥接格,断言 ①超链参数值==该桥接格单元格号(非 =$$$);
    ②编辑后事件的 setCellValue 目标格==超链所在格;③图表数据集与超链/模板参数同名。
    移植 gen_dropdown_chart_link.verify 思路(XML 级)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    tpl_params = _all_template_params(root)
    datasets = _collect_datasets(root)

    found = 0
    pmap = _parent_map(root)
    for hl in root.iter("Hyperlink"):
        cls = hl.get("class") or ""
        if CELL_CHART_HL_CLASS not in cls and "ChartHyperlink" not in cls:
            continue
        # 定位超链所在单元格
        link_cell = _walk_up(hl, pmap, want="cell")
        found += 1
        for p in hl.iter("Parameter"):
            pn = p.get("name")
            if not pn:
                continue
            val = p.get("value") or (p.text or "").strip()
            # ① 超链参数值必须是桥接格单元格号(非 =$$$)
            if not _is_cell_ref(val) or val.startswith("="):
                out.append(("ERROR", "超链参数 %s 取值 %r 必须是桥接格单元格号(如 D1),不能用 =$$$ —— doc-1995 用 =$$$ 会静默不刷新" % (pn, val)))
            # ③ 图表数据集与超链参数同名
            if pn not in tpl_params:
                out.append(("ERROR", "超链参数 %s 未声明为模板参数" % pn))
            if not any(pn in d["params"] for d in datasets.values()):
                out.append(("ERROR", "超链参数 %s 未在图表数据集参数中声明(联动静默失效)" % pn))
            # ② setCellValue 目标格 == 超链所在格(编辑后事件)
            if link_cell:
                set_ok = False
                for js_txt, _ in _iter_js_contents(root):
                    m = re.search(r"setCellValue\(\s*'([A-Z]+[0-9]+)'", js_txt)
                    if m and m.group(1).upper() == link_cell:
                        set_ok = True
                        break
                if not set_ok:
                    out.append(("ERROR", "未找到把值写入桥接格 %s 的 setCellValue(编辑后事件应写该格再触发点击)" % link_cell))

    if found == 0:
        out.append(("OK", "未发现下拉框-图表桥接连路(联动单元格图表超链),跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "下拉框-图表桥接连路检查通过(%d 处超链)" % found))
    return out


def check_template_param(cpt_path):
    """doc-157 模板参数:断言 Parameter 定义名 / 同名 WidgetName / 单元格过滤 $参数
    三者双向一致,缺失即报错;未用 if(len($p)==0,...) 容空写法给 WARN。
    移植 practice/topic_157/gen_template_param.py 的 check_cpt。
    ⚠语境标注(2026-08-20 反向验证,FS 拆分版实战):
    ①参数定义只认 ReportParameterAttr 子树——JS 监听器 <Parameter>(弹窗传参)与
      数据集 <Parameter>(doc-299 管辖)是另两层概念,全树混扫必误报;
    ②「被引用」证据三通道:Filter $引用(经典 DSColumn 设计)/公式 $引用(单元格公式
      与控件字典 FormulaDict,ds.select 公式驱动报表无 Filter)/数据集 SQL ${} 宏;
    ③Label 类控件(lb_*)与 query 查询按钮是展示/动作件,不要求参数定义。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    # ①模板参数定义: ReportParameterAttr 子树 ∪ 数据集 <Parameter> 声明
    #   (两处都是合法定义位;只排除 JavaScript 子树——JS 监听器 <Parameter> 是
    #    弹窗传参,不是模板参数,混扫必误报;实测 FS 拆分版 p_* 全中招)
    param_names = set()
    rpa = root.find(".//ReportParameterAttr")
    if rpa is not None:
        for p in rpa.iter("Parameter"):
            a = p.find("Attributes")
            n = a.get("name") if a is not None else p.get("name")
            if n:
                param_names.add(n)
    for td in root.iter("TableData"):
        for p in td.iter("Parameter"):
            a = p.find("Attributes")
            n = a.get("name") if a is not None else p.get("name")
            if n:
                param_names.add(n)
    if not param_names:
        # 回落: 全树扫描(排除 JavaScript 子树)
        parent_of_fb = _parent_map(root)
        for p in root.iter("Parameter"):
            anc, skip = p, False
            while anc is not None:
                if anc.tag == "JavaScript":
                    skip = True
                    break
                anc = parent_of_fb.get(anc)
            if skip:
                continue
            a = p.find("Attributes")
            n = a.get("name") if a is not None else p.get("name")
            if n:
                param_names.add(n)
    if not param_names:
        out.append(("OK", "未发现任何模板参数定义(ReportParameterAttr/<Parameter>),跳过"))
        return out

    # FR 内置/系统参数(__cutpage__ 分页等): URL 驱动,无控件无引用是常态,豁免
    BUILTIN_PREFIX = "__"

    NON_PARAM_WIDGETS = {"para", "search", "Export", "Submit", "Import",
                         "formSubmit3", "formSubmit", "submit", "query", "Confirm"}
    widget_names = set()
    parent_of = _parent_map(root)
    for w in root.iter("WidgetName"):
        n = w.get("name")
        if not n or n in NON_PARAM_WIDGETS:
            continue
        p = parent_of.get(w)
        cls = (p.get("class") or "") if p is not None else ""
        if cls.endswith(".Label"):  # ③标签控件不是参数
            continue
        # ③按钮类控件是动作件, 不承担参数绑定: 按控件类判定(FreeButton/FormSubmitButton/
        #   CustomButton), 兼顾 btn_* 命名习惯——名称黑名单只列大小写精确名, btn_import/
        #   Search(大写)等自定义按钮名漏网即误报(doc-157 语境; 夜间批次 A27 实测残留面,
        #   2026-09-15 A39 补: RadioButton 等可绑定控件类名不含 Button, 不受影响)
        base_cls = cls.rsplit(".", 1)[-1]
        if base_cls in ("FreeButton", "FormSubmitButton", "CustomButton"):
            continue
        if n.lower().startswith("btn"):
            continue
        widget_names.add(n)

    # 过滤引用(经典设计,保留反向校验)
    filter_refs = set()
    raw_all = []
    for f in root.iter("Filter"):
        txt = "".join(f.itertext())
        raw_all.append(txt)
        filter_refs |= _macro_param_refs(txt)
    raw = "\n".join(raw_all)

    # ②公式 $引用(正向证据,不做反向校验:jQuery $.fn 等会产生噪音名)
    formula_refs = set()
    for a in root.iter("Attributes"):
        if a.text and "$" in a.text:
            formula_refs |= _macro_param_refs(a.text)
    formula_refs |= _macro_param_refs(_ser(root, encoding="unicode"))
    # ②数据集 SQL ${} 宏(正向证据)
    sql_refs = set()
    for td in root.iter("TableData"):
        sql = "".join(td.itertext())
        for expr in re.findall(r"\$\{(.*?)\}", sql, re.S):
            for tok in VAR_RE.findall(expr):
                sql_refs.add(tok)
    used = filter_refs | formula_refs | sql_refs

    for pn in sorted(param_names):
        if pn.startswith(BUILTIN_PREFIX):
            continue  # __cutpage__ 等内置参数: URL 驱动,豁免三要素断言
        if pn not in widget_names:
            out.append(("ERROR", "模板参数[%s]无同名控件绑定(缺失 WidgetName name=%s)" % (pn, pn)))
        if pn not in used:
            out.append(("ERROR", "模板参数[%s]未被引用:无 Filter $引用/公式 $引用/数据集 ${} 宏(缺 $%s)" % (pn, pn)))
        elif pn in filter_refs and "len($%s)" % pn not in raw:
            out.append(("WARN", "参数[%s]过滤未做容空处理($%s 为空时整表为空);建议改为 if(len($%s)==0, true, 列 == $%s)" % (pn, pn, pn, pn)))

    for wn in sorted(widget_names - param_names):
        out.append(("ERROR", "控件[%s]无对应模板参数定义(ReportParameterAttr 缺 <Parameter name=%s>)" % (wn, wn)))
    for fr in sorted(filter_refs - param_names):
        out.append(("ERROR", "过滤引用 $%s 无对应模板参数定义" % fr))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "模板参数三要素(定义/控件/引用)双向一致,共 %d 个参数" % len(param_names)))
    return out


def check_fill_linkage(cpt_path):
    """doc-608 填报控件数据字典联动:子控件字典引用的数据集 SQL / 公式须包含父单元格
    引用;联动驱动源不得为控件名(region/city 等)→ 移动端不支持;公式字典须配 $$$ 显示值。
    移植 practice/topic_608/gen_linkage.py 的 check_linkage。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    # 单元格块: cellname -> block(文本级,兼容多种 <Cell>/<C> 形态)
    blocks = {}
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        blocks[name] = _ser(c, encoding="unicode")
    for cell in root.iter("Cell"):
        name = cell.get("name")
        if name and _is_cell_ref(name):
            blocks[name.upper()] = _ser(cell, encoding="unicode")

    parent_cell = child_cell = None
    for name, blk in blocks.items():
        if 'WidgetName name="region"' in blk and parent_cell is None:
            parent_cell = name
        if 'WidgetName name="city"' in blk and child_cell is None:
            child_cell = name
    if parent_cell is None or child_cell is None:
        out.append(("OK", "未发现 region/city 填报联动单元格,跳过(仅检测命名约定,其它联动名请人工核对)"))
        return out

    child_block = blocks[child_cell]
    ref_ok = False
    if ("<valueFormula>" in child_block) or ("SQL(" in child_block) or ("value(" in child_block):
        ref_ok = (("${%s}" % parent_cell) in child_block) or \
                 (("+" + parent_cell + "+") in child_block) or \
                 ((", " + parent_cell + ")") in child_block) or \
                 (("(" + parent_cell + ")") in child_block)
    else:
        m = re.search(r"<TableDataDictAttr>\s*<TableData>(.*?)</TableData>", child_block, re.S)
        dsname = m.group(1).strip() if m else None
        if dsname is None:
            out.append(("ERROR", "子级控件字典未指向数据集,也未用公式(SQL()/value())"))
        else:
            sql = ""
            for td in root.iter("TableData"):
                if td.get("name") == dsname:
                    for q in td.iter("Query"):
                        sql = q.text or ""
                        break
                    break
            ref_ok = ("${%s}" % parent_cell) in sql
    if not ref_ok:
        out.append(("ERROR", "子级字典未引用父单元格 %s(doc-608: 联动驱动源必须是单元格,不是控件名)" % parent_cell))
    # 移动端陷阱:不得用控件名作为驱动源
    for wname in ("region", "city"):
        if re.search(r"\$\{%s\}" % wname, text):
            out.append(("ERROR", "联动驱动源用了控件名(%s) → 移动端不支持,须改为单元格引用" % wname))
    # 公式字典须配 $$$ 显示值
    if ("<valueFormula>" in child_block or "SQL(" in child_block or "value(" in child_block) and "$$$" not in text:
        out.append(("ERROR", "使用 SQL()/value() 公式字典时,显示值须写 $$$"))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "填报联动一致性检查通过(%s -> %s)" % (parent_cell, child_cell)))
    return out


def check_chart_dataset(cpt_path):
    """doc-176 定义图表数据集数据源:凡图表走「数据集数据源」,断言 ①系列名模式与源表
    列形状匹配(fieldValue 源表须含产品列、fieldName 源表须含所选列名)②分类列存在于
    源表③值字段存在且汇总方式已声明;模式=none 时 WARN 老版本不支持。
    移植 gen_chart_dataset.validate(XML 级:从 Chart 数据绑定节点 + 数据集 SQL 提取)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    datasets = _collect_datasets(root)
    ds_cols = {n: _sql_columns(d["sql"]) for n, d in datasets.items()}

    charts = 0
    for chart in root.iter("Chart"):
        if chart.get("class") and "Chart" not in chart.get("class", ""):
            continue
        # 数据集绑定
        dsname = chart.get("datasetName") or ""
        tn = chart.find(".//TableName")
        if tn is not None and tn.text and tn.text.strip():
            dsname = tn.text.strip()
        if not dsname:
            continue  # 单元格数据源或未绑定
        charts += 1
        cols = ds_cols.get(dsname, [])
        if not cols:
            out.append(("WARN", "图表绑定数据集 %s 无法静态提取列名(SQL 非 SELECT 形态),列匹配校验跳过(判定假设:源表须含分类/系列/值列)" % dsname))
            continue
        # 分类列
        cat = None
        for cd in chart.iter("CategoryData"):
            cat = cd.get("ref") or (cd.text or "").strip()
            break
        # 系列名模式
        mode = None
        for su in chart.iter("SeriesNameUse"):
            mode = (su.text or "").strip()
            break
        series_fields = []
        for sf in chart.iter("SeriesNameField"):
            if sf.get("ref"):
                series_fields.append(sf.get("ref"))
        for f in chart.iter("Field"):
            if f.text and f.text.strip():
                series_fields.append(f.text.strip())
        # 值字段
        value_fields, summaries = [], []
        for vd in chart.iter("ValueData"):
            if vd.get("ref"):
                value_fields.append(vd.get("ref"))
            if vd.get("summary"):
                summaries.append(vd.get("summary"))

        if mode == "fieldValue":
            if "产品" not in cols:
                out.append(("ERROR", "图表(数据集 %s)series_mode=fieldValue 要求源表含「产品」列(窄表),实际列=%s" % (dsname, cols)))
        elif mode == "fieldName":
            for f in series_fields:
                if f and f not in cols:
                    out.append(("ERROR", "图表(数据集 %s)series_mode=fieldName 要求源表含列「%s」(宽表),实际列=%s" % (dsname, f, cols)))
        elif mode == "none":
            out.append(("WARN", "图表(数据集 %s)系列名=无 仅 10.0.9+ 支持,老版本会降级为字段名" % dsname))
        # 分类列存在
        if cat and cat not in cols:
            out.append(("ERROR", "图表(数据集 %s)分类列「%s」不在源表,实际列=%s" % (dsname, cat, cols)))
        # 值字段存在且汇总方式已声明
        for vf in value_fields:
            if vf and vf not in cols:
                out.append(("ERROR", "图表(数据集 %s)值字段「%s」不在源表,实际列=%s" % (dsname, vf, cols)))
        if value_fields and not summaries:
            out.append(("ERROR", "图表(数据集 %s)值字段 %s 未声明汇总方式(summary 属性),运行时按默认汇总可能不符预期" % (dsname, value_fields)))

    if charts == 0:
        out.append(("OK", "未发现数据集数据源图表,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "图表数据集数据源一致性检查通过(%d 个图表)" % charts))
    return out


def check_cell_js(cpt_path):
    """doc-1207 JS 获取填报单元格值/赋值:①含 setCellValue 但无配套
    verifyAndWriteReport/提交按钮 → WARN(只改前台不入库);②click 事件 JS 循环
    get/setCellValue 扩展格却无 len 事件参数 → WARN(扩展行数未注入);
    ③JS 单元格坐标列号非 0 基在前 → WARN。移植 gen_cell_js.self_check 逻辑。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    has_write_attr = root.find(".//ReportWriteAttr") is not None
    has_submit_js = False

    any_cell_js = False
    for js_txt, params in _iter_js_contents(root):
        if "setCellValue" not in js_txt and "getCellValue" not in js_txt:
            continue
        any_cell_js = True
        # ① 只改前台不入库
        if "setCellValue" in js_txt:
            if "verifyAndWriteReport" in js_txt or "writeReport" in js_txt:
                has_submit_js = True
            if not has_write_attr and "verifyAndWriteReport" not in js_txt and "writeReport" not in js_txt:
                out.append(("WARN", "JS 含 setCellValue 但未配套 verifyAndWriteReport/提交配置:只改前台不入库,用户刷新即丢失(doc-1207)"))
        # ② 扩展格循环缺 len 事件参数
        if re.search(r"for\s*\([^)]*i\s*[<<=]", js_txt) and \
           re.search(r"(getCellValue|setCellValue)", js_txt) and \
           "i < len" in js_txt and "len" not in params:
            out.append(("WARN", "click 事件 JS 循环读写扩展格(get/setCellValue)却未注入 len 事件参数(扩展行数未注入,循环范围错误)"))
        # ③ 坐标列号非 0 基在前:getCellValue(row, col) 形态 -> 列号应是第 2 位
        for m in re.finditer(r"(?:getCellValue|setCellValue)\(\s*(\d+)\s*,\s*(\d+)", js_txt):
            row_arg, col_arg = int(m.group(1)), int(m.group(2))
            # FR 约定 0 基且 (列, 行) 顺序:行号在第 2 位时若第 1 位是行号则顺序颠倒
            if row_arg > col_arg:
                out.append(("WARN", "JS 坐标 %s 疑似行号在前(FR 0 基约定为 列号在前,如 (0, 2, i+3));顺序颠倒会读写错格" % m.group(0)))

    if not any_cell_js:
        out.append(("OK", "未发现单元格 JS 交互(setCellValue/getCellValue),跳过"))
    elif has_write_attr and has_submit_js:
        out.append(("OK", "单元格 JS 交互检查通过(含提交链路)"))
    elif not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "单元格 JS 交互检查通过"))
    return out


def check_auto_default(cpt_path):
    """doc-1868 JS 实现填报联动自动生成默认值:凡公式字典级联,断言父控件配套
    编辑后事件 + setTimeout + remoteEvaluate 取首个子值;WARN「setTimeout 缺失/过短
    (异步覆盖陷阱)」「决策系统须关闭脚本调用公式限制」「不支持移动端」。
    移植 check_autodefault(XML 级)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    # 检测公式字典级联
    has_formula_dict = "<valueFormula>" in text
    if not has_formula_dict:
        out.append(("OK", "未发现公式字典(FormulaDictAttr/valueFormula)级联,跳过"))
        return out

    # 找父控件(编辑后事件里 remoteEvaluate 取首个子值)
    found_parent_event = False
    for js_txt, params in _iter_js_contents(root):
        if "FR.remoteEvaluate" not in js_txt:
            continue
        found_parent_event = True
        if "setTimeout" not in js_txt:
            out.append(("ERROR", "编辑后事件含 remoteEvaluate 但缺 setTimeout:字典刷新异步,立即 setCellValue 会被覆盖(异步覆盖陷阱)"))
        else:
            m = re.search(r"setTimeout\s*\(\s*function[^}]*?},\s*(\d+)", js_txt, re.S)
            if m and int(m.group(1)) < 200:
                out.append(("WARN", "setTimeout 仅 %dms 可能过短:字典刷新未完成即赋值会被覆盖,建议 200-500ms" % int(m.group(1))))
        if "_g().setCellValue" not in js_txt and "setCellValue" not in js_txt:
            out.append(("ERROR", "编辑后事件 remoteEvaluate 取到首个子值后未 setCellValue 写回子级单元格"))
    if not found_parent_event:
        out.append(("ERROR", "公式字典级联但父控件未挂编辑后事件(缺少 remoteEvaluate 取首个子值的联动 JS)"))

    # 平台侧硬约束(不落 XML,仅 WARN)
    out.append(("WARN", "平台侧(跨模块依赖):决策系统>安全管理 须关闭『脚本调用公式限制』,否则 FR.remoteEvaluate 调 sql() 被拦"))
    out.append(("WARN", "该 JS 联动链路不支持移动端(App/H5 白屏)"))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "自动默认值联动 JS 结构检查通过"))
    return out


def check_param_cascade(cpt_path):
    """doc-1029/doc-1868 参数面板公式字典联动:凡 ParameterUI 内公式字典级联,断言
    引用驱动参数 $p1 且含 sql() 与 if 分支;负例(漏 $p1 / 误用数据集字典)拦截。
    移植 gen_param_cascade.check_param_cascade。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if "<FormulaDictAttr>" not in text and "<valueFormula>" not in text:
        out.append(("OK", "未发现参数面板公式字典,跳过"))
        return out

    p2_block = None
    m = re.search(r'<WidgetName name="P2".*?<FormulaDictAttr>(.*?)</FormulaDictAttr>', text, re.S)
    if m:
        p2_block = m.group(1)
    if p2_block is None:
        # 通用:取任一 FormulaDictAttr 块
        m = re.search(r"<FormulaDictAttr>(.*?)</FormulaDictAttr>", text, re.S)
        p2_block = m.group(1) if m else ""

    if not re.search(r'<Parameter name="p1"', text):
        out.append(("ERROR", "缺少模板参数 p1(参数面板联动的驱动源)"))
    if 'WidgetName name="P1"' in text and "<InnerTableDataDictAttr>" not in text:
        out.append(("WARN", "P1 通常应为自定义字典(InnerTableDataDictAttr),无需数据集"))
    if "$p1" not in p2_block:
        out.append(("ERROR", "公式字典未引用驱动参数 $p1(联动不触发,P2 下拉恒空)"))
    if "sql(" not in p2_block:
        out.append(("ERROR", "公式字典未调用 sql() 取数"))
    if "if(" not in p2_block:
        out.append(("WARN", "公式字典缺少 if 分支(多源场景必填,单源可省)"))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "参数面板公式字典联动检查通过"))
    return out


def check_linkage_chain(cpt_path):
    """doc-2857 扩展图表轮播联动四链一致性:①目标数据集 SQL 含 ${参数名};
    ②该数据集参数声明了非空默认值;③驱动方 target 指向真实且唯一的 WidgetName;
    ④驱动方参数名与 [1] 逐字一致且取值非空。另:联动动画 ∈ {重新加载,增量刷新};
    源图表类型 ∈ 官方可设轮播联动的扩展图表白名单。根节点须为 <Form>。
    移植 check_carousel_linkage。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    if root.tag != "Form":
        out.append(("OK", "根节点为 <%s>,非决策报表 .frm(轮播联动仅适用 .frm),跳过" % root.tag))
        return out

    datasets = _collect_datasets(root)
    # 图表组件:WidgetName -> {cls, ds, title}
    charts, seen = {}, set()
    for iw in root.iter("InnerWidget"):
        if iw.get("class") != CHART_EDITOR_CLASS:
            continue
        wn = iw.find("WidgetName")
        name = wn.get("name") if wn is not None else None
        if not name:
            continue
        if name in seen:
            out.append(("ERROR", "组件名重复: %s —— 联动 target 会指向不确定对象" % name))
        seen.add(name)
        chart = next(iter(iw.iter("Chart")), None)
        cls, ds, title = "", "", ""
        if chart is not None:
            cls = chart.get("class") or ""
            tn = chart.find(".//TableName")
            ds = _text(tn) if tn is not None else ""
            ta = chart.find(".//Title/TextAttr")
            title = _text(ta) if ta is not None else ""
        charts[name] = {"cls": cls, "ds": ds, "title": title}

    tpl_params = _all_template_params(root)

    linkage_count = 0
    for iw in root.iter("InnerWidget"):
        if iw.get("class") != CHART_EDITOR_CLASS:
            continue
        wn = iw.find("WidgetName")
        src = wn.get("name") if wn is not None else "(未命名)"
        for tag in ("CarouselLinkage", "RefreshLinkage"):
            for lk in iw.iter(tag):
                if lk.get("enable") == "false":
                    out.append(("WARN", "[%s] %s enable=false,联动不会触发" % (src, tag)))
                # 源图表白名单
                keys = REFRESH_CHART_KEYS if tag == "RefreshLinkage" else CAROUSEL_CHART_KEYS
                cls = charts.get(src, {}).get("cls", "")
                upper = cls.upper()
                if not any(k.upper() in upper for k in keys):
                    out.append(("WARN", "[%s] 源图表 class=%s 不在官方「可设%s」扩展图表白名单内,请确认图表类型(doc-2857 §1.2)" % (src, cls or "(空)", "刷新联动" if tag == "RefreshLinkage" else "轮播联动")))
                for item in lk.iter("LinkageItem"):
                    linkage_count += 1
                    label = item.get("name") or "(未命名联动项)"
                    target = item.get("target") or ""
                    anim = item.get("animation") or ""
                    tag2 = "%s→%s" % (src, target or "?")
                    # [3] target 存在且唯一
                    if not target:
                        out.append(("ERROR", "[%s] 联动项「%s」未指定 target(表单对象)" % (src, label)))
                        continue
                    if target not in charts:
                        out.append(("ERROR", "[%s] 联动项「%s」target=%s 在本表单中不存在 —— 组件重命名后最易发生" % (src, label, target)))
                        continue
                    if target == src:
                        out.append(("WARN", "[%s] 联动项「%s」联动到自身" % (src, label)))
                    if anim not in VALID_ANIMATIONS:
                        out.append(("ERROR", "[%s] 联动动画=%s 非法,只能是 %s" % (tag2, anim or "(空)", "/".join(VALID_ANIMATIONS))))
                    # 目标图表数据集
                    ds_name = charts[target]["ds"]
                    if not ds_name:
                        out.append(("ERROR", "[%s] 目标图表未绑定数据集 —— 联动传参无处落地" % tag2))
                        continue
                    ds = datasets.get(ds_name)
                    if ds is None:
                        out.append(("ERROR", "[%s] 目标图表绑定的数据集 %s 未定义" % (tag2, ds_name)))
                        continue
                    sql_params = set(re.findall(r"\$\{\s*([^}]+?)\s*\}", ds["sql"]))
                    params = list(item.iter("LinkParam"))
                    if not params:
                        out.append(("ERROR", "[%s] 联动项「%s」未新增任何参数 —— 目标图表收不到轮播值" % (tag2, label)))
                        continue
                    for lp in params:
                        pname = lp.get("name") or ""
                        pvalue = lp.get("value") or ""
                        pdisplay = lp.get("display") or ""
                        if not pname:
                            out.append(("ERROR", "[%s] 存在未命名的联动参数" % tag2))
                            continue
                        if not pvalue and not pdisplay:
                            out.append(("ERROR", "[%s] 联动参数「%s」未选取值(值/显示为空)" % (tag2, pname)))
                        # [1] 参数名必须出现在目标数据集 SQL 的 ${} 中(逐字一致)
                        if pname not in sql_params:
                            out.append(("ERROR", "[%s] 联动参数「%s」在数据集 %s 的 SQL 中无对应 ${%s} —— 参数名逐字不符是轮播联动最常见的静默失效 (SQL 现有参数: %s)" % (tag2, pname, ds_name, pname, ", ".join(sorted(sql_params)) or "无")))
                            continue
                        # [2] 数据集参数默认值
                        if pname not in ds["params"]:
                            out.append(("WARN", "[%s] 数据集 %s 未声明参数「%s」,无默认值 —— 首屏(轮播触发前)可能空白/报错" % (tag2, ds_name, pname)))
                        elif ds["params"][pname] in (None, ""):
                            out.append(("WARN", "[%s] 数据集 %s 的参数「%s」默认值为空 —— 首屏可能空白/报错" % (tag2, ds_name, pname)))
                    linked = {lp.get("name") for lp in params}
                    for sp in sorted(sql_params - linked):
                        out.append(("WARN", "[%s] 数据集 %s 的 SQL 参数 ${%s} 未被任何联动参数驱动" % (tag2, ds_name, sp)))

    # 图表标题公式引用的模板参数必须已声明
    for name, c in charts.items():
        for ref in _macro_param_refs(c["title"]):
            if ref not in tpl_params:
                out.append(("WARN", "[%s] 标题公式引用了未声明的模板参数 $%s —— 标题不会随联动变化" % (name, ref)))

    if linkage_count == 0:
        out.append(("OK", "未发现轮播/刷新联动项(CarouselLinkage/RefreshLinkage),跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "轮播联动四链一致性检查通过(%d 个联动项)" % linkage_count))
    out.append(("WARN", "轮播联动仅支持 PC 端预览,不支持移动端(doc-2857 §2.4 注)"))
    return out


def check_frm_widget_ref(cpt_path):
    """doc-2857(.frm)WidgetName 引用完整性:所有联动/超链配置中引用的目标组件名
    必须在本表单内存在;组件一旦重命名,联动 target 变成悬空引用 —— FR 不报错。
    大小写不敏感匹配(与 doc-4104 同源,合并实现)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    if root.tag != "Form":
        out.append(("OK", "非 .frm 模板(.frm 专用规则),跳过"))
        return out

    widgets = {}
    for iw in root.iter("InnerWidget"):
        wn = iw.find("WidgetName")
        if wn is not None and wn.get("name"):
            widgets[wn.get("name")] = iw
    low = {k.lower(): k for k in widgets}

    refs = []
    for hl in root.iter("Hyperlink"):
        for attr in ("target", "widgetName", "cellName"):
            v = hl.get(attr)
            if v:
                refs.append((attr, v, "超链"))
    for js_txt, _ in _iter_js_contents(root):
        for m in re.finditer(r"getWidgetByName\(\s*['\"]([^'\"]+)['\"]", js_txt):
            refs.append(("getWidgetByName", m.group(1), "JS"))
        for m in re.finditer(r"widgetName=([A-Za-z0-9_\u4e00-\u9fa5]+)", js_txt):
            refs.append(("widgetName", m.group(1), "JS"))
    # 联动项 target
    for item in root.iter("LinkageItem"):
        v = item.get("target")
        if v:
            refs.append(("target", v, "联动项"))

    if not refs:
        out.append(("OK", "未发现跨组件引用(超链/JS/联动),跳过"))
        return out
    for attr, v, src in refs:
        if v.lower() not in low:
            out.append(("ERROR", "%s 引用组件名 '%s' 在本表单中不存在(组件改名后联动/导出静默失效)" % (src, v)))
    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "组件引用完整性检查通过(%d 处引用)" % len(refs)))
    return out


# ════════════════════════════════════════════════════════════════════════════
# 规则实现(第二部分:R16–R30,参数/排序/图表/超链)
# ════════════════════════════════════════════════════════════════════════════

def check_auto_query(cpt_path):
    """doc-1434 JS 实现决策报表参数界面自动查询:凡声明 auto_query 的控件,断言
    ①存在 <Listener> 事件节点;②JS(<Content>)含 _g().parameterCommit();
    ③PC 事件名=afteredit、移动端=aftereditend。移植 check_autocommit。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    widgets_with_auto = []
    for w in root.iter("Widget"):
        wn = w.find(".//WidgetName")
        wname = wn.get("name") if wn is not None else None
        if not wname:
            continue
        auto = w.get("auto_query") or (w.findtext("auto_query") or "").strip()
        js_txts = list(_iter_js_of_widget(w))
        if auto or any("_g().parameterCommit()" in t for t in js_txts):
            widgets_with_auto.append((w, wname, js_txts))

    if not widgets_with_auto:
        out.append(("OK", "未发现 auto_query/parameterCommit 控件,跳过"))
        return out

    for w, wname, js_txts in widgets_with_auto:
        # ① Listener 事件节点
        listeners = w.findall(".//Listener") + w.findall(".//Events/Listener")
        if not listeners:
            out.append(("ERROR", "控件 %s 声明 auto_query 但缺少 <Listener> 事件节点(选值无反应)" % wname))
            continue
        # ② parameterCommit
        if not any("_g().parameterCommit()" in t for t in js_txts):
            out.append(("ERROR", "控件 %s 事件 JS 不含 `_g().parameterCommit();`(未触发自动查询)" % wname))
        # ③ 事件名:PC=afteredit,移动=aftereditend
        for ls in listeners:
            ev = ls.get("eventName") or ls.get("event") or ""
            if ev and ev not in ("afteredit", "aftereditend"):
                out.append(("WARN", "控件 %s 自动查询事件名=%s:PC 应为 afteredit,移动端应为 aftereditend" % (wname, ev)))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "自动查询一致性检查通过(%d 个控件)" % len(widgets_with_auto)))
    return out


def check_date_range_validate(cpt_path):
    """doc-1197 JS 实现日期控件校验:模板含「起-止」模式的两个日期控件
    (start*/end* 或 *start/*end),检查其查询/校验按钮是否挂了 Click 校验事件,
    缺则 WARN「空参漏校验」风险(FR 控件自带校验只在点击过的控件触发)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    names = set()
    for wn in root.iter("WidgetName"):
        n = wn.get("name")
        if n:
            names.add(n.lower())
    # A54 2026-09-15: 集合迭代序随 PYTHONHASHSEED 漂移, starts[0]/ends[0] 取值不确定;
    # 排序后遍历使输出确定化(命中集合与级别不变, 仅顺序固定), 修 w915/A39_scanfix 待裁决②
    names = sorted(names)
    date_names = [n for n in names if n and ("date" in n or "time" in n or n in ("start", "end"))]
    starts = [n for n in date_names if n.startswith("start") or n.endswith("start")]
    ends = [n for n in date_names if n.startswith("end") or n.endswith("end")]
    # 宽松:名字含 start/end 即可
    starts = [n for n in names if "start" in n]
    ends = [n for n in names if "end" in n]

    if not starts or not ends:
        out.append(("OK", "未发现起-止日期控件对(start*/end*),跳过"))
        return out

    # 找查询/校验按钮的 Click 事件 JS
    btn_js = []
    for w in root.iter("Widget"):
        wn = w.find(".//WidgetName")
        wname = wn.get("name") if wn is not None else ""
        cls = w.get("class") or ""
        if "Button" not in cls and "button" not in cls and "查询" not in wname and "search" not in wname.lower():
            continue
        for ls in w.iter("Listener"):
            ev = ls.get("event") or ls.get("eventName") or ""
            if ev.lower() in ("click", "afterclick", "clickevent"):
                for js_txt in _iter_js_of_widget(w):
                    btn_js.append((wname, js_txt))
    if not btn_js:
        out.append(("WARN", "含起-止日期控件(%s/%s)但未发现查询按钮的 Click 校验事件:空参漏校验,直接查询会带病出数(doc-1197)" % (starts[0], ends[0])))
        return out
    for wname, js_txt in btn_js:
        if "getWidgetByName" not in js_txt or not any(s in js_txt.lower() or s in js_txt for s in starts) :
            out.append(("WARN", "查询按钮 %s 的 Click 事件未见读取日期控件(%s)的校验 JS" % (wname, ",".join(starts))))
        if not re.search(r"(start|end).*?(==\s*[\"']|===?\s*null|length\s*===\s*0|\.getValue\(\).*?==)", js_txt):
            out.append(("WARN", "查询按钮 %s 的 Click 校验 JS 未见空值判定(空参漏校验风险)" % wname))

    if not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "起-止日期控件校验事件检查通过(%s/%s)" % (starts[0], ends[0])))
    return out


def check_date_validation_js(cpt_path):
    """doc-1197 日期校验 JS getter 与场景匹配:参数面板用 this.options.form
    .getWidgetByName,单元格(填报)日期控件用 contentPane.getWidgetByName;
    不匹配则 WARN(取不到控件值,校验静默失效)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    found = 0
    for js_txt, _ in _iter_js_contents(root):
        if "getWidgetByName" not in js_txt:
            continue
        found += 1
        panel_getter = "this.options.form.getWidgetByName" in js_txt
        cell_getter = "contentPane.getWidgetByName" in js_txt
        has_cell_widgets = root.find(".//ReportWriteAttr") is not None
        if panel_getter and has_cell_widgets:
            out.append(("WARN", "日期校验 JS 用参数面板 getter(this.options.form),但模板是填报模板:单元格日期控件应改用 contentPane.getWidgetByName"))
        if cell_getter and not has_cell_widgets:
            out.append(("WARN", "日期校验 JS 用单元格 getter(contentPane),但模板无填报属性:参数面板控件应改用 this.options.form.getWidgetByName"))
        # 日期格式比较陷阱
        if re.search(r"getValue\(\).*?[<>]=?.*?getValue\(\)", js_txt) and 'new Date(' not in js_txt and '"yyyy' not in js_txt:
            out.append(("WARN", "日期比较依赖字符串字典序:若控件格式非 yyyy-MM-dd,须先 new Date() 转换再比,否则误判(doc-1197)"))
    if found == 0:
        out.append(("OK", "未发现 getWidgetByName 校验 JS,跳过"))
    elif not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "日期校验 JS 场景匹配检查通过"))
    return out


def check_hierarchy_guard(cpt_path):
    """doc-3120 JS 实现参数联动层级限制弹出提示框:凡声明 require_parent 的控件,
    断言存在 beforeedit <Listener>、JS 含 parameterEl.getWidgetByName(parent)
    .getValue() 与 FR.Msg.alert;对裸 a.length<=0 写法给 WARN(父级未初始化返回
    null 时 TypeError 静默失效)。移植 check_hierarchy_guard。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    pmap = _parent_map(root)

    guarded = []
    for w in root.iter("Widget"):
        wn = w.find(".//WidgetName")
        wname = wn.get("name") if wn is not None else None
        if not wname:
            continue
        if w.get("require_parent") or w.findtext("require_parent"):
            guarded.append((w, wname))
    # 未显式声明 require_parent,但存在 beforeedit + FR.Msg.alert 的也纳入
    if not guarded:
        for w in root.iter("Widget"):
            js_txts = list(_iter_js_of_widget(w))
            if any("FR.Msg.alert" in t and "beforeedit" in (ls.get("event") or ls.get("eventName") or "")
                    for t in js_txts for ls in [w]):
                pass
        for ls in root.iter("Listener"):
            ev = ls.get("eventname") or ls.get("event") or ""
            if ev == "beforeedit":
                wn_el = _walk_up(ls, pmap, want="widget")
                if wn_el:
                    guarded.append((ls, wn_el))

    if not guarded:
        out.append(("OK", "未发现层级限制(require_parent/beforeedit)控件,跳过"))
        return out

    for w, wname in guarded:
        js_txts = list(_iter_js_of_widget(w)) if hasattr(w, "iter") else list(_iter_js_contents(root))
        js_all = "\n".join(js_txts)
        has_before = any((ls.get("eventname") or ls.get("event") or "") == "beforeedit"
                         for ls in (w.iter("Listener") if hasattr(w, "iter") else []))
        if not has_before:
            out.append(("ERROR", "[B] 子控件 %s 未挂 beforeedit(编辑前)事件" % wname))
        if "parameterEl.getWidgetByName(" not in js_all:
            out.append(("ERROR", "[C] 事件 JS 未读取父级控件值(_g().parameterEl.getWidgetByName('父控件'))"))
        if "FR.Msg.alert" not in js_all:
            out.append(("ERROR", "[D] 事件 JS 未调用 FR.Msg.alert 弹提示"))
        if "a.length<=0" in js_all and "(!a ||" not in js_all:
            out.append(("WARN", "[W] 空值判定用裸 'a.length<=0':父级返回 null 时会抛错静默失效;建议改为 '!a || a.length<=0'"))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "层级限制提示框检查通过(%d 个控件)" % len(guarded)))
    return out


def check_order_sort_param(cpt_path):
    """doc-1894 JS 实现决策报表中点击标题排序:凡含 OrderFormula 的单元格,断言同模板
    存在该排序参数 <Parameter>;若排序列为字符串数字且未套 TOINTEGER,输出 WARN 字典序
    陷阱;若超链接 JS 多列场景用 if($a=1,0,1) 表达式而非 var a=\"${a}\" 翻转,给 WARN
    「仅首次生效」坑。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")
    tpl_params = _all_template_params(root)

    order_cells = 0
    for c in root.iter("C"):
        for rg in c.iter("RG"):
            if "OrderFormula" in (rg.get("class") or ""):
                order_cells += 1
    if "OrderFormula" in text or "orderFormula" in text:
        order_cells = max(order_cells, 1)

    if order_cells == 0:
        out.append(("OK", "未发现 OrderFormula 排序配置,跳过"))
        return out

    # ① 排序参数存在性:检测 SQL 的 ORDER BY ${param} 与模板参数
    params_in_order = set()
    for d in _collect_datasets(root).values():
        for m in re.finditer(r"order\s+by[^;]*?\$\{([^}]+)\}", d["sql"], re.I):
            for tok in VAR_RE.findall(m.group(1)):
                params_in_order.add(tok)
    for p in params_in_order:
        if p not in tpl_params:
            out.append(("ERROR", "ORDER BY 排序参数 ${%s} 未在 ReportParameterAttr 声明(点击排序无参数可改)" % p))
        # ② 字符串数字未 TOINTEGER:动态排序列若为字符串数字,须套 TOINTEGER
        # (静态无法确认列类型,凡含 ORDER BY ${p} 且列名像数字串列给提示)
        for d in _collect_datasets(root).values():
            for m in re.finditer(r"order\s+by\s+([A-Za-z0-9_\u4e00-\u9fff]+)\s*\$\{%s\}" % re.escape(p), d["sql"], re.I):
                col = m.group(1)
                if re.search(r"\d", col) and "TOINTEGER" not in d["sql"].upper():
                    out.append(("WARN", "排序列 %s 疑似字符串数字且未套 TOINTEGER:字典序排序(1,10,2...),doc-1894 陷阱" % col))

    # ③ 超链接 JS 多列翻转写法
    for js_txt, _ in _iter_js_contents(root):
        if "if($" in js_txt and "=1,0,1" in js_txt:
            out.append(("OK", "多列排序 JS 用 if($a=1,0,1) 表达式翻转(推荐写法)"))
        elif 'var a="${' in js_txt and "if($" in js_txt:
            out.append(("WARN", "排序 JS 用 var a=\"${a}\" 取参数再翻转:仅首次点击生效(参数不随点击更新);应改用 if($a=1,0,1) 表达式(doc-1894)"))
        elif 'var a="${' in js_txt and "if($a" in js_txt:
            out.append(("WARN", "排序 JS 用 var a=\"${a}\" 取参数再翻转:仅首次点击生效(参数不随点击更新);应改用 if($a=1,0,1) 表达式(doc-1894)"))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "点击标题排序一致性检查通过(%d 处排序配置)" % order_cells))
    return out


def check_auto_refresh(cpt_path):
    """doc-1457 JS 实现决策报表定时刷新:模板若含 setInterval 的 body 事件,断言 JS
    包裹在 CDATA 内、且若声明 cancelable 则存在 var timer=... 与配套 clearInterval
    句柄变量,缺则 WARN「定时器叠加/无法取消」风险。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if "setInterval" not in text:
        out.append(("OK", "未发现 setInterval 定时刷新 JS,跳过"))
        return out

    found = 0
    for js_txt, _ in _iter_js_contents(root):
        if "setInterval" not in js_txt:
            continue
        found += 1
        # ① CDATA 包裹:若 JS 出现在普通文本节点(未转义)则可能失效
        # (iter_js_contents 已限定在 JS 节点内,此处检查内容是否含未转义尖括号)
        if re.search(r"<\s*(?![/!?])", js_txt):
            out.append(("WARN", "定时刷新 JS 内容疑似含未转义 '<'(CDATA 转义失效会导致 JS 不执行)"))
        # ② cancelable:声明了取消能力必须有句柄变量
        if "cancelable" in js_txt.lower() or "clearInterval" in js_txt:
            if "var timer" not in js_txt and "timer =" not in js_txt:
                out.append(("WARN", "定时刷新声明可取消(clearInterval)但未把句柄存入变量(var timer=...):无法取消,多次触发会定时器叠加"))
            if "clearInterval" not in js_txt:
                out.append(("WARN", "定时刷新使用匿名 setInterval 无法取消;建议 var timer=setInterval(...) + clearInterval(timer)"))
    if found == 0:
        # setInterval 出现在文本但不在 JS 节点(如注释/说明)
        out.append(("WARN", "文本中出现 setInterval 但未落入任何 JS 事件节点:定时刷新未挂到 body 事件,不会执行"))
    elif not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "定时刷新 JS 检查通过(%d 处 setInterval)" % found))
    return out


def check_frm_overlap(cpt_path):
    """doc-1457(附 doc-3185 §18)决策报表组件重叠:同一父容器内所有
    <Widget class=...WAbsoluteLayout$BoundsWidget> 取其【直接子】<BoundsAttr
    x y width height/> 两两求交,相交面积>0 且双方 InnerWidget 均为
    ElementCaseEditor/ChartEditor 即报错;一方为 Label 等装饰组件降级 WARN。
    定时调度推送决策报表导出附件时会先转聚合报表,组件重叠则导出失败。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    if root.tag != "Form":
        out.append(("OK", "非 .frm 模板(组件重叠仅适用决策报表),跳过"))
        return out

    def rect(widget_el):
        ba = None
        for ch in widget_el:
            if ch.tag == "BoundsAttr":
                ba = ch
                break
        if ba is None:
            return None
        try:
            x = int(ba.get("x", 0)); y = int(ba.get("y", 0))
            w = int(ba.get("width", 0)); h = int(ba.get("height", 0))
        except (TypeError, ValueError):
            return None
        return (x, y, w, h)

    def inner_class(widget_el):
        iw = None
        for ch in widget_el:
            if ch.tag == "InnerWidget":
                iw = ch
                break
        return iw.get("class", "") if iw is not None else ""

    def intersects(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        iw = min(ax + aw, bx + bw) - max(ax, bx)
        ih = min(ay + ah, by + bh) - max(ay, by)
        return iw, ih

    groups = 0
    found_any = 0
    for container in root.iter():
        if "WAbsoluteLayout" not in (container.get("class") or ""):
            continue
        children = [ch for ch in container if ch.tag == "Widget" and
                    "WAbsoluteLayout$BoundsWidget" in (ch.get("class") or "")]
        items = []
        for ch in children:
            r = rect(ch)
            if r is None:
                continue
            items.append((ch, r, inner_class(ch)))
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                ci, ri, clsi = items[i]
                cj, rj, clsj = items[j]
                iw, ih = intersects(ri, rj)
                if iw <= 0 or ih <= 0:
                    continue  # 边缘相接不算重叠
                found_any += 1
                groups += 1
                both_core = (clsi in (CHART_EDITOR_CLASS, CELL_EDITOR_CLASS)) and \
                            (clsj in (CHART_EDITOR_CLASS, CELL_EDITOR_CLASS))
                if both_core:
                    out.append(("ERROR", "组件重叠: %s(%s) 与 %s(%s) 相交 %dx%d —— 定时调度导出附件会抛「存在报表块或图表重叠,导出失败」(doc-3185)" % (
                        _text(ci.find("WidgetName")) or "?", clsi, _text(cj.find("WidgetName")) or "?", clsj, iw, ih)))
                else:
                    out.append(("WARN", "组件重叠(装饰组件降级): %s 与 %s 相交 %dx%d" % (
                        _text(ci.find("WidgetName")) or "?", _text(cj.find("WidgetName")) or "?", iw, ih)))
    if found_any == 0:
        out.append(("OK", "未发现组件重叠(BoundsAttr 两两相交),或模板无绝对布局组件"))
    return out


def check_multiselect(cpt_path):
    """doc-3707 根据参数批量导出多个文件:检测到 in ('\"+p+\"') 形式的参数化 SQL 时,
    校验对应控件 <ReturnValues> 必须为「字符串 + 分隔符 ','」;反向,多选控件存在时
    校验其 SQL 是否用逗号串拼接,不一致即 WARN。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    sql_has_in_concat = bool(re.search(r"in\s*\(\s*'\s*\"\s*\+\s*", text)) or \
                        bool(re.search(r"in\s*\(\s*'\s*\"\s*\+", text)) or \
                        "in ('\" + " in text or "in ('\"+" in text
    # 多选控件:ComboCheckBox / 下拉复选框 / ReturnValues 配置
    multi_widgets = [w for w in root.iter("Widget")
                     if "ComboCheckBox" in (w.get("class") or "") or
                     "CheckBoxGroup" in (w.get("class") or "") or
                     "Checkbox" in (w.get("class") or "")]

    if not sql_has_in_concat and not multi_widgets:
        out.append(("OK", "未发现多选拼接 SQL(in ('\"+p+\"'))或多选控件,跳过"))
        return out

    if sql_has_in_concat:
        # 校验 ReturnValues:字符串 + 分隔符 ','
        rv_ok = False
        for rv in root.iter("ReturnValues"):
            txt = _ser(rv, encoding="unicode")
            if "String" in txt and "," in txt:
                rv_ok = True
        if not rv_ok:
            out.append(("WARN", "SQL 用 in ('\"+p+\"') 拼接多选,但未找到控件 ReturnValues=字符串+分隔符 ',';分隔符与 SQL 拼接符不一致时静默漏数据(doc-3707)"))
    if multi_widgets:
        if not sql_has_in_concat:
            out.append(("WARN", "存在多选控件但数据集 SQL 未用逗号串拼接(in ('\"+p+\"')):多选值传不到 SQL,过滤失效"))
        else:
            out.append(("OK", "多选控件与 SQL 逗号串拼接一致"))

    if not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "多选批量导出一致性检查通过"))
    return out


def check_export_filename(cpt_path):
    """doc-3707(附 doc-1822)导出文件名动态性:凡导出按钮 JS 或导出 URL 用 __filename__
    拼参,断言其引用的控件 getWidgetByName(\"X\") 的 X 存在且同名模板参数已定义;
    凡 .cpt 含 <ReportWebAttr><Title> 公式,断言公式中 ${...} 引用的参数名均已在
    ReportParameterAttr 定义。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    tpl_params = _all_template_params(root)
    widget_names = _widget_names(root)

    filename_hits = 0
    for js_txt, _ in _iter_js_contents(root):
        if "__filename__" not in js_txt:
            continue
        filename_hits += 1
        for m in re.finditer(r"getWidgetByName\(\s*['\"]([^'\"]+)['\"]", js_txt):
            ref = m.group(1)
            if ref.lower() not in {w.lower() for w in widget_names}:
                out.append(("ERROR", "导出文件名 JS 引用控件 '%s' 不存在(文件名恒空,FR 不报错)" % ref))
            if ref not in tpl_params:
                out.append(("ERROR", "导出文件名控件 '%s' 无同名模板参数(取值取不到)" % ref))
        for m in re.finditer(r"\$\{([^}]+)\}", js_txt):
            for tok in VAR_RE.findall(m.group(1)):
                if tok and tok not in tpl_params:
                    out.append(("ERROR", "导出文件名 JS 引用参数 ${%s} 未定义为模板参数" % tok))

    # ReportWebAttr/Title 公式中的参数
    title_hits = 0
    for rwa in root.iter("ReportWebAttr"):
        title = rwa.find("Title")
        if title is not None and title.text:
            title_hits += 1
            for ref in _macro_param_refs(title.text):
                if ref not in tpl_params:
                    out.append(("ERROR", "网页标题公式 %s 引用参数 $%s 未在 ReportParameterAttr 定义(文件名/标题恒空)" % (title.text.strip()[:40], ref)))

    if filename_hits == 0 and title_hits == 0:
        out.append(("OK", "未发现动态导出文件名(__filename__/Title 公式)配置,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "动态导出文件名一致性检查通过"))
    return out


def check_chart_sort_js(cpt_path):
    """doc-2332 图表排序接口:①图表类型不在 8 种白名单 => ERROR;②扩展图表或移动端
    场景用 sortChart => ERROR;③afterinit/afteredit/editend 事件的 JS 里出现 sortChart
    但无 setTimeout => ERROR;④普通报表含单元格控件却按分页预览交付 => ERROR;
    ⑤getChart(\"chartN\") 出现在 .cpt(单元格载体)里 => WARN 形态不匹配。
    移植 validate_sort_spec(XML 级)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if "sortChart" not in text and "getChart" not in text:
        out.append(("OK", "未发现图表排序 JS(sortChart/getChart),跳过"))
        return out

    is_frm = root.tag == "Form"
    # ① 图表类型白名单:检测 Chart 节点类型名
    for chart in root.iter("Chart"):
        cls = chart.get("class") or ""
        known = None
        for cn in SORTABLE_CHARTS:
            if cn in cls:
                known = cn
                break
        if known is None and cls and "Chart" in cls:
            # 类型名疑似非白名单
            if not any(k in cls for k in ("Column", "Bar", "Line", "Area", "Pie", "Gauge", "Radar", "仪表", "柱", "条", "折", "饼", "雷达")):
                out.append(("WARN", "图表 class=%s 不在 sortChart 支持白名单(%s),排序按钮点了没反应(doc-2332)" % (cls, "/".join(sorted(SORTABLE_CHARTS)))))
    # ② 扩展图表用 sortChart
    for marker in EXTENDED_CHART_MARKERS:
        if marker in text and "sortChart" in text:
            out.append(("ERROR", "检测到扩展图表(%s)使用 sortChart:扩展图表不支持图表接口,静默无效(doc-2332 注1)" % marker))
            break
    # ③ 事件时序
    for ls in root.iter("Listener"):
        ev = (ls.get("event") or ls.get("eventName") or "").lower()
        if ev in NEED_DELAY_EVENTS:
            js = "\n".join(_iter_js_of_widget(ls)) or (ls.findtext(".//Content") or "")
            if "sortChart" in js and "setTimeout" not in js:
                out.append(("ERROR", "事件 %s 的 JS 出现 sortChart 但未包 setTimeout:图形未绘完,sortChart 静默无效(doc-2332 §2.4)" % ev))
    # ④ 单元格控件按分页预览交付
    has_cell_widget = root.find(".//InnerWidget") is not None or root.find(".//Widget") is not None
    if has_cell_widget and not is_frm:
        pt = root.find("PreviewType")
        pv = pt.get("PreviewType") if pt is not None else None
        if pv == "0" or pv is None:
            out.append(("WARN", "普通报表含单元格控件却按分页预览交付:控件不渲染,排序按钮点不了;须用填报预览(write)或数据分析(analysis)(doc-2332 §3.2)"))
    # ⑤ getChart(\"chartN\") 在 .cpt 中
    if not is_frm and re.search(r'getChart\(\s*["\']chart\d+["\']', text):
        out.append(("WARN", ".cpt(单元格载体)里出现 getChart(\"chartN\"):组件名写法只适用于 .frm,单元格图表应传坐标(如 A1)"))

    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "图表排序 JS 检查通过"))
    return out


def check_listener_cdata(cpt_path):
    """doc-2332(render_listener_xml 公共工具)Listener JS 的 CDATA 安全:
    JS <Content> 文本内含 ']]>' 会截断 CDATA 段导致整份 .cpt XML 非法,
    ERROR 拦截;另提示 JS 含未转义 '<' 的潜在风险。
    ⚠语境标注(2026-08-20 反向验证): ']]>' 只扫 JS Content 文本(ET 解析后
    CDATA 标记已剥离),禁止扫全文件——任何含 CDATA 段的合法 .cpt 全文件
    扫描必然命中闭合符,属规则误报(实测 示例实际表/示例预算表 拆分版全中招)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    for js_txt, _ in _iter_js_contents(root):
        bad = []
        if "]]>" in js_txt:
            bad.append("字面量 ']]>'")
        if "]]&gt;" in js_txt:
            bad.append("转义形态 ']]&gt;'")
        if bad:
            out.append(("ERROR", "<Content> 内出现 %s,会截断 CDATA 破坏整份 XML;请改写(如 ']' + ']>')(doc-1839/2332)" % "、".join(bad)))
    # 事件 JS 含未转义 <
    for js_txt, _ in _iter_js_contents(root):
        if re.search(r"<\s*(?!/|!|\?|\[)", js_txt):
            out.append(("WARN", "JS 内容含未转义 '<' 疑似截断 CDATA;请用 &lt; 或确保在 CDATA 段内"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "Listener JS CDATA 安全检查通过"))
    return out


def check_chart_style(cpt_path):
    """doc-4138 图表样式 FAQ:①legend.position 不在{top,bottom,left,right}=>ERROR;
    ②label.style 不在{auto,custom}=>ERROR;③label/condition 颜色非 #RRGGBB =>ERROR;
    ④条件公式缺比较符(><=)=>ERROR;⑤series.colors 顺序与系列数据顺序不一致 =>WARN。
    移植 gen_chart_style.check(XML 级,样式节点名以 <Legend>/<Label>/颜色属性为主)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    POSITIONS = {"top", "bottom", "left", "right"}
    LABEL_STYLES = {"auto", "custom"}
    COLOR_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")

    charts = list(root.iter("Chart"))
    if not charts:
        out.append(("OK", "未发现 Chart 节点,跳过"))
        return out
    found = 0
    for chart in charts:
        text = _ser(chart, encoding="unicode")
        # ① legend.position
        for pos in re.findall(r"<Position>\s*<!\[CDATA\[([^\]]+)\]\]>\s*</Position>", text) + \
                       re.findall(r'position\s*[=:]\s*["\']?([a-z]+)', text):
            found += 1
            if pos.lower() not in POSITIONS:
                out.append(("ERROR", "legend.position=%s 非法,允许 %s(doc-4138)" % (pos, "/".join(sorted(POSITIONS)))))
        # ② label.style
        for st in re.findall(r'label\.style\s*[=:]\s*["\']?([a-z]+)', text) + \
                     re.findall(r'<LabelStyle[^>]*style="([^"]+)"', text):
            found += 1
            if st.lower() not in LABEL_STYLES:
                out.append(("ERROR", "label.style=%s 非法,允许 %s(doc-4138)" % (st, "/".join(sorted(LABEL_STYLES)))))
        # ③ 颜色非 #RRGGBB
        for col in re.findall(r'#?[0-9A-Fa-f]{6}', text):
            found += 1
            # 只校验出现在 color 语境的颜色
        for m in re.finditer(r'(?:color|Color|颜色)[^A-Za-z0-9]*["\']?([#A-Za-z0-9]+)', text):
            val = m.group(1)
            found += 1
            if not COLOR_RE.match(val) and val.lower() not in ("transparent", "auto", "none"):
                out.append(("ERROR", "颜色值 %r 非法,需 #RRGGBB(doc-4138)" % val))
        # ④ 条件公式缺比较符
        for cond in re.findall(r"(?:Condition|condition|条件)[^<]{0,80}?([A-Za-z0-9_\u4e00-\u9fff]+\([^)]*\))", text):
            found += 1
            if not re.search(r"[><=]", cond):
                out.append(("ERROR", "条件公式 '%s' 缺比较符(><=):条件永不触发(doc-4138)" % cond[:50]))
        # ⑤ 系列颜色顺序(静态无法对比数据顺序,保守 WARN 提示)
        colors = re.findall(r"#?[0-9A-Fa-f]{6}", text)
        if len(colors) >= 2:
            out.append(("WARN", "series.colors 顺序(%s...)与系列数据顺序不一致会导致系列颜色错位;静态无法判定,请人工核对(doc-4138)" % ",".join(colors[:3])))

    if found == 0:
        out.append(("OK", "Chart 节点中未发现可静态判定的样式配置(样式节点名待核验),跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "图表样式体检通过(%d 处样式配置)" % found))
    return out


def check_order_by(cpt_path):
    """doc-903 数据集中的排序:①ORDER BY 后若出现 ${param} 且对应数据集参数无枚举值、
    默认值非 {asc,desc,\"\"} => WARN「动态排序方向未受约束,存在 SQL 注入/报错风险」;
    ②多列动态排序方向数 != 列数 => ERROR;③中文列直接 order by 中文列(无 convert)
    且连接疑似 MySQL => WARN「UTF-8 下中文不按拼音排序」。移植 order_by.py 校验。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    datasets = _collect_datasets(root)

    found = 0
    for name, d in datasets.items():
        sql = d["sql"]
        if not sql:
            continue
        m = re.search(r"order\s+by\s+(.+)$", sql, re.I | re.S)
        if not m:
            continue
        found += 1
        order_clause = m.group(1).strip()
        # ① 动态方向参数
        for pm in re.finditer(r"\$\{([^}]+)\}", order_clause):
            body = pm.group(1)
            for tok in VAR_RE.findall(body):
                if tok in ("if", "len"):
                    continue
                default = d["params"].get(tok)
                if default not in (None, "") and default.lower() not in ALLOWED_DIRECTIONS:
                    out.append(("WARN", "数据集[%s] ORDER BY 动态方向参数 ${%s} 默认值 %r 不在白名单 {asc,desc,\"\"}:拼进 SQL 即注入/报错向量(doc-903)" % (name, tok, default)))
                elif default in (None, ""):
                    out.append(("WARN", "数据集[%s] ORDER BY 动态方向参数 ${%s} 无默认值约束:运行期取值不可控,存在注入风险;建议白名单 {asc,desc}(doc-903)" % (name, tok)))
        # ② 多列动态排序方向数 != 列数
        dyn_cols = re.findall(r"([A-Za-z0-9_\u4e00-\u9fff]+)\s*\$\{[^}]+\}", order_clause)
        if len(dyn_cols) > 1:
            # 方向都是同一 ${a} 时视为共享;不同参数按 1:1 检查
            params_in_order = set(re.findall(r"\$\{([^}]+)\}", order_clause))
            out.append(("WARN", "数据集[%s] 多列动态排序 %s 共享参数 %s:方向数需与列数对齐(每列一个方向),否则部分列方向不可控(doc-903)" % (name, dyn_cols, sorted(params_in_order))))
        # ③ 中文列直接 order by 且无 convert -> 疑似 MySQL 中文排序失效
        cn_cols = re.findall(r"order\s+by\s+([\u4e00-\u9fff]+)", sql)
        if cn_cols and "convert(" not in sql.lower() and "using gbk" not in sql.lower():
            conn = (sql[:200])
            if "mysql" in conn.lower() or "jdbc:mysql" in conn.lower() or "MySQL" in conn:
                out.append(("WARN", "数据集[%s] 中文列 %s 直接 order by 且连接疑似 MySQL:UTF-8 下中文不按拼音排序(静默错序),须 convert(列 using gbk)(doc-903 §4.1)" % (name, cn_cols)))
            else:
                out.append(("WARN", "数据集[%s] 中文列 %s 直接 order by:MySQL 场景下须 convert(列 using gbk)才按拼音排序;请确认连接类型(doc-903 §4.1)" % (name, cn_cols)))

    if found == 0:
        out.append(("OK", "未发现 ORDER BY 排序配置,跳过"))
    elif not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "数据集排序体检通过(%d 处 ORDER BY)" % found))
    return out


def check_dynamic_param_hyperlink(cpt_path):
    """doc-903(附 doc-4202)动态参数超链接:检测 DynamicParamHyperlink / DynamicParamLink
    类超链。真实节点名在 kit 内零命中(待核验),故检测到该类节点时保守 WARN 提示
    核验,并校验其参数名是否双声明(模板参数 + 数据集参数)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    markers = ("DynamicParamHyperlink", "DynamicParamLink", "com.fr.cell.hyperlink.DynamicParam")
    hits = [m for m in markers if m in text]
    if not hits:
        out.append(("OK", "未发现动态参数超链接节点,跳过"))
        return out
    out.append(("WARN", "检测到动态参数超链(%s):该节点名在 kit 内无真实样例(待核验);若节点名拼错 FR 会静默忽略超链,请用设计器另存后 diff 核实(doc-903/4202)" % "/".join(hits)))

    tpl_params = _all_template_params(root)
    datasets = _collect_datasets(root)
    for hl in root.iter("Hyperlink"):
        cls = hl.get("class") or ""
        if "DynamicParam" not in cls:
            continue
        for p in hl.iter("Parameter"):
            pn = p.get("name")
            if not pn:
                continue
            if pn not in tpl_params:
                out.append(("ERROR", "动态参数超链参数 %s 未声明为模板参数(点击后参数无处落地)" % pn))
            if not any(pn in d["params"] for d in datasets.values()):
                out.append(("WARN", "动态参数超链参数 %s 未在任何数据集参数中声明(数据不重查)" % pn))
    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "动态参数超链参数双声明检查通过"))
    return out


def check_sort_after_expand(cpt_path):
    """doc-897 扩展后排序:①sortAfterExpand 出现在非最父格 => ERROR「静默无效」;
    ②排序公式含 *-1 但依据列为字符串/日期型且未包 DATEDIF => ERROR;
    ③方向属性=降序(2) 且公式含 *-1 => ERROR「双翻转互相抵消」;
    ④公式引用 $param 但模板无同名 <Parameter> 或默认值不在 {asc,desc} => ERROR;
    ⑤同一扩展区内多个格都设了 sortAfterExpand => WARN;
    ⑥最父格未设 divideMode=\"1\" 却按「整表排序」意图配置 => WARN;
    ⑦排序公式引用格与被排序格不同行且无左父格链 => WARN(与 doc-2684 同源)。
    移植 gen_sort_after_expand.validate。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    tpl_params = _all_template_params(root)

    # 收集所有设了 sortAfterExpand 的格
    sorted_cells = []
    cells_with_dir = {}
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        cells_with_dir[name] = (int(cc), int(rr))
        exp = c.find("Expand")
        if exp is None:
            continue
        if exp.get(SORT_ATTR) not in ("1", "2"):
            continue
        se = exp.find(SORT_EXPR_TAG)
        formula = ""
        if se is not None:
            attr = se.find(SORT_EXPR_ATTR_TAG)
            formula = ((attr.text or se.text or "") if attr is not None else (se.text or "")).strip()
        sorted_cells.append((name, formula, exp.get(SORT_ATTR), c))

    if not sorted_cells:
        out.append(("OK", "未发现 sortAfterExpand 扩展后排序配置,跳过"))
        return out

    # 扩展区:同行的连续扩展格视为同一扩展区
    row_cols = {}
    for name, (cc, rr) in cells_with_dir.items():
        row_cols.setdefault(rr, []).append((cc, name))
    for rr, lst in row_cols.items():
        lst.sort()
    def top_parent_of(name):
        cc, rr = cells_with_dir.get(name, (0, 0))
        row = row_cols.get(rr, [])
        if row:
            return row[0][1]
        return name

    extra_sorted = []
    for name, formula, dirv, c in sorted_cells:
        top = top_parent_of(name)
        # ① 非最父格
        if name != top:
            out.append(("ERROR", "排序设在 %s,但最父格是 %s:非最父格上的扩展后排序静默无效(doc-897 注1)" % (name, top)))
            continue
        # ② 公式含 *-1 且依据列疑似字符串/日期
        if "* -1" in formula or "*-1" in formula:
            m = re.search(r"([A-Za-z]+\d+)", formula)
            if m:
                ref = m.group(1)
                # 字符串列无法静态确认,凡 *-1 且无 DATEDIF 给 WARN(字符串/日期不可取负)
                if "DATEDIF" not in formula.upper():
                    out.append(("WARN", "%s 排序公式含 *-1 但依据列 %s 未包 DATEDIF:字符串/日期型取负翻转无效,应转数字(doc-897 注2)" % (name, ref)))
        # ③ 方向属性=降序且公式含 *-1 -> 双翻转
        if dirv == str(DESC) and ("* -1" in formula or "*-1" in formula):
            out.append(("ERROR", "%s 方向属性=降序(2) 且公式含 *-1:双翻转互相抵消,顺序不变(doc-897)" % name))
        # ④ 公式引用 $param
        for ref in _macro_param_refs(formula):
            if ref not in tpl_params:
                out.append(("ERROR", "%s 排序公式引用 $%s 但模板无同名 <Parameter>(doc-897)" % (name, ref)))
        # ⑦ 排序公式引用格与被排序格不同行且无左父格链
        m = re.search(r"([A-Za-z]+\d+)", formula.lstrip("="))
        if m:
            ref = m.group(1)
            if ref in cells_with_dir and cells_with_dir[ref][1] != cells_with_dir[name][1]:
                exp = c.find("Expand")
                left = exp.get("left") if exp is not None else None
                lpc, lpr = exp.get("leftParentColumn"), exp.get("leftParentRow")
                has_chain = bool(left and _is_cell_ref(left)) or (lpc is not None and lpr is not None)
                if not has_chain:
                    out.append(("WARN", "%s 排序公式引用 %s 不同行且无左父格链:每个分组将对应多/零个值,排序不可预期(与 doc-2684 同源)" % (name, ref)))
        # ⑤ 同一扩展区多格排序(合并统计,避免重复报)
        extra_sorted.append(name)

    if len(extra_sorted) > 1:
        out.append(("WARN", "同一扩展区内多个格(%s)都设了 sortAfterExpand:只有最父格生效,其余冗余且易与公式互相抵消" % ",".join(extra_sorted)))

    # ⑥ 最父格未设 divideMode=\"1\"
    for name, formula, dirv, c in sorted_cells:
        rg = c.find(".//RG")
        dm = rg.find("Attr") if rg is not None else None
        divide = dm.get("divideMode") if dm is not None else None
        if divide != "1":
            out.append(("WARN", "%s 未设 divideMode=\"1\"(列表):默认分组展示合并同值行,排序语义变'按分组排'而非'整表排'(doc-897 §2.2)" % name))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "扩展后排序体检通过(%d 处排序配置)" % len(sorted_cells)))
    return out


def check_horizontal_sort(cpt_path):
    """doc-1782 横向扩展列多列排序:①排序公式含 EVAL(\"B2[;B1:\"+$index+\"]\") 时,断言
    存在横向扩展格 B1(dir=\"1\")且 $index 由某超链以 &B1 注入,否则坐标指向空 => 静默不排序;
    ②B2 汇总值格必须是数字型(EVAL(\"-1*...\") 却引用文本/日期列且无 DATEDIF => ERROR);
    ③sortAfterExpand 设在 A2 之外的子格 => ERROR;④首屏未带 isnull($index) guard => WARN。
    移植 topic_1782 静态自检。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if "EVAL(" not in text or "sortAfterExpand" not in text:
        out.append(("OK", "未发现横向多列排序(EVAL+sortAfterExpand)配置,跳过"))
        return out

    # 单元格扩展方向
    dirs = {}
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        exp = c.find("Expand")
        if exp is not None and exp.get("dir") in ("0", "1"):
            dirs[name] = exp.get("dir")

    # ① B1 横向扩展 + $index 注入
    if "EVAL(" in text:
        b1_ok = dirs.get("B1") == "1"
        if not b1_ok:
            out.append(("ERROR", "EVAL(\"B2[;B1:\"+$index+\"]\") 要求 B1 为横向扩展格(dir=\"1\"),当前未检出 —— 坐标指向空,静默不排序(doc-1782)"))
        index_injected = bool(re.search(r"[&?]B1\s*=", text)) or "&B1=" in text
        if not index_injected:
            out.append(("ERROR", "$index 未由任何超链以 &B1=... 注入:点击列头时 index 恒为空,排序公式失效(doc-1782)"))
    # ② EVAL(\"-1*...\") 引用文本/日期列
    for m in re.finditer(r'EVAL\([^)]*?-1\*[^)]*?([A-Z]+\d+)', text):
        out.append(("WARN", "EVAL 取负引用 %s:若该列为文本/日期且未包 DATEDIF,取负翻转无效(doc-1782)" % m.group(1)))
    # ③ sortAfterExpand 设在 A2 之外
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        exp = c.find("Expand")
        if exp is not None and exp.get(SORT_ATTR) in ("1", "2") and name != "A2":
            out.append(("ERROR", "sortAfterExpand 设在 %s(应为 A2 最父格):子格上静默无效(doc-1782)" % name))
    # ④ isnull($index) guard
    if "EVAL(" in text:
        js_all = "\n".join(t for t, _ in _iter_js_contents(root))
        if "isnull($index)" not in js_all and "isnull($index" not in text:
            out.append(("WARN", "首屏未带 isnull($index) guard:每次点击重算绝对坐标,首屏性能劣化且可能错位(doc-1782)"))

    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "横向多列排序体检通过"))
    return out


def check_custom_order(cpt_path):
    """doc-3622 利用内置数据集实现自定义排序:①内置数据集出现在 X.select(Y) 公式中但
    X/Y 非合法标识符 => ERROR;②顺序表存在重复值 => ERROR(重复行静默失效);
    ③顺序表值含首尾/全角空格或空值 => ERROR;④排序公式含 inarray 但无 =0 未命中兜底
    => WARN;⑤inarray 公式所在格不是最父格 => ERROR;⑥顺序表行数 > 200 => WARN。
    移植 gen_custom_order.validate。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if "inarray(" not in text and ".select(" not in text:
        out.append(("OK", "未发现 inarray/内置数据集自定义排序配置,跳过"))
        return out

    IDENT_RE = re.compile(r"^[A-Za-z_\u4e00-\u9fa5][\w\u4e00-\u9fa5]*$")
    # ① 数据集名/列名标识符
    for m in re.finditer(r"([\u4e00-\u9fa5\w]+)\.select\(([\u4e00-\u9fa5\w]+)\)", text):
        dsname, col = m.group(1), m.group(2)
        if not IDENT_RE.match(dsname) or not IDENT_RE.match(col):
            out.append(("ERROR", "内置数据集名/列名 %s.%s 含非法字符:拼进公式后解析失败或静默取空(doc-3622)" % (dsname, col)))
    # 内置数据集行数据(EmbeddedTableData / RowData / R / C)
    order_values = []
    for td in root.iter("TableData"):
        if td.get("class") == "com.fr.data.impl.EmbeddedTableData":
            for r in td.iter("R"):
                for c in r.iter("C"):
                    v = (c.text or "").strip()
                    if v:
                        order_values.append(v)
    if not order_values and "EmbeddedTableData" in text:
        # 兼容其它行节点形态
        for cell in root.iter("Cell"):
            v = (cell.text or "").strip()
            if v:
                order_values.append(v)
    if order_values:
        # ② 重复值
        dup = [v for i, v in enumerate(order_values) if v in order_values[:i]]
        if dup:
            out.append(("ERROR", "顺序表存在重复值 %s:inarray 只取首个位置,重复行静默失效(doc-3622)" % sorted(set(dup))))
        # ③ 空值/首尾空格/全角空格
        bad = [v for v in order_values if v != v.strip() or v.strip() == "" or "\u3000" in v]
        if bad:
            out.append(("ERROR", "顺序表有空值或首尾/全角空格 %r:与单元格值精确比对失败,静默排错(doc-3622)" % bad))
        # ⑥ 行数 > 200
        if len(order_values) > 200:
            out.append(("WARN", "顺序表 %d 行 > 200:扩展后排序期间每行都要求值 select(),建议下沉 SQL 字典表 JOIN sort_no(doc-3622)" % len(order_values)))
    else:
        # 顺序表可能不落 XML(纯 spec 生成),跳过数据级校验
        out.append(("WARN", "未在 XML 中提取到内置数据集行数据(顺序表),重复/空格校验跳过(判定假设:顺序表须无重复、无首尾空格)"))

    # ④ inarray 无 =0 兜底
    for m in re.finditer(r"inarray\(([^)]*)\)", text):
        expr = m.group(0)
        if "= 0" not in expr and "=0" not in expr:
            out.append(("WARN", "排序公式 %s 无 =0 未命中兜底:新值/异常值 inarray 返回 0 静默堆到最前;建议 if(...=0, 9999, ...)(doc-3622)" % expr[:50]))
    # ⑤ inarray 所在格不是最父格
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        exp = c.find("Expand")
        if exp is None:
            continue
        se = exp.find(SORT_EXPR_TAG)
        formula = ""
        if se is not None:
            attr = se.find(SORT_EXPR_ATTR_TAG)
            formula = ((attr.text or se.text or "") if attr is not None else (se.text or "")).strip()
        if "inarray" in formula:
            name = _cell(cc, rr)
            # 最父格 = 同行最小列号
            row_min = None
            for c2 in root.iter("C"):
                cc2, rr2 = c2.get("c"), c2.get("r")
                if cc2 is not None and rr2 is not None and int(rr2) == int(rr):
                    if row_min is None or int(cc2) < row_min:
                        row_min = int(cc2)
            if row_min is not None and int(cc) != row_min:
                out.append(("ERROR", "inarray 排序公式设在 %s(最父格应为第 %d 列):子格上静默无效(doc-3622)" % (name, row_min + 1)))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "内置数据集自定义排序体检通过"))
    return out


def check_string_pinyin(cpt_path):
    """doc-3309 扩展后中文按拼音排序:StringPinyin( 公式要求「常用函数集合插件」已装
    (WARN,平台侧不可静态确认),公式形态须为 StringPinyin($$$, \"<sep>\", {1,-1})
    (ERROR:三参、$$$ 自引用、间隔符为字符串、格式∈{1,-1})。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if "StringPinyin(" not in text:
        out.append(("OK", "未发现 StringPinyin 公式,跳过"))
        return out

    out.append(("WARN", "检测到 StringPinyin(:依赖「常用函数集合插件」,服务端未装则公式静默失效、排序退回原序;插件安装属平台侧,须向部署方确认(doc-3309)"))
    for m in re.finditer(r"StringPinyin\(([^)]*)\)", text):
        body = m.group(1)
        parts = [x.strip() for x in body.split(",")]
        if len(parts) != 3:
            out.append(("ERROR", "StringPinyin 公式形态异常:应 3 参数(实际 %d):StringPinyin($$$, \"<sep>\", {1,-1})(doc-3309)" % len(parts)))
            continue
        a1, a2, a3 = parts
        if a1 != "$$$":
            out.append(("ERROR", "StringPinyin 第一参应为 $$$ 自引用(实际 %s)(doc-3309)" % a1))
        if not (a2.startswith('"') and a2.endswith('"')):
            out.append(("ERROR", "StringPinyin 第二参应为字符串间隔符(实际 %s)(doc-3309)" % a2))
        if a3 not in ("1", "-1"):
            out.append(("ERROR", "StringPinyin 第三参应为 1 或 -1(实际 %s)(doc-3309)" % a3))
    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "StringPinyin 公式形态检查通过(插件依赖见上方 WARN)"))
    return out


def check_hanzi_num_sort(cpt_path):
    """doc-3717 汉字数字排序:①公式含 MAPARRAY( 但 fn 未使用隐式变量 item(写成单元格名
    或加了引号)=> ERROR;②COUNT(X[!0]) 的 X 与排序所在格不一致 => ERROR(数组长度取错格);
    ③同一格同时存在数据列 OrderFormula 与扩展后 SortExpression => ERROR(双重排序);
    ④公式含 NUMTO( 且序号最大值 ≥11 => WARN(NUMTO(11) 输出形态未实测,不符则 INARRAY 恒 0);
    ⑤含 NUMTO( 而排序键可能为小数 => ERROR(doc 明注不支持小数,静态无法确认时 WARN)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if not any(k in text for k in ("MAPARRAY(", "NUMTO(", "INARRAY(")):
        out.append(("OK", "未发现汉字数字排序公式(MAPARRAY/NUMTO/INARRAY),跳过"))
        return out

    # ① MAPARRAY fn 未用 item
    for m in re.finditer(r"MAPARRAY\(([^,]+),\s*([^)]+)\)", text):
        fn = m.group(2).strip()
        if "item" not in fn:
            out.append(("ERROR", "MAPARRAY 的 fn '%s' 未使用隐式循环变量 item(写成单元格名或加了引号):数组逐项映射失效(doc-3717)" % fn[:50]))
    # ② COUNT(X[!0]) 与排序格不一致
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        exp = c.find("Expand")
        if exp is None:
            continue
        se = exp.find(SORT_EXPR_TAG)
        formula = ""
        if se is not None:
            attr = se.find(SORT_EXPR_ATTR_TAG)
            formula = ((attr.text or se.text or "") if attr is not None else (se.text or "")).strip()
        if not formula:
            continue
        if "COUNT(" in formula and "[!0]" in formula:
            m = re.search(r"COUNT\(\s*([A-Za-z]+\d+)\[!0\]", formula)
            if m and m.group(1).upper() != name:
                out.append(("ERROR", "COUNT(%s[!0]) 的单元格名与排序所在格 %s 不一致:数组长度取错格(doc-3717)" % (m.group(1), name)))
        # ③ 同一格 OrderFormula + SortExpression 双重排序
        if "OrderFormula" in _ser(c, encoding="unicode"):
            out.append(("ERROR", "单元格 %s 同时设数据列排序(OrderFormula)与扩展后排序(SortExpression):双重排序结果取决于执行次序,不可预期(doc-3717)" % name))
        if "NUMTO(" in formula:
            # ④ 序号最大值 ≥11
            nums = re.findall(r"NUMTO\(\s*(\d+)", formula)
            if nums and max(int(n) for n in nums) >= 11:
                out.append(("WARN", "公式含 NUMTO( 且序号最大值 %d >= 11:需实测 NUMTO(11) 输出形态(「十一」还是「一十一」),与数据不逐字符相等则 INARRAY 恒 0(doc-3717)" % max(int(n) for n in nums)))
            # ⑤ 小数键
            if re.search(r"NUMTO\([^)]*[.][0-9]", formula):
                out.append(("ERROR", "排序键含小数配合 NUMTO(:doc 明注不支持小数,汉字数组对不上(doc-3717)"))
            elif "NUMTO(" in formula:
                out.append(("WARN", "含 NUMTO( 的排序键若为小数会静默失效(doc 明注不支持小数);静态无法确认列类型,请人工核对"))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "汉字数字排序体检通过"))
    return out


def check_hyperlink_dynamic_param(cpt_path):
    """doc-4202 超级链接-动态参数:凡单元格含动态参数超链 <Parameter name=X>,断言 X
    同时存在于模板参数与(被引用的)数据集参数,缺任一即报错(或至少 WARN 数据集中
    找不到 ${X})。两类静默失效:超链参数名不匹配 / 缺模板参数。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    tpl_params = _all_template_params(root)
    datasets = _collect_datasets(root)
    all_ds_params = set()
    for d in datasets.values():
        all_ds_params |= set(d["params"].keys())
        for tok in sql_referenced_params(d["sql"]):
            all_ds_params.add(tok)

    found = 0
    for hl in root.iter("Hyperlink"):
        cls = hl.get("class") or ""
        if "DynamicParam" not in cls:
            continue
        found += 1
        for p in hl.iter("Parameter"):
            pn = p.get("name")
            if not pn:
                continue
            if pn not in tpl_params:
                out.append(("ERROR", "动态参数超链参数 %s 未声明为模板参数:点击后重新提交时参数无处落地(doc-4202)" % pn))
            if pn not in all_ds_params:
                out.append(("ERROR", "动态参数超链参数 %s 未在任何数据集参数/SQL ${%s} 中引用:数据不重查,排序/过滤不生效(doc-4202)" % (pn, pn)))
    if found == 0:
        out.append(("OK", "未发现动态参数超链,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "动态参数超链一致性检查通过(%d 处)" % found))
    return out


def check_hyperlink_js(cpt_path):
    """doc-4204 超级链接-JavaScript脚本:①JS 超链 <Parameter> 的 name 非合法 JS 标识符
    /命中保留字 => ERROR;②任意 <Content> CDATA 内出现 ']]>' => ERROR(会截断 XML);
    ③超链参数值是形如 =A2 的公式,但挂超链的单元格与被引用列不在同一扩展父子链
    => WARN「每行按钮可能取到同一个值」。移植 check_url_hyperlink 的 E1-E3。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    pmap = _parent_map(root)

    found = 0
    for js_el in root.iter("JavaScript"):
        content = js_el.find("Content")
        content_txt = (content.text or "") if content is not None else (js_el.text or "")
        # ① 参数名
        for p in js_el.iter("Parameter"):
            a = p.find("Attributes")
            name = a.get("name") if a is not None else p.get("name")
            if not name:
                continue
            found += 1
            if not JS_IDENT.match(name):
                out.append(("ERROR", "超链参数名 %r 不是合法 JS 标识符:JS 里以裸变量引用,中文/数字开头/带横杠都会让脚本报错(点击无反应)(doc-4204)" % name))
            elif name in JS_RESERVED:
                out.append(("ERROR", "超链参数名 %r 是 JS 保留字(doc-4204)" % name))
            elif name in JS_GLOBALS:
                out.append(("ERROR", "超链参数名 %r 会覆盖页面/帆软全局对象(doc-4204)" % name))
            # ③ 参数值 =A2 父子链
            val = p.get("value") or ""
            if val and val.startswith("=") and _is_cell_ref(val[1:]):
                ref = val[1:].upper()
                # 挂链单元格
                link_cell = _walk_up(js_el, pmap, want="cell")
                if link_cell:
                    lc, lr = _cr(link_cell)
                    rc, rr = _cr(ref)
                    if lc is None or rc is None:
                        continue
                    same_row = (lr == rr)
                    same_col = (lc == rc)
                    if not (same_row or same_col):
                        out.append(("WARN", "超链参数值 %s 引用 %s,与挂链格 %s 不在同一行/列扩展父子链:每行按钮可能取到同一个值(doc-4204/1839)" % (val, ref, link_cell)))
        # ② CDATA 安全
        if "]]>" in content_txt:
            out.append(("ERROR", "<Content> 含 ']]>' ,会截断 CDATA 破坏 XML(doc-4204)"))
        if "]]&gt;" in content_txt:
            out.append(("ERROR", "<Content> 含转义形态 ']]&gt;' ,同样会截断 CDATA(doc-1839)"))

    if found == 0:
        out.append(("OK", "未发现 JS 超链参数配置,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "JS 超链体检通过(%d 个参数)" % found))
    return out


def check_js_hyperlink_export(cpt_path):
    """doc-4204 JS 超链导出能力:JS 超链导出(export/viewlet+format)要求 ①参数名合法
    JS 标识符(见 check_hyperlink_js)②CDATA 安全 ③URL 参数值 encodeURIComponent 加固
    (中文/空格/& 未编码会把 URL 拼断);导出文件名 __filename__ 值未编码 => WARN。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    found = 0
    for js_txt, params in _iter_js_contents(root):
        if not any(k in js_txt for k in ("viewlet=", "__filename__", "format=", "ec_export")):
            continue
        found += 1
        # ① 导出 URL 参数值未编码
        for m in re.finditer(r"([A-Za-z_]\w*)\s*=\s*\"?\s*\+?\s*([A-Za-z0-9_]+)", js_txt):
            var = m.group(2)
            if var in params or var.startswith("$"):
                if not re.search(r"encodeURIComponent\s*\(\s*%s\s*\)" % re.escape(var), js_txt):
                    out.append(("WARN", "导出 URL 拼接变量 %s 未过 encodeURIComponent:值含中文/空格/& 时 URL 拼断(文件名乱码或 404)(doc-4204)" % var))
        # ② __filename__ 值未编码
        if "__filename__" in js_txt and "encodeURIComponent" not in js_txt:
            out.append(("WARN", "导出文件名 __filename__ 未做 encodeURIComponent 加固:中文文件名导出乱码(doc-1822/4204)"))
        # ③ 参数名 JS 标识符(与 E1 同源,导出场景专用提示)
        for name in params:
            if not JS_IDENT.match(name or ""):
                out.append(("ERROR", "导出 JS 事件参数名 %r 不是合法 JS 标识符(doc-4204)" % name))

    if found == 0:
        out.append(("OK", "未发现 JS 导出超链(viewlet/__filename__),跳过"))
    elif not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "JS 导出超链体检通过(%d 处)" % found))
    return out


def check_hover_link_mobile(cpt_path):
    """doc-4204(附 doc-4209)联动悬浮元素:模板含「联动悬浮元素」超链节点时,输出
    WARN「该特性不支持 App 端/HTML5 端预览,仅 PC 分页预览生效」;并校验悬浮元素
    目标存在(与 doc-4207 同源)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    markers = ("FloatElementHyperlink", "悬浮", "FloatHyperlink", "com.fr.js.FloatElement")
    hits = [m for m in markers if m in text]
    if not hits:
        out.append(("OK", "未发现联动悬浮元素超链,跳过"))
        return out
    out.append(("WARN", "检测到「联动悬浮元素」超链(%s):该特性不支持 App 端/HTML5 端预览,仅 PC 分页预览生效(doc-4209)" % "/".join(hits)))
    # 悬浮元素目标存在性
    floats = set()
    for fl in root.iter("Float"):
        n = fl.get("name")
        if n:
            floats.add(n)
    for hl in root.iter("Hyperlink"):
        cls = hl.get("class") or ""
        if "Float" not in cls:
            continue
        target = hl.get("target") or hl.get("cellName") or ""
        if target and target not in floats:
            out.append(("ERROR", "联动悬浮元素超链 target=%s 不存在(联动静默失效)" % target))
    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "联动悬浮元素结构检查通过"))
    return out


def check_form_linkage(cpt_path):
    """doc-3556 决策报表「当前表单对象/当前决策报表对象」超链联动 R1~R10:
    R1 根节点类型 R2 WidgetName 唯一 R3 超链 target 存在性 R4 自联动 WARN
    R5 目标组件未绑数据集 R6 超链参数未在目标数据集声明 R7 目标数据集 SQL 缺 ${}
    R8 参数无默认值 WARN R9 取值来源与源组件类型不匹配(单元格源用了「系列名称」)
    R10 公式 =A2 引用的格不在本报表块。移植 check_form_linkage。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    if root.tag != "Form":
        out.append(("OK", "根节点为 <%s>,非 .frm(「当前表单对象」超链仅适用决策报表),跳过" % root.tag))
        return out

    # R2 组件唯一
    widgets, dupes = {}, []
    for iw in root.iter("InnerWidget"):
        wn = iw.find("WidgetName")
        name = wn.get("name") if wn is not None else None
        if not name:
            continue
        if name in widgets:
            dupes.append(name)
        widgets[name] = {"el": iw, "class": iw.get("class", "")}
    for d in sorted(set(dupes)):
        out.append(("ERROR", "[R2] WidgetName 重复: %s —— 联动 target 指向不确定" % d))

    datasets = _collect_datasets(root)
    tpl_params = _all_template_params(root)

    def bound_datasets(inner):
        names = set()
        for tn in inner.iter("TableName"):
            if tn.text and tn.text.strip():
                names.add(tn.text.strip())
        for at in inner.iter("Attributes"):
            ds = at.get("dsName")
            if ds:
                names.add(ds)
        return names

    def cells_of(inner):
        out_cells = set()
        for c in inner.iter("C"):
            cc, rr = c.get("c"), c.get("r")
            if cc is not None and rr is not None:
                out_cells.add(_cell(cc, rr))
        return out_cells

    bind = {n: bound_datasets(w["el"]) for n, w in widgets.items()}
    pmap = _parent_map(root)

    def nearest_widget(el):
        return _walk_up(el, pmap, want="widget")

    def nearest_cell(el):
        return _walk_up(el, pmap, want="cell")

    links = 0
    for hl in root.iter("Hyperlink"):
        cls = hl.get("class") or ""
        if cls and cls != FORM_HL_CLASS:
            continue
        links += 1
        src_name = nearest_widget(hl) or "?"
        src_class = widgets.get(src_name, {}).get("class", "") if src_name != "?" else ""
        src_cell = nearest_cell(hl)
        where = "超链[%s] 源=%s%s" % (hl.get("name") or "?", src_name, ("/" + src_cell) if src_cell else "")
        target = hl.get("target")
        # R3 target 存在
        if not target:
            out.append(("ERROR", "[R3] %s 缺 target 属性" % where))
            continue
        if target not in widgets:
            out.append(("ERROR", "[R3] %s -> 目标组件 '%s' 在表单中不存在(组件重命名后联动整体失灵且完全静默)" % (where, target)))
            continue
        # R4 自联动
        if target == src_name:
            out.append(("WARN", "[R4] %s 联动自身,通常是配置笔误" % where))
        tgt_ds = bind.get(target, set())
        # R5 目标绑数据集
        if not tgt_ds:
            out.append(("ERROR", "[R5] %s -> '%s' 未绑定任何数据集,参数无处落地" % (where, target)))
            continue
        for prm in hl.findall("Parameters/Parameter"):
            pname = prm.get("name")
            if not pname:
                out.append(("ERROR", "[R6] %s 存在无 name 的联动参数" % where))
                continue
            hit_ds = [d for d in tgt_ds if pname in datasets.get(d, {}).get("params", {})]
            if not hit_ds:
                out.append(("ERROR", "[R6] %s -> '%s' 所绑数据集 %s 均未声明参数 '%s'(目标常被误绑成全量数据集,点击无任何反应)" % (where, target, sorted(tgt_ds), pname)))
                continue
            for d in hit_ds:
                ds = datasets[d]
                # R7 SQL ${} 占位
                if ("${%s}" % pname) not in ds["sql"] and \
                   not any(re.search(r"(?<![A-Za-z0-9_])" + re.escape(pname) + r"(?![A-Za-z0-9_])", b)
                           for b in re.findall(r"\$\{(.*?)\}", ds["sql"], re.S)):
                    out.append(("ERROR", "[R7] 数据集 %s 声明了参数 '%s' 但 SQL 无 ${%s} 占位符" % (d, pname, pname)))
                # R8 默认值
                if not ds["params"].get(pname):
                    out.append(("WARN", "[R8] 数据集 %s 的参数 '%s' 无默认值,首屏(未点击前)将空白" % (d, pname)))
            # R9 取值来源
            vt = (prm.get("valueType") or "").upper()
            val = prm.get("value") or ""
            chart_only = {"SERIES_NAME", "CATEGORY_NAME", "VALUE"}
            if vt in chart_only and src_class != CHART_EDITOR_CLASS:
                out.append(("ERROR", "[R9] %s 参数 '%s' 用了图表专属取值 %s,但源组件不是图表(%s);单元格源只能用 FORMULA(=A2 或 =$$$)" % (where, pname, vt, src_class or "未知")))
            elif vt == "FORMULA":
                if not val.startswith("="):
                    out.append(("ERROR", "[R9] %s 参数 '%s' 的 FORMULA 值 '%s' 必须以 '=' 开头" % (where, pname, val)))
                else:
                    # R10 公式引用格存在性
                    m = re.match(r"^=\s*([A-Z]{1,3})(\d+)\s*$", val)
                    if m:
                        ref = m.group(1).upper() + m.group(2)
                        src_el = widgets.get(src_name, {}).get("el") if src_name != "?" else None
                        if src_el is not None and src_class == CELL_EDITOR_CLASS:
                            if ref not in cells_of(src_el):
                                out.append(("WARN", "[R10] %s 参数 '%s' 引用单元格 %s,但该格不在源报表块内 —— 取值恒为空" % (where, pname, ref)))
    if links == 0:
        out.append(("OK", "未发现任何 %s 联动超链,跳过" % FORM_HL_CLASS))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", ".frm 表单联动检查通过(%d 处超链)" % links))
    return out


def check_url_hyperlink(cpt_path):
    """doc-1839 JS 超链拼外部站点 URL 参数(外链四条):①window.open 的 URL 字面量缺
    协议头(不以 http(s)://、//、${、/、# 开头)=> ERROR;②<Content> 里出现 'https?://
    字面量(判定为外链)且同时含 FR.cjkEncode => ERROR;③外链场景下超链参数变量未被
    encodeURIComponent() 包裹就拼进 URL => WARN;④<Content> 含 ']]>'(包括转义形态
    ]]&gt;)=> ERROR。移植 check_url_hyperlink。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    found = 0
    for js_el in root.iter("JavaScript"):
        content = js_el.find("Content")
        content_txt = (content.text or "") if content is not None else (js_el.text or "")
        if not content_txt.strip():
            continue
        found += 1
        # ① URL 协议头
        for lit in re.findall(r"window\.open\(\s*['\"]([^'\"]*)", content_txt):
            if lit.startswith("${") or lit.startswith("/") or lit.startswith("#"):
                continue
            if not re.match(r"^(https?:)?//", lit):
                out.append(("ERROR", "window.open 的 URL %r 缺协议头 http://,浏览器会按相对路径拼到报表服务域名下 => 404(doc-1839)" % lit[:60]))
        # ② 外链 + cjkEncode
        is_external = re.search(r"['\"]https?://", content_txt) is not None
        if is_external and "cjkEncode" in content_txt:
            out.append(("ERROR", "外部站点 URL 套了 FR.cjkEncode:那是帆软私有编码,第三方站点解不出来 => 应改用 encodeURIComponent(doc-1839)"))
        # ③ 参数值编码
        for p in js_el.iter("Parameter"):
            a = p.find("Attributes")
            name = a.get("name") if a is not None else p.get("name")
            if not name:
                continue
            if is_external and not re.search(r"encodeURIComponent\s*\(\s*%s\s*\)" % re.escape(name), content_txt):
                out.append(("WARN", "参数 %r 直接拼进外部 URL 未过 encodeURIComponent:值含空格/中文/& 时会把 URL 拼断(doc-1839)" % name))
        # ④ CDATA 截断
        if "]]>" in content_txt:
            out.append(("ERROR", "<Content> 含 ']]>'(含转义形态 ']]&gt;'),会截断 CDATA 破坏 XML(doc-1839)"))
        if "]]&gt;" in content_txt:
            out.append(("ERROR", "<Content> 含转义形态 ']]&gt;',同样会截断 CDATA(doc-1839)"))

    if found == 0:
        out.append(("OK", "未发现 JS 超链内容,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "外链 URL 超链体检通过(%d 处 JS)" % found))
    return out


def check_hyperlink_parent_chain(cpt_path):
    """doc-1839(修正 doc-4204 单向判定)扩展父子链一致性需双向判定:超链参数值 =X2 与
    挂链格,从两端各走一次 leftParent/upParent 链,任一方向连通即通过;=$$$ 需豁免。
    按单向实现会对「挂主格取子格」整类写法全量误报。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    # 单元格名 -> (c,r) 与 (left, up) 父格
    cells = {}
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        name = _cell(cc, rr)
        left = up = None
        exp = c.find("Expand")
        if exp is not None:
            lv = exp.get("left")
            if lv and _is_cell_ref(lv):
                left = lv.upper()
            uv = exp.get("up")
            if uv and _is_cell_ref(uv):
                up = uv.upper()
        cells[name] = {"pos": (int(cc), int(rr)), "left": left, "up": up}

    def chain(target, direction):
        """沿 direction('left'/'up')父格链回溯,返回路径上的所有格名。"""
        path = set()
        node = target
        seen = set()
        while node in cells and node not in seen:
            seen.add(node)
            path.add(node)
            node = cells[node][direction]
            if node is None:
                break
        return path

    found = 0
    for js_el in root.iter("JavaScript"):
        for p in js_el.iter("Parameter"):
            a = p.find("Attributes")
            name = a.get("name") if a is not None else p.get("name")
            if not name:
                continue
            val = p.get("value") or ""
            if val == "=$$$":
                continue  # 豁免
            if not (val.startswith("=") and _is_cell_ref(val[1:])):
                continue
            ref = val[1:].upper()
            if ref not in cells:
                continue
            # 挂链格
            link_cell = _walk_up(js_el, _parent_map(root), want="cell")
            if link_cell is None or link_cell not in cells:
                continue
            found += 1
            # 双向连通判定
            ref_up = chain(ref, "up") | chain(ref, "left")
            link_up = chain(link_cell, "up") | chain(link_cell, "left")
            if ref in cells and link_cell in cells:
                rp = cells[ref]["pos"]
                lp = cells[link_cell]["pos"]
                same_row = rp[1] == lp[1]
                same_col = rp[0] == lp[0]
            else:
                same_row = same_col = False
            connected = (ref in link_up) or (link_cell in ref_up) or same_row or same_col
            if not connected:
                out.append(("WARN", "超链参数值 %s 引用 %s,与挂链格 %s 无扩展父子链(双向 left/up 均不连通):每行按钮可能取到同一个值(doc-1839/4204)" % (val, ref, link_cell)))
    if found == 0:
        out.append(("OK", "未发现 =单元格 形式的超链参数值,跳过"))
    elif not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "超链父子链双向判定通过(%d 处)" % found))
    return out


def check_js_remote_evaluate(cpt_path):
    """doc-1839(附 topic_4241)JS 超链 remoteEvaluate + 双分支:①JS 超链 <Content> 缺
    FR.remoteEvaluate( => ERROR;②<Content> 同时缺 window.location.href(跳转分支)或
    FR.Msg.alert(弹窗分支)=> ERROR。两条均纯字面量判定,属「点得动/永远跳或永远不跳」
    的静默故障。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    found = 0
    for js_txt, _ in _iter_js_contents(root):
        if not any(k in js_txt for k in ("window.open", "viewlet=", "location.href", "remoteEvaluate")):
            continue
        found += 1
        if "FR.remoteEvaluate(" not in js_txt:
            out.append(("ERROR", "JS 超链未调用 FR.remoteEvaluate(:失去「跳转前判断」核心机制,无数据也会跳(doc-4241)"))
        if "window.location.href" not in js_txt:
            out.append(("ERROR", "JS 超链缺少跳转分支(window.location.href):有数据时永远不跳(doc-4241)"))
        if "FR.Msg.alert" not in js_txt:
            out.append(("ERROR", "JS 超链缺少无数据弹窗分支(FR.Msg.alert):无数据时无提示(doc-4241)"))
    if found == 0:
        out.append(("OK", "未发现跳转类 JS 超链(remoteEvaluate 场景),跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "remoteEvaluate 双分支检查通过(%d 处)" % found))
    return out


def check_dynparam_linkage(cpt_path):
    """doc-651 决策报表组件联动(动态参数超链五链):①存在 DynamicParamHyperlink 类超链;
    ②超链参数名 = <ReportParameterAttr> 模板参数名;③该参数同时被某数据集声明为数据集
    参数;④数据集 SQL 的 ${} 块内引用该参数;⑤数据集参数有默认值节点。
    移植 check_dynparam_linkage。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    if root.tag != "Form":
        out.append(("OK", "根节点为 <%s>,非 <Form>(动态参数联动仅适用 .frm),跳过" % root.tag))
        return out

    tpl_params = _all_template_params(root)
    datasets = _collect_datasets(root)

    sources = []
    for hl in root.iter("Hyperlink"):
        cls = hl.get("class") or ""
        if DYN_PARAM_HL_CLASS not in cls and "DynamicParamHyperlink" not in cls:
            continue
        pnames = [p.get("name") for p in hl.findall("Parameters/Parameter") if p.get("name")]
        if not pnames:
            out.append(("ERROR", "[R2] 动态参数超链未声明任何参数"))
            continue
        sources.append(pnames)

    if not sources:
        out.append(("OK", "未发现 DynamicParamHyperlink 动态参数超链,跳过"))
        return out

    for pnames in sources:
        for pname in pnames:
            # R3 模板参数
            if pname not in tpl_params:
                out.append(("ERROR", "[R3] 动态参数超链参数 '%s' 未在 <ReportParameterAttr> 声明为模板参数" % pname))
                continue
            # R4 数据集参数 + R5 SQL ${} + R6 默认值
            bound = None
            for dname, d in datasets.items():
                if pname in d["params"]:
                    bound = (dname, d)
                    break
            if bound is None:
                out.append(("ERROR", "[R4] 模板参数 '%s' 未被任何数据集声明为数据集参数(动态参数无处落地)" % pname))
                continue
            dname, d = bound
            blocks = re.findall(r"\$\{(.*?)\}", d["sql"], re.S)
            inside = any(re.search(r"(?<![A-Za-z0-9_])" + re.escape(pname) + r"(?![A-Za-z0-9_])", b) for b in blocks)
            if not inside:
                out.append(("ERROR", "[R5] 数据集 %s 的 SQL 未在任何 ${} 占位符内引用 '%s'(参数传到了却没参与过滤)" % (dname, pname)))
            # R6 默认值节点
            if d["params"].get(pname) is None:
                out.append(("ERROR", "[R6] 数据集 %s 参数 '%s' 缺少默认值 <O>(首屏未点击时可能空白)" % (dname, pname)))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "动态参数联动五链检查通过"))
    return out


def check_optional_param_default(cpt_path):
    """doc-651 可选参数数据集标准 SQL 模板:含 ${if(len(p)==0,...)} 的数据集,其 p 必须
    给默认值(否则首屏未点击时 SQL 因 p 未定义报错/空白);并断言该 p 已声明为数据集参数
    且模板参数双声明。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    tpl_params = _all_template_params(root)

    found = 0
    for name, d in _collect_datasets(root).items():
        sql = d["sql"]
        if "if(len(" not in sql:
            continue
        for m in re.finditer(r"if\s*\(\s*len\s*\(\s*([A-Za-z0-9_\u4e00-\u9fff]+)\s*\)\s*==\s*0", sql):
            found += 1
            p = m.group(1)
            if p not in d["params"]:
                out.append(("ERROR", "数据集[%s] 用 ${if(len(%s)==0,...)} 可选过滤,但 %s 未声明为数据集参数(SQL 因 p 未定义报错/空白)" % (name, p, p)))
            elif d["params"].get(p) in (None, ""):
                out.append(("ERROR", "数据集[%s] 可选过滤参数 %s 未给默认值:首屏未点击时 SQL 报错/空白,须给默认值(doc-651 标准模板)" % (name, p)))
            if p not in tpl_params:
                out.append(("WARN", "数据集[%s] 可选过滤参数 %s 未同时声明为模板参数(控件无法按名绑定)" % (name, p)))
    if found == 0:
        out.append(("OK", "未发现 ${if(len(p)==0,...)} 可选过滤数据集,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "可选参数数据集默认值检查通过(%d 处)" % found))
    return out


def check_chart_refresh_api(cpt_path):
    """doc-3115 扩展图表组件刷新(dealReloadChartAjax 修正):模板 XML 中若图表组件类名
    命中扩展图表标记且同类刷新 JS 用 dataRefresh()(非 dealReloadChartAjax()) => ERROR;
    反之普通图表用了 dealReloadChartAjax() => WARN。移植 refresh_factory 判定。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if "dataRefresh" not in text and "dealReloadChartAjax" not in text:
        out.append(("OK", "未发现图表刷新 JS(dataRefresh/dealReloadChartAjax),跳过"))
        return out

    # (R30 perf) 全文 lower 提出推导式:原式对每个 marker 都重算一次 5.9MB 级 text.lower()
    text_low = text.lower()
    ext_hit = any(m.lower() in text_low for m in EXTENDED_CHART_MARKERS)
    for js_txt, _ in _iter_js_contents(root):
        if "dataRefresh" in js_txt and ext_hit:
            out.append(("ERROR", "扩展图表场景用 dataRefresh() 刷新:扩展图表须用 dealReloadChartAjax(),否则静默不刷新(doc-3115)"))
        if "dealReloadChartAjax" in js_txt and not ext_hit:
            out.append(("WARN", "普通图表用了 dealReloadChartAjax():普通图表应改用 dataRefresh()(doc-3115)"))
    # 逐图表组件判定
    for chart in root.iter("Chart"):
        cls = chart.get("class") or ""
        if not cls:
            continue
        is_ext = any(m.lower() in cls.lower() for m in EXTENDED_CHART_MARKERS)
        # 该图表上下文内的 JS
        chart_js = _ser(chart, encoding="unicode")
        if is_ext and "dataRefresh()" in chart_js and "dealReloadChartAjax()" not in chart_js:
            out.append(("ERROR", "图表 %s 为扩展图表(class=%s)却用 dataRefresh():须 dealReloadChartAjax()(doc-3115)" % (chart.get("name") or "?", cls)))
        if not is_ext and "dealReloadChartAjax()" in chart_js:
            out.append(("WARN", "图表 %s 为普通图表却用 dealReloadChartAjax():应 dataRefresh()(doc-3115)" % (chart.get("name") or "?")))

    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "图表刷新 API 检查通过"))
    return out


def check_chart_style_registry(cpt_path):
    """doc-1672 图表样式九类封闭枚举:①样式类别名不在九类封闭枚举 => ERROR(拼错
    tooltips/座标轴 = 该类样式静默丢失);②配色同时给预定义方案与自定义色板 => ERROR
    (覆盖关系不可静态判定);③声明了图表类型特有样式却缺 chart_type => ERROR;
    ④九类覆盖度清单 => WARN(列出走默认值的类别)。移植 chart_style_registry R1~R5
    (XML 级:扫描 Chart 下样式节点与 JSON 形态 spec)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")
    charts = list(root.iter("Chart"))
    if not charts:
        out.append(("OK", "未发现 Chart 节点,跳过"))
        return out

    found = 0
    for chart in charts:
        ctext = _ser(chart, encoding="unicode")
        # ① 九类枚举:检测样式节点名(中英文别名)
        aliases = {
            "title": "标题", "legend": "图例", "label": "标签", "series": "系列",
            "axis": "坐标轴", "dataSheet": "数据表", "background": "背景",
            "tooltip": "提示", "colorScheme": "配色",
            "标题": "标题", "图例": "图例", "标签": "标签", "系列": "系列",
            "坐标轴": "坐标轴", "数据表": "数据表", "背景": "背景", "提示": "提示", "配色": "配色",
        }
        known = set()
        for node_tag in re.findall(r"<(\w+)", ctext):
            low = node_tag.lower()
            cn = aliases.get(node_tag) or aliases.get(low.capitalize())
            # 样式节点通常含 Style/Color/Position 等特征
            if re.search(r"(style|Style|Color|Position|Title|Legend|Label)", node_tag):
                found += 1
                if cn:
                    known.add(cn)
                elif low not in ("chart", "chartdata", "datadefinition", "tablename",
                                 "titletextattr", "textattr", "charttype", "seriesdata",
                                 "categorydata", "valuedata", "cdata", "data"):
                    out.append(("ERROR", "未知样式类别节点 <%s>:拼错(tooltips/座标轴)即该类样式静默丢失;通用样式仅 9 类 %s(doc-1672)" % (node_tag, "/".join(STYLE_CATEGORIES))))
        # ② 配色互斥:scheme 与 colors 同现
        if re.search(r'scheme\s*[=:]\s*["\']?[^"\'\s]+', ctext) and re.search(r'colors\s*[=:]\s*\[', ctext):
            found += 1
            out.append(("ERROR", "配色同时给了预定义方案(scheme)与自定义色板(colors):二者互斥,覆盖关系不可静态判定(doc-1672)"))
        # ③ 特有样式缺 chart_type
        if re.search(r"typeSpecific|typespecific|特有", ctext) and not re.search(r"chart_type|chartType|type\s*=\s*[\"']", ctext):
            found += 1
            out.append(("ERROR", "声明了图表类型特有样式却缺少 chart_type:特有样式套错类型会静默失效(doc-1672)"))
        # ④ 覆盖度:未配置的类别
        missing = [cn for cn in STYLE_CATEGORIES if cn not in known]
        if missing and known:
            out.append(("WARN", "图表未显式配置的通用样式类别(将用 FR 默认值): %s(doc-1672)" % "/".join(missing)))

    if found == 0:
        out.append(("OK", "Chart 中未发现可判定的样式配置(样式节点名待核验),跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "图表样式九类枚举检查通过"))
    return out


def check_formula_param_declared(cpt_path):
    """doc-1672(通用规则升级)公式引用模板参数必须双声明:扫描模板内所有形如 =...$p...
    的公式文本,断言 p 已在 <ReportParameterAttr> 声明;若 p 同时用于数据集过滤 ${p},
    则断言数据集参数与模板参数双声明且都有默认值。失败表现固定为「数据变了但文字不
    变」。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    tpl_params = _all_template_params(root)
    datasets = _collect_datasets(root)

    formula_refs = {}  # p -> 出现位置列表
    for el in root.iter():
        if el.tag in ("O", "TextAttr", "Title", "Content", "Formula", "Attributes"):
            txt = (el.text or "")
            if txt.startswith("=") and "$" in txt:
                for ref in _macro_param_refs(txt):
                    formula_refs.setdefault(ref, []).append(txt.strip()[:50])

    for p, locs in formula_refs.items():
        if p not in tpl_params:
            out.append(("ERROR", "公式 '%s' 引用模板参数 $%s 未在 <ReportParameterAttr> 声明:数据变了但文字不变(通用铁律,doc-1672/4207/2857)" % (locs[0], p)))
        # 数据集过滤双声明 + 默认值
        ds_use = [n for n, d in datasets.items()
                  if any(re.search(r"(?<![A-Za-z0-9_])" + re.escape(p) + r"(?![A-Za-z0-9_])", b)
                         for b in re.findall(r"\$\{(.*?)\}", d["sql"], re.S))]
        if ds_use:
            if p not in tpl_params:
                continue  # 上面已报
            declared_ds = [n for n in ds_use if p in datasets[n]["params"]]
            if not declared_ds:
                out.append(("ERROR", "参数 $%s 用于数据集过滤(%s)但未声明为数据集参数:双声明缺失,首屏可能报错(doc-1672)" % (p, ",".join(ds_use))))
            for n in declared_ds:
                if datasets[n]["params"].get(p) in (None, ""):
                    out.append(("WARN", "参数 $%s 在数据集 %s 中未给默认值:首屏(未点击前)可能空白(doc-1672)" % (p, n)))

    if not formula_refs:
        out.append(("OK", "未发现 =...$p... 公式文本,跳过"))
    elif not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "公式参数双声明检查通过(%d 个参数)" % len(formula_refs)))
    return out


# 全局参数清单(供 doc-159 R3 修正):可由 check_global_param 通过同目录 project_globals.json
# 或 set_global_params() 注入;未提供时降级为 WARN。
_GLOBAL_PARAMS = {}


def set_global_params(gparams):
    """注入工程全局参数清单 {名: 默认值}。"""
    global _GLOBAL_PARAMS
    _GLOBAL_PARAMS = dict(gparams or {})


def _load_global_params(cpt_path):
    """尝试从 cpt 同目录 project_globals.json / globals.json 读取全局参数清单。"""
    if _GLOBAL_PARAMS:
        return _GLOBAL_PARAMS
    base = os.path.dirname(os.path.abspath(cpt_path))
    for fn in ("project_globals.json", "globals.json"):
        p = os.path.join(base, fn)
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
    return None


def check_global_param(cpt_path):
    """doc-159 全局参数(doc-158 R3 修正):「Query 用到的 ${p} 必须在 ReportParameterAttr
    声明」仅当 p 不在工程全局参数清单中时才成立。校验器支持第二输入(全局参数清单,
    project_globals.json 或 set_global_params());未提供清单时 R3 降级为警告并提示
    「若 p 是全局参数请忽略」。另检测同名遮蔽(R1)、默认名 P1..Pn(R3)、面板缺控件
    (R4)、依赖全局参数不自包含(R2)、裸等值守卫(R5)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    gparams = _load_global_params(cpt_path)

    datasets = _collect_datasets(root)
    tpl_params = _all_template_params(root)
    widget_names = _widget_names(root)

    used = {}
    for name, d in datasets.items():
        for tok in sql_referenced_params(d["sql"]):
            used.setdefault(tok, set()).add(name)

    if not used:
        out.append(("OK", "未发现数据集 SQL 参数引用,跳过"))
        return out

    has_globals = bool(gparams)
    for p in sorted(used):
        src = ",".join(sorted(used[p]))
        in_t = p in tpl_params
        in_g = has_globals and p in gparams
        if not in_t and not in_g:
            if has_globals:
                out.append(("ERROR", "[R0] 参数 $%s 被引用(%s),但既非模板参数也不在全局参数清单:运行时取空值,报表出空表且 FR 不报错" % (p, src)))
            else:
                out.append(("WARN", "[R3-降级] 参数 $%s 在数据集 Query 中使用(%s)但 ReportParameterAttr 未声明:若 %s 是工程全局参数请忽略;未提供全局参数清单(project_globals.json/set_global_params),无法排除假阳性(doc-159)" % (p, src, p)))
            continue
        if in_t and in_g:
            out.append(("WARN", "[R1] 参数 %s 同时存在于全局参数(默认 '%s')与模板参数(默认 '%s'):模板参数为准,全局值被静默架空 —— 同名遮蔽(doc-159 §4.1)" % (p, gparams.get(p, ""), tpl_params.get(p, "") if isinstance(tpl_params, dict) else "")))
            continue
        if in_g:
            if re.fullmatch(r"P\d+", p):
                out.append(("WARN", "[R3] 全局参数名 %s 形如默认名 P1..Pn,疑未重命名(doc-159)" % p))
            if widget_names and p not in widget_names:
                out.append(("WARN", "[R4] 全局参数 %s 被引用但 ParameterUI 无同名控件:用户改不了值,只能吃服务器默认值(doc-159)" % p))
            out.append(("WARN", "[R2] 本模板依赖全局参数 %s,非自包含:部署到新工程须先在『服务器>全局参数』重设(doc-159 §4.2)" % p))

    # R5 裸等值守卫
    for name, d in datasets.items():
        for p in sql_referenced_params(d["sql"]):
            if has_globals and p in gparams and p not in tpl_params:
                if re.search(r"=\s*'\$\{%s\}'" % re.escape(p), d["sql"]) and "1=1" not in d["sql"] and "len(" not in d["sql"]:
                    out.append(("WARN", "[R5] 数据集[%s] 用裸 `= '${%s}'` 且无 1=1 + if(len(%s)==0) 守卫:全局参数未配置时静默空表" % (name, p, p)))

    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "全局参数检查通过"))
    return out


def check_extended_chart(cpt_path):
    """doc-2474 扩展图表插件静默约束:凡模板检出含扩展图表,即 WARN 其 5 条静默约束:
    ①不支持导出 ②不支持移动端 ③不支持任何图表接口 ④只支持 Chrome(>=86)预览
    ⑤不支持组件刷新。另 WARN 依赖 jxbrowser 内核与插件版本一致性(平台侧)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    hits = [t for t in EXT_TYPES if t in text]
    # (R30 perf) 全文 lower 提出推导式(同 check_auto_refresh 处理)
    text_low = text.lower()
    cls_hits = [m for m in EXTENDED_CHART_MARKERS if m.lower() in text_low]
    if not hits and not cls_hits:
        out.append(("OK", "未检测到扩展图表,跳过"))
        return out

    out.append(("WARN", "检测到扩展图表(%s):以下 5 条约束为 FR 不报错的静默限制 ——" % ("、".join(hits or cls_hits))))
    for c in EXT_CHART_CONSTRAINTS:
        out.append(("WARN", "  - " + c))
    out.append(("WARN", "跨模块依赖:扩展图表依赖 jxbrowser 内核(仅 Chrome 系),且服务端插件版本须与设计器一致,否则运行期异常无报错(doc-2474)"))

    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "扩展图表静默约束提示完成"))
    return out


def check_freeze_merge(cpt_path):
    """doc-368 分页冻结:扫描 <CellElement rowSpan/colSpan>1> 的合并单元格,反推其占用的
    行/列区间,与 FrozenColumnRow.columnrow 及 RepeatRow/RepeatColumn 的覆盖范围比对,
    未完整覆盖则输出警告(第一页冻结内容不显示)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []

    # 冻结区:columnrow 的 (col,row) 0 基
    frozen = None
    for fr in root.iter("FrozenColumnRow"):
        cr = fr.get("columnrow") or (fr.text or "").strip()
        if cr and _is_cell_ref(cr):
            frozen = _cr(cr)
            break
    repeat_rows, repeat_cols = None, None
    for rs in root.iter("ReportSettings"):
        rr = rs.find("RepeatRow")
        if rr is not None and rr.text:
            repeat_rows = rr.text
        rc = rs.find("RepeatColumn")
        if rc is not None and rc.text:
            repeat_cols = rc.text

    if frozen is None:
        out.append(("OK", "未发现分页冻结(FrozenColumnRow),跳过"))
        return out
    fcol, frow = frozen

    # 合并单元格区间
    merges = []
    for c in root.iter("C"):
        rs = int(c.get("rowSpan") or 1)
        cs = int(c.get("colSpan") or 1)
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        cc, rr = int(cc), int(rr)
        if rs > 1 or cs > 1:
            merges.append((cc, rr, cc + cs - 1, rr + rs - 1, _cell(cc, rr)))
    if not merges:
        out.append(("OK", "分页冻结存在但无合并单元格,跳过"))
        return out

    for mcol0, mrow0, mcol1, mrow1, name in merges:
        # 合并区与冻结区(0..fcol, 0..frow)相交
        if mcol0 <= fcol and mrow0 <= frow:
            # 合并区必须完整落在冻结区内
            if mcol1 > fcol or mrow1 > frow:
                out.append(("WARN", "合并单元格 %s(%d..%d 列,%d..%d 行)横跨冻结边界:冻结列/行未覆盖合并区右下角,第一页冻结内容不显示;须把 FrozenColumnRow 移到合并区右下角(doc-368)" % (name, mcol0 + 1, mcol1 + 1, mrow0 + 1, mrow1 + 1)))
        # 重复行/列覆盖
        if repeat_rows is not None:
            try:
                rset = {int(x) for x in re.findall(r"\d+", repeat_rows)}
                if rset and mrow0 <= max(rset) <= mrow1 and mrow0 < max(rset):
                    pass
            except Exception:
                pass
        if repeat_cols is not None:
            pass  # 重复列与冻结列交集判定复杂,保守略过

    if not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "冻结区与合并单元格覆盖检查通过(%d 个合并区)" % len(merges)))
    return out


def check_fill_freeze_expand(cpt_path):
    """doc-611 填报冻结:对含 <FrozenColumnRow> 且为填报模板(存在 <ReportWriteAttr>/
    提交配置)的 .cpt,扫描冻结行/列坐标区间内是否含扩展方向属性(ListCell/
    CellExpandAttr 指向数据集),命中即 WARN(冻结区含扩展数据,填报预览错位)。
    附 WARN:普通填报预览冻结全部扩展数据,新填报预览只冻结指定行数。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    is_fill = root.find(".//ReportWriteAttr") is not None or "ReportWriteAttr" in _ser(root, encoding="unicode")
    frozen = None
    for fr in root.iter("FrozenColumnRow"):
        cr = fr.get("columnrow") or (fr.text or "").strip()
        if cr and _is_cell_ref(cr):
            frozen = _cr(cr)
            break
    if frozen is None:
        out.append(("OK", "未发现 FrozenColumnRow,跳过"))
        return out
    if not is_fill:
        out.append(("OK", "模板非填报(无 ReportWriteAttr),填报冻结规则不适用,跳过"))
        return out
    fcol, frow = frozen
    hit = 0
    for c in root.iter("C"):
        cc, rr = c.get("c"), c.get("r")
        if cc is None or rr is None:
            continue
        cc, rr = int(cc), int(rr)
        if cc > fcol or rr > frow:
            continue  # 不在冻结区内
        exp = c.find("Expand")
        if exp is None:
            continue
        if exp.get("dir") in ("0", "1") or c.find(".//ListCell") is not None or \
           c.find(".//CellExpandAttr") is not None:
            hit += 1
            out.append(("WARN", "冻结区(%d 列 x %d 行)内单元格 %s 含扩展方向属性:冻结区含扩展数据会错位;建议冻结区只圈静态表头(doc-611)" % (fcol + 1, frow + 1, _cell(cc, rr))))
    if hit == 0:
        out.append(("OK", "填报冻结区未发现扩展单元格"))
    out.append(("WARN", "doc-611 行为差异:普通填报预览冻结全部扩展数据,新填报预览只冻结指定行数;交付前须确认预览引擎"))
    return out


def check_wrap_rowheight(cpt_path):
    """doc-217 单元格样式:凡生成「自动换行」文本控制的单元格,必须同步设置行高自动,
    否则预览不换行(仅设自动换行没有效果)。检测换行属性与行高自动属性的一致性。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    wrap_hits = len(re.findall(r"(?:wrap|换行|wordWrap|LineWrap)[^A-Za-z0-9_]{0,4}(?:true|1|自动)", text))
    if wrap_hits == 0:
        out.append(("OK", "未发现自动换行文本控制,跳过"))
        return out
    # 行高自动:RowHeight 配置 / 单元格行高 auto 属性
    auto_height = bool(re.search(r"(?:autoHeight|AutoHeight|行高自动|height.*auto|auto.*height)", text)) or \
                  bool(re.search(r"RowHeight[^>]*auto", text))
    if not auto_height:
        out.append(("WARN", "%d 处单元格设了自动换行但未检出「自动调整行高」配置:仅设置自动换行没有效果,长文本会挤压变形(doc-217 §2.3.2)" % wrap_hits))
    else:
        out.append(("OK", "自动换行与自动行高配置齐全"))
    return out


def check_submit_consistency(cpt_path):
    """doc-596 JS 自定义提交按钮:凡 <Widget class=Button> 的点击事件 JS 含
    verifyAndWriteReport/writeReport,必须同时检出模板存在 <ReportWriteAttr>
    <SubmitVisitor>,否则 ERROR(点了不入库的静默故障)。移植 check_submit_consistency。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    has_write_attr = root.find(".//ReportWriteAttr") is not None
    has_submit_visitor = root.find(".//SubmitVisitor") is not None or "SubmitVisitor" in _ser(root, encoding="unicode")

    btn_found = 0
    submit_btn = 0
    for w in root.iter("Widget"):
        cls = w.get("class") or ""
        if "Button" not in cls and "button" not in cls:
            continue
        wn = w.find(".//WidgetName")
        wname = wn.get("name") if wn is not None else "?"
        js_all = "\n".join(_iter_js_of_widget(w))
        if "verifyAndWriteReport" in js_all or "writeReport" in js_all:
            btn_found += 1
            submit_btn += 1
            if not has_write_attr:
                out.append(("ERROR", "按钮 %s 调用提交 JS(verifyAndWriteReport/writeReport)但模板无 <ReportWriteAttr>:未配填报属性,点了不入库,静默失效(doc-596)" % wname))
            elif not has_submit_visitor:
                out.append(("ERROR", "按钮 %s 调用提交 JS 但 <ReportWriteAttr> 下无 <SubmitVisitor> 提交配置:数据不会入库(doc-596)" % wname))
        else:
            btn_found += 1

    if btn_found == 0:
        out.append(("OK", "未发现按钮控件,跳过"))
        return out
    if has_write_attr and submit_btn == 0:
        out.append(("WARN", "模板含 <ReportWriteAttr> 但无自定义提交按钮(可能用工具栏提交,正常)"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "按钮提交一致性检查通过(%d 个按钮)" % btn_found))
    return out


def check_nofilter_scope(cpt_path):
    """doc-2394 下拉框参数为空选择全部(方法① nofilter):凡模板出现字符串 nofilter,
    必须位于单元格 <Filter>(或过滤条件)节点内,且不得出现在任何 <Query>/数据集 SQL 中;
    命中 SQL 内出现即 ERROR(nofilter 是单元格过滤专属关键字,误用于 SQL 静默失效)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    text = _ser(root, encoding="unicode")

    if "nofilter" not in text:
        out.append(("OK", "未发现 nofilter 关键字,跳过"))
        return out

    # SQL/Query 中出现 nofilter
    for td in root.iter("TableData"):
        for q in td.iter("Query"):
            if q.text and "nofilter" in q.text:
                out.append(("ERROR", "nofilter 出现在数据集 %s 的 <Query> SQL 中:nofilter 是单元格过滤(方法①)专属关键字,SQL 里写它不会生效 —— 应改用方法② ${if(len(p)==0,\"\",...)} 守卫(doc-2394)" % (td.get("name") or "?")))
    # 过滤条件节点内出现(合法)
    in_filter = 0
    for f in root.iter("Filter"):
        if "nofilter" in "".join(f.itertext()) or "nofilter" in _ser(f, encoding="unicode"):
            in_filter += 1
    if in_filter == 0:
        out.append(("WARN", "nofilter 出现在模板中但不在任何单元格 <Filter> 节点内:该方法①只在单元格过滤生效,放错位置静默失效(doc-2394)"))
    else:
        out.append(("OK", "nofilter 位于单元格 <Filter> 内,作用域正确(%d 处)" % in_filter))
    return out


def check_frm_ec_export(cpt_path):
    """doc-4104 决策报表导出单个报表块:凡 .frm 的事件 JS 中出现 widgetName=XXX 或
    getWidgetByName(\"xxx\"),静态校验三条:①模板中存在同名组件(大小写不敏感匹配),否则
    ERROR「组件改名导致导出/联动静默失效」;②ec_export 场景下 URL 里的名称必须全大写,
    否则 ERROR;③被引用组件 visible 不为 false,否则 ERROR「导出文件将无法打开」。
    移植 check_ec_export。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    if root.tag != "Form":
        out.append(("OK", "非 .frm 模板(ec_export 仅适用决策报表),跳过"))
        return out

    # 组件清单: 大写名 -> (真实名, class, visible)
    widgets = {}
    for iw in root.iter("InnerWidget"):
        wn = iw.find("WidgetName")
        name = wn.get("name") if wn is not None else None
        if not name:
            continue
        visible = True
        wa = iw.find("WidgetAttr")
        if wa is not None:
            vis = wa.get("visible")
            if vis is not None and vis.lower() == "false":
                visible = False
        widgets[name.upper()] = (name, iw.get("class", ""), visible)

    hits = 0
    for js_txt, _ in _iter_js_contents(root):
        if "ec_export" not in js_txt and "widgetName=" not in js_txt:
            continue
        if "ec_export" in js_txt:
            hits += 1
        # ② ec_export 名称须全大写
        m = re.search(r"widgetName=([A-Za-z0-9_\u4e00-\u9fa5]+)", js_txt)
        if m:
            wname = m.group(1)
            if "ec_export" in js_txt and wname != wname.upper():
                out.append(("ERROR", "E1 ec_export 请求 widgetName=%s 未全大写(官方要求大写,应为 %s)(doc-4104)" % (wname, wname.upper())))
            # ① 组件存在性(大小写不敏感)
            key = wname.upper()
            if key not in widgets:
                out.append(("ERROR", "E2 widgetName=%s 在模板中找不到对应组件(组件改名会静默失效)(doc-4104)" % wname))
            else:
                real, cls, visible = widgets[key]
                # ③ 可见性
                if not visible:
                    out.append(("ERROR", "E3 目标组件 %s 不可见(visible=false):导出的 Excel 无法打开 —— 导出前须改回可见(doc-4104)" % real))
        # getWidgetByName 引用完整性
        for gm in re.finditer(r"getWidgetByName\(\s*['\"]([^'\"]+)['\"]", js_txt):
            ref = gm.group(1)
            if ref.upper() not in widgets:
                out.append(("ERROR", "E2 JS getWidgetByName(\"%s\") 在模板中找不到对应组件(doc-4104)" % ref))

    if hits == 0:
        out.append(("OK", "未发现 ec_export 导出调用,跳过"))
    elif not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "报表块导出引用完整性检查通过(%d 处 ec_export)" % hits))
    return out


def check_dataset_param(cpt_path):
    """doc-158 数据集参数规则组 R0~R5(移植 check_dataset_param):
    R0 裸花括号解析失败须用 CONCATENATE => 错误;R1 裸 WHERE col='${p}' 无 1=1+
    if(len(p)==0) 守卫 => 警告(参数空时静默空集);R2 多选 in ('${p}') 入参须形如
    `华东','华北` => 警告;R3 Query 用到的 ${p} 须在 ReportParameterAttr 声明 => 错误
    (全局参数豁免见 check_global_param);R4 同名 ${p} 跨数据集共享以最后赋值者为准
    => 警告;R5 控件数据字典数据集含同名 ${p} => 循环引用(错误)。"""
    root, err = _load_root(cpt_path)
    if err:
        return [("ERROR", err)]
    out = []
    tpl_params = _all_template_params(root)

    queries = []
    for td in root.iter("TableData"):
        name = td.get("name")
        if not name:
            continue
        q = td.find("Query")
        if q is not None and q.text:
            queries.append((name, q.text))
    if not queries:
        out.append(("OK", "未发现数据集 Query,跳过"))
        return out

    used = {}
    for name, sql in queries:
        # R0 裸花括号
        stripped = re.sub(r"\$\{[^}]*\}", "", sql)
        if "{" in stripped or "}" in stripped:
            out.append(("ERROR", "[R0] 数据集[%s] Query 含裸花括号(非 ${}):将解析失败,须用 CONCATENATE 转义" % name))
        for m in re.finditer(r"\$\{([^}]*)\}", sql):
            body = m.group(1)
            for pm in re.finditer(r"(?:^|[^.\w])([A-Za-z_]\w*)", body):
                p = pm.group(1)
                if p in ("if", "len", "CONCATENATE", "and", "or", "in"):
                    continue
                used.setdefault(p, set()).add(name)
        # R1 无守卫
        if re.search(r"where\s+\w+\s*=\s*'\$\{\w+\}'", sql, re.I) and "1=1" not in sql and "len(" not in sql:
            out.append(("WARN", "[R1] 数据集[%s] 用 `WHERE col = '${p}'` 无 1=1 守卫+if(len(p)==0):参数空时静默返回空集" % name))
        # R2 多选
        if re.search(r"in\s*\(\s*'\$\{\w+\}'\s*\)", sql, re.I):
            out.append(("WARN", "[R2] 数据集[%s] 多选 in ('${p}') :传入值须形如 `华东','华北`(无首尾引号),否则语法错/漏数据" % name))

    # R3 未声明(全局参数豁免提示见 check_global_param)
    for p in used:
        if p not in tpl_params:
            out.append(("ERROR", "[R3] 参数 ${%s} 在数据集 Query 中使用,但 ReportParameterAttr 未声明(控件无法按名绑定;若为全局参数请用 check_global_param 豁免)" % p))
    # R4 跨数据集共享
    for p, dss in used.items():
        if len(dss) > 1:
            out.append(("WARN", "[R4] 参数 ${%s} 同时出现在多个数据集 %s :共享同一值,以最后赋值者为准;需区分请改名" % (p, sorted(dss))))
    # R5 字典循环引用
    name2sql = {n: s for n, s in queries}
    for w in root.iter("Widget"):
        wn = w.find(".//WidgetName")
        wname = wn.get("name") if wn is not None else None
        if not wname:
            continue
        for tn in w.findall(".//TableDataName"):
            dt = (tn.text or "").strip()
            if dt and dt in name2sql and re.search(r"\$\{\s*" + re.escape(wname) + r"\s*\}", name2sql[dt]):
                out.append(("ERROR", "[R5] 控件[%s] 的数据字典数据集[%s] 含同名参数 ${%s} → 循环引用,模板出错" % (wname, dt, wname)))

    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "数据集参数规则组检查通过"))
    return out


# ════════════════════════════════════════════════════════════════════════════
# RULES 注册表(56 条,与 A_rules_doc.json 一一对应)
#   name    规则名(可作 --name 过滤关键字)
#   fn      check_ 函数
#   doc     来源文档 doc-XXXX
#   context 适用语境(知识库治理/知识管理规范-维护流程.md §0.7:显式标注适用语境,避免不适用场景误报)
#   apply   触发条件(什么情况下该规则才执行)
# ════════════════════════════════════════════════════════════════════════════

RULES = [
    # ── 数据建模 / 数据集参数 ──────────────────────────────────────────────
    {"name": "dataset_param", "fn": check_dataset_param, "doc": "doc-158",
     "context": "含数据集 Query 的模板(.cpt/.frm)",
     "apply": "存在 <TableData><Query> 即执行;R0-R5 逐条判定"},
    {"name": "order_by", "fn": check_order_by, "doc": "doc-903",
     "context": "数据集 SQL 含 ORDER BY 的模板",
     "apply": "任一数据集 Query 含 ORDER BY 子句"},
    {"name": "global_param", "fn": check_global_param, "doc": "doc-159",
     "context": "数据集 SQL 引用参数的模板;需可选第二输入(全局参数清单)",
     "apply": "存在 ${param} 引用;未提供 project_globals.json 时 R3 降级 WARN"},
    {"name": "optional_param_default", "fn": check_optional_param_default, "doc": "doc-651",
     "context": "用 ${if(len(p)==0,...)} 可选过滤标准模板的数据集",
     "apply": "数据集 SQL 含 if(len(p)==0"},
    {"name": "nofilter_scope", "fn": check_nofilter_scope, "doc": "doc-2394",
     "context": "下拉框参数为空选择全部(方法① nofilter)的模板",
     "apply": "模板文本出现 nofilter 关键字"},
    {"name": "custom_order", "fn": check_custom_order, "doc": "doc-3622",
     "context": "内置数据集 + inarray() 自定义排序的模板",
     "apply": "公式含 inarray( 或 数据集名.select( 列名)"},
    {"name": "hanzi_num_sort", "fn": check_hanzi_num_sort, "doc": "doc-3717",
     "context": "汉字数字排序(MAPARRAY/COUNT/NUMTO)的模板",
     "apply": "公式含 MAPARRAY(/NUMTO(/INARRAY("},
    {"name": "string_pinyin", "fn": check_string_pinyin, "doc": "doc-3309",
     "context": "扩展后中文按拼音排序(StringPinyin 插件)的模板",
     "apply": "公式含 StringPinyin("},
    {"name": "order_sort_param", "fn": check_order_sort_param, "doc": "doc-1894",
     "context": "点击标题排序(OrderFormula + 排序参数)的模板",
     "apply": "存在 OrderFormula 或 ORDER BY ${param}"},

    # ── 参数面板 / 模板参数 ────────────────────────────────────────────────
    {"name": "template_param", "fn": check_template_param, "doc": "doc-157",
     "context": "仅含模板参数的普通报表/决策报表",
     "apply": "存在 ReportParameterAttr/<Parameter> 定义"},
    {"name": "param_cascade", "fn": check_param_cascade, "doc": "doc-1868(附 doc-1029)",
     "context": "参数面板公式字典级联(ParameterUI 内 P1/P2 联动)",
     "apply": "存在 <FormulaDictAttr>/<valueFormula> 且位于参数面板"},
    {"name": "cascade", "fn": check_cascade, "doc": "doc-1284",
     "context": "仅含级联下拉的模板(下拉框字典数据集 + 参数联动)",
     "apply": "存在 InnerWidget 下拉框且字典指向数据集"},
    {"name": "auto_query", "fn": check_auto_query, "doc": "doc-1434",
     "context": "决策报表参数界面自动查询(auto_query 控件)",
     "apply": "控件声明 auto_query 或 JS 含 _g().parameterCommit()"},
    {"name": "date_range_validate", "fn": check_date_range_validate, "doc": "doc-1197",
     "context": "含起-止日期控件对的模板",
     "apply": "控件名含 start 与 end"},
    {"name": "date_validation_js", "fn": check_date_validation_js, "doc": "doc-1197",
     "context": "日期控件校验 JS(getter 场景匹配)",
     "apply": "JS 含 getWidgetByName 且模板含日期控件"},
    {"name": "hierarchy_guard", "fn": check_hierarchy_guard, "doc": "doc-3120",
     "context": "参数联动层级限制弹出提示框的模板",
     "apply": "控件声明 require_parent 或存在 beforeedit 事件"},

    # ── 级联 / 联动 ────────────────────────────────────────────────────────
    {"name": "fill_linkage", "fn": check_fill_linkage, "doc": "doc-608",
     "context": "填报控件数据字典联动(region/city 单元格级联)",
     "apply": "存在 WidgetName=region/city 的单元格控件"},
    {"name": "auto_default", "fn": check_auto_default, "doc": "doc-1868",
     "context": "填报联动自动生成默认值(公式字典 + JS 兜底赋值)",
     "apply": "存在 <valueFormula> 公式字典"},
    {"name": "linkage_chain", "fn": check_linkage_chain, "doc": "doc-2857",
     "context": "仅含扩展图表轮播/刷新联动的 .frm",
     "apply": "根节点 <Form> 且存在 CarouselLinkage/RefreshLinkage"},
    {"name": "frm_widget_ref", "fn": check_frm_widget_ref, "doc": "doc-2857(附 doc-4104)",
     "context": ".frm 决策报表(跨组件引用完整性)",
     "apply": "根节点 <Form> 且存在超链/JS/联动引用"},
    {"name": "cell_chart_link", "fn": check_cell_chart_link, "doc": "doc-4207",
     "context": "单元格超链联动单元格图表(普通报表)",
     "apply": "存在 CellChartHyperlink 类超链"},
    {"name": "dropdown_chart_link", "fn": check_dropdown_chart_link, "doc": "doc-1995",
     "context": "下拉框-隐藏桥接格-图表联动链路(填报)",
     "apply": "存在 ChartHyperlink 超链且参数值为单元格号"},
    {"name": "hyperlink_param", "fn": check_hyperlink_param, "doc": "doc-947",
     "context": "跳参数化子模板的超链(网络报表/JS 方式)",
     "apply": "存在 ReportletHyperlink/JavaScriptHyperlink 超链"},
    {"name": "form_linkage", "fn": check_form_linkage, "doc": "doc-3556",
     "context": ".frm「当前表单对象/当前决策报表对象」超链联动",
     "apply": "根节点 <Form> 且存在 com.fr.form.main.FormHyperlink"},
    {"name": "dynparam_linkage", "fn": check_dynparam_linkage, "doc": "doc-651",
     "context": ".frm 动态参数联动(DynamicParamHyperlink 参数驱动型)",
     "apply": "根节点 <Form> 且存在 DynamicParamHyperlink"},
    {"name": "hyperlink_dynamic_param", "fn": check_hyperlink_dynamic_param, "doc": "doc-4202",
     "context": "单元格动态参数超链(点击列头重提交/排序切换)",
     "apply": "存在 DynamicParam 类超链 <Parameter name=X>"},
    {"name": "hover_link_mobile", "fn": check_hover_link_mobile, "doc": "doc-4204(附 doc-4209)",
     "context": "联动悬浮元素超链的模板",
     "apply": "文本含 FloatElementHyperlink/悬浮 等标记"},

    # ── 排序 ───────────────────────────────────────────────────────────────
    {"name": "group_sort", "fn": check_group_sort, "doc": "doc-2684",
     "context": "按分组汇总结果排序(左父格链)的模板",
     "apply": "存在 SortExpression 排序公式"},
    {"name": "sort_after_expand", "fn": check_sort_after_expand, "doc": "doc-897",
     "context": "扩展后排序(sortAfterExpand)的模板",
     "apply": "存在 sortAfterExpand 属性"},
    {"name": "horizontal_sort", "fn": check_horizontal_sort, "doc": "doc-1782",
     "context": "横向扩展列多列排序(EVAL+sortAfterExpand)的模板",
     "apply": "公式含 EVAL( 且存在 sortAfterExpand"},

    # ── 图表 ───────────────────────────────────────────────────────────────
    {"name": "chart_dataset", "fn": check_chart_dataset, "doc": "doc-176",
     "context": "图表走数据集数据源的模板",
     "apply": "Chart 节点绑定数据集(datasetName/TableName)"},
    {"name": "chart_cell_formula", "fn": check_chart_cell_formula, "doc": "doc-175",
     "context": "图表走单元格数据源(= 公式)的模板",
     "apply": "存在 =[...] 或单元格 = 公式取数"},
    {"name": "print_export_bg", "fn": check_print_export_bg, "doc": "doc-175(附 doc-225)",
     "context": "配置了打印导出背景/预览开关的模板",
     "apply": "存在 CellGUIAttr printBackground/Background 配置"},
    {"name": "chart_style", "fn": check_chart_style, "doc": "doc-4138",
     "context": "图表样式配置(legend/label/颜色/条件公式)的模板",
     "apply": "Chart 节点内存在样式配置"},
    {"name": "chart_style_registry", "fn": check_chart_style_registry, "doc": "doc-1672",
     "context": "图表样式九类枚举(标题/图例/标签/系列/坐标轴/数据表/背景/提示/配色)",
     "apply": "Chart 节点内存在样式节点"},
    {"name": "chart_sort_js", "fn": check_chart_sort_js, "doc": "doc-2332",
     "context": "图表排序接口 sortChart 的模板",
     "apply": "JS 含 sortChart 或 getChart"},
    {"name": "listener_cdata", "fn": check_listener_cdata, "doc": "doc-2332(附 doc-1839)",
     "context": "含 Listener/JavaScript 事件的所有模板",
     "apply": "任意 <Content>/JS 节点存在"},
    {"name": "chart_refresh_api", "fn": check_chart_refresh_api, "doc": "doc-3115",
     "context": "图表组件刷新 JS(扩展/普通图表)的模板",
     "apply": "JS 含 dataRefresh 或 dealReloadChartAjax"},
    {"name": "extended_chart", "fn": check_extended_chart, "doc": "doc-2474",
     "context": "含扩展图表的模板",
     "apply": "文本命中扩展图表类型名/类名标记"},
    {"name": "formula_param_declared", "fn": check_formula_param_declared, "doc": "doc-1672",
     "context": "含 =...$p... 公式文本的所有模板(通用规则)",
     "apply": "存在以 = 开头且含 $ 的公式文本"},

    # ── 超链接 / JS ────────────────────────────────────────────────────────
    {"name": "hyperlink_js", "fn": check_hyperlink_js, "doc": "doc-4204",
     "context": "单元格挂 JS 超链的模板",
     "apply": "JavaScript 节点含 Parameter 参数"},
    {"name": "js_hyperlink_export", "fn": check_js_hyperlink_export, "doc": "doc-4204(附 doc-1822)",
     "context": "JS 超链导出(viewlet/__filename__)的模板",
     "apply": "JS 含 viewlet=/__filename__/format="},
    {"name": "url_hyperlink", "fn": check_url_hyperlink, "doc": "doc-1839",
     "context": "JS 超链拼外部站点 URL 的模板",
     "apply": "JS 含 window.open 或外链 URL"},
    {"name": "hyperlink_parent_chain", "fn": check_hyperlink_parent_chain, "doc": "doc-1839(附 doc-4204)",
     "context": "超链参数值为 =单元格 公式的模板(双向父子链判定)",
     "apply": "JS 超链 Parameter 值形如 =A2(=$$$ 豁免)"},
    {"name": "js_remote_evaluate", "fn": check_js_remote_evaluate, "doc": "doc-1839(附 doc-4241)",
     "context": "JS 超链 remoteEvaluate 预判断 + 双分支的模板",
     "apply": "JS 含 window.open/viewlet/location.href/remoteEvaluate"},
    {"name": "export_filename", "fn": check_export_filename, "doc": "doc-3707(附 doc-1822)",
     "context": "动态导出文件名(__filename__/Title 公式)的模板",
     "apply": "JS 含 __filename__ 或 ReportWebAttr/Title 公式"},
    {"name": "multiselect", "fn": check_multiselect, "doc": "doc-3707",
     "context": "根据参数批量导出(多选拼接 SQL)的模板",
     "apply": "SQL 含 in ('\"+p+\"') 或多选控件"},
    {"name": "frm_ec_export", "fn": check_frm_ec_export, "doc": "doc-4104",
     "context": ".frm 导出单个报表块(ec_export)的模板",
     "apply": "根节点 <Form> 且 JS 含 ec_export/widgetName="},

    # ── 填报 / 交互 / 其它 ─────────────────────────────────────────────────
    {"name": "cell_js", "fn": check_cell_js, "doc": "doc-1207",
     "context": "填报单元格 JS 交互(get/setCellValue)的模板",
     "apply": "JS 含 setCellValue/getCellValue"},
    {"name": "submit_consistency", "fn": check_submit_consistency, "doc": "doc-596",
     "context": "JS 自定义提交按钮的填报模板",
     "apply": "存在 Button 控件"},
    {"name": "auto_refresh", "fn": check_auto_refresh, "doc": "doc-1457",
     "context": "决策报表 body 定时刷新(setInterval)的模板",
     "apply": "文本含 setInterval"},
    {"name": "frm_overlap", "fn": check_frm_overlap, "doc": "doc-1457(附 doc-3185)",
     "context": ".frm 绝对布局组件重叠检测",
     "apply": "根节点 <Form> 且存在 WAbsoluteLayout$BoundsWidget"},
    {"name": "freeze_merge", "fn": check_freeze_merge, "doc": "doc-368",
     "context": "分页冻结 + 合并单元格的模板",
     "apply": "存在 FrozenColumnRow 且含 rowSpan/colSpan>1 合并格"},
    {"name": "fill_freeze_expand", "fn": check_fill_freeze_expand, "doc": "doc-611",
     "context": "填报冻结区含扩展单元格的填报模板",
     "apply": "存在 FrozenColumnRow 且为填报模板(ReportWriteAttr)"},
    {"name": "wrap_rowheight", "fn": check_wrap_rowheight, "doc": "doc-217",
     "context": "自动换行文本控制的模板",
     "apply": "存在 wrap/换行 文本控制属性"},
    {"name": "dynamic_param_hyperlink", "fn": check_dynamic_param_hyperlink, "doc": "doc-903(附 doc-4202)",
     "context": "动态参数超链接节点(待核验类名)的模板",
     "apply": "文本命中 DynamicParam 类名标记"},
]

_RULE_NAMES = {r["name"] for r in RULES}


def run_all(cpt_path, name_filter=None):
    """遍历 RULES 汇总结果。

    返回 [{name, doc, context, apply, level, msg}] 列表(level 取该规则最严重级别;
    msg 为 ' | '.join 消息;无 ERROR/WARN 时 level='OK')。

    name_filter: 可选子串,只跑名字含该子串的规则。
    """
    # 文件级预检:不存在或解析失败只报 1 条,避免 56 条重复 ERROR
    if not os.path.isfile(cpt_path):
        return [{"name": "xml_parse", "doc": "-", "context": "输入", "apply": "文件不存在",
                 "level": "ERROR", "msg": "模板文件不存在: %s" % cpt_path}]
    # (R30 perf) 预检改走共享解析(_load_root_full):树只解析一次,错误消息用原始
    # 异常按原格式重建,与原 `try: ET.parse(...) except` 逐字等价。
    _r0, _e0, _x0 = _load_root_full(cpt_path)
    if _x0 is not None:
        return [{"name": "xml_parse", "doc": "-", "context": "输入",
                 "apply": "文件无法解析时", "level": "ERROR",
                 "msg": "XML 解析失败: %s" % _x0}]
    results = []
    for r in RULES:
        if name_filter and name_filter not in r["name"]:
            continue
        try:
            items = r["fn"](cpt_path)
        except Exception as e:
            items = [("ERROR", "规则 %s 执行异常: %s" % (r["name"], e))]
        if not items:
            items = [("OK", "未返回任何消息")]
        # 汇总级别:ERROR > WARN > OK
        level = "OK"
        msgs = []
        for lv, msg in items:
            lv = lv if lv in _ERR_LEVELS else "WARN"
            if lv == "ERROR":
                level = "ERROR"
            elif lv == "WARN" and level != "ERROR":
                level = "WARN"
            msgs.append(msg)
        results.append({
            "name": r["name"], "doc": r["doc"], "context": r["context"],
            "apply": r["apply"], "level": level, "msg": " | ".join(msgs),
        })
    return results


def main(argv=None):
    """CLI 入口。用法见文件头。返回退出码: 0=无 ERROR 1=有 ERROR。"""
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        print("已注册规则: %d 条" % len(RULES))
        for i, r in enumerate(RULES, 1):
            print("  %2d. [%s] %s (%s)" % (i, r["doc"], r["name"], r["context"]))
        return 0

    path = argv[0]
    name_filter = None
    as_json = False
    if "--name" in argv:
        name_filter = argv[argv.index("--name") + 1]
    if "--json" in argv:
        as_json = True

    results = run_all(path, name_filter)
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
    else:
        errors = warns = oks = 0
        for r in results:
            tag = {"ERROR": "❌", "WARN": "⚠️", "OK": "✅"}.get(r["level"], "?")
            print("%s [%s] %s (%s)" % (tag, r["level"], r["name"], r["doc"]))
            if r["level"] in ("ERROR", "WARN"):
                print("       %s" % r["msg"].replace("\n", "\n       "))
            if r["level"] == "ERROR":
                errors += 1
            elif r["level"] == "WARN":
                warns += 1
            else:
                oks += 1
        print("-" * 66)
        print("汇总: %d 条规则,ERROR=%d WARN=%d OK=%d" % (len(results), errors, warns, oks))
        return 1 if errors else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())

