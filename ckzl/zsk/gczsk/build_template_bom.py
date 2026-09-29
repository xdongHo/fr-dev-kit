# -*- coding: utf-8 -*-
"""模板构件 BOM 构建工具：从夜战 campaign/rebuild 产物提实体+关系 → template_bom.sqlite
背景(CAR-014 / R-0002): 旧 api_kb.sqlite bom 表 99% 是 METHOD_OF 归属, 已判沉睡;
本脚本用「模板域活数据」重造其 装配查询+高频统计 职能 —— 数据直接来自真实模板产物 ET 解析。

v2 (2026-09-15, 夜间批次/A7 SOP-0904): 接入 H3 悬挂分类器(LDAN1/2 人工分诊实证判据)
  - dangling 表加 classification/basis 列(R0陈旧/R1笔误/R2真缺失/R3良性·运行时/R4误报·生成链注入)
  - 宏提取改嵌套感知+引号内剔除+函数名剔除(token_roles), 压 R4 提取误报
  - 收数据集级参数盲区(TableData* 下 <Parameter name=..> 属性形态)
  - meta 增 built_at/staleness_rule(固定库口径) + reports 增 src_mtime, 供 R0-陈旧事后判别
  - 新增 --out <path>: 重建产物可写他处(默认仍为 ckzl/zsk/gczsk/template_bom.sqlite)

实体:
  report   模板(seq 即 rebuild/<seq>.cpt|frm, project 由 campaign/pool.tsv 推导)
  dataset  数据集(name + 连接 + 类型 DBTableData/NameTableData/Embedded...)
  param    参数(name + 默认值)
  widget   控件(name + 类型类名; 含参数面板/frm 画布/内嵌报表块/图表块)
  cell     单元格(坐标 A1 态 + 绑定 dsName/columnName 或公式)
  chart    图表(类型 Plot 短名 + 绑定数据集)
关系:
  report  -USES->        dataset
  report  -HAS->         param
  widget  -BINDS->       param      (控件名 == 参数名, FR 命名约定)
  cell    -BINDS->       dataset    (DSColumn dsName / 公式 value("ds",..))
  chart   -USES->        dataset    (MoreNameCDDefinition TableData Name)
  dataset -REFERENCES->  param      (SQL ${p_xxx} 宏)

抽样: --every N 每第 N 个文件 + 全量图表件(默认 every=8, 约 570 件, 覆盖主要形态即可, 原型验证优先)
用法:
  python build_template_bom.py                # 默认抽样建库
  python build_template_bom.py --every 4     # 更密抽样
  python build_template_bom.py --all          # 全量 4593 件(慢)
  python build_template_bom.py --stats        # 只打印统计不建库
"""
import ast
import os
import re
import sys
import glob
import time
import sqlite3
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "template_bom.sqlite")
ROOT = os.path.dirname(BASE)
REBUILD = os.path.join(ROOT, "_runs", "night", "campaign", "rebuild")
POOL = os.path.join(ROOT, "_runs", "night", "campaign", "pool.tsv")
FRAG_DIR = os.path.join(ROOT, "_runs", "night", "campaign", "_b5")  # 生成链 frag spec

MACRO_RE = re.compile(r"\$\{([^}]*)\}")                      # (v2 仅注释留存) 旧粗提取正则
MACRO_ID_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
VALUE_DS_RE = re.compile(r'value\(\s*"([^"]+)"')             # 公式 value("ds", ...)
COLROW_RE = re.compile(r"^[A-Z]+[0-9]+$")
SQL_KW = {"if", "len", "eq", "and", "or", "not", "switch", "find", "format", "sum",
          "in", "on", "as", "by", "case", "when", "then", "else", "end", "select",
          "where", "from", "null", "true", "false", "like", "distinct", "between",
          "is", "left", "right", "join", "union", "all", "group", "order", "desc",
          "asc", "having", "limit", "sql", "value", "p", "colcount", "rowcount"}
DS_CELLDATA_RE = re.compile(r"^ds_c\d+$")                    # FR 图表「单元格数据」内部源(良性)

INPUT_CTRL_EXCL = ("Label", "Button", "container", "WTitle", "Tab", "MobileBookMark")

# ---- v2 悬挂分类器(H3_classify.py 判据接入, 2026-09-15 SOP-0904 A7) --------------
# R0=BOM陈旧(构建后产物已变) R1=笔误/半改名 R2=真缺失 R3=良性/运行时宏 R4=提取误报/生成链注入
RUNTIME = {
    "fine_username", "fine_password", "fine_role", "fine_display_name", "fine_email",
    "fine_mobile", "fine_employee_number", "fine_company_id", "fine_company_name",
    "fine_department_id", "fine_department_name", "fine_position_id", "fine_position_name",
    "fine_post_id", "fine_post_name", "fr_locale", "fr_locale_name", "fr_sessionid",
    "sessionid", "session_id", "op", "bde_locked", "fr_isroot", "fr_authority",
    "fine_custom_no", "currentuser", "current_user", "userid", "user_id",
    "fr_pagenumber", "fr_rowcount", "fr_pageindex", "fr_viewindex", "fr_currentpage",
}
RUNTIME_PREFIX = ("fine_custom_",)
# ${if(...)} 公式片段残余函数名/字面量(SQL_KW 未覆盖部分)
FUNC_LIKE = {
    "concat", "mid", "upper", "lower", "trim", "now", "today", "isnull", "round",
    "replace", "count", "abs", "tabledatafilter", "map", "index", "joinarray",
    "split", "sub", "add", "daysbetween",
}
REF_FILTER_KW = {k.lower() for k in SQL_KW} | {k.lower() for k in FUNC_LIKE}
MACRO_BLOCK_NESTED_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_\u4e00-\u9fff]*")  # FR 公式允许中文参数名


def find_blocks(sql):
    """括号深度扫描 ${...} 块, 支持嵌套(如 ${if(sql("..","..${u}..")>0,..)});
    旧版 [^}] 截断正则会把嵌套宏切成碎片 token(如 'u'/'erson_gid'), 是 R4 误报主源之一"""
    out, i, n = [], 0, len(sql or "")
    while i < n - 1:
        if sql[i] == "$" and sql[i + 1] == "{":
            depth, j = 1, i + 2
            while j < n and depth:
                if sql[j] == "{":
                    depth += 1
                elif sql[j] == "}":
                    depth -= 1
                j += 1
            out.append(sql[i + 2:j - 1] if depth == 0 else sql[i + 2:j])
            i = j
        else:
            i += 1
    return out


def strip_quoted(body):
    """FR 公式语义: ${...} 内 '...'/"..." 是 SQL 字面量, 引号内标识符不是参数引用"""
    return re.sub(r"'[^']*'|\"[^\"]*\"", " ", body)


def token_roles(sql):
    """对每个 ${...} 块(嵌套感知)内 token 判定角色:
    ('func',名) 函数调用名 / ('ref',名) 参数引用位(引号外, 允许中文参数名);
    内层 ${ident} 视为 ref(嵌套宏属于上层公式求值)"""
    funcs, refs = set(), set()
    for body in find_blocks(sql):
        st = strip_quoted(body)
        for t in MACRO_BLOCK_NESTED_TOKEN.finditer(st):
            name = t.group(0)
            rest = st[t.end():].lstrip()
            if rest.startswith("("):
                funcs.add(name)
            else:
                refs.add(name)
        for inner in re.finditer(r"\$\{([^{}]*)\}", body):
            # v2.1: 仅当内层宏整体是一个标识符(${p_x})才视为参数引用;
            # 多 token 内层(如生成器残留 ${Mfg Sub Group})会产生碎片噪声, 不收
            core = inner.group(1).strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_\u4e00-\u9fff]*", core):
                refs.add(core)
    return funcs, refs


def parse_sql_macros(sql):
    """SQL 文本里的 ${...} 宏 → 真实参数引用位(v2: 嵌套感知+引号内剔除+函数名剔除, 压 R4 提取误报)"""
    _funcs, refs = token_roles(sql)
    return {r for r in refs if r.lower() not in REF_FILTER_KW}


def load_frag_names():
    """生成链 frag spec 数据集名(_b5/_frag_*.xml 内 NameTableData <Name>), 供 R4-生成链注入判别"""
    names = set()
    try:
        for f in glob.glob(os.path.join(FRAG_DIR, "_frag_*.xml")):
            txt = open(f, encoding="utf-8", errors="ignore").read()
            for m in re.finditer(r"<TableData[^>]*>\s*<Name>\s*(?:<!\[CDATA\[)?([^\]<]+)", txt):
                names.add(m.group(1).strip())
    except OSError:
        pass
    return names


FRAG_NAMES = load_frag_names()


def load_projects():
    """seq -> project (campaign/pool.tsv 第 1/3 列)"""
    proj = {}
    try:
        with open(POOL, encoding="utf-8", errors="ignore") as f:
            next(f)
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 3 and p[0].isdigit():
                    proj[int(p[0])] = p[2]
    except OSError:
        pass
    return proj


def short_cls(cls):
    """com.fr.form.ui.ComboBox -> ComboBox"""
    if not cls:
        return ""
    return cls.split("$")[-1].split(".")[-1]


def cell_pos(c, r):
    """0 基 c/r -> A1 态坐标"""
    s, c0 = "", (int(c) if c is not None else 0)
    while True:
        s = chr(65 + c0 % 26) + s
        c0 = c0 // 26 - 1
        if c0 < 0:
            return s + str((int(r) if r is not None else 0) + 1)


def parse_sql_macros(sql):
    """SQL 文本里的 ${...} 宏 → 候选参数标识符(剔除 SQL 关键字/函数名)"""
    ids = set()
    for m in MACRO_RE.finditer(sql or ""):
        ids.update(MACRO_ID_RE.findall(m.group(1)))
    return {i for i in ids if i.lower() not in SQL_KW}


def clean_name(name):
    """产物源件偶有生成器残留(如 name="('p_sub_bu', '')"), 还原为真名"""
    if name and name.startswith("('") and name.endswith("')"):
        try:
            v = ast.literal_eval(name)
            if isinstance(v, tuple) and v and isinstance(v[0], str):
                return v[0]
        except (ValueError, SyntaxError):
            pass
    return name


# ---- v2 悬挂分类判据(移植 _runs/night/R71_h/H3_classify.py, LDAN1/2 人工分诊实证) ----
def near_match(macro, declared):
    """近声明判定: 大小写差 / p_前缀差 / 尾部2冗余(生成器变体) / 后缀近似"""
    ml = macro.lower()
    for d in declared:
        dl = d.lower()
        if ml == dl:
            return d, "大小写差"
        if ("p_" + macro) == d or macro == ("p_" + d):
            return d, "p_前缀差"
        if ("p_" + ml) == dl or ml == ("p_" + dl):
            return d, "p_前缀差(忽略大小写)"
        if macro == d + "2" or macro == d + "22":
            return d, "尾部2冗余(生成器变体残留)"
        if len(d) >= 4 and macro.endswith("_" + d):
            return d, "后缀近似(疑参数改名后SQL未同步)"
    return None, None


def all_commented(macro, sqls):
    """宏在SQL中的出现是否全部位于 -- 注释行内"""
    total = commented = 0
    for s in sqls:
        for line in s.split("\n"):
            for pos in [m.start() for m in re.finditer(r"(?<![A-Za-z0-9_])" +
                                                       re.escape(macro) +
                                                       r"(?![A-Za-z0-9_])", line)]:
                total += 1
                if "--" in line[:pos]:
                    commented += 1
    return total > 0 and total == commented


def nonascii_fragment(macro, sqls):
    """宏是否为中文参数名的 ASCII 前缀切片(如 YFAS ⊂ YFAS客户代码)"""
    pat = re.compile(re.escape(macro) + r"[^\x00-\x7f]")
    for s in sqls:
        if pat.search(s):
            return True
    return False


def is_runtime(name):
    return name.lower() in RUNTIME or name.lower().startswith(RUNTIME_PREFIX)


class TemplateParser:
    """解析一个 cpt/frm 产物 → 实体行 + 关系行"""

    def __init__(self, seq, path, project):
        self.seq, self.path, self.project = seq, path, project
        self.kind = "frm" if path.lower().endswith(".frm") else "cpt"
        self.datasets = {}     # name -> (conn, cls)
        self.params = {}       # name -> default (模板级声明)
        self.ds_params = set() # 数据集级 <TableData><Parameters><Parameter name=..>(v2 新收, 旧版盲区)
        self.widgets = []      # (name, cls, scope root/para/body)
        self.cells = []        # (pos, ds, col, formula, scope)
        self.charts = []       # (name, type, ds)
        self.edges = []        # (src_kind, src, rel, dst_kind, dst, detail)
        self.macros = set()    # dataset sql 里引用的参数候选
        self.sql_texts = []    # 数据集 SQL 原文(供注释行/中文切片/1=1兜底 判据)

    # ---- 顶层入口 -------------------------------------------------------
    def parse(self):
        try:
            root = ET.parse(self.path).getroot()
        except Exception as e:
            self.error = str(e)[:120]
            return False
        self.error = ""
        self._datasets(root)
        self._params(root)
        self._widgets(root)
        self._reports(root)
        self._charts(root)
        self._wire()
        return True

    # ---- 实体提取 -------------------------------------------------------
    def _datasets(self, root):
        for tdm in root.iter("TableDataMap"):
            for td in tdm:
                name = td.get("name", "")
                cls = td.get("class", "")
                conn = ""
                q = td.find("Query")
                if q is not None:
                    conn = q.get("databaseName") or q.get("connection") or ""
                    for a in q.iter("Attribute"):
                        conn = conn or a.get("databaseName", "")
                    if (q.text or "").strip():
                        self.sql_texts.append(q.text)
                    self.macros |= parse_sql_macros(q.text or "")
                    # Connection 名在 <Query databaseName=...> 或同层 <Connection>
                for cc in td.iter("Connection"):
                    conn = conn or cc.get("name", "")
                self.datasets[name] = (conn, short_cls(cls))

    def _params(self, root):
        # v2: 先收数据集级参数(<TableData*><Parameters><Parameter name=..> 属性形态,
        # 旧版只读 Attributes.name 且不区分层级 → R4-BOM盲区误报源)
        ds_ps_ids = set()
        for td in root.iter():
            if not td.tag.endswith("TableData"):
                continue
            for ps in td.iter("Parameters"):
                ds_ps_ids.add(id(ps))
                for p in ps:
                    if p.tag != "Parameter":
                        continue
                    nm = clean_name(p.get("name"))
                    if not nm:                     # Attributes 形态(与 H3_classify 双通道一致)
                        at = p.find("Attributes")
                        nm = clean_name(at.get("name")) if at is not None else None
                    if nm:
                        self.ds_params.add(nm)
        for ps in root.iter("Parameters"):
            if id(ps) in ds_ps_ids:            # 数据集级已单独收, 防混入模板级
                continue
            for p in ps:
                if p.tag != "Parameter":
                    continue
                at = p.find("Attributes")
                name = clean_name(at.get("name")) if at is not None else None
                if not name:                   # v2: 属性形态 <Parameter name=".."> 兜底
                    name = clean_name(p.get("name"))
                if not name:
                    continue
                default = ""
                for o in p.iter("O"):
                    default = (o.text or "").strip()[:80]
                    break
                self.params[name] = default

    @staticmethod
    def _widget_name(w):
        for wn in w.iter("WidgetName"):
            return wn.get("name", "")
        return ""

    def _widgets(self, root):
        # 参数面板(scope=para) + frm 画布/工具栏(scope=body)
        para_ids = set()
        for ui in root.iter("ParameterUI"):
            para_ids |= {id(e) for e in ui.iter()}
            for w in ui.iter("Widget"):
                inner = w.find("InnerWidget")      # BoundsWidget 包装: 真控件在内层
                if inner is not None:
                    self._add_widget(inner, "para")
                else:
                    self._add_widget(w, "para")
        for tag in ("Widget", "InnerWidget"):
            for w in root.iter(tag):
                if id(w) in para_ids:              # 参数面板已单独收, 防重复
                    continue
                cls = w.get("class", "")
                if "Bounds" in cls:                # 容器包装: 真控件在 InnerWidget
                    continue
                self._add_widget(w, "body")

    def _add_widget(self, w, scope):
        cls = w.get("class", "")
        short = short_cls(cls)
        if not short:
            return
        self.widgets.append((clean_name(self._widget_name(w)), short, scope))

    def _reports(self, root):
        # 顶层 Report(cpt 主体) + frm 内嵌 ElementCaseEditor 里的 Report
        reps = root.findall("Report") or root.findall(".//Report")
        for rep in reps:
            scope = "body"
            for cel in rep.iter("CellElementList"):
                for c in cel.findall("C"):
                    pos = cell_pos(c.get("c"), c.get("r"))
                    o = c.find("O")
                    ds = col = formula = ""
                    if o is not None:
                        if o.get("t") == "DSColumn":
                            at = o.find("Attributes")
                            if at is not None:
                                ds = at.get("dsName", "")
                                col = at.get("columnName", "")
                        elif o.get("t") == "XMLable" and "Formula" in (o.get("class") or ""):
                            at = o.find("Attributes")
                            if at is not None and at.text:
                                formula = (at.text or "").strip()[:160]
                                m = VALUE_DS_RE.search(formula)
                                if m:
                                    ds = m.group(1)
                    if ds:
                        self.cells.append((pos, ds, col, formula, scope))

    def _charts(self, root):
        for i, ch in enumerate(root.iter("Chart")):
            ctype = ""
            for plot in ch.iter("Plot"):           # Plot 常嵌在内层 Chart 里
                ctype = short_cls(plot.get("class", ""))
                break
            if not ctype:
                ctype = short_cls(ch.get("chartClass", ""))
            ds = ""
            for td in ch.iter("TableData"):
                nm = td.find("Name")
                if nm is not None and nm.text:
                    ds = nm.text.strip()
                    break
            self.charts.append((f"{ch.get('name', '默认')}#{i}", ctype, ds))

    # ---- 关系装配 -------------------------------------------------------
    def _wire(self):
        rid = f"{self.seq}"
        for name, (conn, cls) in self.datasets.items():
            self.edges.append(("report", rid, "USES", "dataset", name,
                               f"{cls}|{conn}"))
        for name in self.params:
            self.edges.append(("report", rid, "HAS", "param", name, ""))
        for nm, cls, _scope in self.widgets:
            if nm and nm in self.params and not any(x in cls for x in INPUT_CTRL_EXCL):
                self.edges.append(("widget", nm, "BINDS", "param", nm,
                                   f"{self.seq}|{cls}"))
        for pos, ds, col, _f, _s in self.cells:
            self.edges.append(("cell", f"{self.seq}!{pos}", "BINDS", "dataset", ds,
                               col or "-"))
        for n, _t, ds in self.charts:
            if ds:
                self.edges.append(("chart", f"{self.seq}:{n}", "USES", "dataset", ds,
                                   "chart"))
        for m in self.macros:
            self.edges.append(("dataset", "*", "REFERENCES", "param", m, str(self.seq)))

    def dangling(self):
        """悬挂引用 + v2 分类: (类型, 引用方, 目标, classification, basis)
        classification 口径(承 LDAN1/2 人工分诊): R0-BOM陈旧 / R1-笔误半改名 / R2-真缺失 /
        R3-良性·运行时宏 / R4-提取误报·生成链注入 / R9-解析失败
        注: 本库为构建时点快照(同刻解析), R0 天然不落库; 陈旧判别走 meta.built_at + reports.src_mtime
        """
        out = []
        ds_names = set(self.datasets)
        declared_all = set(self.params) | self.ds_params
        for pos, ds, col, _f, _s in self.cells:
            if ds and ds not in ds_names:
                cls, basis = self._cls_ds_ref(ds)
                out.append(("cell->dataset", f"{self.seq}!{pos}", ds, cls, basis))
        for _n, _t, ds in self.charts:
            if ds and ds not in ds_names:
                typ = "chart->dataset[ds_cN·良性]" if DS_CELLDATA_RE.match(ds) \
                    else "chart->dataset"
                cls, basis = self._cls_ds_ref(ds)
                out.append((typ, self.seq, ds, cls, basis))
        for nm, cls_, scope in self.widgets:
            if (scope == "para" and nm and not any(x in cls_ for x in INPUT_CTRL_EXCL)
                    and nm not in self.params):
                if nm in self.ds_params:
                    c, b = "R4", ("BOM盲区已修: 控件名命中数据集级参数声明, "
                                  "控件-参数约定成立(旧版只读模板级 Attributes.name 漏收)")
                elif is_runtime(nm):
                    c, b = "R3", "FR运行时注入宏作控件名(登录态/会话), 非模板声明职责"
                else:
                    d, why = near_match(nm, declared_all)
                    if d:
                        c, b = "R1", f"笔误/半改名: 近声明存在 {d} ({why})"
                    else:
                        c, b = "R2", "死引用: 面板控件无同名声明参数(不进SQL/不拦值, 仅展示)"
                out.append(("widget->param", f"{self.seq}|{nm}", "-", c, b))
        for m in self.macros:
            if m not in self.params:
                c, b = self._cls_macro(m, declared_all)
                out.append(("sql->param", f"{self.seq}:${{{m}}}", m, c, b))
        return out

    def _cls_macro(self, m, declared_all):
        """sql->param 悬挂宏分类(H3 四型判据按序求值)"""
        if m in self.ds_params:
            return "R4", ("BOM盲区已修: 宏由数据集级<Parameter name=..>声明覆盖"
                          "(旧版建库只读模板级 Attributes.name 漏收)")
        if is_runtime(m):
            return "R3", "FR运行时注入宏(登录态/会话/内置公式变量), 非模板声明职责"
        if all_commented(m, self.sql_texts):
            return "R4", "BOM噪声: 宏出现全部位于SQL注释(--)内, 无运行时影响"
        if nonascii_fragment(m, self.sql_texts):
            return "R4", "BOM噪声: 中文参数名ASCII切片(提取正则不含中文)"
        d, why = near_match(m, declared_all)
        if d:
            return "R1", f"笔误/半改名: 近声明存在 {d} ({why})"
        fallback = any("1=1" in s for s in self.sql_texts)
        tail = ("SQL含1=1兜底→条件静默丢失(全表)" if fallback
                else "SQL无1=1兜底→FR空串替换后语法报错")
        return "R2", f"真引用位且无任何来源(非声明/非数据集级/非运行时/非注释); {tail}"

    def _cls_ds_ref(self, ds):
        """chart/cell ->dataset 悬挂绑定分类"""
        if DS_CELLDATA_RE.match(ds):
            return "R3", "良性: FR图表「单元格数据」运行时内部源ds_cN"
        if ds in FRAG_NAMES:
            return "R4", ("生成链注入: 目标∈_b5/_frag_*.xml spec 名"
                          "(_b2auto 对 frag 盲注默认绑定), 非模板声明缺陷")
        return "R2", "绑定引用位指向未建数据集(DSColumn/图表活绑定), 真缺失"


# ---------------------------------------------------------------- 建库
SCHEMA = """
DROP TABLE IF EXISTS nodes;   DROP TABLE IF EXISTS edges;
DROP TABLE IF EXISTS reports; DROP TABLE IF EXISTS meta;
CREATE TABLE nodes(
  id INTEGER PRIMARY KEY, kind TEXT, name TEXT, subkind TEXT,
  project TEXT, freq INTEGER DEFAULT 0, attrs TEXT);
CREATE TABLE edges(
  id INTEGER PRIMARY KEY, seq INTEGER, project TEXT,
  src_kind TEXT, src TEXT, rel TEXT, dst_kind TEXT, dst TEXT, detail TEXT);
CREATE TABLE reports(
  seq INTEGER PRIMARY KEY, kind TEXT, project TEXT, path TEXT,
  n_ds INTEGER, n_param INTEGER, n_widget INTEGER, n_cell INTEGER, n_chart INTEGER,
  error TEXT, src_mtime TEXT);
CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
CREATE INDEX idx_nodes_kind ON nodes(kind,name);
CREATE INDEX idx_edges_src  ON edges(src);
CREATE INDEX idx_edges_dst  ON edges(dst);
CREATE INDEX idx_edges_rel  ON edges(rel);
CREATE INDEX idx_edges_proj ON edges(project);
"""


def pick_files(every, all_files):
    # v2: 只收纯数字序名(seq 命名空间); 后入 corpus 的 NOSEQ_* 等命名件不属 BOM seq 体系
    files = [p for p in glob.glob(os.path.join(REBUILD, "*.cpt")) +
             glob.glob(os.path.join(REBUILD, "*.frm"))
             if os.path.splitext(os.path.basename(p))[0].isdigit()]
    files.sort(key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    if all_files:
        return files
    picked = set(files[::every])
    # 图表件全收(形态稀缺, 保证 chart-USES-dataset 有样本)
    for f in files:
        try:
            head = open(f, encoding="utf-8", errors="ignore").read(20000)
        except OSError:
            continue
        if "ChartCollection" in head:
            picked.add(f)
    return sorted(picked, key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))


def build(every=8, all_files=False, out=DB):
    proj = load_projects()
    files = pick_files(every, all_files)
    conn = sqlite3.connect(out)
    conn.executescript(SCHEMA)
    freq = {}                     # (kind,name/subkind) -> count
    node_rows, edge_rows, rep_rows, dang_rows = [], [], [], []
    for path in files:
        seq = int(os.path.splitext(os.path.basename(path))[0])
        tp = TemplateParser(seq, path, proj.get(seq, "未知"))
        ok = tp.parse()
        try:
            mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
        except OSError:
            mt = ""
        rep_rows.append((seq, tp.kind, tp.project, os.path.basename(path),
                         len(tp.datasets), len(tp.params), len(tp.widgets),
                         len(tp.cells), len(tp.charts), tp.error, mt))
        if not ok:
            dang_rows.append((seq, tp.project, "parse-error", tp.path, tp.error,
                              "R9-解析失败", "rebuild 产物 XML 解析失败(生成器产物损坏), 非模板语义缺陷"))
            continue
        # nodes: report 1 行 + dataset/param/widget/chart
        node_rows.append((None, "report", str(seq), tp.kind, tp.project, 1,
                          os.path.basename(path)))
        freq[("report", str(seq))] = 1
        for name, (cn, cls) in tp.datasets.items():
            node_rows.append((None, "dataset", name, cls, tp.project, 0, cn))
            freq[("dataset", name)] = freq.get(("dataset", name), 0) + 1
        for name, dft in tp.params.items():
            node_rows.append((None, "param", name, "", tp.project, 0, dft))
            freq[("param", name)] = freq.get(("param", name), 0) + 1
        for nm, cls, _s in tp.widgets:
            if not nm:
                nm = f"__anon_{cls}"
            node_rows.append((None, "widget", nm, cls, tp.project, 0, ""))
            freq[("widget", cls)] = freq.get(("widget", cls), 0) + 1
        for pos, ds, col, fml, _s in tp.cells:
            node_rows.append((None, "cell", f"{seq}!{pos}", "", tp.project, 0,
                              f"{ds}.{col}" if col else (fml or "")))
        for n, t, ds in tp.charts:
            node_rows.append((None, "chart", f"{seq}:{n}", t, tp.project, 0, ds))
            key = t or "Unknown"
            freq[("chart", key)] = freq.get(("chart", key), 0) + 1
        for sk, src, rel, dk, dst, det in tp.edges:
            edge_rows.append((seq, tp.project, sk, src, rel, dk, dst, det))
        for typ, who, tgt, cls, basis in tp.dangling():
            dang_rows.append((seq, tp.project, typ, who, tgt, cls, basis))
    # freq 回填 + 去重 dataset/param/widget 节点(全库唯一, project 记首次出现)
    seen, uniq = set(), []
    for row in node_rows:
        _n, kind, name, sub, projn, _f, attrs = row
        key = (kind, name)
        if key in seen and kind != "report":
            continue
        seen.add(key)
        uniq.append((None, kind, name, sub, projn,
                     freq.get((kind if kind != "widget" else "widget",
                              name if kind != "widget" else sub), 0), attrs))
    conn.executemany("INSERT INTO nodes(kind,name,subkind,project,freq,attrs) "
                     "VALUES(?,?,?,?,?,?)",
                     [r[1:] for r in uniq])
    conn.executemany("INSERT INTO edges(seq,project,src_kind,src,rel,dst_kind,dst,detail) "
                     "VALUES(?,?,?,?,?,?,?,?)", edge_rows)
    conn.executemany("INSERT INTO reports VALUES(?,?,?,?,?,?,?,?,?,?,?)", rep_rows)
    conn.executescript("""
      DROP TABLE IF EXISTS dangling;
      CREATE TABLE dangling(seq INTEGER, project TEXT, typ TEXT, who TEXT, target TEXT,
        classification TEXT, basis TEXT);
    """)
    conn.executemany("INSERT INTO dangling VALUES(?,?,?,?,?,?,?)", dang_rows)
    n_reports = len(rep_rows)
    cls_stat = {}
    for r in dang_rows:
        c = r[5]
        cls_stat[c] = cls_stat.get(c, 0) + 1
    conn.executemany("INSERT INTO meta VALUES(?,?)", [
        ("built", "build_template_bom.py v2(SOP-0904 A7: 接H3悬挂分类器)"),
        ("built_at", time.strftime("%Y-%m-%d %H:%M:%S")),
        ("source", "campaign/rebuild 产物 ET 解析"),
        ("sample", f"every={every}" + ("+ALL" if all_files else "")),
        ("reports", str(n_reports)),
        ("edges", str(len(edge_rows))),
        ("dangling", str(len(dang_rows) - sum(1 for r in rep_rows if r[9]))),
        ("dangling_classification", ";".join(f"{k}={v}" for k, v in sorted(cls_stat.items()))),
        ("staleness_rule",
         "固定库口径: 本库为 built_at 时点 corpus(rebuild/)只读快照; 产物 mtime 或 "
         "reports.src_mtime 晚于 built_at → 该模板内容可能已更新, 其 dangling 行须重估"
         "(R0-BOM陈旧 不落库, 由本字段+src_mtime 事后判别)"),
        ("classifier", "R0-BOM陈旧/R1-笔误半改名/R2-真缺失/R3-良性·运行时宏/"
                       "R4-提取误报·生成链注入/R9-解析失败; 判据=H3_classify.py(LDAN1/2 实证)"),
    ])
    conn.commit()
    k = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    e = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    d = conn.execute("SELECT COUNT(*) FROM dangling").fetchone()[0]
    conn.close()
    print(f"[build] 抽样 {n_reports} 件(every={every}{' +ALL' if all_files else ''}) "
          f"→ 节点 {k} / 关系 {e} / 悬挂 {d} → {out}")
    print(f"[build] 悬挂分类分布: {cls_stat}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--stats" in args:
        for f in pick_files(8, "--all" in args)[:5]:
            print(f)
        print(f"共 {len(pick_files(8, '--all' in args))} 件入样")
    else:
        out = DB
        if "--out" in args:
            out = args[args.index("--out") + 1]
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        build(every=int(args[args.index("--every") + 1]) if "--every" in args else 8,
              all_files="--all" in args, out=out)
