# -*- coding: utf-8 -*-
"""_common.py — dsl/skills 三生成器共享底座（R39 标准组件技能库）。

职责
----
1. semantic_layer.yaml 装载（唯一事实源，口径一律从这里取，禁止硬编码）
2. SQL 织入片段（numeric 转换 / period CASE / ORG+PERM）——全部由 semantic org/conventions
   模板参数化而来，与 dsl/compile.py 同口径
3. 房式 cpt 文档包装器（WorkBook 骨架与 compile.py 产物逐字同构）
4. guardrails 调用与 G5 环境类错误降级（对齐 compile.py 的 G5_ENV_RULES）

本目录是 R39 泳道独占写区（历史夜间批次 §三 并发纪律）；不改 dsl/ 任何既有文件。
"""
import datetime
import os
import sys
import xml.etree.ElementTree as ET

_HERE = os.path.dirname(os.path.abspath(__file__))
DSL_DIR = os.path.dirname(_HERE)                 # dsl/
REPO_ROOT = os.path.dirname(DSL_DIR)             # 仓库根

sys.path.insert(0, DSL_DIR)
import guardrails  # noqa: E402  （dsl/guardrails.py，产物验收闸）


class SkillError(Exception):
    """技能自身校验拒绝（坏 spec 的标准出口；golden runner 捕获后判 PASS）。"""


# ---------------------------------------------------------------- semantic 装载
def load_semantic(path=None):
    """装载 semantic_layer.yaml 为 dict。缺省取 dsl/semantic_layer.yaml。"""
    import yaml
    path = path or os.path.join(DSL_DIR, "semantic_layer.yaml")
    with open(path, "r", encoding="utf-8") as f:
        sem = yaml.safe_load(f.read()) or {}
    for key in ("org", "conventions", "meta"):
        if key not in sem:
            raise SkillError(f"semantic_layer 缺少 {key} 段（唯一事实源不完整）")
    return sem


def connection_name(sem):
    return (sem.get("meta") or {}).get("fr_connection_name") or "demo_connection"


# ---------------------------------------------------------------- SQL 织入片段
def numeric_cast(col, sem, alias=""):
    """varchar 数值列保护：COALESCE(NULLIF(col,'')::numeric,0)（semantic numeric_cast_template）。"""
    tpl = (sem["conventions"].get("numeric_cast_template")
           or "COALESCE(NULLIF({col},'')::numeric,0)")
    full = f"{alias}.{col}" if alias else col
    return tpl.replace("{col}", full)


def period_case(param, sem):
    """period CASE 模板（'Sep'→'9'）。param ∈ {para_month, para_month_bud}。"""
    tpl = sem["conventions"]["period_case_template"]
    return tpl.replace("para_month", param).strip()


def org_filter(sem, alias):
    """ORG 组织并集过滤（entity IN (四字段并集)，alias 化）。"""
    cond = sem["org"]["cascade_cond_template"].strip()
    union = sem["org"]["entity_union_template"].replace("{cascade_cond}", cond).strip()
    return union.replace("entity IN", f"{alias}.entity IN", 1)


def perm_filter(sem, alias=None):
    """PERM 权限过滤：管理员旁路 OR 用户 plant 映射。alias 给定时走 perm_on_alias 模板。"""
    if alias:
        return sem["org"]["perm_on_alias_template"].replace("{alias}", alias).strip()
    return sem["org"]["perm_template"].strip()


def _perm_for_table(spec, ds_entry, sem, alias):
    """按表列事实选择 PERM 形态（G5 实库冒烟教训：scenario_mapping 无 entity 列，
    entity IN 形态会直接 SQL 报错）:
      - spec.perm_form 显式指定（entity|plant）→ 按指定织入（调用方对列存在性负责，G5 兜底）
      - 表有 entity 列 → perm_on_alias（entity IN 用户映射，ORG 联动形态）
      - 表有 plant_code 列（无 entity）→ perm_exists_alias（EXISTS 形态，compile.py org 字典同构）
      - 列事实未固化/两列皆无 → SkillError（拒绝产出，不猜列名）
    """
    override = spec.get("perm_form")
    if override is not None:
        if override == "entity":
            return perm_filter(sem, alias)
        if override == "plant":
            return sem["org"]["perm_exists_alias_template"].replace("{alias}", alias).strip()
        raise SkillError(f"perm_form 只允许 entity|plant，得到 [{override}]")
    cols_fact = datasource_columns(ds_entry)
    if cols_fact and "entity" in cols_fact:
        return perm_filter(sem, alias)
    if cols_fact and "plant_code" in cols_fact:
        return sem["org"]["perm_exists_alias_template"].replace("{alias}", alias).strip()
    raise SkillError(
        f"[{spec.get('name')}] 表 {ds_entry.get('schema')}.{ds_entry.get('table')} 无 entity/plant_code "
        f"列事实（columns={'缺' if cols_fact is None else sorted(cols_fact)}），无法织入行级 PERM——"
        f"按纪律拒绝；如列存在请在 spec 显式给 perm_form=entity|plant，"
        f"或先在 semantic_layer.datasources.<key>.columns 固化列事实")


def cascade_params(sem):
    """ORG 过滤引用的级联参数（由 cascade_cond 模板事实推导，不硬编码）。"""
    import re
    cond = sem["org"]["cascade_cond_template"]
    seen, out = set(), []
    for name in re.findall(r"\$\{(para_[a-z_]+)\}", cond):
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def datasource_table(spec_source, sem):
    """semantic datasources 键 → schema.table 全名（防解析到 demo_ads 同名副本）。"""
    ds = (sem.get("datasources") or {}).get(spec_source)
    if not ds:
        raise SkillError(f"source [{spec_source}] 不在 semantic_layer.datasources: "
                         f"{sorted(sem.get('datasources') or {})}")
    return f"{ds['schema']}.{ds['table']}", ds


def datasource_columns(ds_entry):
    """数据源列事实（semantic columns 映射）；无映射时返回 None（跳过列校验）。"""
    cols = ds_entry.get("columns")
    return set(cols) if cols else None


# ---------------------------------------------------------------- 数据集 SQL 工厂
def build_fact_sql(spec, sem):
    """spec → 标准业务数据集 SQL（numeric 转换 / 过滤 / ORG+PERM / period CASE / ORDER BY）。

    spec 键（dataset_skill 与 chart_skill 共用契约）:
      source       semantic datasources 键（必填）
      alias        表别名（缺省 t）
      fields       输出列（必填，非空）
      numeric_cols 数值列（permission=full 时必填≥1，自动 numeric_cast）
      filters      原生 SQL 条件列表（AND 连接；禁分号/禁 ${{）
      params       引用参数名列表（用于声明；ORG 级联参数自动并入）
      period_param 织入 period CASE 的参数（para_month|para_month_bud，可选）
      permission   full|dict|none（full=ORG+PERM；dict=仅 PERM 且名字须 dict_ 前缀；
                   none=豁免（param_guard 回显集）且名字须 param_guard 前缀）
      order_by     排序列列表（可选）
    """
    validate_dataset_spec(spec, sem)
    table, ds_entry = datasource_table(spec["source"], sem)
    alias = spec.get("alias") or "t"
    cols = []
    numeric = set(spec.get("numeric_cols") or [])
    for f in spec["fields"]:
        if f in numeric:
            cols.append(f"{numeric_cast(f, sem, alias)} AS {f}")
        else:
            cols.append(f"{alias}.{f} AS {f}")
    where = [f"{' AND '.join(spec['filters'])}" if spec.get("filters") else None]
    if spec.get("period_param"):
        where.append(f"{alias}.period = {period_case(spec['period_param'], sem)}")
    perm = spec.get("permission") or "full"
    if perm in ("full", "dict"):
        where.append(_perm_for_table(spec, ds_entry, sem, alias))
    if perm == "full":
        where.append(org_filter(sem, alias))
    sql = (f"SELECT {'DISTINCT ' if spec.get('distinct') else ''}{', '.join(cols)}\n"
           f"FROM {table} {alias}\n"
           + "WHERE " + "\n  AND ".join(w for w in where if w))
    if spec.get("order_by"):
        ob = ", ".join(f"{alias}.{c}" for c in spec["order_by"])
        sql += f"\nORDER BY {ob}"
    return sql


# ---------------------------------------------------------------- 数据集 spec 校验
def validate_dataset_spec(spec, sem):
    """dataset/ chart 共用 spec 校验；违例抛 SkillError（坏 spec 拒绝出口）。"""
    if not isinstance(spec, dict):
        raise SkillError("spec 必须是 dict")
    name = spec.get("name")
    if not name or not _NAME_RE.fullmatch(name):
        raise SkillError(f"数据集名 [{name}] 非法（须字母开头，字母数字下划线）")
    perm = spec.get("permission") or "full"
    if perm not in ("full", "dict", "none"):
        raise SkillError(f"permission [{perm}] 非法（full|dict|none）")
    if perm == "dict" and not name.startswith("dict_"):
        raise SkillError(f"permission=dict 要求数据集名以 dict_ 前缀（G4 dict_ 豁免口径），得到 [{name}]")
    if perm == "none" and not name.startswith("param_guard"):
        raise SkillError(f"permission=none（G4 全豁免）要求数据集名以 param_guard 前缀，得到 [{name}]")
    if perm == "full" and (name.startswith("dict_") or name.startswith("param_guard")):
        raise SkillError(f"permission=full 的数据集不应占用豁免前缀 dict_/param_guard: [{name}]")
    fields = spec.get("fields")
    if not fields:
        raise SkillError("fields 必填非空")
    numeric = spec.get("numeric_cols") or []
    table, ds_entry = datasource_table(spec["source"], sem)   # source 必须可 grounding
    known = datasource_columns(ds_entry)
    if known is not None:
        bad = [c for c in list(fields) + list(numeric) if c not in known]
        if bad:
            raise SkillError(f"[{name}] 列不在 {table} 的 semantic columns 事实中: {bad}"
                             f"（可用: {sorted(known)}）")
    if perm == "full" and not numeric:
        raise SkillError(f"[{name}] 事实集(permission=full)必须 ≥1 个 numeric_cols"
                         f"（G3 numeric_cast 硬闸：varchar 数值须 NULLIF+显式转换）")
    unknown_num = [c for c in numeric if c not in fields]
    if unknown_num:
        raise SkillError(f"[{name}] numeric_cols {unknown_num} 未出现在 fields 中")
    pp = spec.get("period_param")
    if pp is not None and pp not in ("para_month", "para_month_bud"):
        raise SkillError(f"period_param 只允许 para_month|para_month_bud，得到 [{pp}]")
    std = set(sem["conventions"].get("standard_params") or [])
    glob = set(sem["conventions"].get("global_params") or [])
    unknown_p = [p for p in (spec.get("params") or []) if p not in std and p not in glob]
    if unknown_p:
        raise SkillError(f"[{name}] params 不在 semantic standard_params/global_params: {unknown_p}")
    for f in (spec.get("filters") or []):
        if ";" in f:
            raise SkillError(f"[{name}] filters 含分号（多语句禁入）: {f!r}")
        if "${{" in f:
            raise SkillError(f"[{name}] filters 含禁用残留 ${{{{: {f!r}}}")
    return True


_NAME_RE = __import__("re").compile(r"[A-Za-z][A-Za-z0-9_]*")


# ---------------------------------------------------------------- cpt 文档包装器
def declare_params_xml(names):
    return "".join(f'<Parameter><Attributes name="{p}"/><O><![CDATA[]]></O></Parameter>'
                   for p in names)


def connection_xml(sem):
    return ('<Attributes maxMemRowCount="-1"/>'
            '<Connection class="com.fr.data.impl.NameDatabaseConnection">'
            f'<DatabaseName><![CDATA[{connection_name(sem)}]]></DatabaseName></Connection>')


def tabledata_xml(name, sql, sem, params=()):
    """DBTableData 房式 XML（TableDataMap 成员）。params 为该数据集内局部声明。"""
    ps = "".join(f'<Parameter><Attributes name="{p}"/><O><![CDATA[]]></O></Parameter>'
                 for p in params)
    return (f'<TableData name="{name}" class="com.fr.data.impl.DBTableData">'
            f'<Parameters>{ps}</Parameters>{connection_xml(sem)}'
            f'<Query><![CDATA[{sql}]]></Query>'
            f'<PageQuery><![CDATA[]]></PageQuery></TableData>')


def workbook_cpt(report_name, cells_xml, tabledata_xml_, sem, param_names,
                 widgets_xml="", panel_bg=None, lock_js=None, style_list=""):
    """房式 WorkBook 骨架（与 dsl/compile.py 产物同构；panel 可选嵌入）。

    param_names: ReportParameterAttr ∪ ParameterUI 声明参数（G2 闭合依据）。
    widgets_xml/lock_js 同时给出才渲染 Listener（纯数据集页可不带面板交互）。
    """
    th = sem["theme"]
    bg = panel_bg if panel_bg is not None else th["panel_bg"]
    listener = ""
    if lock_js:
        listener = (f'<Listener event="afterinit" name="init1">\n'
                    f'<JavaScript class="com.fr.js.JavaScriptImpl">\n<Parameters/>\n<Content>\n'
                    f'<![CDATA[{lock_js}]]></Content>\n</JavaScript>\n</Listener>')
    params_xml = declare_params_xml(param_names)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<WorkBook xmlVersion="20211223" releaseVersion="10.0.0">
<ReportWebAttr><ServerPrinter/></ReportWebAttr>
<ReportFitAttr fitStateInPC="2" fitFont="false"/>
<Report class="com.fr.report.worksheet.WorkSheet" name="{report_name}">
<ReportPageAttr><HR/><FR/><HC/><FC/></ReportPageAttr>
<ColumnPrivilegeControl/><RowPrivilegeControl/>
<RowHeight defaultValue="{th["row_height"]["default"]}"><![CDATA[]]></RowHeight>
<ColumnWidth defaultValue="2743200"><![CDATA[]]></ColumnWidth>
<CellElementList>{cells_xml}</CellElementList>
<ReportAttrSet>
<ReportSettings headerHeight="0" footerHeight="0">
<PaperSetting><PaperSize width="42768000" height="60480000"/>
<Margin top="576000" left="0" bottom="0" right="0"/></PaperSetting>
<Background name="ColorBackground" color="-1"/></ReportSettings>
<Header reportPageType="0"><Background name="NullBackground"/><LeftList/><CenterList/><RightList/></Header>
<Footer reportPageType="0"><Background name="NullBackground"/><LeftList/><CenterList/><RightList/></Footer>
</ReportAttrSet>
<PrivilegeControl/>
</Report>
<TableDataMap>{tabledata_xml_}</TableDataMap>
<ReportParameterAttr><Attributes showWindow="true" delayPlaying="false" windowPosition="1" align="0" useParamsTemplate="true" currentIndex="0"/><PWTitle><![CDATA[参数]]></PWTitle>
{params_xml}
<ParameterUI class="com.fr.form.main.parameter.FormParameterUI">
<Parameters>{params_xml}</Parameters>
<Layout class="com.fr.form.ui.container.WParameterLayout">
<WidgetName name="para"/>
<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">
<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>
<PrivilegeControl/></WidgetAttr>
<Margin top="0" left="0" bottom="0" right="0"/>
<Background name="ColorBackground" color="{bg}"/>
<LCAttr vgap="0" hgap="0" compInterval="0"/>
{widgets_xml}
{listener}</Layout>
</ParameterUI>
</ReportParameterAttr>
<StyleList>{style_list}</StyleList>
<DesignerVersion DesignerVersion="KAA"/>
<PreviewType PreviewType="1"/>
</WorkBook>'''


# ---------------------------------------------------------------- guardrails 出入口
G5_ENV_RULES = {"connect_failed", "no_conn", "psycopg2_missing", "unresolved_param"}


def run_guardrails(doc, sem, do_smoke=False, param_values=None):
    """产物验收：G1-G4 硬闸 + G5 冒烟可选（环境类失败降级为警告，不阻塞静态产物）。
    返回 (blocking_errors, warn_list)。"""
    sql_list = guardrails.extract_sql_list(doc)
    conn = None
    if do_smoke:
        db = (sem.get("meta") or {}).get("db") or {}
        conn = {"host": db.get("host"), "port": db.get("port"), "dbname": db.get("dbname"),
                "user": db.get("user"), "password": db.get("password"), "connect_timeout": 15}
    gerrs = guardrails.check(doc, sem, sql_list, do_smoke=do_smoke,
                             conn=conn, param_values=param_values)
    blocking, warns = [], []
    for e in gerrs:
        if e.get("severity") == "info" or (e["gate"] == "G5" and e["rule"] in G5_ENV_RULES):
            warns.append(e)
        else:
            blocking.append(e)
    return blocking, warns


def now_stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
