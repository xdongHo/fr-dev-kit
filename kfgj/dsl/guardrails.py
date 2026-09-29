# -*- coding: utf-8 -*-
"""guardrails.py — 示例项目 FS 报表 DSL 编译产物护栏（G1-G5 + 可选 G6 扩展闸），独立可复用模块。

公开接口
--------
check(doc_xml, semantic, sql_list, do_smoke=False, conn=None, param_values=None,
      enable_ext=False) -> list[dict]
    doc_xml       编译产物 cpt 全文（str）
    semantic      semantic_layer.yaml 反序列化后的 dict（本模块只读 conventions 键）
    sql_list      [(ds_name, sql), ...]（compile.py 从 TableDataMap 收集）
    do_smoke      True 时执行 G5 真实冒烟
    conn          psycopg2.connect(**conn) 连接参数 dict（G5 用）
    param_values  {参数名: 值}（G5 占位符替换用）
    enable_ext    True 时追加 G6 扩展闸（R01-R15，L5 差分学习产出，2026-09-05 R25 合入）；
                  默认 False —— G1-G5 输出与合入前逐字节一致（向后兼容承诺）
    返回错误列表；每条 {"gate","rule","message"[,"detail"][,"severity"]}。
    severity="info" 为非错误信息（G5 冒烟行数），调用方不计入失败。
    本函数只收集不抛异常；单闸崩溃以 internal_error 条目呈现，不中断其余闸。
check_rules_ext(doc_xml, semantic, sql_list) -> list[dict]
    只跑 G6 扩展闸（R01-R15），参数与返回风格同 check。
check_clarifications(page, semantic) -> list[dict]
    G0 前置闸（编译前）：扫描 page DSL/语义层 dict 的未消歧 NEEDS_CLARIFICATION 标记
    （同级键 needs_clarification 或值内联 [NEEDS CLARIFICATION: ...]），任一命中→拒绝编译。
    语义=T11 spec-kit「歧义显式化、clarify 未过不能 plan」；约定声明见
    semantic_layer.yaml conventions.needs_clarification（声明节点本身被扫描器跳过）。
check_with_base(doc_xml, semantic, sql_list, do_smoke=False, conn=None, param_values=None)
    = check(..., enable_ext=True) 兼容别名（原 rules_ext.check_with_base 语义）。

G6 与 G1-G5 的重复判定关系（2026-09-05 R25 逐条评审结论，详见 _runs/night/R25/REPORT.md）
--------
字面/语义重复 4 条，均已标注「强化版」并挂回原闸条目（G6 侧保留独立 rule id 以维持
L5 夹具 30/30 命中口径；默认路径行为零改动，是否用强化版反向升级原闸留晨间裁决）：
  R04 ⊋ G2/widget_param_mismatch（豁免族 label→label/button/submit/layout/rhiframe）
  R05 ⊃ G3/forbidden_residue（${{ 残留检查从 Query 扩到全元素 text/tail）
  R08 ⊃ G2/ds_ref（DSColumn 路径同判定 + 新增 TableDataDictAttr 字典引用路径）
  R11 ⊃ G2/param_ref（数据集作用域感知，修复 G2 对数据集局部参数的误报盲区）
其余 11 条（R01/R02/R03/R06/R07/R09/R10/R12-R15）为 G1-G5 未覆盖的独立判定。

CLI
----
python guardrails.py <cpt路径> --semantic <yaml路径> [--smoke] [--ext]
                     [--param K=V ...] [--pg-host H --pg-port P --pg-db D --pg-user U --pg-password W]
从 cpt 原文正则提取 TableDataMap 各 Query 组成 sql_list，逐条打印 [Gx] rule: message；
有错 exit 1，干净打印 GUARDRAILS: 0 errors。--semantic 解析需要 PyYAML（缺失则明确报错退出码 2）。
--ext 追加 G6 扩展闸（compile.py 同名开关，默认不开）。
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET

__all__ = ["check", "extract_sql_list", "check_rules_ext", "check_with_base",
           "scan_clarifications", "check_clarifications"]

# ---- semantic_layer.yaml 缺省 conventions（与主线契约一致，yaml 提供值优先） ----
DEFAULT_HYGIENE = {
    "numeric_cast_marker": "COALESCE(NULLIF(",
    "numeric_cast_cast": "::numeric",
    "period_case_marker": "CASE upper('",
    "org_markers": ["fin_demo_auth_base_info", "UNION ALL"],
    "perm_markers": ["fin_demo_config_user_role", "fine_username"],
    "forbidden_residue": "${{",
    "values_union_marker": "UNION ALL",
}
DEFAULT_GLOBAL_PARAMS = ["fine_username"]
DEFAULT_EXCEPTIONS = ["param_guard", "dict_"]

# G4 PERM 片段判定：SQL 必须实际引用其中一张鉴权表做过滤（仅出现 ${fine_username} 不算）
PERM_TABLE_ROLE = "fin_demo_config_user_role"
PERM_TABLE_MAP = "fin_demo_auth_base_user_map"

# ---------------- G0 需求歧义前置闸（NEEDS_CLARIFICATION；T11 spec-kit 语义，2026-09-06 CAR-012 合入） ----------------
NEEDS_CLARIFICATION_KEY = "needs_clarification"
NEEDS_CLARIFICATION_DECL_PATH = ("conventions", NEEDS_CLARIFICATION_KEY)
_INLINE_CLARIFICATION = re.compile(r"\[NEEDS CLARIFICATION:?\s*([^\]]*)\]")


def _clarification_question(v):
    """归一化标记值为澄清问题文本（str / {question:..} / list 皆可）。"""
    if isinstance(v, dict):
        q = str(v.get("question") or v.get("q") or v).strip()
    elif isinstance(v, (list, tuple)):
        q = "; ".join(str(x).strip() for x in v if str(x).strip())
    else:
        q = str(v).strip()
    return q or "(未填写澄清问题)"


def scan_clarifications(node, path="", skip=()):
    """递归扫描已装载的 DSL/语义层数据，收集未消歧 NEEDS_CLARIFICATION 标记。

    标记两种形态（可混用，约定声明见 semantic_layer.yaml conventions.needs_clarification）:
      1) 同级键: 任意映射内 needs_clarification: "<澄清问题>"（值接受 str/{question}/list）
      2) 值内联: 任意字符串值内 [NEEDS CLARIFICATION: <澄清问题>]（spec-kit 原生形态）
    skip: 跳过的点分路径集合（约定声明节点本身=定义非实例，默认调用方传 DECL 路径）。
    返回 [{"path", "question"}]; path=点分槽位路径（list 下标 [i]），指向标记所在槽位。
    """
    marks = []
    if isinstance(node, dict):
        for k, v in node.items():
            sub = f"{path}.{k}" if path else str(k)
            if sub in skip:
                continue
            if k == NEEDS_CLARIFICATION_KEY:
                marks.append({"path": path or "<root>", "question": _clarification_question(v)})
                continue
            marks.extend(scan_clarifications(v, sub, skip))
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            marks.extend(scan_clarifications(v, f"{path}[{i}]", skip))
    elif isinstance(node, str):
        for m in _INLINE_CLARIFICATION.finditer(node):
            q = m.group(1).strip() or "(未填写澄清问题)"
            marks.append({"path": path or "<root>", "question": q})
    return marks


def check_clarifications(page, semantic):
    """G0 前置闸：编译前扫描 page DSL + semantic_layer 的未消歧 NEEDS_CLARIFICATION 标记。
    返回 gate=G0 错误条目列表（空=无歧义可编译）。compile.py 在 grounding 之前调用；
    存在任一条目→拒绝产出 cpt（spec-kit 语义：clarify 未过不能 plan）。"""
    skip_prefix = ".".join(NEEDS_CLARIFICATION_DECL_PATH)
    errs = []
    for tag, node in (("page", page), ("semantic", semantic)):
        for m in scan_clarifications(node or {}, tag, {f"{tag}.{skip_prefix}"}):
            errs.append(_err("G0", "needs_clarification",
                             f"{m['path']}: {m['question']}",
                             path=m["path"], question=m["question"]))
    return errs


_SPAN = re.compile(r"\$\{([^{}]*)\}")
_SPAN_Q = re.compile(r"'\$\{([^{}]*)\}'")
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_P_LIKE = re.compile(r"p_[A-Za-z0-9_]+")

_TD_RE = re.compile(r"<TableData\b[^>]*?\bname=\"([^\"]+)\"[^>]*>(.*?)</TableData>", re.S)
_QUERY_RE = re.compile(r"<Query>(?:<!\[CDATA\[(.*?)\]\]>|(.*?))</Query>", re.S)


def _err(gate, rule, message, severity="error", **detail):
    e = {"gate": gate, "rule": rule, "message": message}
    if severity != "error":
        e["severity"] = severity
    if detail:
        e["detail"] = detail
    return e


def _conventions(semantic):
    c = (semantic or {}).get("conventions") or {}
    hy = dict(DEFAULT_HYGIENE)
    hy.update(c.get("sql_hygiene") or {})
    exc = c.get("sql_exceptions")
    return {
        "global_params": list(c.get("global_params") or DEFAULT_GLOBAL_PARAMS),
        "sql_hygiene": hy,
        "sql_exceptions": list(exc if exc is not None else DEFAULT_EXCEPTIONS),
        # 已知偏差豁免通道（T2-2b 2026-09-06）：线上既有缺陷照实复现时的最小豁免登记，
        # 来源 semantic_layer.yaml conventions.known_deviations（须附 snapshot_at）；缺省空=行为与旧版一致。
        "known_deviations": dict(c.get("known_deviations") or {}),
    }


def _kd_match(name, patterns):
    """已知偏差命中：精确名或前缀（前缀以结尾下划线标识，如 ds_cr_）。"""
    for p in patterns or []:
        if p == name or (p.endswith("_") and name.startswith(p)):
            return True
    return False


def extract_sql_list(doc_xml):
    """从 cpt 原文提取各数据集 SQL（正则，不依赖 XML 解析，G1 失败时仍可用）。"""
    out = []
    for m in _TD_RE.finditer(doc_xml):
        q = _QUERY_RE.search(m.group(2))
        if q:
            out.append((m.group(1), q.group(1) if q.group(1) is not None else q.group(2)))
    return out


# ---------------- G1 XML well-formed ----------------
def _g1(doc_xml):
    errs = []
    try:
        root = ET.fromstring(doc_xml.encode("utf-8"))
    except ET.ParseError as e:
        line, col = (getattr(e, "position", None) or (None, None))
        errs.append(_err("G1", "xml_wellformed",
                         f"XML 解析失败: {e.msg} (line {line}, col {col})"))
        return errs, None
    except Exception as e:  # 编码声明等非常规问题
        errs.append(_err("G1", "xml_wellformed", f"XML 解析异常: {e!r}"))
        return errs, None
    return errs, root


# ---------------- G2 引用闭合 ----------------
def _declared_params(root):
    """声明参数 = ReportParameterAttr 直属 Parameters ∪ ParameterUI 直属 Parameters。
    （TableData 自带 <Parameters> 不算声明，只算数据集内局部声明。）"""
    names = []
    for tag in ("ReportParameterAttr", "ParameterUI"):
        for holder in root.iter(tag):
            for attrs in holder.findall("Parameters/Parameter/Attributes"):
                n = attrs.get("name")
                if n:
                    names.append(n)
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _param_refs(text):
    """提取全文 ${...} 引用的参数名。
    ${name} 直接引用取全名；${if(len(para_x)==0,...)} 宏体内提取 para_*/p_* 形态标识符。"""
    refs = set()
    for m in _SPAN.finditer(text):
        content = m.group(1).strip()
        if _IDENT.fullmatch(content):
            refs.add(content)
        else:
            for tok in _IDENT.findall(content):
                if tok.startswith("para_") or _P_LIKE.fullmatch(tok):
                    refs.add(tok)
    return refs


def _g2(root, doc_xml, conv):
    errs = []
    if root is None:
        errs.append(_err("G2", "skipped", "XML 解析失败（见 G1），引用闭合检查跳过"))
        return errs
    declared = _declared_params(root)
    declared_set = set(declared)
    global_params = set(conv["global_params"])
    kd = conv.get("known_deviations") or {}

    # (a) DSColumn dsName ⊆ TableDataMap 数据集
    ds_set = {td.get("name") for td in root.iter("TableData") if td.get("name")}
    for attrs in root.findall(".//O[@t='DSColumn']/Attributes[@dsName]"):
        dn = attrs.get("dsName")
        if dn and dn not in ds_set:
            if dn in (kd.get("ds_undefined_refs") or []):
                continue  # 已知偏差豁免（照实复现，登记见 conventions.known_deviations）
            errs.append(_err("G2", "ds_ref",
                             f"单元格 DSColumn 引用了未定义数据集: {dn}",
                             dsName=dn, known=sorted(x for x in ds_set if x)))

    # (b) ${} 参数引用 ⊆ 声明参数（conventions.global_params 豁免，如 fine_username）
    for ref in sorted(_param_refs(doc_xml) - declared_set - global_params):
        if ref in (kd.get("params_undeclared") or []):
            continue  # 已知偏差豁免（如 示例实际表页 para_adj 控件补参）
        errs.append(_err("G2", "param_ref",
                         f"引用了未声明参数: ${{{ref}}}",
                         param=ref, declared=declared))

    # (c) 控件名=参数名铁律：非 Label 的 InnerWidget 名必须 ∈ 声明参数；lb_ 前缀豁免
    for iw in root.iter("InnerWidget"):
        wn = iw.find("WidgetName")
        name = wn.get("name") if wn is not None else None
        if not name or name.startswith("lb_"):
            continue
        if "Label" in (iw.get("class") or ""):
            continue
        if name in (kd.get("widgets_nonparam") or []):
            continue  # 已知偏差豁免（动作按钮 query/formSubmit 非参数控件）
        if name not in declared_set:
            errs.append(_err("G2", "widget_param_mismatch",
                             f"面板控件名 [{name}] 不是已声明参数（控件名=参数名铁律）",
                             widget=name, declared=declared))
    return errs


# ---------------- G3 SQL 卫生 ----------------
_CAST_AS_NUMERIC = re.compile(r"CAST\s*\([^)]*AS\s+numeric\s*\)", re.I)


def _numeric_protected(sql, hy):
    """varchar 数值保护判定：NULLIF 空串防护 + 显式 numeric 转换（::numeric 或 CAST(... AS numeric)）。
    （2026-09-04 放宽：存量 CR 数据集用 CAST(NULLIF(trim(x),'') AS numeric) 形态， doctrine 等价。）"""
    if "NULLIF(" not in sql:
        return False
    cast = hy["numeric_cast_cast"]
    if isinstance(cast, str) and cast in sql:
        return True
    if isinstance(cast, list) and any(c in sql for c in cast):
        return True
    return bool(_CAST_AS_NUMERIC.search(sql))


def _g3(sql_list, conv):
    errs = []
    hy = conv["sql_hygiene"]
    exceptions = conv["sql_exceptions"]
    kd = conv.get("known_deviations") or {}
    no_orgperm = kd.get("ds_no_orgperm_prefix") or []
    for ds_name, sql in sql_list:
        tag = ds_name or "<unnamed>"
        # 豁免前缀（param_guard 回显集 / dict_ 字典集）只做残留检查：
        # 字典集是 DISTINCT 单查询、回显集无业务表，天然无 numeric/period/ORG/VALUES 幅面（2026-09-04 主线定性）
        fact_only = not any(tag.startswith(p) for p in exceptions)
        kd_orgperm = _kd_match(tag, no_orgperm)
        if fact_only and tag not in (kd.get("ds_no_numeric") or []) \
                and not _numeric_protected(sql, hy):
            errs.append(_err("G3", "numeric_cast",
                             f"[{tag}] varchar 数据参与运算缺显式 numeric 保护"
                             f"（需 NULLIF + {'::numeric' if isinstance(hy['numeric_cast_cast'], str) else '/'.join(hy['numeric_cast_cast'])} 或 CAST(... AS numeric)）",
                             ds=tag))
        if fact_only and tag not in (kd.get("ds_no_period_case") or []) \
                and ("${para_month}" in sql or "${para_month_bud}" in sql) \
                and hy["period_case_marker"] not in sql:
            errs.append(_err("G3", "period_case",
                             f"[{tag}] 引用月份参数但缺 period CASE 模板（{hy['period_case_marker']}...）",
                             ds=tag))
        if fact_only and not kd_orgperm:
            missing_org = [mk for mk in hy["org_markers"] if mk not in sql]
            if missing_org:
                errs.append(_err("G3", "org_markers",
                                 f"[{tag}] 缺 ORG 标记: {missing_org}", ds=tag, missing=missing_org))
            if not any(pmk in sql for pmk in hy["perm_markers"]):
                errs.append(_err("G3", "perm_markers",
                                 f"[{tag}] 缺 PERM 标记（任一即可）: {hy['perm_markers']}", ds=tag))
        residue = hy.get("forbidden_residue")
        if residue and residue in sql:
            errs.append(_err("G3", "forbidden_residue",
                             f"[{tag}] 含禁用残留 {residue!r}（疑似模板/f-string 双花括号泄漏）", ds=tag))
        if fact_only and "AS sgn" in sql and hy["values_union_marker"] not in sql:
            errs.append(_err("G3", "values_union",
                             f"[{tag}] 含 AS sgn（VALUES 构成片段）但缺 {hy['values_union_marker']}", ds=tag))
    return errs


# ---------------- G4 权限强制 ----------------
def _g4(sql_list, conv):
    errs = []
    hy = conv["sql_hygiene"]
    exceptions = conv["sql_exceptions"]
    kd = conv.get("known_deviations") or {}
    no_orgperm = kd.get("ds_no_orgperm_prefix") or []
    no_dict_perm = kd.get("dict_no_perm") or []
    for ds_name, sql in sql_list:
        tag = ds_name or "<unnamed>"
        if _kd_match(tag, no_orgperm):
            continue  # 已知偏差豁免：CR/Comments 族无 ORG+PERM（照实复现，登记见 conventions.known_deviations）
        exc = next((p for p in exceptions if tag.startswith(p)), None)
        perm_ok = (PERM_TABLE_ROLE in sql) or (PERM_TABLE_MAP in sql)
        if exc:
            # dict_ 类豁免前缀仅降级为「只要求 PERM」；其余豁免前缀（param_guard 等）全免
            if tag.startswith("dict_") and not perm_ok and not _kd_match(tag, no_dict_perm):
                errs.append(_err("G4", "perm_missing",
                                 f"[{tag}] 字典集缺权限片段（dict_ 豁免 ORG 但仍要求 PERM）", ds=tag))
            continue
        missing_org = [mk for mk in hy["org_markers"] if mk not in sql]
        if missing_org:
            errs.append(_err("G4", "org_missing",
                             f"[{tag}] 数据集缺 ORG 过滤片段", ds=tag, missing=missing_org))
        if not perm_ok:
            errs.append(_err("G4", "perm_missing",
                             f"[{tag}] 数据集缺 PERM 权限片段（需 {PERM_TABLE_ROLE} 或 {PERM_TABLE_MAP} 实际过滤）",
                             ds=tag))
    return errs


# ---------------- G5 冒烟（可选） ----------------
def _sql_literal(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def _substitute(sql, values):
    """${name} 占位符替换（2026-09-04 修复：SQL 内占位符通常已包在引号里）。
    带引号形态 '${name}' → 用裸值替换（仅做 '' 转义，不再包引号）；
    裸形态 ${name} → 用 SQL 字面量（加引号）；宏体/缺值保持原样并记入 unresolved（不执行）。"""
    unresolved = []

    def rep_quoted(m):
        name = m.group(1).strip()
        if _IDENT.fullmatch(name):
            if name in values:
                return "'" + str(values[name]).replace("'", "''") + "'"
            unresolved.append(name)
        else:
            unresolved.append("macro<${" + m.group(1).strip()[:60] + "}>")
        return m.group(0)

    def rep(m):
        content = m.group(1).strip()
        if _IDENT.fullmatch(content):
            if content in values:
                return _sql_literal(values[content])
            unresolved.append(content)
            return m.group(0)
        return m.group(0)   # 宏体已在带引号遍历中记录，此处保持原样

    sql = _SPAN_Q.sub(rep_quoted, sql)
    sql = _SPAN.sub(rep, sql)
    return sql, unresolved


# G5 静态宏求值：${if(len(P)=0,默认值,P)}（主表 ds_fs 实测形态；t2_paritel_compare.subst 同款先例）
_MACRO_IF_G5 = re.compile(r"\$\{if\(len\((\w+)\)\s*=\s*0\s*,\s*([^,]*?)\s*,\s*\w+\s*\)\}")


def _static_macro(sql, values):
    def rep(m):
        p = m.group(1)
        if p in values and str(values[p]) != "":
            return str(values[p])
        return m.group(2)
    return _MACRO_IF_G5.sub(rep, sql)


def _g5(sql_list, conn, param_values, known_broken=None):
    errs = []
    known_broken = set(known_broken or [])
    try:
        import psycopg2  # noqa: F401
    except ImportError:
        errs.append(_err("G5", "psycopg2_missing",
                         "G5 冒烟需要 psycopg2（pip install psycopg2-binary），导入失败"))
        return errs
    if not conn:
        errs.append(_err("G5", "no_conn", "do_smoke=True 但未提供 conn（psycopg2.connect kwargs dict）"))
        return errs
    values = dict(param_values or {})
    try:
        cn = psycopg2.connect(**conn)
    except Exception as e:
        errs.append(_err("G5", "connect_failed", f"数据库连接失败: {e}"))
        return errs
    cur = None
    try:
        cur = cn.cursor()
        for ds_name, sql in sql_list:
            tag = ds_name or "<unnamed>"
            try:
                resolved, unresolved = _substitute(_static_macro(sql, values), values)
            except Exception as e:
                errs.append(_err("G5", "substitute_crash", f"[{tag}] 参数替换崩溃: {e!r}", ds=tag))
                continue
            if unresolved:
                errs.append(_err("G5", "unresolved_param",
                                 f"[{tag}] 占位符缺 param_values 值或为宏不可静态替换: {unresolved}",
                                 ds=tag, unresolved=unresolved))
                continue
            try:
                cur.execute(resolved)
                rows = cur.fetchall()
                errs.append(_err("G5", "smoke_ok", f"[{tag}] 执行 OK, {len(rows)} 行",
                                 severity="info", ds=tag))
            except Exception as e:
                if ds_name in known_broken:
                    # 已知偏差豁免：线上既有 SQL 缺陷照实复现（登记见 conventions.known_deviations.ds_sql_broken）
                    errs.append(_err("G5", "sql_failed_known_deviation",
                                     f"[{tag}] 执行失败（已知偏差，照实复现不修复）: {str(e)[:160]}",
                                     severity="info", ds=tag))
                else:
                    errs.append(_err("G5", "sql_failed", f"[{tag}] 执行失败: {e}", ds=tag))
                try:
                    cn.rollback()
                except Exception:
                    pass
    finally:
        try:
            if cur is not None:
                cur.close()
            cn.close()
        except Exception:
            pass
    return errs


# ---------------- G6 扩展闸（R01-R15，可选；L5 产出 2026-09-04，R25 合入 2026-09-05） ----------------
# 代码自 rules_ext.py 原样迁入（零逻辑改动，错误 dict 逐字节一致）；rules_ext.py 降级为兼容 shim。
# 重复判定与强化版关系见模块 docstring「G6 与 G1-G5 的重复判定关系」。

GATE = "G6"

_ORDER_BY = re.compile(r"ORDER\s+BY", re.I)
_MACRO_IF = re.compile(r"\$\{\s*if\b")
_EXPAND_DIR_ATTRS = ("dir", "direction")
_EXPAND_DIR_LEGAL = {"0", "1", "2"}

# 规则注册表（评审元数据，仅供检索/报表；不参与判定）
RULE_REGISTRY = {
    "r01_style_index_range":      {"reinforces": None, "note": "C@s ∈ [0, StyleList Style 数)"},
    "r02_dsc_expand_pairing":     {"reinforces": None, "note": "O@t=DSColumn 的 C 必须有 <Expand>（单向)"},
    "r03_param_name_unique":      {"reinforces": None, "note": "声明持有者内 Parameter name 唯一"},
    "r04_widget_param_coverage":  {"reinforces": "G2/widget_param_mismatch",
                                   "note": "强化版: 豁免族 label/button/submit/layout/rhiframe"},
    "r05_cdata_double_brace":     {"reinforces": "G3/forbidden_residue",
                                   "note": "强化版: ${{ 残留检查 Query-only → 全元素 text/tail"},
    "r06_cell_coord_integrity":   {"reinforces": None, "note": "C 的 c/r 必填非负 + (c,r) 全文档唯一"},
    "r07_tabledata_name_unique":  {"reinforces": None, "note": "TableData@name 全文档唯一"},
    "r08_ds_ref_closure":         {"reinforces": "G2/ds_ref",
                                   "note": "强化版: 补 TableDataDictAttr 字典引用路径"},
    "r09_hyperlink_group_pairing": {"reinforces": None, "note": "NameJavaScriptGroup 至少 1 个 NameJavaScript"},
    "r10_sql_macro_orderby":      {"reinforces": None, "note": "${if( 宏 SQL 须有 ORDER BY 且在最后宏之后"},
    "r11_sql_param_scope":        {"reinforces": "G2/param_ref",
                                   "note": "强化版: 数据集作用域感知，修复 G2 局部参数误报盲区"},
    "r12_expand_dir_enum":        {"reinforces": None, "note": "Expand@dir/direction ∈ {0,1,2}"},
    "r13_bounds_attr_sane":       {"reinforces": None, "note": "BoundsAttr 四属性齐全且非负整数"},
    "r14_bookmark_name_unique":   {"reinforces": None, "note": "MobileBookMark@bookMarkName 非空即全文档唯一"},
    "r15_parameter_has_name":     {"reinforces": None, "note": "Parameter 双形态（@name / Attributes@name）取名"},
}


def _err6(rule, message, **detail):
    return _err(GATE, rule, message, **detail)


def _coord(c_el):
    return f'(c={c_el.get("c")},r={c_el.get("r")})'


def _param_name(p_el):
    """Parameter 双形态取名: 属性态 @name 优先，其次子元素态 Attributes@name（可能均空）。"""
    n = (p_el.get("name") or "").strip()
    if n:
        return n
    attrs = p_el.find("Attributes")
    return (attrs.get("name").strip() if attrs is not None and attrs.get("name") else "")


def _declared_global_params(root):
    """声明参数 = ReportParameterAttr ∪ ParameterUI 直属 Parameters（口径同 G2，
    但用 _param_name 双形态解析——较 G2/_declared_params 多认属性态，见 R15 评审）。"""
    names = set()
    for tag in ("ReportParameterAttr", "ParameterUI"):
        for holder in root.iter(tag):
            for p in holder.findall("Parameters/Parameter"):
                n = _param_name(p)
                if n:
                    names.add(n)
    return names


def _as_nonneg_int(v):
    try:
        n = int(v)
    except (TypeError, ValueError):
        return None
    return n if n >= 0 else None


# 豁免类族（2026-09-04 实测）: Label=标签; Button/Submit=动作按钮(formSubmit3/query 均为
# com.fr.form.ui.FreeButton); Layout=嵌套容器(absolute0 等); RHIframe=iframe 容器
# (画布语料 150 例 com.fr.plugin.form.widget.core.RHIframe)——均非参数编辑器
_WIDGET_EXEMPT = ("label", "button", "submit", "layout", "rhiframe")


def _r01_style_index(root, errs):
    style_counts = [len(sl.findall("Style")) for sl in root.iter("StyleList")]
    n_styles = max(style_counts) if style_counts else 0
    for c in root.iter("C"):
        s = c.get("s")
        if s is None:
            continue
        idx = _as_nonneg_int(s)
        if idx is None:
            errs.append(_err6("r01_style_index_range",
                              f"单元格 {_coord(c)} s 属性非非负整数: {s!r}", s=s))
            continue
        if n_styles == 0:
            if idx != 0:
                errs.append(_err6("r01_style_index_range",
                                  f"文档无 StyleList 但单元格 {_coord(c)} s={idx}（仅允许缺省/0）",
                                  s=s))
        elif idx >= n_styles:
            errs.append(_err6("r01_style_index_range",
                              f"单元格 {_coord(c)} s={idx} 越界（StyleList 仅 {n_styles} 个 Style）",
                              s=idx, style_count=n_styles))


def _r02_dsc_expand(root, errs):
    for c in root.iter("C"):
        o = c.find("O")
        if o is not None and o.get("t") == "DSColumn" and c.find("Expand") is None:
            attrs = o.find("Attributes")
            errs.append(_err6("r02_dsc_expand_pairing",
                              f"DSColumn 单元格 {_coord(c)} 缺 <Expand>（数据列不扩展只显单值）",
                              dsName=attrs.get("dsName") if attrs is not None else None,
                              columnName=attrs.get("columnName") if attrs is not None else None))


def _r03_param_unique(root, errs):
    for tag in ("ReportParameterAttr", "ParameterUI"):
        for holder in root.iter(tag):
            seen = set()
            for p in holder.findall("Parameters/Parameter"):
                n = _param_name(p)
                if not n:
                    continue
                if n in seen:
                    errs.append(_err6("r03_param_name_unique",
                                      f"{tag} 内参数 [{n}] 重复声明", holder=tag, param=n))
                else:
                    seen.add(n)


def _r04_widget_param(root, errs, global_params):
    declared = _declared_global_params(root) | set(global_params)
    for iw in root.iter("InnerWidget"):
        wn = iw.find("WidgetName")
        name = wn.get("name") if wn is not None else None
        if not name or name.startswith("lb_"):
            continue
        cls = (iw.get("class") or "").lower()
        if any(k in cls for k in _WIDGET_EXEMPT):
            continue
        if name not in declared:
            errs.append(_err6("r04_widget_param_coverage",
                              f"面板控件 [{name}]({iw.get('class')}) 未对应任何声明参数（控件名=参数名铁律）",
                              widget=name, widget_class=iw.get("class"), declared=sorted(declared)))


def _r05_cdata_residue(root, errs):
    for el in root.iter():
        for kind, txt in (("text", el.text), ("tail", el.tail)):
            if txt and "${{" in txt:
                i = txt.index("${{")
                errs.append(_err6("r05_cdata_double_brace",
                                  f"{el.tag}.{kind} 含禁用残留 '${{{{'（模板/f-string 双花括号泄漏）: "
                                  f"...{txt[max(0, i - 20):i + 40]}...",
                                  tag=el.tag, snippet=txt[i:i + 60]))


def _r06_cell_coord(root, errs):
    seen = {}
    for c in root.iter("C"):
        for a in ("c", "r"):
            if c.get(a) is None:
                errs.append(_err6("r06_cell_coord_integrity",
                                  f"单元格缺 {a} 属性", el=_coord(c)))
            elif _as_nonneg_int(c.get(a)) is None:
                errs.append(_err6("r06_cell_coord_integrity",
                                  f"单元格 {a} 属性非非负整数: {c.get(a)!r}", el=_coord(c)))
        for a in ("cs", "rs"):
            if c.get(a) is not None and _as_nonneg_int(c.get(a)) is None:
                errs.append(_err6("r06_cell_coord_integrity",
                                  f"单元格 {a}（跨格数）非非负整数: {c.get(a)!r}", el=_coord(c)))
        key = (c.get("c"), c.get("r"))
        if key in seen:
            errs.append(_err6("r06_cell_coord_integrity",
                              f"单元格坐标重复 {_coord(c)}（与先前 C 元素冲突）",
                              coord=list(key)))
        else:
            seen[key] = True


def _r07_tabledata_unique(root, errs):
    seen = set()
    for td in root.iter("TableData"):
        n = td.get("name")
        if not n:
            continue
        if n in seen:
            errs.append(_err6("r07_tabledata_name_unique",
                              f"数据集 [{n}] 重复定义（TableData name 必须唯一）", ds=n))
        seen.add(n)


def _r08_ds_ref(root, errs):
    defined = {td.get("name") for td in root.iter("TableData") if td.get("name")}
    for attrs in root.findall(".//O[@t='DSColumn']/Attributes[@dsName]"):
        dn = attrs.get("dsName")
        if dn and dn not in defined:
            errs.append(_err6("r08_ds_ref_closure",
                              f"DSColumn 引用未定义数据集: {dn}",
                              dsName=dn, known=sorted(defined)))
    for tdd in root.iter("TableDataDictAttr"):
        for nm in tdd.findall("TableData/Name"):
            dn = (nm.text or "").strip()
            if dn and dn not in defined:
                errs.append(_err6("r08_ds_ref_closure",
                                  f"控件字典引用未定义数据集: {dn}",
                                  dsName=dn, via="TableDataDictAttr", known=sorted(defined)))


def _r09_hyperlink_group(root, errs):
    for g in root.iter("NameJavaScriptGroup"):
        k = len(g.findall("NameJavaScript"))
        if k == 0:
            errs.append(_err6("r09_hyperlink_group_pairing",
                              "NameJavaScriptGroup 内无任何 NameJavaScript（空超链组）"))


def _r10_macro_orderby(sql_list, errs):
    for ds_name, sql in sql_list or []:
        tag = ds_name or "<unnamed>"
        if not _MACRO_IF.search(sql):
            continue
        if not _ORDER_BY.search(sql):
            errs.append(_err6("r10_sql_macro_orderby",
                              f"[{tag}] 含 ${{if( 宏但缺 ORDER BY（级联 SQL 规范）", ds=tag))
            continue
        last_macro_end = max(m.end() for m in _SPAN.finditer(sql))
        ob_last = max((m.start() for m in _ORDER_BY.finditer(sql)), default=-1)
        if ob_last < last_macro_end:
            errs.append(_err6("r10_sql_macro_orderby",
                              f"[{tag}] ORDER BY 位于最后一个 ${{}} 宏之前（宏展开会破坏排序语义）",
                              ds=tag))


def _r11_sql_param_scope(root, sql_list, errs, global_params):
    declared_global = _declared_global_params(root) | set(global_params)
    for ds_name, sql in sql_list or []:
        tag = ds_name or "<unnamed>"
        local = set()
        for td in root.iter("TableData"):
            if td.get("name") != ds_name:
                continue
            for p in td.findall("Parameters/Parameter"):
                n = _param_name(p)
                if n:
                    local.add(n)
        allow = declared_global | local
        for ref in sorted(_param_refs(sql) - allow):
            errs.append(_err6("r11_sql_param_scope",
                              f"[{tag}] 引用参数 ${{{ref}}} 未在全局或本数据集声明",
                              ds=tag, param=ref,
                              local=sorted(local), declared=sorted(declared_global)))


def _r12_expand_dir(root, errs):
    for exp in root.iter("Expand"):
        for a in _EXPAND_DIR_ATTRS:
            v = exp.get(a)
            if v is not None and v not in _EXPAND_DIR_LEGAL:
                errs.append(_err6("r12_expand_dir_enum",
                                  f"Expand@{a}={v!r} 不在合法枚举 {{0,1,2}}", value=v))


def _r13_bounds(root, errs):
    for b in root.iter("BoundsAttr"):
        vals = {}
        for a in ("x", "y", "width", "height"):
            v = b.get(a)
            n = _as_nonneg_int(v)
            if v is None:
                vals[a] = "missing"
            elif n is None:
                vals[a] = v
            else:
                vals[a] = n
        bad = {a: v for a, v in vals.items() if isinstance(v, str)}
        if bad:
            errs.append(_err6("r13_bounds_attr_sane",
                              f"BoundsAttr 属性缺失或非法（须非负整数）: {bad}", bad=bad))


def _r14_bookmark_unique(root, errs):
    seen = {}
    for mb in root.iter("MobileBookMark"):
        n = mb.get("bookMarkName")
        if not n:
            continue
        if n in seen:
            errs.append(_err6("r14_bookmark_name_unique",
                              f"bookMarkName [{n}] 重复（移动端书签冲突）", bookmark=n))
        seen[n] = True


def _r15_parameter_has_name(root, errs):
    """FR 存在两种合法序列化形态（2026-09-04 线上实测）:
    属性态 <Parameter name="x" CustomData="false"> 与 子元素态 <Parameter><Attributes name="x"/>。
    两种皆合法；两处皆缺名才算违规。"""
    for p in root.iter("Parameter"):
        attrs = p.find("Attributes")
        n_attr = (p.get("name") or "").strip()
        n_child = (attrs.get("name") if attrs is not None else "") or ""
        if not n_attr and not n_child.strip():
            errs.append(_err6("r15_parameter_has_name",
                              "Parameter 缺参数名（属性态 @name 与子元素态 Attributes@name 均未声明）"))


def check_rules_ext(doc_xml, semantic, sql_list):
    """G6 扩展闸主入口（R01-R15）。参数与返回风格同 check；只收集不抛异常。"""
    conv = _conventions(semantic)
    errs = []
    try:
        root = ET.fromstring(doc_xml.encode("utf-8"))
    except ET.ParseError as e:
        line, col = (getattr(e, "position", None) or (None, None))
        errs.append(_err6("skipped", f"XML 解析失败（见 G1），G6 跳过: {e.msg} (line {line}, col {col})"))
        return errs
    except Exception as e:
        errs.append(_err6("skipped", f"XML 解析异常（见 G1），G6 跳过: {e!r}"))
        return errs
    steps = (
        ("R01", lambda: _r01_style_index(root, errs)),
        ("R02", lambda: _r02_dsc_expand(root, errs)),
        ("R03", lambda: _r03_param_unique(root, errs)),
        ("R04", lambda: _r04_widget_param(root, errs, conv["global_params"])),
        ("R05", lambda: _r05_cdata_residue(root, errs)),
        ("R06", lambda: _r06_cell_coord(root, errs)),
        ("R07", lambda: _r07_tabledata_unique(root, errs)),
        ("R08", lambda: _r08_ds_ref(root, errs)),
        ("R09", lambda: _r09_hyperlink_group(root, errs)),
        ("R10", lambda: _r10_macro_orderby(sql_list or [], errs)),
        ("R11", lambda: _r11_sql_param_scope(root, sql_list or [], errs, conv["global_params"])),
        ("R12", lambda: _r12_expand_dir(root, errs)),
        ("R13", lambda: _r13_bounds(root, errs)),
        ("R14", lambda: _r14_bookmark_unique(root, errs)),
        ("R15", lambda: _r15_parameter_has_name(root, errs)),
    )
    for gate, fn in steps:
        try:
            fn()
        except Exception as e:
            errs.append(_err6("internal_error", f"{gate} 检查器崩溃: {e!r}"))
    return errs


def check_with_base(doc_xml, semantic, sql_list, do_smoke=False, conn=None, param_values=None):
    """G1-G5 + G6 联检兼容别名（原 rules_ext.check_with_base 语义，等价 check(enable_ext=True)）。"""
    return check(doc_xml, semantic, sql_list, do_smoke=do_smoke,
                 conn=conn, param_values=param_values, enable_ext=True)


# ---------------- 汇总入口 ----------------
def check(doc_xml, semantic, sql_list, do_smoke=False, conn=None, param_values=None,
          enable_ext=False):
    """五+一道闸主入口；只收集不抛异常，单闸崩溃不中断整体。返回错误列表（含 severity=info 行）。
    enable_ext=True 时在 G1-G5（含可选 G5）全部结束后追加 G6 扩展闸（R01-R15）；
    默认 False，G1-G5 输出与 2026-09-05 合入前逐字节一致。"""
    conv = _conventions(semantic)
    errs = []
    try:
        g1_errs, root = _g1(doc_xml)
        errs.extend(g1_errs)
    except Exception as e:
        root = None
        errs.append(_err("G1", "internal_error", f"G1 检查器崩溃: {e!r}"))
    for gate, fn in (
        ("G2", lambda: _g2(root, doc_xml, conv)),
        ("G3", lambda: _g3(sql_list or [], conv)),
        ("G4", lambda: _g4(sql_list or [], conv)),
    ):
        try:
            errs.extend(fn())
        except Exception as e:
            errs.append(_err(gate, "internal_error", f"{gate} 检查器崩溃: {e!r}"))
    if do_smoke:
        try:
            errs.extend(_g5(sql_list or [], conn, param_values,
                            known_broken=(conv.get("known_deviations") or {}).get("ds_sql_broken")))
        except Exception as e:
            errs.append(_err("G5", "internal_error", f"G5 检查器崩溃: {e!r}"))
    if enable_ext:
        try:
            errs.extend(check_rules_ext(doc_xml, semantic, sql_list))
        except Exception as e:
            errs.append(_err("G6", "internal_error", f"G6 检查器崩溃: {e!r}"))
    return errs


# ---------------- CLI ----------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="示例项目 FS 报表 cpt 护栏（G1-G5，--ext 加 G6 扩展闸）")
    ap.add_argument("cpt", help="待检 cpt 路径")
    ap.add_argument("--semantic", required=True, help="semantic_layer.yaml 路径")
    ap.add_argument("--smoke", action="store_true", help="执行 G5 真实冒烟")
    ap.add_argument("--ext", action="store_true", help="追加 G6 扩展闸（R01-R15，默认不开）")
    ap.add_argument("--param", action="append", default=[], metavar="K=V", help="G5 参数值，可重复")
    ap.add_argument("--pg-host"); ap.add_argument("--pg-port", default=None)
    ap.add_argument("--pg-db");   ap.add_argument("--pg-user")
    ap.add_argument("--pg-password", default=None)
    args = ap.parse_args(argv)

    try:
        with open(args.cpt, "r", encoding="utf-8") as f:
            doc = f.read()
    except OSError as e:
        print(f"GUARDRAILS ERROR: 无法读取 cpt: {e}", file=sys.stderr)
        return 2
    try:
        import yaml
    except ImportError:
        print("GUARDRAILS ERROR: --semantic 需要 PyYAML（pip install pyyaml）；"
              "或在代码中改用 check() API 直接传 dict", file=sys.stderr)
        return 2
    try:
        with open(args.semantic, "r", encoding="utf-8") as f:
            semantic = yaml.safe_load(f.read()) or {}
    except OSError as e:
        print(f"GUARDRAILS ERROR: 无法读取 semantic yaml: {e}", file=sys.stderr)
        return 2
    except yaml.YAMLError as e:
        print(f"GUARDRAILS ERROR: semantic yaml 解析失败: {e}", file=sys.stderr)
        return 2

    sql_list = extract_sql_list(doc)
    param_values = {}
    for kv in args.param:
        k, _, v = kv.partition("=")
        param_values[k.strip()] = v
    conn = None
    if args.smoke and args.pg_host:
        conn = {"host": args.pg_host, "port": args.pg_port, "dbname": args.pg_db,
                "user": args.pg_user, "password": args.pg_password}

    errs = check(doc, semantic, sql_list, do_smoke=args.smoke,
                 conn=conn, param_values=param_values or None, enable_ext=args.ext)
    for e in errs:
        line = f'[{e["gate"]}] {e["rule"]}: {e["message"]}'
        if e.get("detail"):
            line += f"  detail={e['detail']}"
        if e.get("severity") == "info":
            line = "INFO " + line
        print(line)
    n_err = sum(1 for e in errs if e.get("severity", "error") == "error")
    if n_err:
        print(f"GUARDRAILS: {n_err} errors")
        return 1
    print("GUARDRAILS: 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
