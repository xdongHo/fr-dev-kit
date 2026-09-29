# -*- coding: utf-8 -*-
"""
fr_rules_export.py —— 导出 / 定时调度 / 权限 / 数据连接 / 移动端 / 环境类静态校验规则集
=========================================================================================

来源: C:\\Users\\Admin\\Desktop\\fr_overnight\\merge_batch2\\B_rules_export.json 全部 42 条
      (每条规则 docstring 标注来源 doc-XXXX;详见 ckzl/bb/外部依赖与归档声明.md/LEARNINGS.md 对应小节)
参考实现: ckzl/bb/外部依赖与归档声明.md/practice/topic_<docid>/ 下各脚本(移植其校验逻辑, 均已在规则内注明)

模块约定(必须遵循):
  - 每条规则: `def check_<name>(cpt_path: str) -> list[tuple[str, str]]`
    返回 (级别, 消息) 列表, 级别 ∈ {'ERROR','WARN','OK'}
  - 模块级注册表: RULES = [{'name','fn','doc','context','apply'}, ...]
      context = 适用语境(ckzl/bb/外部依赖与归档声明.md知识管理规范-维护流程.md §0.7 要求每条校验规则显式标注适用语境)
      apply   = 触发条件(何时启用该规则)
  - def run_all(cpt_path) -> list  遍历 RULES 汇总结果
  - 只用标准库(xml.etree.ElementTree + os/re/json);不联网;不 import fr_check.py
  - 级别语义: ERROR=静态可判定且必然出错 / WARN=风险或需人工确认(含「用途标记缺失时
    的降级假设」)/ OK=通过或提示性信息

「模板被标为某用途」类规则(定时调度/挂载/per-user/FTP/SFTP/短信/平台通知等)的判定方式:
  在 .cpt 内找可静态观察的标记(XML 注释、参数名、节点名、JS 串、关键字);
  找不到可靠标记时降级为 WARN 并说明判定假设。
无法静态判断的规则(环境 GLIBC、HSQL 连接清单、连接白名单、调度 spec 等)写成保守的
WARN 并说明判定假设;需要第二输入的规则可先设置模块级 OPTIONS 再调用。

用法:
    python fr_rules_export.py <模板.cpt|.xml|.frm> [--only name1,name2] [--list]
    python fr_rules_export.py <模板> --json out.json
退出码: 0=全部通过 / 1=有 ERROR / 2=仅 WARN(对齐 fr_check.py 约定)
"""

from __future__ import annotations

# --- console-safe guard (2026-09-11 SOP 提速) ---
try:
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        if _s is not None and hasattr(_s, 'reconfigure'):
            try:
                _s.reconfigure(errors='replace')
            except Exception:
                pass
except Exception:
    pass
# --- end guard ---

import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ERROR, WARN, OK = "ERROR", "WARN", "OK"

# ---------------------------------------------------------------------------
# 模块级选项:凡需要「第二输入」(调度 spec / 连接白名单 / 清单 / 行数列数等)的规则
# 从这里取值;不设置则规则按「保守 WARN + 假设说明」降级。调用方可在 run_all 前赋值。
# ---------------------------------------------------------------------------
OPTIONS = {
    "conn_whitelist": None,      # set[str] 目标服务器数据连接名白名单 (doc-299/4153)
    "schedule_spec": None,       # dict 定时调度任务 spec (doc-2208/683/3573-2/3315)
    "privilege_spec": None,      # dict 细粒度权限 spec (doc-866, 结构见 practice privilege_spec.py)
    "peruser_spec": None,        # dict {"staff_rows": [...], "default_user_group": [...]} (doc-695)
    "ftp_cfg": None,             # dict FTP 上传附件配置 (doc-682)
    "sftp_cfg": None,            # dict SFTP 上传附件配置 (doc-3573)
    "sms_cfg": None,             # dict 短信参数配置 (doc-2210)
    "notify_spec": None,         # dict 平台通知/APP通知 spec (doc-4432/1387)
    "notify_link": None,         # str 自定义对外链接 (doc-1387)
    "mount_name": None,          # str 挂载平台「挂载名称」 (doc-2209)
    "dispatch_formula": None,    # str 公式判断执行条件, 如 "D5<20000" (doc-688/3315)
    "export_url": None,          # str 无头导出 URL (doc-4418)
    "fr_version": "10.0.19",     # str 服务器版本 (doc-135 R4 自定义按钮 HTML)
    "expect_ext": None,          # str 预期导出扩展名, 如 "xlsx"/"zip" (doc-1120)
    "total_rows": None,          # int 预计数据行数 (doc-1120/4524)
    "total_cols": None,          # int 报表列数 (doc-1120/4524)
    "fixed_rows_per_page": None, # int 固定行数分页每页行数 (doc-1120)
    "max_rows_per_file": None,   # int 单个 Excel 最大行数 (doc-1120)
    "dialect": None,             # str 数据库方言 sqlite/access/sqlserver2005/sqlserver2008/sqlserver2012/informix/sybase/oracle/mysql/hsql (doc-996)
    "hsql_manifest": None,       # str 数据连接清单 json 路径 (doc-2574)
}

# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------

def _read_text(cpt_path: str) -> str:
    """读原始文本(含 XML 注释), 解码失败用 replace 兜底。

    (R30 perf 2026-09-05) 同一文件(mtime_ns/size 未变)只读盘+解码一次,
    跨规则共享同一字符串对象(约 28 条规则原本各自重读 5.9MB 文件)。
    """
    try:
        st = os.stat(cpt_path)
        key = (os.path.abspath(cpt_path), st.st_mtime_ns, st.st_size)
    except OSError:
        key = None
    if key is not None and key in _TEXT_CACHE:
        return _TEXT_CACHE[key]
    with open(cpt_path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8", "replace")
    if key is not None:
        if len(_TEXT_CACHE) >= 4 and key not in _TEXT_CACHE:
            _TEXT_CACHE.clear()   # 批量场景内存上限
            _LOWER_CACHE.clear()
        _TEXT_CACHE[key] = text
        _LOWER_CACHE.clear()      # 新文本新 id
    return text


def _load_root(cpt_path: str):
    """解析 XML, 失败返回 None(调用方自行降级)。

    (R30 perf 2026-09-05) 同一文件(mtime_ns/size 未变)只解析一次, 跨规则共享同一棵树。
    行为等价前提: 本模块规则对树只读(2026-09-05 审计: 无 .set/.text=/tail=/remove 变更)。
    """
    root, _exc = _load_root_full(cpt_path)
    return root


def _load_root_full(cpt_path: str):
    """(R30 perf) _load_root 的内部版: 额外返回触发失败的原始异常(成功为 None),
    供 run_all 预检以原有「XML 解析失败: %s」格式重建消息, 免去预检的重复解析。"""
    try:
        st = os.stat(cpt_path)
        key = (os.path.abspath(cpt_path), st.st_mtime_ns, st.st_size)
    except OSError:
        key = None
    if key is not None and key in _LOAD_CACHE:
        return _LOAD_CACHE[key]
    try:
        root = ET.parse(cpt_path).getroot()
        exc = None
    except Exception as e:
        root, exc = None, e
    if key is not None:
        if len(_LOAD_CACHE) >= 8 and key not in _LOAD_CACHE:
            _LOAD_CACHE.clear()   # 批量场景内存上限: 换文件即弃旧树
            _SER_CACHE.clear()
        _LOAD_CACHE[key] = (root, exc)
        _SER_CACHE.clear()        # 新树新 id: 序列化缓存只对当前树有效
    return root, exc


def _xml_text(root) -> str:
    """root 序列化为纯文本(不含注释), 用于关键字扫描。

    (R30 perf) 走按元素 memoize 的 _ser, 同一元素重复序列化直接取缓存。
    """
    return _ser(root)


# (R30 perf 2026-09-05) 解析/序列化复用缓存 ─────────────────────────────
# R8 定位: fr_check 全量对 5.9MB 模板重复解析 16 次 + 全树 tostring 占 65% 耗时。
# 本模块 16 条规则对同一棵树只读, 缓存行为等价。
_LOAD_CACHE = {}   # (abspath, mtime_ns, size) -> (root 或 None, exc 或 None)
_SER_CACHE = {}    # id(el) -> (el, text); 钉住元素引用防 id 复用串键
_TEXT_CACHE = {}   # (abspath, mtime_ns, size) -> 全文文本(_read_text 复用)
_LOWER_CACHE = {}  # id(raw) -> (raw, lowered)(_has 全文小写副本复用)


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


def _has(raw: str, *keywords: str) -> bool:
    """大小写不敏感的多关键字命中(任一命中即 True)。

    (R30 perf 2026-09-05) lowered 副本按 id(raw) memoize(钉住 raw 防串键):
    raw 来自 _read_text 共享缓存时同一文本只 lower 一次;行为与逐次 lower 完全一致。
    """
    hit = _LOWER_CACHE.get(id(raw))
    if hit is not None and hit[0] is raw:
        low = hit[1]
    else:
        low = raw.lower()
        if len(_LOWER_CACHE) >= 4:
            _LOWER_CACHE.clear()
        _LOWER_CACHE[id(raw)] = (raw, low)
    return any(k.lower() in low for k in keywords)


def _row_engine_enabled(root) -> bool:
    """检测行式引擎: RowEngineAttr/@rowEngineEnabled=true(全树扫描, 与嵌套层级解耦)。"""
    if root is None:
        return False
    for el in root.iter():
        tag = el.tag.rsplit("}", 1)[-1].lower()
        if "rowengine" in tag:
            val = el.get("rowEngineEnabled") or el.get("rowEngine") or ""
            if val.strip().lower() in ("true", "1", "yes"):
                return True
    return False


def _template_params(root) -> dict:
    """模板参数名 -> 默认值字符串。兼容两种 XML 形态:
        <ReportParameterAttr><Parameters><Parameter><Attributes name="p"/><O>..</O></Parameter>
        <ReportParameterAttr><Parameter name="p" value=".."/>"""
    params = {}
    if root is None:
        return params
    attr = root.find(".//ReportParameterAttr")
    if attr is None:
        return params
    for p in attr.iter("Parameter"):
        nm = p.get("name") or ""
        if not nm:
            a = p.find("Attributes")
            nm = (a.get("name") or "") if a is not None else ""
        if not nm:
            continue
        o = p.find("O")
        default = (o.text or "").strip() if o is not None else ""
        if not default:
            default = (p.get("value") or "").strip()
        params[nm] = default
    return params


def _all_parameters(root) -> dict:
    """全树所有 <Parameter name=..> -> 默认值(模板参数 + 数据集参数声明, 供引用校验)。"""
    params = {}
    if root is None:
        return params
    for p in root.iter("Parameter"):
        nm = p.get("name") or ""
        if not nm:
            a = p.find("Attributes")
            nm = (a.get("name") or "") if a is not None else ""
        if not nm:
            continue
        o = p.find("O")
        default = (o.text or "").strip() if o is not None else ""
        if not default:
            default = (p.get("value") or "").strip()
        params[nm] = default
    return params


def _table_datas(root) -> list:
    """[(数据集名, 连接名, SQL, PageQuery)] —— 只取 DBTableData。"""
    out = []
    if root is None:
        return out
    for td in root.iter("TableData"):
        if "DBTableData" not in (td.get("class") or ""):
            continue
        name = td.get("name") or "<匿名数据集>"
        conn = ""
        cn = td.find("./Connection/DatabaseName")
        if cn is not None:
            conn = (cn.text or "").strip()
        q = td.find("./Query")
        sql = (q.text or "") if q is not None else ""
        pq = td.find("./PageQuery")
        page = (pq.text or "") if pq is not None else ""
        out.append((name, conn, sql, page))
    return out


def _sql_refs(sql: str) -> set:
    """抽取 SQL 内 ${...} 引用的裸标识符。

    先剔除字符串字面量(单/双引号), 避免把 if(len(p)==0,"",\"and col='\"+p+\"'\") 守卫写法
    里的列名/字面量(如 'ALL')误当参数; 再剔除 if/len/and/or 等函数名与 fine_* 系统参数。
    """
    s = re.sub(r"'(?:[^']|'')*'", "''", sql or "")
    s = re.sub(r'"(?:[^"]|"")*"', '""', s)
    refs = set()
    # 宏表达式内常见函数名(大小写不敏感; SQL 侧大写 LEN/IF/AND 等会被误当参数名,
    # 夜间批次 A39 实测 4028 的 ${if(LEN(p)==0,...)} 误报 "SQL 引用参数 ${LEN}"):
    stop = {"if", "len", "and", "or", "true", "false", "now", "today", "concatenate"}
    for block in re.findall(r"\$\{([^}]*)\}", s):
        for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", block):
            if tok.lower() in stop:
                continue
            if tok.startswith("fine_"):  # 用户全局系统参数, 无需模板声明
                continue
            refs.add(tok)
    return refs


def _widget_names(root) -> set:
    """参数面板/表单控件名集合(WidgetName name / Widget name)。"""
    names = set()
    if root is None:
        return names
    for e in root.iter("WidgetName"):
        if e.get("name"):
            names.add(e.get("name"))
    for e in root.iter("Widget"):
        if e.get("name"):
            names.add(e.get("name"))
    return names


def _cell_map(root) -> dict:
    """<(c, r) 0-based> -> <C 元素>。"""
    cells = {}
    if root is None:
        return cells
    for c in root.iter("C"):
        ca, ra = c.get("c"), c.get("r")
        if ca is None or ra is None:
            continue
        try:
            cells[(int(ca), int(ra))] = c
        except ValueError:
            continue
    return cells


def _cell_type(c_el) -> str:
    """单元格内容类型: 'number' | 'formula' | 'text' | 'other'。"""
    o = c_el.find("O")
    if o is None:
        return "other"
    t = o.get("t")
    if t in ("Number", "Formula"):
        return t.lower()
    text = (o.text or "").strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", text):
        return "number"
    return "text"


def _col_to_idx(col: str) -> int:
    idx = 0
    for ch in col:
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def _formula_cells(formula: str) -> list:
    return [(m.group(1), int(m.group(2))) for m in
            re.finditer(r"([A-Z]{1,3})(\d+)", formula or "")]


def _parent_map(root) -> dict:
    return {c: p for p in root.iter() for c in p}


def _in_param_panel(node, parent_map) -> bool:
    p = parent_map.get(node)
    while p is not None:
        if p.tag == "ParameterUI":
            return True
        if "WParameterLayout" in (p.get("class") or ""):
            return True
        if "ParameterLayout" in (p.get("class") or ""):
            return True
        p = parent_map.get(p)
    return False


# ---------------------------------------------------------------------------
# 1. doc-3315 定时调度支持的公式 —— scheduling 一致性检查
# ---------------------------------------------------------------------------
def check_schedule_formula(cpt_path: str):
    """doc-3315 定时调度支持的公式: 模板被用作调度对象时, 校验模板参数/数据集参数
    定义齐全、被公式判断引用的单元格存在于默认 sheet, 并提示「用户全局参数需勾选
    单独生成结果」「公式/主题/收件人过长可能致任务失败」。
    来源: doc-3315 (LEARNINGS.md 注1~注8)。"""
    out = []
    raw = _read_text(cpt_path)
    if not _has(raw, "定时调度", "调度对象", "schedule"):
        return [("WARN",
                 "未发现「定时调度对象」标记(扫描: 注释/文本含 定时调度|调度对象|schedule);"
                 "假设该模板未被用作调度对象, 跳过强校验。若将用于调度, 请标注或在 OPTIONS['schedule_spec'] 提供 spec(doc-3315)。")]
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验调度公式一致性(doc-3315)")]

    # ① 数据集参数声明齐全: SQL ${...} 裸变量必须声明于数据集参数(DBTableDataParameters/Parameters)
    # 或模板参数(fine_* 用户全局系统参数除外)
    tpl_params = _template_params(root)
    for td in root.iter("TableData"):
        if "DBTableData" not in (td.get("class") or ""):
            continue
        dname = td.get("name") or "?"
        q = td.find("./Query")
        sql = (q.text or "") if q is not None else ""
        declared = _dataset_param_names(td)
        for ref in sorted(_sql_refs(sql)):
            if ref not in declared and ref not in tpl_params:
                out.append(("ERROR",
                            "数据集 %s 的 SQL 引用 ${%s}, 但未声明于数据集参数/模板参数"
                            " —— 调度执行时取不到值, 结果空白且调度日志不指名(doc-3315 注3)"
                            % (dname, ref)))

    # ② 公式判断引用的单元格必须存在于默认 sheet
    formula = OPTIONS.get("dispatch_formula") or ""
    if not formula:
        m = re.search(r"(?:公式判断|执行条件)[^。\n]*?([A-Z]{1,3}\d+\s*[<>=!][^。\n]*)", raw)
        if m:
            formula = m.group(1).strip()
    if formula:
        cells = _cell_map(root)
        for col, row in _formula_cells(formula):
            key = (_col_to_idx(col), row - 1)
            if key not in cells:
                out.append(("ERROR",
                            "公式判断 %r 引用单元格 %s%d, 但默认 sheet 中不存在该单元格"
                            " —— 公式永远 false, 定时预警静默失效(doc-3315 注4)" % (formula, col, row)))
            else:
                ct = _cell_type(cells[key])
                if ct not in ("number", "formula"):
                    out.append(("WARN",
                                "公式判断 %r 引用单元格 %s%d 类型为 %s, 数值比较结果不可预期, "
                                "请确认是数值/聚合指标(doc-3315 注4)" % (formula, col, row, ct)))

    # ③ 提示: 用户全局参数需勾选「单独生成结果」
    if _has(raw, "$fine_username", "$fine_role", "$fine_position"):
        out.append(("OK",
                    "模板引用用户全局参数($fine_*): 调度侧须勾选「除通用结果外, 根据默认用户组"
                    "内的用户单独生成结果」才生效; 挂载平台/FTP/打印文件走通用结果时不可用"
                    "(doc-3315 注2)。"))

    # ④ 公式/主题/收件人过长可能致任务失败
    spec = OPTIONS.get("schedule_spec") or {}
    fh = spec.get("file_handle") or {}
    long_items = []
    for key, val in [("主题", fh.get("subject") or ""), ("收件人", fh.get("recipient") or "")]:
        if isinstance(val, str) and len(val) > 500:
            long_items.append("%s长度 %d" % (key, len(val)))
    for c_el in root.iter("C"):
        o = c_el.find("O")
        if o is not None and o.get("t") == "Formula" and len(o.text or "") > 1000:
            long_items.append("单元格公式长度 %d" % len(o.text or ""))
            break
    if long_items:
        out.append(("WARN", "存在过长项: %s —— 可能导致定时任务执行失败(doc-3315 注7)" % "; ".join(long_items)))

    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "调度公式一致性检查通过: 参数声明齐全, 无静默失败点(doc-3315)。"))
    return out


# ---------------------------------------------------------------------------
# 2. doc-3260 移动端简约下拉样式插件 —— 作用范围检查
# ---------------------------------------------------------------------------
DROP_CLASSES = ("com.fr.form.ui.ComboBox", "com.fr.form.ui.ComboCheckBox")
TREE_CLASSES = ("TreeComboBox", "com.fr.form.ui.TreeComboBox", "Tree")


def check_mobile_dropdown_scope(cpt_path: str):
    """doc-3260 移动端简约下拉样式插件: 仅覆盖表单 body 内的 ComboBox/ComboCheckBox;
    参数面板(ParameterUI/WParameterLayout)、填报 CPT、视图树控件(TreeComboBox)不被覆盖。
    移植 practice/topic_3260/check_mobile_style_scope.py。来源: doc-3260。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验移动端下拉样式作用范围(doc-3260)")]
    pm = _parent_map(root)
    found = 0
    for inner in root.iter("InnerWidget"):
        cls = inner.get("class") or ""
        wn = inner.find("WidgetName")
        name = (wn.get("name") if wn is not None else "") or (inner.findtext("WidgetName") or "")
        if any(t in cls for t in TREE_CLASSES):
            found += 1
            out.append(("WARN",
                        "视图树控件 [%s] (%s) 不被「移动端简约下拉样式插件」覆盖, 移动端无下拉美化"
                        "(doc-3260 §2.1)" % (name or "?", cls)))
            continue
        if not any(d in cls for d in DROP_CLASSES):
            continue
        found += 1
        if _in_param_panel(inner, pm):
            out.append(("WARN",
                        "参数面板下拉控件 [%s] (%s) 不被插件覆盖 —— 设了插件也毫无变化, "
                        "改用参数面板 CSS 注入(doc-3260 §2.1)" % (name or "?", cls)))
        else:
            out.append(("OK", "表单 body 下拉控件 [%s] (%s) 可被该插件样式化(doc-3260)" % (name or "?", cls)))
    if not found:
        out.append(("OK", "未发现下拉/下拉复选框/视图树控件, 本规则不适用(doc-3260)。"))
    return out


# ---------------------------------------------------------------------------
# 3. doc-3045 日期移动端日历样式插件 —— 作用范围 + 根节点检查
# ---------------------------------------------------------------------------
DATE_CLASSES = ("com.fr.form.ui.DateEditor",)


def check_mobile_calendar_scope(cpt_path: str):
    """doc-3045 日期移动端日历样式插件: 仅决策报表(<Form>) body 内的 DateEditor 生效;
    参数面板内 DateEditor 不支持; 普通报表 .cpt(<WorkBook>) 不受其影响。
    移植 practice/topic_3045/check_mobile_calendar_scope.py(与 doc-3260 合并为
    mobile-plugin-scope 通用规则)。来源: doc-3045。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验移动端日历样式作用范围(doc-3045)")]
    root_tag = root.tag
    if root_tag != "Form":
        out.append(("WARN",
                    "根节点为 <%s>, 非决策报表 <Form>: 「日期移动端日历样式」插件只作用于"
                    "决策报表 body, 此模板不受其影响; 若需求是移动端日历美化, 请确认模板类型"
                    "(doc-3045 §2.1)" % root_tag))
    pm = _parent_map(root)
    found = 0
    for inner in root.iter("InnerWidget"):
        cls = inner.get("class") or ""
        if not any(c in cls for c in DATE_CLASSES):
            continue
        found += 1
        wn = inner.find("WidgetName")
        name = (wn.get("name") if wn is not None else "") or (inner.findtext("WidgetName") or "")
        if _in_param_panel(inner, pm):
            out.append(("WARN",
                        "参数面板日期控件 [%s] 不被插件覆盖(doc-3045 明确不支持参数面板) —— "
                        "移动端美化改走参数面板 CSS 注入" % (name or "?")))
        elif root_tag == "Form":
            out.append(("OK",
                        "决策报表 body 日期控件 [%s] 可设「移动端>样式模板」(默认/导航日历/简约日历), "
                        "需服务器/JAR/APP/HTML5 插件 ≥ V10.4.49(doc-3045 §1.1)" % (name or "?")))
        else:
            out.append(("WARN",
                        "普通报表 .cpt 内日期控件 [%s] 不在插件作用范围(仅决策报表 body 生效)"
                        % (name or "?")))
    if not found:
        out.append(("OK", "未发现 DateEditor 日期控件, 本规则不适用(doc-3045)。"))
    return out


# ---------------------------------------------------------------------------
# 4. doc-299 预览模板数据集配置错误 —— 数据集/连接配置规则组
# ---------------------------------------------------------------------------
def _dataset_param_names(td) -> set:
    """数据集级参数声明名(兼容 DBTableDataParameters 与 Parameters 两种包装)。"""
    names = set()
    for pp in list(td.findall("./DBTableDataParameters/Parameter")) + list(td.findall("./Parameters/Parameter")):
        nm = pp.get("name") or ""
        if not nm:
            a = pp.find("Attributes")
            nm = (a.get("name") or "") if a is not None else ""
        if nm:
            names.add(nm)
    return names


def _conn_name_of(td) -> str:
    """数据连接名: 优先 <Connection class=..NameDatabaseConnection><DatabaseName>(text),
    兼容 <Database name=".."/> 形态。"""
    cn = td.find("./Connection/DatabaseName")
    if cn is not None and (cn.text or "").strip():
        return (cn.text or "").strip()
    db = td.find("Database")
    if db is not None and (db.get("name") or "").strip():
        return (db.get("name") or "").strip()
    return ""


def check_dataset_conn(cpt_path: str):
    """doc-299 预览模板数据集配置错误: ①每个 TableData 的 <Database name> 非空
    (空则预览报 31300013); ②给定连接名白名单时断言引用名全部在内(否则 WARN);
    ③<Query> 内 ${...} 裸变量必须声明于 DBTableDataParameters/模板参数(否则 ERROR,
    11300001 隐患)。移植 practice/topic_299/check_dataset_conn.py。来源: doc-299。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验数据集/连接配置(doc-299)")]
    tables, tpl_params = [], _template_params(root)
    for td in root.iter("TableData"):
        if "DBTableData" not in (td.get("class") or ""):
            continue
        tname = td.get("name") or "?"
        q = td.find("Query")
        sql = (q.text or "") if q is not None else ""
        tables.append((tname, _conn_name_of(td), sql, td))
    if not tables:
        return [("OK", "未发现任何 TableData 数据集, 本规则不适用(doc-299)。")]
    whitelist = OPTIONS.get("conn_whitelist")
    for tname, conn, sql, td in tables:
        if not conn:
            out.append(("ERROR",
                        "数据集 [%s] 数据连接名为空(<Connection>/<Database name> 缺失) -> 预览将报"
                        "31300013「找不到数据连接」(doc-299)" % tname))
        elif whitelist is not None and conn not in whitelist:
            out.append(("WARN",
                        "数据集 [%s] 连接名 %r 不在目标服务器连接白名单内, 需先配好"
                        "(连接存在性属服务器侧, doc-299)" % (tname, conn)))
        declared = _dataset_param_names(td)
        for ref in sorted(_sql_refs(sql)):
            if ref not in declared and ref not in tpl_params:
                out.append(("ERROR",
                            "数据集 [%s] SQL 引用参数 ${%s} 但未在 DBTableDataParameters/模板参数"
                            "中声明 -> 11300001 数据集配置错误隐患(doc-299)" % (tname, ref)))
    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "数据集/连接配置检查通过: 连接名非空、参数声明齐全(doc-299)。"))
    return out


# ---------------------------------------------------------------------------
# 5. doc-1123 Excel 导出 —— 行式引擎 + 分Sheet / 超长数值列
# ---------------------------------------------------------------------------
LONG_NUM_HEADERS = ("身份证", "证件号", "银行卡", "卡号", "手机号", "电话")


def check_excel_export_rowengine_sheet(cpt_path: str):
    """doc-1123 Excel导出: ①行式引擎(RowEngineAttr.rowEngineEnabled=true)开启时
    配置分Sheet导出(extype=sheet) -> ERROR; ②身份证/银行卡类超长数值列未按文本处理
    (未见 TO_TEXT/CAST AS CHAR) -> WARN(15 位精度静默失真)。来源: doc-1123。"""
    out = []
    raw = _read_text(cpt_path)
    root = _load_root(cpt_path)
    eng = _row_engine_enabled(root)
    if eng and re.search(r"extype\s*=\s*['\"]?sheet", raw, re.I):
        out.append(("ERROR",
                    "行式引擎已开启却配置分Sheet导出(extype=sheet): 行式引擎不支持分 Sheet, "
                    "该导出会静默失效/回退(doc-1123 注1)"))
    if not eng and not re.search(r"excel|导出|extype", raw, re.I):
        return [("OK", "未发现 Excel 导出相关配置, 本规则不适用(doc-1123)。")]
    # ② 超长数值列: 表头命中关键字且未见文本化处理 → 15 位精度坑
    hit_headers = [h for h in LONG_NUM_HEADERS if h in raw]
    if hit_headers:
        if not re.search(r"TO_TEXT|CAST\s*\([^)]*AS\s+CHAR|text\s*=\s*['\"]true|TextFormat",
                         raw, re.I):
            out.append(("WARN",
                        "检测到超长数值类表头(%s): 若其单元格为数值格式, 超过 15 位会静默失真, "
                        "建议按文本处理(TO_TEXT / CAST AS CHAR / 文本格式)(doc-1123 注2)"
                        % "、".join(hit_headers)))
        else:
            out.append(("OK", "超长数值列已按文本处理(命中 TO_TEXT/CAST/文本格式), 无精度风险(doc-1123)。"))
    if eng:
        out.append(("OK", "行式引擎已开启: 注意 Excel 导出会回退 2003 .xls(见 xlsx_readiness 规则, doc-1123/1121)。"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "Excel 导出一致性检查通过(doc-1123)。"))
    return out


# ---------------------------------------------------------------------------
# 6. doc-1123/.xlsx 导出就绪(行式引擎回退 + poi2007 部署清单)
# ---------------------------------------------------------------------------
def check_xlsx_readiness(cpt_path: str):
    """doc-1121/.xlsx 导出就绪: 行式引擎开启时 Excel 导出强制回退 2003 .xls(即便服务端
    配了 poi2007_fat.jar); 并输出部署清单提示(JAR<2016-10-10 需手动放 jar / >= 内置;
    JDK1.8>=8u102)。移植 practice/topic_1121/xlsx_readiness.py。来源: doc-1123/doc-1121。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验 .xlsx 导出就绪(doc-1121)")]
    eng = _row_engine_enabled(root)
    if eng:
        out.append(("WARN",
                    "行式引擎(RowEngineAttr@rowEngineEnabled=true)已开启: 即便服务端部署了 "
                    "poi2007_fat.jar, Excel 导出仍回退为 2003(.xls)。需 .xlsx 请关闭该模板行式引擎"
                    "(doc-1121 注)"))
    else:
        out.append(("OK", "行式引擎未开启, 模板级不阻止 .xlsx 导出(doc-1121)。"))
    out.append(("OK", "部署清单提示: JAR<2016-10-10 需手动拷贝 poi2007_fat.jar 到 "
                      "%FR_HOME%/webapps/webroot/WEB-INF/lib; JAR>=2016-10-10 poi 已内置; "
                      "设计器需 JDK1.8 且小版本 >= 8u102; .xlsx 链路不支持移动端(doc-1121)。"))
    return out


# ---------------------------------------------------------------------------
# 7. doc-786 导出 Excel 方式选择控件插件 —— 工具栏导出按钮体检
# ---------------------------------------------------------------------------
BUILTIN_EXPORT = {"ExcelP", "ExcelO", "ExcelS", "Word", "PDF", "Image"}
NON_EXPORT = {"First", "Previous", "Next", "Last", "PageNavi", "Separator",
              "Print", "Email", "Save", "Submit", "Import", "AppendRow",
              "DeleteRow", "Verify", "StashRow", "Search", "Flash"}


def check_export_toolbar(cpt_path: str):
    """doc-786 工具栏导出按钮体检: ①<ShortCut name> 不在内置白名单 -> WARN(FR 静默丢弃);
    ②命中 Excel*03 插件模式 -> 提示插件依赖(V2.1.4, FR>=8.0, JAR>=2016-07-30)且移动端不支持;
    ③可选 --require-dual 断言 03/07 双通道(此处仅提示)。移植 practice/topic_786/check_export_toolbar.py。
    来源: doc-786。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法体检导出工具栏(doc-786)")]
    names = [sc.get("name") for sc in root.iter("ShortCut") if sc.get("name")]
    if not names:
        return [("OK", "未发现工具栏 ShortCut, 本规则不适用(doc-786)。")]
    exports, plugin_like, unknown = [], [], []
    for n in names:
        low = n.lower()
        if n in BUILTIN_EXPORT:
            exports.append(n)
        elif n in NON_EXPORT:
            continue
        elif "excel" in low and "03" in low:
            plugin_like.append(n)
        else:
            unknown.append(n)
    for n in exports:
        out.append(("OK", "内置导出按钮 %s 无需插件, 无头等价 URL 见 doc-1123 三模式(doc-786)" % n))
    if plugin_like:
        out.append(("WARN",
                    "插件依赖按钮 %s: 依赖「导出 Excel 方式选择控件」插件(V2.1.4, FR>=8.0, "
                    "JAR>=2016-07-30), 目标服务器未装插件时按钮静默消失; 且该插件不支持移动端"
                    "(doc-786)" % "、".join(plugin_like)))
    if unknown:
        out.append(("WARN",
                    "未识别 ShortCut %s: name 写错时按钮不报错、直接不渲染, 请与设计器保存结果"
                    "diff 核对(doc-786)" % "、".join(unknown)))
    if plugin_like and not exports:
        out.append(("WARN", "只有 03 导出路径: 大数据量会撞 2003 单 sheet 行列上限(doc-1121)。"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "工具栏导出按钮全部为内置白名单, 无插件依赖(doc-786)。"))
    return out


# ---------------------------------------------------------------------------
# 8. doc-1130 Word 导出页眉页脚
# ---------------------------------------------------------------------------
def check_word_export(cpt_path: str):
    """doc-1130 Word 导出页眉页脚: ①ReportPageAttr.topMargin==12.7(否则每页多一行空白行);
    ②页眉/页脚容器内无直接 <Image> 元素(仅允许 BackgroundImage, 否则多空白页)。
    移植 practice/topic_1130/set_word_export_headerfooter.py check_word_export。来源: doc-1130。"""
    out = []
    raw = _read_text(cpt_path)
    # 触发条件: 模板自身与 Word 导出/页眉页脚明确相关 ——
    #  (a) 有页眉/页脚/WordExportAttr/Word 工具栏按钮等结构标记;
    #  (b) 或 format=word 且模板自带页面设置(ReportPageAttr), 排除路由跳转其它模板导出的场景。
    structural = (_has(raw, "WordExportAttr", "PageHeader", "PageFooter", "页眉", "页脚")
                  or bool(re.search(r'<ShortCut\s+name="Word"', raw)))
    word_fmt = _has(raw, "format=word")
    page_attr_present = "ReportPageAttr" in raw
    if not (structural or (word_fmt and page_attr_present)):
        return [("OK", "未发现 Word 导出/页眉页脚相关配置, 本规则不适用(doc-1130)。")]
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验 Word 导出页眉页脚(doc-1130)")]
    pa = root.find("ReportPageAttr")
    if pa is None:
        out.append(("ERROR", "缺少 ReportPageAttr: 未设页面边距, 导出 Word 极可能多出空白行(doc-1130)"))
    else:
        top = pa.get("topMargin", "")
        if top != "12.7":
            out.append(("ERROR",
                        "页面上边距=%r 非 12.7mm: Word 默认页眉距顶端 12.7mm, 不一致会导致导出 Word "
                        "除第一页外每页多出一行空白行(doc-1130)" % top))
        else:
            out.append(("OK", "页面上边距为 12.7mm, 与 Word 页眉对齐(doc-1130)。"))
    for tag in ("PageHeader", "PageFooter"):
        container = root.find(tag)
        if container is None:
            continue
        for img in container.iter("Image"):
            out.append(("ERROR",
                        "%s 内出现直接 <Image> 元素: 页面会被撑开, 导出 Word 多出空白页; "
                        "应改用「背景元素>图片」(BackgroundImage)(doc-1130)" % tag))
    if not any(lv == "ERROR" for lv, _ in out):
        out.append(("OK", "Word 导出页眉页脚检查通过(doc-1130)。"))
    return out


# ---------------------------------------------------------------------------
# 9. doc-1128 Word 导出自动调整行高
# ---------------------------------------------------------------------------
def check_word_rowheight(cpt_path: str):
    """doc-1128 Word 导出自动调整行高: 凡 spec 声明「导出可编辑 Word」且 WordExportAttr 为空
    或 fixRowHeight=true -> WARN「二次编辑行高不自动变化」; 该开关仅 PC 分页预览生效、
    移动端不支持。来源: doc-1128。"""
    out = []
    raw = _read_text(cpt_path)
    root = _load_root(cpt_path)
    word_marker = _has(raw, "word", "WordExportAttr", "format=word", "导出word", "可编辑word")
    if not word_marker:
        return [("WARN",
                 "未发现「导出可编辑 Word」标记(扫描: word|WordExportAttr|format=word|导出word);"
                 "假设本模板不走 Word 二次编辑导出, 跳过强校验(doc-1128)。")]
    wea = None
    if root is not None:
        wea = root.find(".//WordExportAttr")
    if wea is None or wea.get("fixRowHeight", "").strip().lower() == "true":
        out.append(("WARN",
                    "Word 导出未设「不固定行高」(WordExportAttr 为空或 fixRowHeight=true): 导出为"
                    "可编辑 Word 后二次编辑时行高不随内容自动变化; 该开关仅 PC 分页预览生效, "
                    "移动端不支持(doc-1128)"))
    else:
        out.append(("OK", "已设不固定行高(fixRowHeight!=true), Word 二次编辑行高可自动变化(doc-1128)。"))
    return out


# ---------------------------------------------------------------------------
# 10. doc-4524 大数据集导出 —— 方案/模板类型一致性 + 层式报表仅导出当前页
# ---------------------------------------------------------------------------
def check_bigdata_export_route(cpt_path: str):
    """doc-4524 大数据集导出: ①JS 导出方案目标为 .cptx, 或新引擎方案却声明「选字段」-> WARN;
    ②层式报表+多数据集+分页/原样/分页分sheet 导出组合 -> WARN「仅导出当前页」;
    ③导出模板的 ${参数} 与模板参数一一对应。来源: doc-4524。"""
    out = []
    raw = _read_text(cpt_path)
    bigdata = _has(raw, "direct/export", "directExportToExcel", "大数据", "bigdata",
                   "format=excel", "extype=")
    if not bigdata:
        return [("OK", "未发现大数据导出/导出 URL 标记, 本规则不适用(doc-4524)。")]
    root = _load_root(cpt_path)
    ext = os.path.splitext(cpt_path)[1].lower()

    # ① 方案与模板类型一致性
    if "directExportToExcel" in raw and ext in (".cptx", ".frm"):
        out.append(("WARN",
                    "JS 方案(directExportToExcel)仅支持 .cpt 普通报表, 当前文件为 %s —— "
                    "该导出链路会静默失效(doc-4524 §2 支持矩阵)" % ext))
    if _has(raw, "direct/export") and _has(raw, "选字段", "colNames", "字段选择"):
        out.append(("WARN",
                    "新计算引擎(direct/export)导出不支持「选字段」, 却声明了字段选择 —— 设置失效"
                    "(doc-4524 §2 支持矩阵)"))

    # ② 层式报表 + 多数据集 + 分页类导出 -> 仅导出当前页
    n_ds = len(_table_datas(root))
    layered = _row_engine_enabled(root) or _has(raw, "层式", "rowengine", "行式")
    page_export = re.search(r"extype\s*=\s*['\"]?(page|simple|sheet)", raw, re.I)
    if layered and n_ds >= 2 and page_export:
        out.append(("WARN",
                    "层式报表(行式引擎)+%d 个数据集+分页/原样/分页分sheet 导出组合: 层式报表导出"
                    "只导出当前页数据, 大数据全量导出不能依赖它(doc-4524 §2.3)" % n_ds))

    # ③ 导出 ${参数} 与模板参数一一对应
    tpl_params = _template_params(root)
    export_params = set()
    for m in re.finditer(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", raw):
        export_params.add(m.group(1))
    for p in sorted(export_params):
        if p not in tpl_params:
            out.append(("WARN",
                        "导出引用参数 ${%s} 但模板未定义该参数: 按参数面板条件导出对应数据将取空"
                        "(doc-4524 §2.4)" % p))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "大数据导出方案/类型/参数一致性检查通过(doc-4524)。"))
    return out


# ---------------------------------------------------------------------------
# 11. doc-4524 大数据集导出 —— 1000W*20 列上限自检(无头导出工具沉淀)
# ---------------------------------------------------------------------------
def check_bigdata_export_scale(cpt_path: str):
    """doc-4524 大数据集导出上限自检: 无头导出前核对行/列数是否超「1000W 行 * 20 列」,
    超阈值提示分批/缩列后再触发导出 URL, 避免「导出成功却只落部分数据」的静默问题。
    行/列数由 OPTIONS['total_rows']/['total_cols'] 提供。来源: doc-4524。"""
    out = []
    raw = _read_text(cpt_path)
    if not _has(raw, "direct/export", "directExportToExcel", "大数据", "bigdata", "format=excel"):
        return [("OK", "未发现大数据导出标记, 本规则不适用(doc-4524)。")]
    rows, cols = OPTIONS.get("total_rows"), OPTIONS.get("total_cols")
    if rows is None or cols is None:
        return [("WARN",
                 "无法核对 1000W*20 列上限(OPTIONS['total_rows']/['total_cols'] 未提供): "
                 "无头大数据导出须自行分批/缩列, 否则可能只导出部分数据且无报错(doc-4524 §2.1)。")]
    cells = int(rows) * int(cols)
    if cells > 1000_0000 * 20:
        out.append(("WARN",
                    "预计 %d 行 × %d 列(共 %d 单元格)超「1000W 行*20 列」建议上限: "
                    "可能只导出部分数据且无报错, 请分批或缩列后再触发导出 URL(doc-4524 §2.1)"
                    % (rows, cols, cells)))
    else:
        out.append(("OK", "预计 %d 行 × %d 列在 1000W*20 建议上限内(doc-4524)。" % (rows, cols)))
    return out


# ---------------------------------------------------------------------------
# 12. doc-3710 根据参数选择导出不同报表 —— report-router 一致性
# ---------------------------------------------------------------------------
def _normalize_path(path: str) -> str:
    p = (path or "").replace("\\", "/").strip()
    if p.lower().startswith("reportlets/"):
        p = p[len("reportlets/"):]
    p = p.lstrip("/")
    if p and not p.lower().endswith(".cpt"):
        p += ".cpt"
    return p


def check_report_router(cpt_path: str):
    """doc-3710 report-router 一致性: 路由下拉框字典实际值必须是 reportlets 相对路径
    —— 无反斜杠、去 reportlets/ 前缀、补 .cpt 后缀, 否则重定向到不存在的 viewlet 静默 404;
    并校验导出按钮 __filename__ 来源的文本控件(NAME)存在且有非空兜底。
    移植 practice/topic_3710/gen_report_router.py normalize_path 思路。来源: doc-3710。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验 report-router(doc-3710)")]
    raw = _xml_text(root)
    items = list(root.iter("DictItem"))
    if not items and "viewlet" not in raw and "__filename__" not in raw:
        return [("OK", "未发现路由下拉字典/导出按钮, 本规则不适用(doc-3710)。")]
    for it in items:
        actual = it.get("actual") or ""
        if "\\" in actual:
            out.append(("ERROR",
                        "下拉字典实际值 %r 含反斜杠: 必须改为 '/' 的 reportlets 相对路径, "
                        "否则重定向 404(doc-3710 注)" % actual))
        if actual.lower().startswith("reportlets/"):
            out.append(("ERROR",
                        "下拉字典实际值 %r 不应带 reportlets/ 前缀(相对路径以报表名开头)(doc-3710 注)"
                        % actual))
        if actual and not actual.lower().endswith(".cpt"):
            out.append(("ERROR",
                        "下拉字典实际值 %r 缺 .cpt 后缀: 重定向到不存在的 viewlet 静默 404(doc-3710)"
                        % actual))
        if actual and actual.startswith("/"):
            out.append(("WARN",
                        "下拉字典实际值 %r 以 '/' 开头: 应为 reportlets 下相对路径(doc-3710)" % actual))
    # __filename__ 来源控件: NAME 必须存在且有非空兜底
    widgets = _widget_names(root)
    for m in re.finditer(r"__filename__\s*[=+]\s*[^;]*?getWidgetByName\(\s*['\"]([^'\"]+)['\"]", raw):
        wname = m.group(1)
        if wname not in widgets:
            out.append(("WARN",
                        "导出按钮 __filename__ 引用控件 %r, 但模板中不存在该控件 —— 文件名恒空"
                        "(doc-3710 注)" % wname))
        else:
            val = ""
            for e in root.iter("Widget"):
                if e.get("name") == wname or (e.find("WidgetName") is not None
                                              and (e.find("WidgetName").get("name") or "") == wname):
                    wv = e.find("WidgetValue")
                    if wv is not None:
                        val = (wv.text or "").strip()
                    break
            if not val:
                out.append(("WARN",
                            "文件名控件 %r 默认值为空: 自定义文件名不支持为空, 建议给非空兜底"
                            "(doc-3710 硬约束①)" % wname))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "report-router 路径/文件名一致性检查通过(doc-3710)。"))
    return out


# ---------------------------------------------------------------------------
# 13. doc-1819 工具栏按钮只导出单一格式文件
# ---------------------------------------------------------------------------
VALID_FORMATS = {"text", "word", "excel", "pdf"}


def check_toolbar_single_export(cpt_path: str):
    """doc-1819 工具栏导出按钮体检: 凡 <ToolBarButton> 点击 JS 以 JS 标识符形态引用
    servletURL + '?viewlet='(注意: 用 ${servletURL} 模板变量形态是 FR 内置变量, 不算),
    断言 <Parameters> 同时含 servletURL/reportName 且值为公式(否则导出 URL 静默为空),
    并校验 format ∈ {text,word,excel,pdf}。来源: doc-1819。"""
    out = []
    raw = _read_text(cpt_path)
    # 仅当 servletURL 以裸 JS 标识符出现(前面不是 $ / { / 字母 / 数字 / 下划线), 才是 JS 变量形态
    bare = re.search(r"(?<![${\w])servletURL", raw)
    if not bare or "viewlet" not in raw:
        return [("OK", "未发现 JS 标识符形态的 servletURL+viewlet 导出按钮(用 ${servletURL} "
                 "模板变量属内置变量, 不适用), 本规则不适用(doc-1819)。")]
    root = _load_root(cpt_path)
    param_names = set()
    if root is not None:
        for p in root.iter("Parameter"):
            nm = p.get("name") or ""
            if not nm:
                a = p.find("Attributes")
                nm = (a.get("name") or "") if a is not None else ""
            if nm:
                param_names.add(nm)
    js_blocks = re.findall(r"servletURL[^;\n]*viewlet[^;\n]*", raw) or \
                re.findall(r"viewlet[^;\n]*servletURL[^;\n]*", raw)
    if not js_blocks:
        return [("OK", "servletURL 与 viewlet 未出现在同一 JS 表达式, 本规则不适用(doc-1819)。")]
    if "servletURL" not in param_names or "reportName" not in param_names:
        out.append(("ERROR",
                    "导出按钮 JS 用 servletURL+viewlet 拼导出 URL, 但 <Parameters> 未同时声明 "
                    "servletURL/reportName(且应为公式) —— 导出 URL 静默为空(doc-1819 头号坑)"))
    else:
        out.append(("OK", "servletURL/reportName 参数已声明(doc-1819)。"))
    fm = re.search(r"format\s*=\s*['\"]?(\w+)", raw)
    if fm and fm.group(1).lower() not in VALID_FORMATS:
        out.append(("WARN",
                    "导出 format=%r 不在白名单 %s —— 可能静默导出非预期格式(doc-1819)"
                    % (fm.group(1), sorted(VALID_FORMATS))))
    return out


# ---------------------------------------------------------------------------
# 14. doc-2208 定时调度任务设置 —— 调度就绪度
# ---------------------------------------------------------------------------
def check_schedule_ready(cpt_path: str):
    """doc-2208 调度就绪度: 凡标为「将挂定时调度」的 .cpt, 断言 <ReportParameterAttr> 下每个
    模板参数要么有非空默认值 <O>, 要么在调度 spec「参数设置」中显式绑定; 两者皆无判 ERROR;
    「调度 spec 中存在但模板中没有」的参数判 WARN(点刷新会消失)。
    移植 practice/topic_2208/check_schedule_ready.py。来源: doc-2208。"""
    out = []
    raw = _read_text(cpt_path)
    if not _has(raw, "定时调度", "调度对象", "schedule") and OPTIONS.get("schedule_spec") is None:
        return [("WARN",
                 "未发现「定时调度对象」标记且未提供 OPTIONS['schedule_spec']; 假设未挂调度, "
                 "跳过参数闭合校验(doc-2208)。")]
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验调度就绪度(doc-2208)")]
    tpl_params = _template_params(root)
    spec = OPTIONS.get("schedule_spec") or {}
    spec_params = {p.get("name"): p for p in (spec.get("object") or {}).get("params", [])}
    if not tpl_params and not spec_params:
        return [("OK", "模板无参数, 调度就绪度检查通过(doc-2208)。")]
    for name, default in sorted(tpl_params.items()):
        if default:
            out.append(("OK", "模板参数 %s 有默认值 %r(调度执行可取到值)(doc-2208)" % (name, default)))
        elif name in spec_params:
            out.append(("OK", "模板参数 %s 无默认值, 但调度「参数设置」已配置(doc-2208)" % name))
        else:
            out.append(("ERROR",
                        "模板参数 %s 既无模板默认值, 调度「参数设置」也未配置 -> 定时执行时取空, "
                        "结果报表空白/SQL 报错(静默)(doc-2208)" % name))
    for name in sorted(set(spec_params) - set(tpl_params)):
        out.append(("WARN",
                    "调度里手工添加的参数 %s 在模板中不存在: 点「刷新」会使其消失, 建议收敛为"
                    "模板参数(doc-2208 4.4 注2)" % name))
    return out


# ---------------------------------------------------------------------------
# 15. doc-866 权限细粒度模板内容控制 —— 12 条规则
# ---------------------------------------------------------------------------
EAGER_INIT_WIDGETS = {"RadioGroup", "CheckBox", "CheckBoxGroup", "ComboCheckBox"}
MOUNT_TO_PREVIEW = {"填报": "write", "分页": "page", "分析": "view"}

CELL_RE = re.compile(r"^([A-Z]{1,3})([1-9]\d*)$")


def _cell_to_rc(ref: str):
    m = CELL_RE.match((ref or "").strip().upper())
    if not m:
        return None
    col = 0
    for ch in m.group(1):
        col = col * 26 + (ord(ch) - 64)
    return col - 1, int(m.group(2)) - 1


def _expand_range(ref: str):
    parts = re.split(r"[~:]", (ref or "").strip())
    if len(parts) == 1:
        rc = _cell_to_rc(parts[0])
        return None if rc is None else [rc]
    if len(parts) != 2:
        return None
    a, b = _cell_to_rc(parts[0]), _cell_to_rc(parts[1])
    if a is None or b is None:
        return None
    out = []
    for c in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
        for r in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
            out.append((c, r))
    return out


def validate_privilege_spec(spec: dict):
    """doc-866 细粒度权限 spec 校验(移植 practice/topic_866/privilege_spec.py 的 12 条 R0~R12)。
    返回 [(level, msg), ...]。来源: doc-866。"""
    out = []
    sheets = spec.get("sheets") or []
    sheet_names = [s["name"] for s in sheets]
    mount = spec.get("mount_type")
    view_carriers = set(spec.get("platform_view_carriers") or [])
    rules = spec.get("rules") or []

    if not sheets:
        out.append(("ERROR", "R0-no-sheet: spec 未声明任何 sheet, 无法定位权限锚点(doc-866)"))
    if mount not in MOUNT_TO_PREVIEW:
        out.append(("ERROR", "R0-mount: mount_type 必须是 %s 之一(doc-866)"
                    % "/".join(MOUNT_TO_PREVIEW)))
    if not view_carriers:
        out.append(("ERROR", "R0-no-view: 未声明 platform_view_carriers —— 细粒度权限前提是角色"
                    "对该目录有「查看」权限(doc-866 §2.9)"))

    hidden_sheets, hidden_cells, visible_cells, hidden_widgets = {}, {}, {}, {}
    roles_touched = set()
    for i, rule in enumerate(rules):
        tag = "rules[%d]" % i
        role = (rule.get("role") or "").strip()
        target = rule.get("target")
        sheet = rule.get("sheet")
        if not role:
            out.append(("ERROR", "R1-role-empty: %s: role 为空(doc-866)" % tag))
        else:
            roles_touched.add(role)
            if ">" in role and (len(role.split(">")) != 2 or not all(s.strip() for s in role.split(">"))):
                out.append(("ERROR", "R1-role-format: %s: role=%r 含 '>' 时必须是「部门>职务」两段"
                            "(doc-866)" % (tag, role)))
        if rule.get("visible") is True and target != "cell_newvalue":
            out.append(("WARN", "R2-redundant-allow: %s: role=%r 配 visible=True 冗余 —— 默认全可见, "
                        "只需为受限角色写 deny(doc-866 §2.3~2.6)" % (tag, role)))
        if target != "sheet" and sheet is not None and sheet not in sheet_names:
            out.append(("ERROR", "R3-sheet-missing: %s: sheet=%r 不在模板 sheet 列表 %s 中(doc-866)"
                        % (tag, sheet, sheet_names)))
        if target == "cell":
            cells = _expand_range(rule.get("range", ""))
            if cells is None:
                out.append(("ERROR", "R4-bad-range: %s: range=%r 非法(doc-866)" % (tag, rule.get("range"))))
            else:
                key = (role, sheet)
                (hidden_cells if rule.get("visible") is False else visible_cells).setdefault(key, set()).update(cells)
        elif target == "widget":
            rc = _cell_to_rc(rule.get("cell", ""))
            if rc is None:
                out.append(("ERROR", "R4-bad-cell: %s: cell=%r 非法(doc-866)" % (tag, rule.get("cell"))))
            else:
                hidden_widgets[(role, sheet, rc)] = rule.get("widget_type") or ""
                if rule.get("visible") is False and rule.get("usable") is True:
                    out.append(("OK", "R4-invisible-usable: %s: 控件 invisible=True 时 usable 无意义(doc-866)"
                                % tag))
        elif target in ("row", "col"):
            idx = rule.get("index")
            if not isinstance(idx, int) or idx < 0:
                out.append(("ERROR", "R5-bad-index: %s: %s 权限需 index(0-based 非负整数)(doc-866)"
                            % (tag, target)))
        elif target == "sheet":
            name = rule.get("name")
            if name not in sheet_names:
                out.append(("ERROR", "R3-sheet-missing: %s: sheet name=%r 不在模板 sheet 列表(doc-866)"
                            % (tag, name)))
            elif rule.get("visible") is False:
                hidden_sheets.setdefault(role, set()).add(name)
        elif target == "toolbar":
            pm = rule.get("preview_mode")
            if pm not in ("write", "page", "view"):
                out.append(("ERROR", "R6-preview-missing: %s: 工具栏权限必须显式声明 preview_mode(doc-866)"
                            % tag))
            elif mount in MOUNT_TO_PREVIEW and pm != MOUNT_TO_PREVIEW[mount]:
                out.append(("ERROR", "R6-preview-mismatch: %s: 模板挂载类型=%s(应配 preview_mode=%s), "
                            "而权限配在 %s 下 —— 权限不生效且无任何报错(doc-866 §2.5 注1)"
                            % (tag, mount, MOUNT_TO_PREVIEW[mount], pm)))
            if not rule.get("buttons"):
                out.append(("ERROR", "R6-no-button: %s: toolbar 规则未指定 buttons(doc-866)" % tag))
        else:
            out.append(("ERROR", "R7-bad-target: %s: 未知 target=%r(doc-866)" % (tag, target)))

    for (role, sheet, rc), wtype in hidden_widgets.items():
        if rc not in hidden_cells.get((role, sheet), set()) and wtype in EAGER_INIT_WIDGETS:
            out.append(("WARN", "R8-eager-widget: role=%r sheet=%r 单元格(c=%d,r=%d): 控件 %s 属"
                        "「加载即初始化」, 控件不可见但单元格可见时数据不显示(doc-866 §2.4 注2)"
                        % (role, sheet, rc[0], rc[1], wtype)))
    total = len(sheet_names)
    for role, hs in hidden_sheets.items():
        if total and len(hs) >= total:
            out.append(("ERROR", "R9-all-sheet-hidden: role=%r 隐藏了全部 %d 个 sheet —— 角色打开模板"
                        "无任何内容(doc-866)" % (role, total)))
    for role in sorted(roles_touched):
        dept = role.split(">")[0] if ">" in role else role
        if view_carriers and role not in view_carriers and dept not in view_carriers:
            out.append(("WARN", "R10-no-view-right: role=%r 不在 platform_view_carriers 中: 该角色"
                        "打不开模板, 细粒度权限是死配置(doc-866)" % role))
    for (role, sheet), cells in hidden_cells.items():
        by_row, by_col = {}, {}
        for c, r in cells:
            by_row.setdefault(r, set()).add(c)
            by_col.setdefault(c, set()).add(r)
        for r, cs in by_row.items():
            if len(cs) >= 4 and max(cs) - min(cs) + 1 == len(cs):
                out.append(("OK", "R11-use-row: role=%r sheet=%r 第 %d 行连续隐藏 %d 格, 可直接设"
                            "「行不可见」(doc-866)" % (role, sheet, r, len(cs))))
        for c, rs in by_col.items():
            if len(rs) >= 4 and max(rs) - min(rs) + 1 == len(rs):
                out.append(("OK", "R11-use-col: role=%r sheet=%r 第 %d 列连续隐藏 %d 格, 可直接设"
                            "「列不可见」(doc-866)" % (role, sheet, c, len(rs))))
    for key, cells in hidden_cells.items():
        dup = cells & visible_cells.get(key, set())
        if dup:
            out.append(("ERROR", "R12-conflict: role=%r sheet=%r 单元格 %s 同时配可见与不可见(doc-866)"
                        % (key[0], key[1], sorted(dup))))
    return out


def check_privilege_content(cpt_path: str):
    """doc-866 权限细粒度模板内容控制: ①若提供 OPTIONS['privilege_spec'], 运行移植自
    practice/topic_866/privilege_spec.py 的 12 条 spec 校验(R0~R12);
    ②模板侧静态扫描: 加载即初始化控件(RadioGroup/CheckBox/CheckBoxGroup/ComboCheckBox)
    设不可见而单元格仍可见 -> WARN(该单元格数据不显示); ③盘点半模板权限控制节点。
    来源: doc-866。"""
    out = []
    spec = OPTIONS.get("privilege_spec")
    if spec is not None:
        out.extend(validate_privilege_spec(spec))
    root = _load_root(cpt_path)
    if root is None:
        if not out:
            return [("ERROR", "XML 解析失败, 无法校验细粒度权限(doc-866)")]
        return out
    raw = _xml_text(root)
    pm = _parent_map(root)

    # 模板侧: 控件可见性 + 类型
    eager_hits = 0
    for inner in root.iter("InnerWidget"):
        cls = inner.get("class") or ""
        wtype = cls.rsplit(".", 1)[-1]
        if wtype not in EAGER_INIT_WIDGETS:
            continue
        invisible = False
        wa = inner.find("WidgetAttr")
        if wa is not None:
            inv = wa.get("visible") or wa.get("invisible") or ""
            if inv.strip().lower() in ("false", "true") and wa.get("visible", "").lower() == "false":
                invisible = True
            if wa.get("invisible", "").lower() == "true":
                invisible = True
        pc = inner.find("PrivilegeControl")
        if not invisible and pc is not None:
            inv2 = pc.get("visible") or pc.get("invisible") or ""
            if inv2.strip().lower() == "false" or pc.get("invisible", "").lower() == "true":
                invisible = True
        if invisible:
            eager_hits += 1
            wn = inner.find("WidgetName")
            name = (wn.get("name") if wn is not None else "") or ""
            out.append(("WARN",
                        "加载即初始化控件 [%s](%s) 设不可见: 若所在单元格仍可见, 该单元格数据将不"
                        "显示 —— doc-866 §2.4 注2 头号静默坑" % (name or "?", cls)))
    if not eager_hits:
        if _has(raw, "PrivilegeControl", "权限编辑", "细粒度"):
            out.append(("OK", "模板含权限控制节点但未发现加载即初始化控件被隐藏, 通过(doc-866)。"))
    # 角色权限本体在平台侧(FineDB), 模板侧无法观察 -> 提示
    if _has(raw, "PrivilegeControl", "CellPrivilegeControl", "RowPrivilegeControl",
            "ColumnPrivilegeControl", "SheetPrivilegeControl"):
        out.append(("OK", "模板含细粒度权限节点; 角色->规则映射在平台侧, 建议提供 OPTIONS['privilege_spec'] "
                          "以运行 12 条 spec 校验(doc-866)。"))
    if not out:
        out.append(("OK", "未发现权限控制相关标记, 本规则不适用(doc-866)。"))
    return out


# ---------------------------------------------------------------------------
# 16. doc-865 权限细粒度参数控制
# ---------------------------------------------------------------------------
FINE_PARAMS = {"$fine_username", "$fine_display_name", "$fine_role", "$fine_position"}


def check_fine_param(cpt_path: str):
    """doc-865 权限细粒度参数控制: ①凡含 $fine_username/$fine_role/$fine_position 引用,
    断言大小写命中白名单, 否则 ERROR; ②$fine_role='...' 裸等号写法 -> WARN(多角色漏判,
    应改 find('角色',$fine_role)>0); ③${fine_username} 内联 SQL 检查引号包裹。
    移植 practice/topic_865/gen_role_filter.py validate_fine_param/role_formula 思路。来源: doc-865。"""
    out = []
    raw = _read_text(cpt_path)
    if "$fine_" not in raw and "${fine_" not in raw:
        return [("OK", "未发现 $fine_* 权限参数引用, 本规则不适用(doc-865)。")]
    # ① 大小写白名单
    for m in re.finditer(r"\$[A-Za-z_][A-Za-z0-9_]*", raw):
        tok = m.group(0)
        if tok.lower().startswith("$fine_") and tok not in FINE_PARAMS:
            out.append(("ERROR",
                        "系统参数 %r 大小写/拼写不在白名单 %s —— 权限过滤静默失效(doc-865 §3.3 注)"
                        % (tok, sorted(FINE_PARAMS))))
    # ② 裸等号
    for m in re.finditer(r"\$fine_role\s*=\s*'", raw):
        out.append(("WARN",
                    "检测到裸等号写法 %r: 多角色用户($fine_role 为 '角色1,角色2')会漏判, "
                    "应改 find('角色',$fine_role)>0(doc-865 §3.3 注)" % m.group(0)))
    # ③ ${fine_username} 内联 SQL 引号包裹
    root = _load_root(cpt_path)
    if root is not None:
        for td in root.iter("TableData"):
            q = td.find("./Query")
            if q is None or not (q.text or ""):
                continue
            sql = q.text
            for m in re.finditer(r"\$\{fine_username\}", sql):
                before = sql[max(0, m.start() - 3):m.start()]
                after = sql[m.end():m.end() + 3]
                if "'" not in before and "'" not in after:
                    out.append(("WARN",
                                "SQL 内联 ${fine_username} 未用引号包裹(如 '${fine_username}'): "
                                "注入形态错误, 可能整串取空(doc-865 §3.3)"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "$fine_* 参数引用检查通过: 大小写正确、无裸等号(doc-865)。"))
    return out


# ---------------------------------------------------------------------------
# 17. doc-684 定时调度邮件通知 —— 收件人=单元格
# ---------------------------------------------------------------------------
AGG_FUNCS = ("select", "sum(", "count(", "max(", "min(", "avg(", "countd(", "median(", "uniquearray(")


def check_email_recipient(cpt_path: str):
    """doc-684 定时调度邮件通知: 凡拟作「收件人=单元格」调度对象的, 断言该单元格公式为
    =ds.select(...)/聚合取数(纵向扩展)而非写死字面量, 且引用数据集存在; 否则邮件只会拿到
    一个固定值(群发退化为单发且不报错)。来源: doc-684。"""
    out = []
    raw = _read_text(cpt_path)
    spec = OPTIONS.get("schedule_spec") or {}
    fh = spec.get("file_handle") or {}
    recipient_marker = _has(raw, "收件人", "recipient", "邮件", "email") or bool(fh.get("recipient"))
    if not recipient_marker:
        return [("WARN",
                 "未发现「邮件通知/收件人」标记(扫描: 收件人|recipient|邮件|email); 假设本模板"
                 "不走「收件人=单元格」调度, 跳过强校验(doc-684)。")]
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验邮件收件人(doc-684)")]
    ds_names = {td.get("name") for td in root.iter("TableData") if td.get("name")}
    formula_cells = [c for c in root.iter("C")
                     if c.find("O") is not None
                     and (c.find("O").get("t") == "Formula"
                          or (c.find("O").text or "").strip().startswith("="))]
    if not formula_cells:
        return [("WARN",
                 "标记为邮件调度但 .cpt 无任何公式单元格: 若收件人取自单元格, 应为 =ds.select(...)"
                 "聚合取数而非字面量, 否则群发退化为单发(doc-684 §3.2 注2)")]
    agg_ok = 0
    for c in formula_cells:
        o = c.find("O")
        formula = (o.text or "")
        low = formula.lower()
        if any(f in low for f in AGG_FUNCS) or re.search(r"\.select\s*\(", low):
            agg_ok += 1
            for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\.select\s*\(", low):
                if m.group(1) not in ds_names:
                    out.append(("WARN",
                                "收件人公式 %r 引用数据集 %r, 但模板中不存在该数据集(doc-684 §3.2 注2)"
                                % (formula, m.group(1))))
        else:
            out.append(("WARN",
                        "公式单元格 %r 不是 ds.select/聚合取数: 收件人取不到扩展后的多值, "
                        "群发退化为单发且不报错(doc-684 §3.2 注2)" % formula))
    if agg_ok:
        out.append(("OK", "存在 %d 个聚合取数公式单元格, 收件人=单元格模式可用(doc-684)。" % agg_ok))
    return out


# ---------------------------------------------------------------------------
# 18. doc-135 分页预览(模板 Web 属性) —— 6 条
# ---------------------------------------------------------------------------
VERIFIED_SHORTCUTS = {"First", "Previous", "PageNavi", "Next", "Last", "ExcelO", "Print"}
LIKELY_SHORTCUTS = {"PDF", "Word", "Image", "Email", "Flash", "Excel", "ExcelP", "ExcelS",
                    "Export", "Search", "Refresh", "PageSetup", "Scale"}
HTML_TAG_RE = re.compile(r"<\s*/?\s*[A-Za-z][A-Za-z0-9]*[^>]*>")


def _ver_ge(a: str, b: str) -> bool:
    pa = [int(x) for x in re.findall(r"\d+", a)]
    pb = [int(x) for x in re.findall(r"\d+", b)]
    pa += [0] * (len(pb) - len(pa))
    pb += [0] * (len(pa) - len(pb))
    return pa >= pb


def check_page_preview(cpt_path: str):
    """doc-135 分页预览 6 条(移植 practice/topic_135/gen_page_preview.py inspect_cpt):
    ①<Report> 个数>1 且存在 <WebPageContent> -> ERROR(分页预览不显示 sheet 标签);
    ②<CSSImport> 出现在 <WebPageContent>/<WebWriteContent> 内部 -> ERROR(须上提为
    <ReportWebAttr> 直接子节点); ③ShortCut@name 不在已验证清单 -> WARN(静默丢弃);
    ④自定义工具栏按钮文本含 HTML 标签且版本>=10.0.19 -> ERROR; ⑤同一 <ToolBar> 内
    ShortCut 重复 -> WARN; ⑥存在 <WebPageContent> -> 提示已脱离服务器分页预览设置。
    来源: doc-135。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验分页预览 Web 属性(doc-135)")]
    reports = root.findall(".//Report")
    wa = root.find(".//ReportWebAttr")
    page = wa.find("WebPageContent") if wa is not None else None
    if wa is None and page is None:
        return [("OK", "无 <ReportWebAttr>/<WebPageContent>: 全部 Web 属性走服务器设置(doc-135)。")]

    if page is None:
        out.append(("OK", "无 <WebPageContent>: 分页预览采用服务器设置(可被服务器配置统一改)(doc-135)。"))
    else:
        out.append(("OK", "存在 <WebPageContent>: 该模板已脱离服务器「分页预览设置」(供全库盘点用, doc-135 ⑥)。"))
        tb = page.find("ToolBars")
        if tb is not None and len(list(tb)) == 0:
            out.append(("OK", "<ToolBars/> 为空 => 分页预览隐藏工具栏(doc-135)。"))
        seen_in_toolbar = {}
        for tbar in page.iter("ToolBar"):
            for sc in tbar.iter("ShortCut"):
                n = sc.get("name")
                if not n:
                    continue
                if n not in VERIFIED_SHORTCUTS:
                    lvl = WARN if n in LIKELY_SHORTCUTS else WARN
                    out.append((lvl, "ShortCut name=%r 不在已验证清单 %s 内: FR 对未知 name 静默丢弃"
                                "该按钮(doc-135 ③)" % (n, sorted(VERIFIED_SHORTCUTS))))
                seen_in_toolbar[n] = seen_in_toolbar.get(n, 0) + 1
        for n, cnt in seen_in_toolbar.items():
            if cnt > 1:
                out.append(("WARN", "同一 <ToolBar> 内 ShortCut %r 重复 %d 次, 设计器渲染多个同名"
                            "按钮, 不报错(doc-135 ⑤)" % (n, cnt)))
        if page.find("CSSImport") is not None:
            out.append(("ERROR", "<CSSImport> 出现在 <WebPageContent> 内部, 必须上提为 "
                        "<ReportWebAttr> 直接子节点, 否则 CSS 静默不加载(铁律 I, doc-135 ②)"))
    wwc = wa.find("WebWriteContent") if wa is not None else None
    if wwc is not None and wwc.find("CSSImport") is not None:
        out.append(("ERROR", "<CSSImport> 出现在 <WebWriteContent> 内部, 必须上提为 <ReportWebAttr>"
                    "直接子节点(doc-135 ②)"))

    if len(reports) > 1 and page is not None:
        out.append(("ERROR", "WorkBook 含 %d 个 <Report> 且配置了分页预览: 分页预览不支持多 sheet"
                    "标签, 用户只能看到第一张(doc-135 ①)" % len(reports)))

    # ④ 自定义工具栏按钮文本含 HTML(版本 >= 10.0.19)
    if _ver_ge(OPTIONS.get("fr_version") or "10.0.19", "10.0.19"):
        for m in re.finditer(r'<Widget class="com\.fr\.form\.ui\.CustomToolBarButton"[^>]*>'
                             r'(?P<body>.*?)</Widget>', _xml_text(root), re.S):
            tm = re.search(r"<Text>\s*<!\[CDATA\[([\s\S]*?)\]\]>\s*</Text>", m.group("body"))
            if tm and HTML_TAG_RE.search(tm.group(1)):
                out.append(("ERROR", "doc §2.4.3 注: 10.0.19 及以后自定义按钮名称不支持 HTML, "
                            "按钮文本 %r 含标签会原样显示或渲染异常(doc-135 ④)" % tm.group(1)))
    return out


# ---------------------------------------------------------------------------
# 19. doc-1736 JS 实现隐藏决策报表组件 —— setVisible 扫描
# ---------------------------------------------------------------------------
SETVISIBLE_RE = re.compile(
    r"_g\(\)\.getWidgetByName\(\s*['\"](?P<target>[^'\"]+)['\"]\s*\)"
    r"\.setVisible\(\s*(?P<visible>true|false)\s*\)",
    re.IGNORECASE)


def check_setvisible(cpt_path: str):
    """doc-1736 JS 隐藏决策报表组件: 扫描所有 _g().getWidgetByName('X').setVisible(bool),
    输出「控件->组件 隐藏/显示」映射; 一旦出现 setVisible(false) -> WARN「导出需带 sessionID,
    否则隐藏组件被一起导出」。移植 practice/topic_1736/scan_setvisible.py。来源: doc-1736。"""
    out = []
    raw = _read_text(cpt_path)
    calls = list(SETVISIBLE_RE.finditer(raw))
    if not calls:
        return [("OK", "未发现 setVisible 调用, 本规则不适用(doc-1736)。")]
    risk = False
    for m in calls:
        visible = m.group("visible").lower() == "true"
        if not visible:
            risk = True
        out.append(("OK", "JS 调用 %s(%s) 控制组件 %r(doc-1736 盘点)" %
                    ("显示" if visible else "隐藏", m.group("visible"), m.group("target"))))
    if risk:
        out.append(("WARN", "存在 setVisible(false): 导出必须带 sessionID, 否则被隐藏的组件会被"
                    "一起导出(doc-1736 注意事项2)"))
    return out


# ---------------------------------------------------------------------------
# 20. doc-3610 大数据集导出事件 —— 配置一致性(移植 bigdata_export_config.py)
# ---------------------------------------------------------------------------
PARAM_TYPES = {"字符串", "整型", "双精度型", "日期", "布尔型", "公式"}


def validate_bigdata_export_event(ev) -> list:
    """doc-3610 大数据集导出事件 validate(移植 practice/topic_3610/bigdata_export_config.py)。
    返回 [(level, msg), ...]。来源: doc-3610。"""
    out = []
    if ev.get("template_params") and ev.get("params"):
        set_names = {p.get("name") for p in ev["params"]}
        missing = [p for p in ev["template_params"] if p not in set_names]
        if missing:
            out.append(("ERROR", "模板参数 %s 存在, 但导出仅设了 %s; 缺失 %s => 数据无法导出(静默空导出)"
                        "(doc-3610)" % (ev["template_params"], sorted(set_names), missing)))
    for c in ev.get("columns") or []:
        if "/" in c:
            out.append(("WARN", "导出列 %r 含转义字符 '/', 导出数据列设置将失效, 退化导出所有字段"
                        "(doc-3610)" % c))
            break
    fn = ev.get("file_name") or ""
    if fn.startswith("=$"):
        pname = fn[2:]
        if pname not in (ev.get("bound_control_params") or []):
            out.append(("WARN", "文件名 %r 引用参数 %r, 但参数未绑定参数面板控件 => 文件名参数无效"
                        "(doc-3610)" % (fn, pname)))
    if "/" in fn:
        out.append(("OK", "文件名 %r 含 '/', 浏览器下载会转义为 '_'(doc-3610)" % fn))
    for p in ev.get("params") or []:
        if p.get("ptype") not in PARAM_TYPES:
            out.append(("ERROR", "参数 %r 类型 %r 不在支持列表 %s(doc-3610)"
                        % (p.get("name"), p.get("ptype"), sorted(PARAM_TYPES))))
        if p.get("ptype") == "公式" and not (p.get("value") or "").startswith("$"):
            out.append(("ERROR", "公式类型参数 %r 值 %r 应以 '$' 引用参数面板控件(如 $地区)(doc-3610)"
                        % (p.get("name"), p.get("value"))))
    return out


def check_bigdata_export_event(cpt_path: str):
    """doc-3610 大数据集导出事件一致性(移植 practice/topic_3610/bigdata_export_config.py 的
    validate()): ①导出事件引用的数据集/参数存在且类型匹配; ②模板多参数却只设部分参数 ->
    ERROR(静默空导出); ③导出列名含 '/' -> WARN(设置失效退全字段); ④文件名 =$参数 中参数未
    绑定参数面板控件 -> WARN; ⑤文件名含 '/' -> 提示(下载转 '_')。来源: doc-3610。"""
    out = []
    raw = _read_text(cpt_path)
    if not _has(raw, "大数据", "bigdata", "directExportToExcel", "数据集导出"):
        return [("OK", "未发现大数据集导出事件标记, 本规则不适用(doc-3610)。")]
    root = _load_root(cpt_path)
    tpl_params = sorted(_template_params(root)) if root is not None else []
    bound = sorted(_widget_names(root))
    ev = {
        "template_params": tpl_params,
        "bound_control_params": bound,
        "params": [],
        "columns": [],
        "file_name": None,
    }
    # 从 JS/文本近似抽取: 列名列表与文件名(事件 XML 落点未公开, 按文本启发式)
    cm = re.search(r"colNames\s*[:=]\s*\[([^\]]*)\]", raw)
    if cm:
        ev["columns"] = [x.strip().strip("'\"") for x in cm.group(1).split(",") if x.strip()]
    fm = re.search(r"file_?name\s*[:=]\s*['\"]([^'\"]+)['\"]", raw, re.I)
    if fm:
        ev["file_name"] = fm.group(1)
    out.extend(validate_bigdata_export_event(ev))
    if tpl_params and not ev["params"]:
        out.append(("WARN",
                    "模板有参数 %s 但未在导出事件中显式设置任何参数: 无法静态确认参数映射, "
                    "若只设部分参数会导致静默空导出(doc-3610)" % tpl_params))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "大数据集导出事件未发现可静态判定的问题(doc-3610)。"))
    return out


# ---------------------------------------------------------------------------
# 21. doc-3342 新计算引擎大数据集导出 —— direct/export 10 条
# ---------------------------------------------------------------------------
EXPORT_PATH_3342 = "direct/export"


def _cdata_of(xml_frag, tag):
    m = re.search(r"<%s>\s*<!\[CDATA\[([\s\S]*?)\]\]>\s*</%s>" % (tag, tag), xml_frag)
    return m.group(1) if m else ""


def check_direct_export(cpt_path: str):
    """doc-3342 新计算引擎大数据集导出(工具栏按钮 + direct/export) 10 条体检
    (移植 practice/topic_3342/gen_bigdata_export_button.py validate()):
    ①无 <WebPageContent> -> ERROR; ②按钮落 <WebWriteContent> -> ERROR; ③CustomToolBarButton
    内出现 <Listener> -> ERROR; ④缺 sessionID -> ERROR; ⑤用 ${sessionID} 而非
    Report.SessionMgr.get() -> WARN; ⑥缺 dsName -> ERROR; ⑦encodeURIComponent 值又进表单
    input -> WARN(双重编码); ⑧参数值引用未 var 定义的裸变量 -> ERROR; ⑨URL 硬编码
    localhost/IP:port -> WARN; ⑩按钮 <Text> 为空 -> WARN。来源: doc-3342。"""
    out = []
    raw = _read_text(cpt_path)
    if EXPORT_PATH_3342 not in raw and "direct/export" not in raw:
        return [("OK", "未发现 direct/export 大数据导出按钮, 本规则不适用(doc-3342)。")]

    if "<WebPageContent" not in raw:
        out.append(("ERROR", "存在 direct/export 按钮但无 <WebPageContent>: 该导出仅在分页预览/"
                    "新分页预览生效, 且分页预览须「为该模板单独设置」(doc-3342)"))
    if re.search(r"<WebWriteContent[\s\S]*?direct/export[\s\S]*?</WebWriteContent>", raw):
        out.append(("ERROR", "导出按钮落在 <WebWriteContent>(填报预览): 不支持, 按钮点了没反应"
                    "(doc-3342)"))

    for m in re.finditer(r'<Widget class="com\.fr\.form\.ui\.CustomToolBarButton"[\s\S]*?</Widget>', raw):
        w = m.group(0)
        if "direct/export" not in w:
            continue
        js = _cdata_of(w, "Content")
        text = _cdata_of(w, "Text")
        if "<Listener" in w:
            out.append(("ERROR", "CustomToolBarButton 内出现 <Listener>: 工具栏按钮的 <JavaScript> "
                        "必须直挂 Widget(Listener 是 FreeButton 写法)(doc-3342)"))
        if "sessionID" not in js:
            out.append(("ERROR", "导出 URL 缺 sessionID: Report.SessionMgr.get() 未传, 取不到会话数据"
                        "(doc-3342)"))
        elif "Report.SessionMgr.get()" not in js and "${sessionID}" in js:
            out.append(("WARN", "用了模板变量 ${sessionID} 而非 Report.SessionMgr.get(): 前者是服务端"
                        "替换、后者是前端 API, 工具栏 JS 里以后者为准(doc-3342)"))
        if "dsName" not in js:
            out.append(("ERROR", "导出 URL 缺 dsName: 未指定要导出的数据集(doc-3342)"))
        if "encodeURIComponent" in js and re.search(r"\$\s*\(\s*[\"']<input", js):
            out.append(("WARN", "encodeURIComponent 的值又塞进表单 input: 表单提交会再编码一次"
                        "(% -> %25), 中文数据集名/参数值反而乱码(doc-3342)"))
        for var in re.findall(r'&\w+=[\"\']\s*\+\s*([A-Za-z_]\w*)', js):
            if var in ("dsName", "url"):
                continue
            if not re.search(r"\bvar\s+%s\b" % re.escape(var), js):
                out.append(("ERROR", "参数值引用未定义变量 %r: 运行时 ReferenceError, 按钮静默无反应; "
                            "应写 var %s = _g().getWidgetByName('控件名').getValue()(doc-3342 §4.1)"
                            % (var, var)))
        m2 = re.search(r'https?://(localhost|127\.0\.0\.1|\d+\.\d+\.\d+\.\d+)[^"\']*', js)
        if m2:
            out.append(("WARN", "URL 硬编码了 %s: 换环境即失效, 建议用相对路径 /webroot/... 由浏览器"
                        "按当前 origin 解析(doc-3342)" % m2.group(0)))
        if not text.strip():
            out.append(("WARN", "自定义按钮 <Text> 为空: 工具栏上是个没有文字的按钮(doc-3342)"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "direct/export 大数据导出按钮 10 项体检全部通过(doc-3342)。"))
    return out


# ---------------------------------------------------------------------------
# 22. doc-1407 Excel 流式导出支持行式引擎插件
# ---------------------------------------------------------------------------
def check_stream_export(cpt_path: str):
    """doc-1407 Excel 流式导出: ①导出目标为 .xls(2003)且走流式(format=excel/extype=stream)
    -> ERROR(流式接口只支持 2007+); ②模板含行式引擎且标注走流式导出 -> WARN「需安装
    Excel 流式导出支持行式引擎 插件, 否则退化为普通导出吃内存」。来源: doc-1407。"""
    out = []
    raw = _read_text(cpt_path)
    root = _load_root(cpt_path)
    stream = _has(raw, "extype=stream", "extype=\"stream\"", "extype='stream'", "流式")
    excel = _has(raw, "format=excel", "format=\"excel\"", "format='excel'", "流式")
    if not (stream or excel):
        return [("OK", "未发现流式导出配置(format=excel/extype=stream), 本规则不适用(doc-1407)。")]
    if re.search(r"\.xls\b|\.xls['\"]|__filename__[^;\n]*\.xls\b", raw, re.I) and (
            _has(raw, "extype=stream", "流式") or (excel and "extype" not in raw)):
        out.append(("ERROR", "导出目标为 .xls(2003)且走流式导出: 流式导出接口只支持 Excel 2007+"
                    "(.xlsx), .xls 必失败(doc-1407)"))
    if _row_engine_enabled(root) and (_has(raw, "extype=stream", "流式") or excel):
        out.append(("WARN", "行式引擎 + 流式导出: 需另装「Excel 流式导出支持行式引擎」插件, 否则"
                    "退化为普通导出吃内存(doc-1407)"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "流式导出配置检查通过(目标 .xlsx、无行式引擎冲突)(doc-1407)。"))
    return out


# ---------------------------------------------------------------------------
# 23. doc-1120 大数据量导出 Excel —— 产物形态三选一 / 行数整数倍约束
# ---------------------------------------------------------------------------
XLS_MAX_ROWS, XLS_MAX_COLS = 65536, 256
CELLS_SAFE, CELLS_RISKY = 100_000 * 10, 100_000 * 50


def max_rows_per_file(fixed_rows_per_page: int, desired=None):
    """doc-1120 §3 两条约束: 必须是「固定行数分页」每页行数的整数倍; 不得超过 65536。"""
    problems = []
    if fixed_rows_per_page <= 0:
        return None, ["ERROR|E-FIXROWS|固定行数分页每页行数必须 > 0(doc-1120)"]
    if fixed_rows_per_page > XLS_MAX_ROWS:
        return None, ["ERROR|E-FIXROWS-TOOBIG|每页固定行数 %d > %d, 不存在合法单文件行数(doc-1120)"
                      % (fixed_rows_per_page, XLS_MAX_ROWS)]
    if desired is None:
        return (XLS_MAX_ROWS // fixed_rows_per_page) * fixed_rows_per_page, problems
    if desired <= 0:
        problems.append("ERROR|E-MAXROWS|单个 Excel 最大行数必须 > 0(doc-1120)")
    if desired > XLS_MAX_ROWS:
        problems.append("ERROR|E-MAXROWS-XLS|单个 Excel 最大行数 %d 超过 .xls 上限 %d(doc-1120)"
                        % (desired, XLS_MAX_ROWS))
    if desired > 0 and desired % fixed_rows_per_page != 0:
        problems.append("ERROR|E-MAXROWS-MULTIPLE|单个 Excel 最大行数 %d 不是固定行数分页 %d 的整数倍"
                        "(doc-1120)" % (desired, fixed_rows_per_page))
    return desired, problems


def validate_export_plan(plan: dict) -> list:
    """doc-1120 validate(移植 practice/topic_1120/bigdata_export_plan.py)。
    plan: {total_rows, cols, row_engine, fixed_rows_per_page, max_rows_per_file, expect_ext}"""
    out = []
    row_engine = bool(plan.get("row_engine"))
    total_rows = int(plan.get("total_rows") or 0)
    cols = int(plan.get("cols") or 0)
    expect_ext = (plan.get("expect_ext") or "").lower().lstrip(".")
    if row_engine:
        out.append(("OK", "行式引擎导出产物是【多个 .xls 打包成 1 个 zip】, 不是单个 Excel; "
                    "下游解压后逐个读(doc-1120 §3)"))
        if expect_ext in ("xls", "xlsx"):
            out.append(("ERROR", "预期扩展名 .%s 与行式引擎产物(zip)不符, 无头下载脚本会把 zip 存成"
                        ".%s 并在读取时失败(doc-1120)" % (expect_ext, expect_ext)))
        fixed = plan.get("fixed_rows_per_page")
        if fixed is None:
            out.append(("ERROR", "行式引擎导出必须先设「固定行数分页」, 单个 Excel 最大行数以它为"
                        "整数倍基数(doc-1120 §3)"))
        else:
            _, probs = max_rows_per_file(int(fixed), plan.get("max_rows_per_file"))
            for p in probs:
                lvl, code, msg = p.split("|", 2)
                out.append((lvl, "%s(doc-1120)" % msg))
        if cols > XLS_MAX_COLS:
            out.append(("ERROR", "列数 %d 超过 .xls 上限 %d; 行式引擎产物是 .xls, 列无处可放(doc-1120)"
                        % (cols, XLS_MAX_COLS)))
    else:
        if total_rows > XLS_MAX_ROWS:
            out.append(("WARN", "数据 %d 行 > %d, 超出部分会【静默溢出到下一个 sheet】; 下游只读"
                        "第一个 sheet 会丢数据(doc-1120 §2.1)" % (total_rows, XLS_MAX_ROWS)))
        if cols > XLS_MAX_COLS:
            out.append(("WARN", "列数 %d > %d, 超出列同样溢出到下一个 sheet(doc-1120)" % (cols, XLS_MAX_COLS)))
        cells = total_rows * cols
        if cells >= CELLS_RISKY:
            out.append(("ERROR", "约 %d 个单元格, 处于「服务器无法承受」区间: 很可能导出失败, 且失败"
                        "产物是【内容无效的 Excel】(HTTP 200、文件非空、打不开)。请改用行式引擎或流式"
                        "导出(doc-1120 §2.2)" % cells))
        elif cells >= CELLS_SAFE:
            out.append(("WARN", "约 %d 个单元格, 已接近临界点; 导出成败取决于内存与列复杂度, 建议改"
                        "行式引擎/流式导出(doc-1120 §2.3)" % cells))
        if plan.get("max_rows_per_file") is not None:
            out.append(("WARN", "未开行式引擎时「单个 Excel 最大行数」无意义, 拆分由 Excel 行上限"
                        "自动切 sheet 决定(doc-1120)"))
    return out


def check_bigdata_export_plan(cpt_path: str):
    """doc-1120 大数据量导出 Excel 体检(移植 practice/topic_1120/bigdata_export_plan.py 的
    validate()): 行式引擎模板判 ①单文件最大行数非每页行数整数倍->ERROR; ②>65536->ERROR;
    ③开行式引擎未设固定行数分页->ERROR; ④预期 .xls/.xlsx 却开行式引擎->ERROR(实际产 zip);
    非行式引擎按预估行/列判 ⑤行>65536->WARN; ⑥列>256->WARN; ⑦单元格总量临界区->WARN/ERROR。
    行/列/分页参数从 .cpt 静态抽取 + OPTIONS 补全。来源: doc-1120。"""
    out = []
    raw = _read_text(cpt_path)
    root = _load_root(cpt_path)
    eng = _row_engine_enabled(root)
    bigdata = _has(raw, "excel", "导出", "bigdata", "大数据", "行式")
    if not bigdata and not eng:
        return [("OK", "未发现 Excel 导出/大数据标记, 本规则不适用(doc-1120)。")]
    cols = OPTIONS.get("total_cols")
    if cols is None and root is not None:
        cs = [int(c.get("c")) for c in root.iter("C") if c.get("c", "").isdigit()]
        cols = (max(cs) + 1) if cs else 0
    rows = OPTIONS.get("total_rows")
    plan = {
        "total_rows": rows if rows is not None else 0,
        "cols": cols if cols is not None else 0,
        "row_engine": eng,
        "fixed_rows_per_page": OPTIONS.get("fixed_rows_per_page"),
        "max_rows_per_file": OPTIONS.get("max_rows_per_file"),
        "expect_ext": OPTIONS.get("expect_ext"),
    }
    out.extend(validate_export_plan(plan))
    if rows is None and not eng:
        out.append(("WARN", "未提供预计行数(OPTIONS['total_rows']): 行数溢出/单元格总量两档无法"
                    "精确判定, 请调用方补全(doc-1120)"))
    return out


# ---------------------------------------------------------------------------
# 24. doc-4518 大数据集导出常见问题 —— 多值参数格式 / 中文编码
# ---------------------------------------------------------------------------
def _top_level_split(s: str) -> list:
    """按顶层逗号切分(忽略引号内与括号内的逗号), 用于解析 directExportToExcel 实参。"""
    parts, depth, cur, quote = [], 0, "", None
    for ch in s:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote, cur = ch, cur + ch
        elif ch in "([{":
            depth += 1
            cur += ch
        elif ch in ")]}":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def check_direct_export_paramstr(cpt_path: str):
    """doc-4518 大数据集导出常见问题: ①directExportToExcel 的 paramStr(第 3 实参)出现
    [ / ] 数组写法, 或对象内多值用 ',' 而非 '',' 拼接 -> ERROR(文档 §2.10 实测这些写法
    导出为空); ②fileName/colNames 含非 ASCII 字符却未包在 encodeURIComponent(...) 中
    -> WARN(中文静默乱码)。来源: doc-4518。"""
    out = []
    raw = _read_text(cpt_path)
    calls = []
    for m in re.finditer(r"directExportToExcel\s*\(", raw):
        i, depth = m.end(), 1
        while i < len(raw) and depth:
            c = raw[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            i += 1
        if depth == 0:
            calls.append(raw[m.end():i - 1])
    if not calls:
        return [("OK", "未发现 directExportToExcel 调用, 本规则不适用(doc-4518)。")]

    encoded = "encodeURIComponent" in raw
    for args in calls:
        parts = _top_level_split(args)
        if len(parts) >= 3:
            ps = parts[2]
            if "[" in ps or "]" in ps:
                out.append(("ERROR", "paramStr 用了数组写法 [..]: 多值参数必须是 {k:\"v1','v2\"} 形态"
                            "({} 对象 + 值间 '',' 拼接), 数组写法导出为空(doc-4518 §2.10)"))
            elif "{" in ps and "," in ps and "','" not in ps:
                out.append(("ERROR", "paramStr 的值未按 '',' 拼接: 多值参数格式是 {k:\"v1','v2\"}, "
                            "值间用 ',' 而非 '',' 时导出为空(doc-4518 §2.10)"))
            elif ps.strip() and not ps.strip().startswith("{"):
                out.append(("ERROR", "paramStr 应为对象字面量 {k:\"v1','v2\"} 形态, 实际=%r(doc-4518 §2.10)"
                            % ps[:60]))
            else:
                out.append(("OK", "paramStr 为对象字面量且值间用 '',' 拼接, 符合硬规矩(doc-4518 §2.10)。"))
            # ② 中文未编码: 实参里含非 ASCII 且全串无 encodeURIComponent
            if re.search(r"[^\x00-\x7f]", args) and not encoded:
                out.append(("WARN", "directExportToExcel 实参含中文(fileName/colNames)却未包在 "
                            "encodeURIComponent(...) 中: 中文名静默乱码(doc-4518 §1 注)"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "directExportToExcel 参数形态检查通过(doc-4518)。"))
    return out


# ---------------------------------------------------------------------------
# 25. doc-4418 大数据模板导出慢问题排查
# ---------------------------------------------------------------------------
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".ico")
CHART_MARKERS = ("ChartCollection", "com.fr.chart.chartattr", "com.fr.chart.charttypes", "ChartAttr")
MSSQL_DRIVER_OLD = "com.microsoft.jdbc.sqlserver.SQLServerDriver"
MSSQL_DRIVER_NEW = "com.microsoft.sqlserver.jdbc.SQLServerDriver"


def _find_webimage_calls(text):
    out = []
    for m in re.finditer(r"webimage\s*\(", text, re.I):
        i, depth = m.end(), 1
        while i < len(text) and depth:
            c = text[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            i += 1
        if depth == 0:
            out.append(text[m.end():i - 1])
    return out


def check_export_perf(cpt_path: str):
    """doc-4418 大数据模板导出慢排查(移植 practice/topic_4418/export_slow_triage.py):
    ①命中图表标记 -> WARN「部署需 j2v8 环境, 否则回退 nashorn 渲染导出慢, 须升级 GCC」;
    ②webimage() 参数不以图片后缀结尾 -> WARN「导出时同步等待外部服务, 扩展 N 行即 N 次串行请求」;
    ③内联 JDBC 连接命中老 SQLServer 驱动 -> WARN「换 sqljdbc42」;
    ④导出 URL(OPTIONS['export_url'])缺 format= -> WARN。来源: doc-4418。"""
    out = []
    raw = _read_text(cpt_path)
    hit = [m for m in CHART_MARKERS if m in raw]
    if hit:
        out.append(("WARN", "模板含图表(命中标记 %s): 服务器缺 j2v8 环境时会回退 nashorn 渲染, "
                    "导出显著变慢; 解决方向是升级 GCC 以启用 j2v8, 而不是改模板(doc-4418)"
                    % ",".join(hit)))
    for arg in _find_webimage_calls(raw):
        s = arg.strip().strip("\"'").lower()
        path = s.split("?", 1)[0].split("#", 1)[0]
        if not path.endswith(IMG_EXT):
            out.append(("WARN", "webimage(%s) 参数不像图片直链, 疑似指向自有服务/接口: 导出时 FR "
                        "会同步等待该服务返回, 扩展 N 行即 N 次串行请求(doc-4418)" % " ".join(arg.split())[:80]))
    if MSSQL_DRIVER_OLD in raw:
        out.append(("WARN", "命中老版 SQLServer 驱动类 %s: 低版本 sqljdbc 有已知性能问题, 应换 "
                    "sqljdbc42(驱动类 %s)(doc-4418)" % (MSSQL_DRIVER_OLD, MSSQL_DRIVER_NEW)))
    url = OPTIONS.get("export_url")
    if url:
        if "format=" not in url:
            out.append(("WARN", "导出 URL 缺 format= 参数: 无头脚本应显式指定, 避免拿到非预期产物"
                        "(doc-4418)"))
        if "sessionID" not in url and "op=export" in url:
            out.append(("WARN", "按模板名导出(viewlet+op=export): 每次导出都重新取数计算; 批量导出"
                        "同一张表多份时优先预览一次+复用 sessionID(doc-4418)"))
    if not any(lv == "WARN" for lv, _ in out):
        out.append(("OK", "未发现导出慢的静态风险点(图表/webimage/老驱动)(doc-4418)。"))
    return out


# ---------------------------------------------------------------------------
# 26. doc-695 定时调度 per-user 邮件分发
# ---------------------------------------------------------------------------
FINE_PARAMS_695 = ("$fine_username", "$fine_role", "$fine_position")


def consistency_check_peruser(staff_rows, default_user_group) -> list:
    """doc-695 §2.1/§2.3 硬约束(移植 practice/topic_695/gen_peruser_dispatch.py
    consistency_check): 默认用户组 ⊆ staff 数据集用户, 且每个用户都要有非空邮箱。"""
    problems = []
    by_name = {r.get("name"): r for r in staff_rows if r.get("name")}
    for u in default_user_group:
        if u not in by_name:
            problems.append("默认用户组用户 %r 不在 staff 数据集中(导入源与取数源不一致)(doc-695)" % u)
        elif not (by_name[u].get("email") or "").strip():
            problems.append("用户 %r 无邮箱, 邮件通知收件人缺失(doc-695)" % u)
    return problems


def check_peruser_dispatch(cpt_path: str):
    """doc-695 定时调度 per-user 分发: ①模板被标为 per-user 用途时, 单元格过滤或数据集 SQL
    至少一处引用 $fine_username/$fine_role/$fine_position —— 否则人人收到同内容;
    ②数据底座(服务器数据集)用户集合 ⊇ 默认用户组且组内用户都有非空邮箱(需 OPTIONS['peruser_spec'])。
    移植 practice/topic_695/gen_peruser_dispatch.py。来源: doc-695。"""
    out = []
    raw = _read_text(cpt_path)
    spec = OPTIONS.get("peruser_spec")
    marked = _has(raw, "per-user", "per user", "单独生成结果", "peruser") or (
        spec is not None and spec.get("per_user_result"))
    if not marked:
        return [("WARN", "未发现「per-user 分发」标记(扫描: per-user|per user|单独生成结果|peruser);"
                 "假设不走按用户单独生成结果, 跳过强校验(doc-695)。")]
    used = [p for p in FINE_PARAMS_695 if p in raw]
    if not used:
        out.append(("ERROR", "per-user 分发用途但模板未引用任何 $fine_username/$fine_role/"
                    "$fine_position: 每人将收到同一份内容, 分发形同虚设(doc-695)"))
    else:
        out.append(("OK", "模板引用 %s, per-user 过滤有绑定来源(doc-695)" % "、".join(used)))
    if spec is not None:
        staff = spec.get("staff_rows") or []
        group = spec.get("default_user_group") or []
        for p in consistency_check_peruser(staff, group):
            out.append(("ERROR", p))
        if group and not any("默认用户组" in m for lv, m in out if lv == "ERROR"):
            out.append(("OK", "默认用户组 ⊆ staff 数据集且邮箱齐全(doc-695)。"))
    else:
        out.append(("WARN", "未提供 OPTIONS['peruser_spec'](staff_rows/default_user_group): 数据底座"
                    "⊇ 默认用户组、邮箱完整性无法静态核对, 请在工程侧人工确认(doc-695)。"))
    return out


# ---------------------------------------------------------------------------
# 27. doc-683 定时调度生成的附件 —— 参数名三处一致
# ---------------------------------------------------------------------------
ILLEGAL_PATH_CHARS = set("\\/:*?\"<>|")


def check_schedule_param_name(cpt_path: str):
    """doc-683 定时调度生成的附件: 凡模板被标为「定时调度/per-user 分发」用途, 校验 .cpt 的
    <Parameter> 名、调度参数设置名、存档目录名须同源一致(第六层目录名直接来自参数名, 不一致
    会跑出空文件或路径错位)。移植 practice/topic_683/schedule_path.py 命名规则。来源: doc-683。"""
    out = []
    raw = _read_text(cpt_path)
    spec = OPTIONS.get("schedule_spec")
    marked = _has(raw, "定时调度", "调度对象", "per-user", "per user", "schedule") or spec is not None
    if not marked:
        return [("WARN", "未发现「定时调度/per-user 分发」标记; 假设不走调度存档, 跳过参数名三处"
                 "一致校验(doc-683)。")]
    root = _load_root(cpt_path)
    tpl_params = _template_params(root) if root is not None else {}
    for nm in tpl_params:
        bad = ILLEGAL_PATH_CHARS.intersection(nm)
        if bad:
            out.append(("ERROR", "模板参数名 %r 含路径非法字符 %s: 旧 JAR 参数层目录名直接取"
                        "「参数名_值」, 会路径错位(doc-683)" % (nm, "".join(sorted(bad)))))
    if spec is not None:
        spec_params = [p.get("name") for p in (spec.get("object") or {}).get("params", [])]
        for nm in spec_params:
            if nm not in tpl_params:
                out.append(("WARN", "调度参数设置里的参数 %r 在模板 <Parameter> 中不存在: 三处命名"
                            "不一致, 定时任务可能跑出空文件(doc-683)" % nm))
        for nm in tpl_params:
            if nm not in spec_params:
                out.append(("WARN", "模板参数 %r 未在调度「参数设置」中绑定: 存档目录参数层将缺失"
                            "该参数(doc-683)" % nm))
        if not any(lv == "WARN" for lv, _ in out) and spec_params:
            out.append(("OK", "模板参数名与调度参数设置名一致, 存档目录命名同源(doc-683)。"))
    else:
        out.append(("WARN", "未提供 OPTIONS['schedule_spec']: 调度参数设置名与存档目录名无法核对, "
                    "请人工保证三处命名一致(doc-683)。"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "参数名三处一致检查通过(doc-683)。"))
    return out


# ---------------------------------------------------------------------------
# 28. doc-688 定时任务执行条件之公式判断
# ---------------------------------------------------------------------------
def check_dispatch_formula(cpt_path: str):
    """doc-688 公式判断执行条件(移植 practice/topic_688/verify_dispatch_formula.py R1/R2):
    解析执行公式(如 D5<20000), 断言每个引用坐标在 .cpt 的 <C c=.. r=..> 中存在(否则 ERROR,
    永远 false)且为数值/公式类型(否则 WARN)。公式来自 OPTIONS['dispatch_formula'] 或文本标记。
    来源: doc-688。"""
    out = []
    raw = _read_text(cpt_path)
    formula = OPTIONS.get("dispatch_formula") or ""
    if not formula:
        m = re.search(r"(?:公式判断|执行条件)[^。\n]*?([A-Z]{1,3}\d+\s*[<>=!][^。\n]*)", raw)
        if m:
            formula = m.group(1).strip()
    if not formula:
        if _has(raw, "公式判断", "执行条件", "dispatch"):
            return [("WARN", "检测到「公式判断」用途标记但未能从文本中解析出公式(如 D5<20000); "
                    "请通过 OPTIONS['dispatch_formula'] 提供(doc-688)。")]
        return [("OK", "未发现公式判断/执行条件标记, 本规则不适用(doc-688)。")]
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验公式判断引用单元格(doc-688)")]
    cells = _cell_map(root)
    refs = _formula_cells(formula)
    if not refs:
        return [("WARN", "公式 %r 未解析出单元格坐标, 无法静态校验(doc-688)" % formula)]
    for col, row in refs:
        key = (_col_to_idx(col), row - 1)
        if key not in cells:
            out.append(("ERROR", "公式 %r 引用 %s%d 但 .cpt 中不存在该单元格 -> 公式永远 false, "
                        "定时预警静默失效(doc-688 R1)" % (formula, col, row)))
        else:
            ct = _cell_type(cells[key])
            if ct in ("number", "formula"):
                out.append(("OK", "%s%d 存在且为 %s 类型, 可被数值比较(doc-688)" % (col, row, ct)))
            else:
                out.append(("WARN", "%s%d 类型为 %s, 参与 < / > 比较结果不可预期, 请确认是数值/聚合"
                            "指标而非文本(doc-688 R2)" % (col, row, ct)))
    return out


# ---------------------------------------------------------------------------
# 29. doc-2209 定时调度挂载平台
# ---------------------------------------------------------------------------
def check_mount_ready(cpt_path: str):
    """doc-2209 定时调度挂载平台(移植 practice/topic_2209/check_mount_ready.py):
    ①「挂载名称」字段不含 ${(含则 ERROR, 会被当字面量目录名); ②WARN 若 .cpt 无模板参数
    (结果报表顶部「使用的参数值」将恒空)。挂载名称由 OPTIONS['mount_name'] 提供。
    来源: doc-2209。"""
    out = []
    raw = _read_text(cpt_path)
    mname = OPTIONS.get("mount_name")
    marked = mname is not None or _has(raw, "挂载", "mount")
    if not marked:
        return [("WARN", "未发现「挂载平台」标记且未提供 OPTIONS['mount_name']; 假设不走挂载平台, "
                 "跳过校验(doc-2209)。")]
    if mname is not None:
        if "${" in mname:
            out.append(("ERROR", "挂载名称 %r 含 '${}' 公式: 挂载平台「挂载名称」不支持公式, 会被"
                        "当成字面量目录名(doc-2209)" % mname))
        else:
            out.append(("OK", "挂载名称 %r 为固定名, 合规(doc-2209)。" % mname))
    root = _load_root(cpt_path)
    params = _template_params(root) if root is not None else {}
    if not params:
        out.append(("WARN", "该 .cpt 无任何模板参数: 挂载后的结果报表顶部「使用的参数值」将为空, "
                    "建议补一个参数以便追溯(doc-2209)"))
    else:
        out.append(("OK", "模板含参数 %s, 结果报表可展示参数值(doc-2209)" % sorted(params)))
    return out


# ---------------------------------------------------------------------------
# 30. doc-4432 定时调度平台通知
# ---------------------------------------------------------------------------
def check_platform_notify(cpt_path: str):
    """doc-4432 定时调度平台通知(平台通知=文件处理第五种, 默认用户组=收件人, 主题/内容公式,
    链接开关): ①默认用户组非空(否则 ERROR, 无人收信); ②主题/内容非空(否则 ERROR);
    ③链接字段取值 ∈ {平台内打开, 无}(否则 WARN)。spec 由 OPTIONS['notify_spec'] 提供。
    来源: doc-4432。"""
    out = []
    raw = _read_text(cpt_path)
    spec = OPTIONS.get("notify_spec")
    if spec is None:
        if _has(raw, "平台通知", "站内信", "notify"):
            return [("WARN", "检测到「平台通知」标记但未提供 OPTIONS['notify_spec'](默认用户组/主题/"
                    "内容/链接字段在任务侧, .cpt 内不可观察): 请提供 spec 后校验(doc-4432)。")]
        return [("WARN", "未发现「平台通知」标记且未提供 OPTIONS['notify_spec']; 假设不走平台通知, "
                 "跳过强校验(doc-4432)。")]
    basic = spec.get("basic") or {}
    cn = spec.get("file_handle") or {}
    if spec.get("basic") is not None and "default_user_group" in basic:
        group = basic.get("default_user_group") or []
    else:
        group = spec.get("default_user_group") or []
    if not group:
        out.append(("ERROR", "默认用户组为空: 平台通知无人收信(收件人=默认用户组, doc-4432)"))
    else:
        out.append(("OK", "默认用户组非空(%s 人), 平台通知有收件人(doc-4432)" % len(group)))
    subject = cn.get("subject") or spec.get("subject") or ""
    content = cn.get("content") or spec.get("content") or ""
    if not (subject or "").strip():
        out.append(("ERROR", "平台通知主题为空: 消息发出去无标题(doc-4432)"))
    if not (content or "").strip():
        out.append(("ERROR", "平台通知内容为空: 消息无正文(doc-4432)"))
    link = cn.get("link") or spec.get("link") or ""
    if link and link not in ("平台内打开", "无"):
        out.append(("WARN", "链接字段取值 %r 不在 {平台内打开, 无} 内 —— 可能静默失效(doc-4432)"
                    % link))
    if subject and content:
        out.append(("OK", "主题/内容非空, 公式用 ${...} 系统函数即可(doc-4432)。"))
    return out


# ---------------------------------------------------------------------------
# 31. doc-2210 定时调度短信通知
# ---------------------------------------------------------------------------
SMS_DEFAULT = {
    "name": ("Formula", "${fine_username}"),
    "taskname": ("Formula", "=$taskname"),
    "time": ("Formula", "=$time"),
}


def check_sms_ready(cpt_path: str):
    """doc-2210 定时调度短信通知(移植 practice/topic_2210/check_sms_ready.py):
    ①.cpt 引用 ${fine_username}(否则 ERROR, per-user 短信 name 无绑定来源);
    ②短信参数 name=`${fine_username}`、taskname/time 以 `=$` 开头(否则 ERROR, 拦截 `=`
    与 `${}` 混写); ③短信参数默认值长度 < DB 字段上限(否则 WARN, 防「任务更新失败」)。
    spec 由 OPTIONS['sms_cfg'] 提供。来源: doc-2210。"""
    out = []
    raw = _read_text(cpt_path)
    cfg = OPTIONS.get("sms_cfg")
    marked = _has(raw, "短信", "sms", "SMS") or cfg is not None
    if not marked:
        return [("WARN", "未发现「短信通知」标记且未提供 OPTIONS['sms_cfg']; 假设不走短信通知, "
                 "跳过强校验(doc-2210)。")]
    if "$fine_username" not in raw:
        out.append(("ERROR", ".cpt 未引用 ${fine_username}: per-user 短信 name 参数无绑定来源"
                    "(doc-2210 R1)"))
    else:
        out.append(("OK", ".cpt 引用 ${fine_username}, per-user 短信 name 有绑定来源(doc-2210)。"))
    params = cfg.get("params") if cfg else SMS_DEFAULT
    for pname, (ptype, val) in params.items():
        if pname == "name" and val != "${fine_username}":
            out.append(("ERROR", "短信 name 参数默认值应为 ${fine_username}, 实际=%r(doc-2210 R2)"
                        % val))
        if pname in ("taskname", "time"):
            if not str(val).startswith("=$"):
                out.append(("ERROR", "短信特有公式 %s 必须以 '=$' 开头(如 =$taskname), 实际=%r; "
                            "勿写成 ${...} 系统函数语法(doc-2210 R3)" % (pname, val)))
            if str(val).startswith("=${"):
                out.append(("ERROR", "短信公式 %s 勿写成 ${...} 形态, 实际=%r(doc-2210 R3)" % (pname, val)))
        if len(str(val)) > 255:
            out.append(("WARN", "短信参数 %s 默认值长度 %d > 255(DB 字段上限假设): 可能报「任务更新"
                        "失败」(doc-2210 R3 注)" % (pname, len(str(val)))))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "短信通知就绪: 参数绑定与公式语法合规(doc-2210)。"))
    return out


# ---------------------------------------------------------------------------
# 32. doc-1387 定时调度客户端通知-APP通知(op=write 对外链接)
# ---------------------------------------------------------------------------
LOCAL_HOSTS = ("localhost", "127.0.0.1", "[::1]", "0.0.0.0")


def check_app_notify(cpt_path: str):
    """doc-1387 客户端通知-APP通知(移植 practice/topic_1387/check_app_notify.py R4/R5/R6):
    凡模板被标为「op=write 对外链接」用途: ①含 ReportWriteAttr/SubmitVisitor(缺失则 ERROR
    —— App 用 op=write 打开也提交不了); ②至少一个单元格挂 com.fr.form.ui.* 控件(缺失则
    WARN —— 手机端无处输入); ③自定义链接不得含 localhost/127.0.0.1(ERROR, 手机不可达)。
    链接由 OPTIONS['notify_link'] 提供。来源: doc-1387。"""
    out = []
    raw = _read_text(cpt_path)
    link = OPTIONS.get("notify_link") or ""
    marked = _has(raw, "op=write", "APP通知", "客户端通知", "app_notify") or bool(link)
    if not marked:
        return [("WARN", "未发现「APP通知/op=write 对外链接」标记且未提供 OPTIONS['notify_link']; "
                 "假设不走对外填报链接, 跳过强校验(doc-1387)。")]
    root = _load_root(cpt_path)
    if root is not None:
        text = _xml_text(root)
        if "ReportWriteAttr" not in text or "SubmitVisitor" not in text:
            out.append(("ERROR", "目标 .cpt 缺 ReportWriteAttr/SubmitVisitor: App 用 op=write 打开"
                        "也提交不了(doc-1387 R6)"))
        else:
            out.append(("OK", "含 ReportWriteAttr/SubmitVisitor, op=write 可提交(doc-1387)。"))
        if "com.fr.form.ui." not in text:
            out.append(("WARN", "目标 .cpt 无任何单元格控件(com.fr.form.ui.*): 手机端无处输入"
                        "(doc-1387 R6)"))
        else:
            out.append(("OK", "存在单元格控件, 手机端可输入(doc-1387)。"))
    if link:
        low = link.lower()
        for h in LOCAL_HOSTS:
            if h in low:
                out.append(("ERROR", "自定义链接含本机地址 %r: 手机端不可达(消息能收到、点开空白), "
                            "须换成手机可达 IP(doc-1387 §3.6 注)" % h))
                break
        if "op=write" in low:
            if "viewlet=" not in low:
                out.append(("ERROR", "自定义链接需在 App 内填报但缺少 viewlet=<模板路径>(doc-1387 R5)"))
        else:
            out.append(("WARN", "自定义链接未带 op=write: App 内只能查看不能填报(doc-1387 R5)"))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "APP通知 op=write 链接可提交性检查通过(doc-1387)。"))
    return out


# ---------------------------------------------------------------------------
# 33. doc-682 定时调度 FTP 上传附件
# ---------------------------------------------------------------------------
VALID_TRANSFER_MODES = {"主动", "被动"}
ILLEGAL_FILENAME_CHARS = set(":\\/?*\"<>|")


def check_ftp_upload(cpt_path: str):
    """doc-682 定时调度 FTP 上传附件(移植 practice/topic_682/check_ftp_upload.py):
    ①主机非空; ②端口∈[1,65535]; ③传输模式∈{主动,被动}(SFTP 则无此字段); ④账号/密码非空;
    ⑤附件名不含 \/:*?"<>; 并 WARN 选 FTP(推荐 SFTP)与保存路径以 '/' 开头(前缀坑)。
    配置由 OPTIONS['ftp_cfg'] 提供。来源: doc-682。"""
    out = []
    raw = _read_text(cpt_path)
    cfg = OPTIONS.get("ftp_cfg")
    if cfg is None:
        if _has(raw, "FTP", "ftp") and not _has(raw, "SFTP", "sftp"):
            return [("WARN", "检测到「FTP 上传」标记但未提供 OPTIONS['ftp_cfg']: FTP 服务器配置在"
                    "任务侧, .cpt 内不可观察, 请提供 cfg 后校验(doc-682)。")]
        return [("WARN", "未发现「FTP 上传附件」标记且未提供 OPTIONS['ftp_cfg']; 假设不走 FTP 上传, "
                 "跳过强校验(doc-682)。")]
    errors, warns = [], []
    protocol = cfg.get("protocol", "FTP")
    if protocol not in ("FTP", "SFTP"):
        errors.append("协议必须是 FTP 或 SFTP, 收到: %r(doc-682)" % protocol)
    elif protocol == "FTP":
        warns.append("协议为 FTP: V10.0.18+ 官方推荐改用更安全的 SFTP(doc-682)")
    if not cfg.get("host"):
        errors.append("服务器地址(主机 ip)为空(doc-682)")
    port = cfg.get("port")
    if not isinstance(port, int) or not (1 <= port <= 65535):
        errors.append("端口 %r 非法, 应 ∈ [1,65535](FTP 默认 21)(doc-682)" % port)
    mode = cfg.get("transfer_mode")
    if protocol == "FTP":
        if mode not in VALID_TRANSFER_MODES:
            errors.append("传输模式 %r 非法, 应 ∈ {主动, 被动}(doc-682)" % mode)
    elif mode is not None:
        warns.append("SFTP 无传输模式概念, 不应传 transfer_mode=%r(doc-682)" % mode)
    save_path = cfg.get("save_path", "")
    if save_path.startswith("/"):
        warns.append("保存路径以 '/' 开头(如 %r): 官方注明超时未落盘时删掉 '/' 可解(doc-682)"
                     % save_path)
    if not cfg.get("username"):
        errors.append("FTP 用户名为空, 连接将被拒绝(doc-682)")
    if not cfg.get("password"):
        errors.append("FTP 密码为空, 连接将被拒绝(doc-682)")
    name = cfg.get("attach_name") or ""
    bad = ILLEGAL_FILENAME_CHARS.intersection(name)
    if bad:
        errors.append("附件名称含非法字符 %s(不可含 \\/:*?\"<>|)(doc-682)" % "".join(sorted(bad)))
    for e in errors:
        out.append(("ERROR", e))
    for w in warns:
        out.append(("WARN", w))
    if not errors and not warns:
        out.append(("OK", "FTP 上传附件配置合规(doc-682)。"))
    return out


# ---------------------------------------------------------------------------
# 34. doc-3573 定时调度 SFTP 上传附件
# ---------------------------------------------------------------------------
SFTP_JAR_MIN = "2020-08-03"
VALID_ATTACH_FORMATS = {"excel03", "excel07", "word", "pdf"}
VALID_AUTH_MODES = {"password", "key"}
VALID_SERVER_OS = {"windows", "linux"}


def check_sftp_upload(cpt_path: str):
    """doc-3573 定时调度 SFTP 上传附件(移植 practice/topic_3573/check_sftp_upload.py):
    ①JAR>=2020-08-03(否则该选项不存在); ②对象类型==报表模板; ③附件存档至少勾一种
    ∈{excel03,excel07,word,pdf}; ④端口∈[1,65535], ==21 时 WARN; ⑤保存路径按 server_os
    分治(Windows=相对 SFTP 根目录, Linux=绝对路径); ⑥auth_mode=key 时 key_format 必须
    OpenSSH 且 file_upload_verify 必须 false; ⑦集群+切换文件服务器时 webroot_copied 必须
    true。配置由 OPTIONS['sftp_cfg'] 提供。来源: doc-3573。"""
    out = []
    raw = _read_text(cpt_path)
    cfg = OPTIONS.get("sftp_cfg")
    if cfg is None:
        if _has(raw, "SFTP", "sftp"):
            return [("WARN", "检测到「SFTP 上传」标记但未提供 OPTIONS['sftp_cfg']: SFTP 服务器配置在"
                    "任务侧, .cpt 内不可观察, 请提供 cfg 后校验(doc-3573)。")]
        return [("WARN", "未发现「SFTP 上传附件」标记且未提供 OPTIONS['sftp_cfg']; 假设不走 SFTP "
                 "上传, 跳过强校验(doc-3573)。")]
    errors, warns = [], []
    jar = cfg.get("jar_version") or ""
    if not jar:
        warns.append("未声明 jar_version: SFTP 上传附件需 JAR >= %s, 无法核验(doc-3573)" % SFTP_JAR_MIN)
    elif jar < SFTP_JAR_MIN:
        errors.append("JAR 版本 %s < %s: 该版本「文件处理」步骤无 SFTP 上传选项(doc-3573)"
                      % (jar, SFTP_JAR_MIN))
    otype = cfg.get("object_type")
    if otype != "报表模板":
        errors.append("调度对象类型为 %r: 仅当对象类型为「报表模板」时才支持 SFTP 上传附件(doc-3573)"
                      % otype)
    fmts = cfg.get("attach_formats") or []
    if not fmts:
        errors.append("「附件存档」未勾选任何格式: 任务会成功执行但 SFTP 上无任何产物(doc-3573)")
    else:
        bad_fmt = [f for f in fmts if f not in VALID_ATTACH_FORMATS]
        if bad_fmt:
            errors.append("附件存档含非法格式 %s, 应 ∈ %s(doc-3573)"
                          % (bad_fmt, sorted(VALID_ATTACH_FORMATS)))
    if not cfg.get("host"):
        errors.append("服务器地址(SFTP 服务器 IP)为空(doc-3573)")
    port = cfg.get("port")
    if not isinstance(port, int) or not (1 <= port <= 65535):
        errors.append("端口 %r 非法, 应 ∈ [1,65535](SFTP 通常 22)(doc-3573)" % port)
    elif port == 21:
        warns.append("端口为 21(FTP 默认端口): SFTP 通常为 22, 请确认未混用 FTP 配置(doc-3573)")
    server_os = (cfg.get("server_os") or "").lower()
    save_path = cfg.get("save_path", "")
    if server_os not in VALID_SERVER_OS:
        errors.append("server_os %r 非法, 应 ∈ {windows, linux}: 保存路径语义由它决定(doc-3573)"
                      % cfg.get("server_os"))
    elif not save_path:
        errors.append("保存路径为空(doc-3573)")
    elif server_os == "windows":
        if ":\\" in save_path:
            errors.append("Windows SFTP 保存路径 %r 像本地绝对路径: 应填相对 SFTP 根目录的路径"
                          "(根目录本身写 '/')(doc-3573)" % save_path)
    elif not save_path.startswith("/"):
        errors.append("Linux SFTP 保存路径 %r 必须是绝对路径(以 '/' 开头)(doc-3573)" % save_path)
    if not cfg.get("username"):
        errors.append("SFTP 用户名为空, 连接将被拒绝(doc-3573)")
    auth = cfg.get("auth_mode")
    if auth not in VALID_AUTH_MODES:
        errors.append("auth_mode %r 非法, 应 ∈ {password, key}(doc-3573)" % auth)
    elif auth == "password":
        if not cfg.get("password"):
            errors.append("认证方式为直接输入密码, 但密码为空(doc-3573)")
    else:
        if not cfg.get("key_file"):
            errors.append("认证方式为上传密钥文件, 但 key_file 为空(doc-3573)")
        if cfg.get("key_format") != "OpenSSH":
            errors.append("密钥格式 %r 不受支持: 定时调度仅支持 OpenSSH 格式, 否则连接 SFTP 失败"
                          "(doc-3573)" % cfg.get("key_format"))
        if cfg.get("file_upload_verify"):
            errors.append("使用密钥文件时必须关闭平台「文件上传校验」开关, 否则密钥无法上传(doc-3573)")
    if cfg.get("cluster") and cfg.get("file_server_switched"):
        if not cfg.get("webroot_copied"):
            errors.append("集群已切换文件服务器方式, 但未把 %FR_HOME%\\webapps\\webroot 复制到文件"
                          "服务器根目录, 定时调度任务无法正常执行(doc-3573)")
    for e in errors:
        out.append(("ERROR", e))
    for w in warns:
        out.append(("WARN", w))
    if not errors and not warns:
        out.append(("OK", "SFTP 上传附件配置合规(doc-3573)。"))
    return out


# ---------------------------------------------------------------------------
# 35. doc-3573 定时调度对象参数默认值
# ---------------------------------------------------------------------------
def check_schedule_object_param(cpt_path: str):
    """doc-3573 定时调度对象参数默认值: 凡 .cpt 被标为「定时调度对象」用途, 断言其所有
    ReportParameter/Parameter 的 value 非空(或在任务侧「调度对象>参数设置」显式绑定),
    否则 ERROR —— 定时任务无人交互, 参数取空时附件照样生成并上传, 用户看到「SFTP 上有文件、
    打开是空的」而排查方向全跑偏。来源: doc-3573。"""
    out = []
    raw = _read_text(cpt_path)
    spec = OPTIONS.get("schedule_spec")
    marked = _has(raw, "定时调度", "调度对象", "schedule") or spec is not None
    if not marked:
        return [("WARN", "未发现「定时调度对象」标记且未提供 OPTIONS['schedule_spec']; 假设未挂调度, "
                 "跳过参数默认值校验(doc-3573)。")]
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验调度对象参数默认值(doc-3573)")]
    tpl_params = _template_params(root)
    if not tpl_params:
        return [("OK", "模板无参数, 调度对象参数默认值检查通过(doc-3573)。")]
    spec_params = {p.get("name"): p for p in (spec.get("object") or {}).get("params", [])} if spec else {}
    for name, default in sorted(tpl_params.items()):
        if default:
            out.append(("OK", "参数 %s 有默认值 %r, 定时执行可取到值(doc-3573)" % (name, default)))
        elif name in spec_params:
            out.append(("OK", "参数 %s 无模板默认值, 但任务侧「调度对象>参数设置」显式绑定(doc-3573)"
                        % name))
        else:
            out.append(("ERROR", "参数 %s 无默认值且未在调度对象参数设置中绑定: 定时执行取空, 附件"
                        "照样生成并上传, 打开是空表且全链路零报错(doc-3573)" % name))
    return out


# ---------------------------------------------------------------------------
# 36. doc-4152 数据连接使用权限 —— 连接依赖抽取(两种写法)
# ---------------------------------------------------------------------------
def _extract_connections(root) -> list:
    """抽取模板引用的全部数据连接名, 覆盖两种写法:
    ①<Connection class="...NameDatabaseConnection"><DatabaseName>(数据集侧)
    ②<DataSource><ConnectionAttr><NameDatabaseConnection><DatabaseName>(填报提交侧,
    元素名即类名无 class 属性)。
    返回 [(连接名或 None, 位置描述), ...](None=空连接名)。
    移植 practice/topic_4152/check_conn_permission.py extract_connections()。"""
    found = []
    parent = _parent_map(root)

    def locate(node):
        cur = node
        while cur is not None:
            if cur.tag == "TableData":
                return "数据集 %s" % (cur.get("name") or "?")
            if cur.tag == "DBManipulation":
                return "填报提交 %s" % (cur.get("table") or "?")
            cur = parent.get(cur)
        return "模板"

    for node in root.iter():
        is_a = node.tag == "Connection" and (node.get("class") or "").endswith("NameDatabaseConnection")
        is_b = node.tag == "NameDatabaseConnection"
        if not (is_a or is_b):
            continue
        dbn = node.find("DatabaseName")
        if dbn is None or not (dbn.text or "").strip():
            found.append((None, locate(node)))
        else:
            found.append(((dbn.text or "").strip(), locate(node)))
    return found


def check_conn_refs(cpt_path: str):
    """doc-4152 数据连接依赖抽取(纯模板侧, 无需第二输入): 抽取并列出模板引用的全部数据连接名,
    必须同时覆盖数据集侧(<Connection class="...NameDatabaseConnection"><DatabaseName>)与填报
    提交侧(<DataSource><ConnectionAttr><NameDatabaseConnection><DatabaseName>); 空 DatabaseName
    报错。移植 practice/topic_4152/check_conn_permission.py extract_connections()。
    来源: doc-4152。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法抽取数据连接依赖(doc-4152)")]
    refs = _extract_connections(root)
    if not refs:
        return [("OK", "模板未引用任何数据连接, 本规则不适用(doc-4152)。")]
    seen = set()
    for name, where in refs:
        if name is None:
            out.append(("ERROR", "%s 的 NameDatabaseConnection 缺 DatabaseName(空连接名) -> 预览/提交"
                        "将报连接错误(doc-4152)" % where))
        else:
            if name not in seen:
                seen.add(name)
                out.append(("OK", "%s 引用数据连接「%s」(doc-4152 依赖清单)" % (where, name)))
    return out


# ---------------------------------------------------------------------------
# 37. doc-4153 数据连接管理权限 —— 连接名白名单
# ---------------------------------------------------------------------------
def check_conn_whitelist(cpt_path: str):
    """doc-4153 数据连接管理权限: 可选「数据连接名白名单」校验 —— 模板引用了白名单外的
    DatabaseName 则 WARN(2)。白名单由 OPTIONS['conn_whitelist'] 提供; 未提供时降级 WARN
    说明假设(连接名是工程级外部依赖, 跨环境交付时「连接名写错/没改」是高频上线事故)。
    来源: doc-4153。"""
    out = []
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验连接名白名单(doc-4153)")]
    refs = _extract_connections(root)
    names = [n for n, _ in refs if n]
    if not names:
        return [("OK", "模板未引用任何数据连接, 本规则不适用(doc-4153)。")]
    wl = OPTIONS.get("conn_whitelist")
    if wl is None:
        return [("WARN", "模板引用连接 %s; 未提供 OPTIONS['conn_whitelist'](目标服务器连接名白名单): "
                 "无法判定越界, 请跨环境交付前核对连接名(连接存在性/权限属服务器侧, doc-4153)"
                 % sorted(set(names)))]
    bad = sorted(set(names) - set(wl))
    if bad:
        out.append(("WARN", "模板引用了白名单外的连接名 %s(白名单: %s): 目标工程可能没有这些连接, "
                    "请确认运行账号对其有「使用」权限(doc-4153)" % (bad, sorted(wl))))
    else:
        out.append(("OK", "模板引用的连接 %s 全部在目标服务器白名单内(doc-4153)" % sorted(set(names))))
    return out


# ---------------------------------------------------------------------------
# 38. doc-2574 [平台]HSQL 数据连接
# ---------------------------------------------------------------------------
HSQL_DRIVER = "com.fr.third.org.hsqldb.jdbcDriver"
HSQL_URL_PREFIX = "jdbc:hsqldb:"
_TABLE_RE = re.compile(r"\b(?:FROM|JOIN)\s+(?!\()([A-Za-z0-9_$.\"\[\]]+)", re.IGNORECASE)
_FR_PARAM_RE = re.compile(r"\$\{[^}]*\}", re.DOTALL)


def check_hsql_conn(cpt_path: str):
    """doc-2574 [平台]HSQL 数据连接: 清单侧(driver/url/schema/FineDB/内存模式/路径可移植性)
    + SQL 侧(表名数字开头/缺 schema 前缀), 退出码沿用 0/1/2。
    清单由 OPTIONS['hsql_manifest'](json 路径)提供; 未提供时降级 WARN 说明假设
    (驱动/URL/模式属服务端事实, .cpt 内只有连接名, 无法静态核对)。
    移植 practice/topic_2574/check_hsql_conn.py 规则形态。来源: doc-2574。"""
    out = []
    manifest_path = OPTIONS.get("hsql_manifest")
    root = _load_root(cpt_path)
    if manifest_path is None:
        return [("WARN", "未提供 OPTIONS['hsql_manifest'](数据连接清单 json): 驱动/URL/schema/FineDB"
                 "等属服务端事实, .cpt 内只有连接名, 无法静态核对 HSQL 规则(doc-2574)。"
                 + ("模板含 %d 个数据集, 若其中连接为 HSQL, 表名不得以数字开头且建议带 schema 前缀"
                    % len(_table_datas(root)) if root is not None else ""))]
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            conns = json.load(f).get("connections", [])
    except Exception as e:
        return [("WARN", "HSQL 清单读取失败(%s): 无法校验(doc-2574)" % e)]
    hsql_names = set()
    for c in conns:
        if str(c.get("type", "")).upper() != "HSQL":
            continue
        name = c.get("name", "<未命名>")
        hsql_names.add(name)
        if c.get("driver") != HSQL_DRIVER:
            out.append(("ERROR", "连接 %s: driver=%r, HSQL 应为 %s(FR 重打包命名空间, 非 "
                        "org.hsqldb.jdbcDriver)(doc-2574 H1)" % (name, c.get("driver"), HSQL_DRIVER)))
        url = c.get("url", "")
        if not url.startswith(HSQL_URL_PREFIX):
            out.append(("ERROR", "连接 %s: url=%r 不是 HSQL URL, 应以 %s 开头(doc-2574 H2)"
                        % (name, url, HSQL_URL_PREFIX)))
            continue
        low = url.lower()
        if "finedb" in low:
            out.append(("ERROR", "连接 %s: url 指向内置 FineDB(%s)。doc-2574 注2 明确『非必要请勿创建"
                        "内置 FineDB 数据库的数据连接』(doc-2574 H3)" % (name, url)))
        if low.startswith("jdbc:hsqldb:mem:"):
            out.append(("WARN", "连接 %s: 使用 mem 内存模式, 重启即丢数据, 不应作为报表取数源"
                        "(doc-2574 H4)" % name))
        if low.startswith("jdbc:hsqldb:file:"):
            path = url[len("jdbc:hsqldb:file:"):]
            if re.match(r"^[A-Za-z]:", path) or "\\" in path:
                out.append(("WARN", "连接 %s: file 路径 %r 为盘符绝对路径/含反斜杠, 跨环境不可移植, "
                            "须逐环境覆盖(doc-2574 H5)" % (name, path)))
        if not c.get("schema"):
            out.append(("WARN", "连接 %s: 未声明 schema。FR 侧不选模式则默认取第一个模式, 建议显式"
                        "声明(HSQL 默认 PUBLIC)(doc-2574 H6)" % name))
    # SQL 侧: 仅对 HSQL 连接的数据集套规则
    if root is not None:
        for td in root.iter("TableData"):
            if "DBTableData" not in (td.get("class") or ""):
                continue
            ds = td.get("name") or "?"
            conn_node = td.find("./Connection/DatabaseName")
            conn = (conn_node.text or "").strip() if conn_node is not None else ""
            if conn not in hsql_names:
                continue
            q = td.find("./Query")
            sql = (q.text or "") if q is not None else ""
            cleaned = _FR_PARAM_RE.sub(" ", sql)
            for m in _TABLE_RE.finditer(cleaned):
                token = m.group(1).rstrip(",")
                bare = token.split(".")[-1].strip('"[]`')
                if not bare:
                    continue
                if bare[0].isdigit():
                    out.append(("ERROR", "数据集 %s(连接 %s): 表名 %r 以数字开头。HSQL 应避免数字"
                                "开头的表名, 否则连接/取数可能报错(doc-2574 H7)" % (ds, conn, token)))
                if "." not in token:
                    out.append(("WARN", "数据集 %s(连接 %s): 表名 %r 未带 schema 前缀, 将落回连接侧"
                                "默认模式, 建议写成 PUBLIC.%s(doc-2574 H8)" % (ds, conn, token, token)))
    if not out:
        out.append(("OK", "HSQL 连接清单与模板 SQL 检查通过(doc-2574)。"))
    return out


# ---------------------------------------------------------------------------
# 39. doc-3550 cpt 模板转 cptx 格式 —— 同名覆盖告警
# ---------------------------------------------------------------------------
def check_cptx_override(cpt_path: str):
    """doc-3550 cpt模板转cptx格式: 若某 .cpt 同级已存在同名 .cptx, 且本次属于 headless 重新
    生成, 输出警告(批量转换「如已存在此文件则进行覆盖」, 重生成流程会静默丢失 cptx)。
    来源: doc-3550。"""
    base = os.path.splitext(cpt_path)[0]
    cptx = base + ".cptx"
    if os.path.isfile(cptx):
        return [("WARN", "同级已存在同名 %s: 若本次属于 headless 重新生成 .cpt, 批量转换会覆盖已"
                "转换的 cptx 产物 —— 请先备份或跳过该模板(doc-3550)" % os.path.basename(cptx))]
    return [("OK", "同级不存在同名 .cptx, 无覆盖风险(doc-3550)。")]


# ---------------------------------------------------------------------------
# 40. doc-996 单数据集分页 SQL(行式引擎)
# ---------------------------------------------------------------------------
DIALECTS = {
    "sqlite":        {"need_page_query": True,  "require_order_by": False},
    "access":        {"need_page_query": True,  "require_order_by": False},
    "sqlserver2005": {"need_page_query": True,  "require_order_by": False},
    "sqlserver2008": {"need_page_query": True,  "require_order_by": False},
    "informix":      {"need_page_query": True,  "require_order_by": False},
    "sybase":        {"need_page_query": True,  "require_order_by": False},
    "oracle":        {"need_page_query": False, "require_order_by": False},
    "mysql":         {"need_page_query": False, "require_order_by": False},
    "hsql":          {"need_page_query": False, "require_order_by": False},
    "sqlserver2012": {"need_page_query": False, "require_order_by": True},
}
DIALECT_HINTS = {
    "sqlite": ("sqlite",), "access": ("access", "mdb"),
    "sqlserver": ("sqlserver", "mssql", "sql server"), "oracle": ("oracle",),
    "mysql": ("mysql",), "hsql": ("hsql",), "informix": ("informix",),
    "sybase": ("sybase",), "db2": ("db2",),
}


def _infer_dialect(root, raw) -> str:
    d = OPTIONS.get("dialect")
    if d:
        return d.lower()
    low = raw.lower()
    for key, hints in DIALECT_HINTS.items():
        if any(h in low for h in hints):
            if key == "sqlserver":
                return "sqlserver2012"
            return key
    return ""


def _select_lists(sql):
    norm = re.sub(r"\$\{[^}]*\}", "_FRVAR_", sql or "", flags=re.S)
    return [re.sub(r"\s+", "", x)
            for x in re.findall(r"select\s+(?:top\s+\S+\s+)?(.*?)\s+from\s", norm, re.S | re.I)]


def _inner_select_list(sql):
    ls = [x for x in _select_lists(sql) if x != "*"]
    return ls[-1] if ls else "*"


def check_page_query(cpt_path: str):
    """doc-996 单数据集分页 SQL(移植 practice/topic_996/gen_page_query.py 的 check()):
    ①必须写分页 SQL 的方言 PageQuery 为空 -> ERROR; ②Query 与 PageQuery 字段顺序不一致 ->
    ERROR; ③视图/无唯一键源却无 row_number() -> ERROR; ④主查询 WHERE 未同步进 PageQuery ->
    ERROR; ⑤PageQuery 缺 fr_rowcount 末页公式或缺 ORDER BY -> ERROR; ⑥SQLServer2012+ 主查询
    无 ORDER BY -> ERROR; ⑦移动端交付+行式引擎 -> WARN。方言由 OPTIONS['dialect'] 或连接名推断。
    来源: doc-996。"""
    out = []
    raw = _read_text(cpt_path)
    root = _load_root(cpt_path)
    if root is None:
        return [("ERROR", "XML 解析失败, 无法校验分页 SQL(doc-996)")]
    tables = _table_datas(root)
    db_tables = [t for t in tables if t[3] is not None or t[2]]
    if not db_tables and "PageQuery" not in raw:
        return [("OK", "未发现带 <PageQuery> 的 DBTableData, 本规则不适用(doc-996)。")]
    dialect = _infer_dialect(root, raw)
    row_engine = _row_engine_enabled(root)
    page_engine = _has(raw, "按页", "分段", "PageEngine", "pageEngine")
    is_view = _has(raw, "视图", "view") and "is_view" in raw or _has(raw, "create view")
    mobile = _has(raw, "移动端", "mobile", "app", "h5")
    if not dialect:
        return [("WARN", "无法推断数据库方言(OPTIONS['dialect'] 未设置且连接名无特征): 分页 SQL "
                 "规则无法精确判定, 请设置 OPTIONS['dialect'](doc-996)。")]
    d = DIALECTS.get(dialect)
    if d is None:
        return [("WARN", "未知数据库方言 %r: 分页 SQL 规则跳过(doc-996)" % dialect)]
    if not row_engine and not _has(raw, "PageQuery"):
        return [("OK", "未开启行式引擎且无分页 SQL, 本规则不适用(doc-996)。")]
    if not (row_engine and page_engine):
        out.append(("ERROR", "报表引擎属性须同时勾选「行式引擎」与「按页运算分段执行」(当前 "
                    "row_engine=%s page_engine=%s), 否则 PageQuery 不生效(doc-996 §3.4)"
                    % (row_engine, page_engine)))
    if mobile and row_engine:
        out.append(("WARN", "行式引擎不支持移动端(App/H5), 该模板若面向移动端需换方案(doc-996 §1 注)"))
    for tname, _conn, query, page_sql in tables:
        if d["need_page_query"] and not (page_sql or "").strip():
            out.append(("ERROR", "数据集 %s: %s 必须编写分页 SQL, <PageQuery> 不能为空, 否则勾了"
                        "行式引擎也不分页(doc-996)" % (tname, dialect)))
        if not d["need_page_query"] and (page_sql or "").strip():
            out.append(("WARN", "数据集 %s: %s 行式引擎自带分页, PageQuery 建议留空(doc-996)"
                        % (tname, dialect)))
        if d["require_order_by"] and not re.search(r"\border\s+by\b", query or "", re.I):
            out.append(("ERROR", "数据集 %s: SQL Server 2012+ 行式引擎要求主查询 <Query> 必须写"
                        "ORDER BY(doc-996)" % tname))
        if (page_sql or "").strip():
            ps = page_sql
            for v in ("fr_pagenumber", "fr_pagesize"):
                if v not in ps:
                    out.append(("ERROR", "数据集 %s: 分页 SQL 缺少变量 %s(doc-996)" % (tname, v)))
            if "fr_rowcount" not in ps:
                out.append(("ERROR", "数据集 %s: 分页 SQL 缺少 fr_rowcount(末页行数公式丢失, 最后"
                            "一页会多取行)(doc-996)" % tname))
            q, p = _select_lists(query or "")[:1], _inner_select_list(ps)
            if q and p and q[0] != "*" and p != "*" and q[0] != p:
                out.append(("ERROR", "数据集 %s: Query 与 PageQuery 字段顺序/列表不一致(%s vs %s), "
                            "导出会与预览有差异(doc-996)" % (tname, q[0], p)))
            if is_view and "row_number" not in ps.lower():
                out.append(("ERROR", "数据集 %s: 视图表分页必须用 row_number() 生成唯一排序键, "
                            "否则多页重复显示(doc-996)" % tname))
            mw = re.search(r"\bwhere\b(.*?)(?:\border\s+by\b|$)", query or "", re.S | re.I)
            if mw:
                cond = re.sub(r"\s+", "", mw.group(1))
                if cond and cond not in re.sub(r"\s+", "", ps):
                    out.append(("ERROR", "数据集 %s: 主查询的 WHERE 条件未写入分页 SQL, 分页时查不"
                                "出数据(doc-996)" % tname))
            if not re.search(r"\border\s+by\b", ps, re.I):
                out.append(("ERROR", "数据集 %s: 分页 SQL 缺少 ORDER BY, 排序不稳定会跨页重复/丢行"
                            "(doc-996)" % tname))
    if not any(lv in ("ERROR", "WARN") for lv, _ in out):
        out.append(("OK", "分页 SQL 规则检查通过(方言 %s)(doc-996)" % dialect))
    return out


# ---------------------------------------------------------------------------
# 41. doc-683 定时调度生成的附件 —— 结果文件扩展名白名单
# ---------------------------------------------------------------------------
RESULT_EXT_WHITELIST = {"cpr", "frr", "doc", "pdf", "xls", "xlsx", "png"}
EXPORT_TYPE_TO_EXT = {"RESULT_REPORT": "cpr", "WORD": "doc", "PDF": "pdf",
                      "EXCEL": "xls", "EXCEL2007": "xlsx", "IMAGE": "png"}
VALID_FORMAT_TOKENS = {"excel", "word", "pdf", "image", "cpr", "frr", "xls", "xlsx", "doc", "png"}


def check_schedule_result_ext(cpt_path: str):
    """doc-683 定时调度生成的附件: 将结果文件扩展名固化为白名单 CPR/FRR、Doc、PDF、XLS、XLSX、
    PNG(含导出类型->扩展名映射, 如 EXCEL2007->xlsx、IMAGE->png)。扫描模板内导出格式引用
    (format=/extype=/文件名后缀), 断言落在合法集合, 防无头导出/校验只认 PDF/XLSX 而漏掉
    CPR/Doc/PNG 等合法定时产物。来源: doc-683。"""
    out = []
    raw = _read_text(cpt_path)
    hits = []
    for m in re.finditer(r"format\s*=\s*['\"]?([A-Za-z0-9_]+)", raw, re.I):
        hits.append(("format", m.group(1).lower()))
    for m in re.finditer(r"__filename__[^;\n]*?\.([A-Za-z0-9]+)", raw, re.I):
        hits.append(("文件名", m.group(1).lower()))
    for m in re.finditer(r"extype\s*=\s*['\"]?([A-Za-z0-9_]+)", raw, re.I):
        hits.append(("extype", m.group(1).lower()))
    if not hits:
        return [("OK", "未发现导出格式/文件名扩展引用, 本规则不适用(doc-683)。")]
    bad = [(kind, v) for kind, v in hits if v not in VALID_FORMAT_TOKENS and v not in
           {"page", "simple", "sheet", "stream"}]
    for kind, v in bad:
        out.append(("WARN", "导出 %s=%r 不在结果文件白名单 %s 内: 定时产物可能被下游漏收(合法七种: "
                    "CPR/FRR、Doc、PDF、XLS、XLSX、PNG)(doc-683)"
                    % (kind, v, sorted(RESULT_EXT_WHITELIST))))
    if not bad:
        out.append(("OK", "导出格式引用全部落在白名单内(扩展名映射: EXCEL2007->xlsx, IMAGE->png 等)"
                    "(doc-683)。"))
    return out


# ---------------------------------------------------------------------------
# 42. doc-3403 图表导出升级说明 —— 环境预检
# ---------------------------------------------------------------------------
def check_chart_export_env(cpt_path: str):
    """doc-3403 图表导出升级说明: 环境预检动作 —— Linux 目标机需核对 GLIBC/GLIBCXX 版本
    (低于 GLIBC_2.17 / GLIBCXX_3.4.22 且 JDK<1.8 且无 J2V8 .so 时, 图表导出空白并硬报错,
    属环境缺陷而非模板错误)。.cpt 静态无法读取目标机环境, 降级为保守 WARN 说明假设;
    若模板含图表则加强提示。来源: doc-3403。"""
    out = []
    raw = _read_text(cpt_path)
    has_chart = any(m in raw for m in CHART_MARKERS)
    if not has_chart:
        return [("OK", "模板不含图表, 图表导出环境预检不适用(doc-3403)。")]
    out.append(("WARN", "模板含图表且目标为 Linux 部署时, 导出/定时调度图表依赖 J2V8 环境: 前置"
                "校验命令 strings /lib64/libc.so.6 | grep GLIBC(需 >= GLIBC_2.17)与 strings "
                "/usr/lib64/libstdc++.so.6 | grep GLIBCXX(需 >= GLIBCXX_3.4.22), 并确保 JDK>=1.8 "
                "或存在 libj2v8_linux_x86_64.so; 否则图表导出空白且报环境错误 —— 该问题只影响图表, "
                "排障先区分「图表空白 vs 整表空白」(doc-3403)。"))
    return out


# ---------------------------------------------------------------------------
# RULES 注册表(42 条, 与 B_rules_export.json 条目一一对应)
# ---------------------------------------------------------------------------
RULES = [
    {"name": "schedule_formula", "fn": check_schedule_formula, "doc": "doc-3315",
     "context": "仅定时调度对象", "apply": "模板被标为「定时调度对象」用途(注释/参数/公式标记)"},
    {"name": "mobile_dropdown_scope", "fn": check_mobile_dropdown_scope, "doc": "doc-3260",
     "context": "仅移动端简约下拉样式插件场景", "apply": "模板含 ComboBox/ComboCheckBox/TreeComboBox 控件"},
    {"name": "mobile_calendar_scope", "fn": check_mobile_calendar_scope, "doc": "doc-3045",
     "context": "仅日期移动端日历样式插件场景", "apply": "模板含 DateEditor 日期控件"},
    {"name": "dataset_conn", "fn": check_dataset_conn, "doc": "doc-299",
     "context": "所有引用数据连接的模板", "apply": "存在 TableData 数据集"},
    {"name": "excel_export_rowengine_sheet", "fn": check_excel_export_rowengine_sheet, "doc": "doc-1123",
     "context": "仅 Excel 导出模板", "apply": "行式引擎开关或 extype=sheet 等导出标记"},
    {"name": "xlsx_readiness", "fn": check_xlsx_readiness, "doc": "doc-1123",
     "context": "仅预期导出 .xlsx 的模板", "apply": "任意 .cpt(行式引擎开关判定)"},
    {"name": "export_toolbar", "fn": check_export_toolbar, "doc": "doc-786",
     "context": "仅 Web 工具栏含导出按钮的模板", "apply": "存在 <ShortCut> 节点"},
    {"name": "word_export_headerfooter", "fn": check_word_export, "doc": "doc-1130",
     "context": "仅 Word 导出模板", "apply": "存在 ReportPageAttr/PageHeader/PageFooter 或 word 标记"},
    {"name": "word_rowheight", "fn": check_word_rowheight, "doc": "doc-1128",
     "context": "仅导出可编辑 Word 模板", "apply": "spec 声明导出可编辑 Word(WordExportAttr/word 标记)"},
    {"name": "bigdata_export_route", "fn": check_bigdata_export_route, "doc": "doc-4524",
     "context": "仅大数据导出模板", "apply": "direct/export、directExportToExcel、format=excel 等标记"},
    {"name": "bigdata_export_scale", "fn": check_bigdata_export_scale, "doc": "doc-4524",
     "context": "仅无头大数据导出调用", "apply": "大数据导出标记 + OPTIONS 提供行/列数"},
    {"name": "report_router", "fn": check_report_router, "doc": "doc-3710",
     "context": "仅参数面板路由导出模板", "apply": "存在 DictItem 路由下拉字典或 viewlet 导出按钮"},
    {"name": "toolbar_single_export", "fn": check_toolbar_single_export, "doc": "doc-1819",
     "context": "仅自定义工具栏导出按钮模板", "apply": "JS 含 servletURL + viewlet 形态"},
    {"name": "schedule_ready", "fn": check_schedule_ready, "doc": "doc-2208",
     "context": "仅定时调度对象", "apply": "模板被标为「将挂定时调度」用途(调度标记/spec)"},
    {"name": "privilege_content", "fn": check_privilege_content, "doc": "doc-866",
     "context": "仅细粒度权限场景", "apply": "模板含 PrivilegeControl 或提供 OPTIONS['privilege_spec']"},
    {"name": "fine_param", "fn": check_fine_param, "doc": "doc-865",
     "context": "仅权限细粒度参数控制模板", "apply": "模板含 $fine_* 系统参数引用"},
    {"name": "email_recipient", "fn": check_email_recipient, "doc": "doc-684",
     "context": "仅「收件人=单元格」的邮件调度", "apply": "模板被标为邮件通知用途(收件人/邮件标记)"},
    {"name": "page_preview", "fn": check_page_preview, "doc": "doc-135",
     "context": "所有含 Web 属性的模板", "apply": "存在 <ReportWebAttr>/<WebPageContent>"},
    {"name": "setvisible", "fn": check_setvisible, "doc": "doc-1736",
     "context": "决策报表/含 JS 的模板", "apply": "存在 _g().getWidgetByName(..).setVisible(..)"},
    {"name": "bigdata_export_event", "fn": check_bigdata_export_event, "doc": "doc-3610",
     "context": "仅大数据集导出事件模板", "apply": "大数据集导出事件标记(bigdata/directExportToExcel)"},
    {"name": "direct_export", "fn": check_direct_export, "doc": "doc-3342",
     "context": "仅 direct/export 按钮模板", "apply": "文本含 direct/export"},
    {"name": "stream_export", "fn": check_stream_export, "doc": "doc-1407",
     "context": "仅流式导出模板", "apply": "format=excel / extype=stream / 流式标记"},
    {"name": "bigdata_export_plan", "fn": check_bigdata_export_plan, "doc": "doc-1120",
     "context": "仅大数据量导出模板", "apply": "行式引擎开关或 Excel 导出标记"},
    {"name": "direct_export_paramstr", "fn": check_direct_export_paramstr, "doc": "doc-4518",
     "context": "仅 directExportToExcel 模板", "apply": "存在 directExportToExcel 调用"},
    {"name": "export_perf", "fn": check_export_perf, "doc": "doc-4418",
     "context": "大数据模板导出慢排查", "apply": "图表/webimage/老驱动标记或提供 export_url"},
    {"name": "peruser_dispatch", "fn": check_peruser_dispatch, "doc": "doc-695",
     "context": "仅 per-user 邮件分发调度", "apply": "per-user 分发标记(单独生成结果/fine_* 引用)"},
    {"name": "schedule_param_name", "fn": check_schedule_param_name, "doc": "doc-683",
     "context": "仅定时调度/per-user 分发", "apply": "调度标记或提供 schedule_spec"},
    {"name": "dispatch_formula", "fn": check_dispatch_formula, "doc": "doc-688",
     "context": "仅公式判断执行条件调度", "apply": "公式判断标记或提供 OPTIONS['dispatch_formula']"},
    {"name": "mount_ready", "fn": check_mount_ready, "doc": "doc-2209",
     "context": "仅挂载平台调度", "apply": "挂载标记或提供 OPTIONS['mount_name']"},
    {"name": "platform_notify", "fn": check_platform_notify, "doc": "doc-4432",
     "context": "仅平台通知调度", "apply": "平台通知标记或提供 OPTIONS['notify_spec']"},
    {"name": "sms_ready", "fn": check_sms_ready, "doc": "doc-2210",
     "context": "仅短信通知调度", "apply": "短信标记或提供 OPTIONS['sms_cfg']"},
    {"name": "app_notify", "fn": check_app_notify, "doc": "doc-1387",
     "context": "仅 APP通知/op=write 对外链接", "apply": "op=write/APP通知标记或提供 notify_link"},
    {"name": "ftp_upload", "fn": check_ftp_upload, "doc": "doc-682",
     "context": "仅 FTP 上传附件调度", "apply": "FTP 标记或提供 OPTIONS['ftp_cfg']"},
    {"name": "sftp_upload", "fn": check_sftp_upload, "doc": "doc-3573",
     "context": "仅 SFTP 上传附件调度", "apply": "SFTP 标记或提供 OPTIONS['sftp_cfg']"},
    {"name": "schedule_object_param", "fn": check_schedule_object_param, "doc": "doc-3573",
     "context": "仅定时调度对象", "apply": "调度标记或提供 schedule_spec"},
    {"name": "conn_refs", "fn": check_conn_refs, "doc": "doc-4152",
     "context": "所有引用数据连接的模板", "apply": "存在 Connection/NameDatabaseConnection 引用"},
    {"name": "conn_whitelist", "fn": check_conn_whitelist, "doc": "doc-4153",
     "context": "跨环境交付模板", "apply": "存在连接引用(白名单由 OPTIONS 提供)"},
    {"name": "hsql_conn", "fn": check_hsql_conn, "doc": "doc-2574",
     "context": "仅 HSQL 数据连接场景", "apply": "提供 OPTIONS['hsql_manifest'] 清单"},
    {"name": "cptx_override", "fn": check_cptx_override, "doc": "doc-3550",
     "context": "仅 headless 重生成 .cpt 流程", "apply": "同级存在同名 .cptx"},
    {"name": "page_query", "fn": check_page_query, "doc": "doc-996",
     "context": "仅行式引擎分页 SQL 模板", "apply": "存在 <PageQuery> 且行式引擎/分页标记"},
    {"name": "schedule_result_ext", "fn": check_schedule_result_ext, "doc": "doc-683",
     "context": "仅定时调度/导出配置", "apply": "模板内出现 format=/extype=/__filename__ 引用"},
    {"name": "chart_export_env", "fn": check_chart_export_env, "doc": "doc-3403",
     "context": "仅 Linux 部署且含图表的模板", "apply": "模板含图表标记(ChartCollection 等)"},
]


# ---------------------------------------------------------------------------
# 汇总入口
# ---------------------------------------------------------------------------
def run_all(cpt_path: str) -> list:
    """遍历 RULES 汇总结果。返回 [{'rule','doc','context','level','msg'}, ...]。"""
    if not os.path.isfile(cpt_path):
        return [{"rule": "_file", "doc": "-", "context": "输入", "level": "ERROR",
                 "msg": "模板文件不存在: %s" % cpt_path}]
    # 文件级预检:解析失败只报 1 条,避免 42 条重复 ERROR
    # (R30 perf) 预检改走共享解析(_load_root_full):树只解析一次,错误消息用原始
    # 异常按原格式重建,与原 `try: ET.parse(...) except` 逐字等价。
    _r0, _x0 = _load_root_full(cpt_path)
    if _x0 is not None:
        return [{"rule": "xml_parse", "doc": "-", "context": "输入", "level": "ERROR",
                 "msg": "XML 解析失败: %s" % _x0}]
    results = []
    for r in RULES:
        try:
            items = r["fn"](cpt_path)
        except Exception as e:  # 单条规则异常不得中断整批
            items = [("ERROR", "规则 %s 执行异常: %s" % (r["name"], e))]
        for level, msg in items:
            results.append({"rule": r["name"], "doc": r["doc"], "context": r["context"],
                            "level": level, "msg": msg})
    return results


def exit_code(results: list) -> int:
    if any(r["level"] == "ERROR" for r in results):
        return 1
    if any(r["level"] == "WARN" for r in results):
        return 2
    return 0


def _print_results(results: list, only_rules=None):
    for r in results:
        if only_rules and r["rule"] not in only_rules:
            continue
        print("[%-5s] %-24s %-9s %s" % (r["level"], r["rule"], r["doc"], r["msg"]))
    n_e = sum(1 for r in results if r["level"] == "ERROR")
    n_w = sum(1 for r in results if r["level"] == "WARN")
    n_o = sum(1 for r in results if r["level"] == "OK")
    print("---- 规则 %d 条, ERROR=%d WARN=%d OK=%d ----" % (len(RULES), n_e, n_w, n_o))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    if "--list" in argv:
        for r in RULES:
            print("%-28s %-9s 语境: %s | 触发: %s" % (r["name"], r["doc"], r["context"], r["apply"]))
        return 0
    path = next((a for a in argv if not a.startswith("--")), None)
    if path is None:
        print("用法: python fr_rules_export.py <模板.cpt|.xml|.frm> [--only name1,name2] [--list]")
        return 2
    only_rules = None
    if "--only" in argv:
        only_rules = set(argv[argv.index("--only") + 1].split(","))
    results = run_all(path)
    _print_results(results, only_rules)
    if "--json" in argv:
        with open(argv[argv.index("--json") + 1], "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
