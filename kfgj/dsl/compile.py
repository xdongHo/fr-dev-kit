# -*- coding: utf-8 -*-
"""compile.py — 示例项目 FS 报表 DSL 编译器（任务书 T2）

读 页面DSL(yaml) + semantic_layer.yaml(唯一事实源) → 按原型展开为完整 cpt。
写前五闸（SOP O1）：G0 clarification（NEEDS_CLARIFICATION 未消歧拒编译，2026-09-06 CAR-012）
→ schema grounding → ET.fromstring → guardrails G1-G4（--smoke 加 G5，
--ext 加 G6 扩展闸 R01-R15，默认不开）→ 全过才落盘。默认输出 dsl/build/，
绝不静默覆盖线上文件（--out 指向既有文件时自动备份）。

退出码: 0=成功落盘  1=编译失败（grounding/护栏/未实现原型）
        2=环境缺依赖（PyYAML）  3=NEEDS_CLARIFICATION 未消歧（G0 前置闸）

用法:
  python compile.py examples/panel_org_demo.yaml
      [--semantic semantic_layer.yaml] [--out <cpt>] [--smoke] [--ext]
      [--param K=V ...]     # --smoke 的参数替换值（缺省用冒烟基线参数集）
      [--pg-host H ...]     # G5 连接参数（缺省取 semantic.meta.db）

原型覆盖: account_drill(完整) / panel_org(完整，共享面板模块) / compare_main(T2-2b 2026-09-06：
主表 cpt 为模板基座的结构重生成——解析→facts/kind/未知偏差闸→DSL 选项变换→规范化重序列化)。

参照实现: _runs/tmp_gen_drill_v2.py（手写编译器原型，本文件的 SQL 片段/面板构件/
单元格生成均由其参数化而来，口径一律取 semantic_layer.yaml）。
"""
import argparse
import datetime
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guardrails  # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover
    print("COMPILE ERROR: 需要 PyYAML（pip install pyyaml）", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))

FRAGMENTS_NOTE = "由原型生成器参数化；口径以 semantic_layer.yaml 为准"


# ---------------------------------------------------------------- 装载与 grounding
def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f.read())


def ground_check(page, sem):
    """schema grounding：DSL 引用的 archetype/表/块必须存在于语义层。返回错误列表。"""
    errs = []
    arch = page.get("archetype")
    if arch not in (sem.get("archetypes") or {}):
        errs.append(f"archetype [{arch}] 不在 semantic_layer.archetypes: "
                    f"{sorted(sem.get('archetypes') or {})}")
    if arch in ("account_drill", "compare_main") and page.get("kind") not in ("actual", "budget"):
        errs.append(f"kind 必须为 actual|budget，得到: {page.get('kind')}")
    blocks = page.get("blocks") or []
    valid_blocks = {
        "panel_org": [[]],
        "account_drill": [["title", "single_row", "compose_region"]],
        "compare_main": [["subject_rows", "vs_columns"]],
    }.get(arch)
    if valid_blocks is None:
        errs.append(f"archetype [{arch}] 无展开器（compare_main 属 T2-2b，见 dsl/README.md）")
    elif arch == "account_drill":
        bad = [b for b in blocks if b not in valid_blocks[0]]
        if bad:
            errs.append(f"account_drill 非法 blocks: {bad}（合法: {valid_blocks[0]}）")
    for key in ("org_sum_actual", "org_sum_budget", "adj_actual_vt", "adj_budget_vt",
                "auth_base_info"):
        if key not in (sem.get("datasources") or {}):
            errs.append(f"语义层缺数据源事实: {key}（datasources 必须先行固化）")
    if arch == "account_drill" and not page.get("subject"):
        errs.append("account_drill 需要 subject: {p_code: from_url, p_name: from_url}")
    return errs


# ---------------------------------------------------------------- SQL 片段工厂（语义层驱动）
class Fragments:
    def __init__(self, sem, page):
        self.sem = sem
        self.page = page
        self.kind = page["kind"]
        org = sem["org"]
        conv = sem["conventions"]
        # 块标量模板末尾带 \n，内嵌 SQL 时必须 strip（否则归一化后残留空格差异）
        self.cond = org["cascade_cond_template"].strip()
        self.org_filter = org["entity_union_template"].replace("{cascade_cond}", self.cond).strip()
        self.perm_plain = org["perm_template"].strip()
        self.perm_exists_alias = org["perm_exists_alias_template"].strip()
        col = conv["column_criteria"]
        self.bud_period = "'12'" if self.kind == "actual" else self.mc("para_month_bud")
        self.cur_table = ("demo_dws.demo_rates_org_sum_budget"
                          if self.kind == "budget"
                          else "demo_ads.demo_rates_org_detail_actual_adj_vt")
        self.cur_scn = "upper('${para_scn_cur}')" if self.kind == "budget" else None

    def mc(self, param="para_month"):
        return self.sem["conventions"]["period_case_template"].replace("para_month", param).strip()

    def org_on(self, alias):
        return self.org_filter.replace("entity IN", alias + ".entity IN", 1)

    def perm_on(self, alias):
        return self.sem["org"]["perm_on_alias_template"].replace("{alias}", alias).strip()

    # ---- 标量取数片段（关联子查询: 外层别名 o；实测参照原型 leaf_sum/leaf_adj/comp_*）----
    def leaf_sum(self, table, scn_expr, yr, period):
        return (f"(SELECT round(sum(COALESCE(NULLIF(t.data,'')::numeric,0)),2) FROM {table} t "
                f"WHERE t.account = '${{p_code}}' AND t.view='YTD' AND t.value='CNY' "
                f"AND t.scenario = {scn_expr} AND t.year = {yr} AND t.period = {period} "
                f"AND {self.org_on('t')} AND {self.perm_on('t')})")

    def leaf_adj(self, period):
        return (f"(SELECT round(sum(CASE '${{para_adj}}' WHEN 'ADJ后' THEN t.ytd_post ELSE t.ytd_orig END),2) "
                f"FROM demo_ads.demo_rates_org_detail_actual_adj_vt t "
                f"WHERE t.account = '${{p_code}}' AND t.year_version = '${{para_year}}' AND t.period = {period} "
                f"AND {self.org_on('t')} AND {self.perm_on('t')})")

    def comp_total(self, table, scn_expr, yr, period, alias, values_sql):
        return (f"(SELECT round(sum(o.sgn * COALESCE(NULLIF({alias}.data,'')::numeric,0)),2) "
                f"FROM ({values_sql}) o JOIN {table} {alias} "
                f"ON {alias}.account = o.comp AND {alias}.view='YTD' AND {alias}.value='CNY' "
                f"AND {alias}.scenario = {scn_expr} AND {alias}.year = {yr} AND {alias}.period = {period} "
                f"WHERE o.expr = '${{p_code}}' AND {self.org_on(alias)} AND {self.perm_on(alias)})")

    def comp_adj_total(self, period, alias, values_sql):
        return (f"(SELECT round(sum(o.sgn * CASE '${{para_adj}}' WHEN 'ADJ后' THEN {alias}.ytd_post "
                f"ELSE {alias}.ytd_orig END),2) "
                f"FROM ({values_sql}) o JOIN demo_ads.demo_rates_org_detail_actual_adj_vt {alias} "
                f"ON {alias}.account = o.comp AND {alias}.year_version = '${{para_year}}' AND {alias}.period = {period} "
                f"WHERE o.expr = '${{p_code}}' AND {self.org_on(alias)} AND {self.perm_on(alias)})")

    def comp_row_sum(self, table, scn_expr, yr, period):
        return (f"(SELECT round(sum(COALESCE(NULLIF(t.data,'')::numeric,0)),2) FROM {table} t "
                f"WHERE t.account = o.comp AND t.view='YTD' AND t.value='CNY' "
                f"AND t.scenario = {scn_expr} AND t.year = {yr} AND t.period = {period} "
                f"AND {self.org_on('t')} AND {self.perm_on('t')})")

    def comp_row_adj(self, period):
        return (f"(SELECT round(sum(CASE '${{para_adj}}' WHEN 'ADJ后' THEN t.ytd_post ELSE t.ytd_orig END),2) "
                f"FROM demo_ads.demo_rates_org_detail_actual_adj_vt t "
                f"WHERE t.account = o.comp AND t.year_version = '${{para_year}}' AND t.period = {period} "
                f"AND {self.org_on('t')} AND {self.perm_on('t')})")

    # ---- kind 矩阵（对齐原型 if is_budget 分支）----
    def cols(self, values_sql):
        PM, PMB = self.mc("para_month"), self.mc("para_month_bud")
        SA, SB = "demo_dws.demo_rates_org_sum_actual", "demo_dws.demo_rates_org_sum_budget"
        PYR = "CAST(${para_year} - 1 AS text)"
        if self.kind == "budget":
            leaf_py = self.leaf_sum(SA, "upper('${para_scn_py}')", PYR, PM)
            leaf_bud = self.leaf_sum(SB, "upper('${para_scn_bud}')", "'${para_year}'", PMB)
            leaf_cur = self.leaf_sum(SB, "upper('${para_scn_cur}')", "'${para_year}'", PM)
            tot_py = self.comp_total(SA, "upper('${para_scn_py}')", PYR, PM, 'sa', values_sql)
            tot_bud = self.comp_total(SB, "upper('${para_scn_bud}')", "'${para_year}'", PMB, 'sb', values_sql)
            tot_cur = self.comp_total(SB, "upper('${para_scn_cur}')", "'${para_year}'", PM, 'sc', values_sql)
            row_py = self.comp_row_sum(SA, "upper('${para_scn_py}')", PYR, PM)
            row_bud = self.comp_row_sum(SB, "upper('${para_scn_bud}')", "'${para_year}'", PMB)
            row_cur = self.comp_row_sum(SB, "upper('${para_scn_cur}')", "'${para_year}'", PM)
        else:
            leaf_py = self.leaf_sum(SA, "upper('${para_scn_py}')", PYR, PM)
            leaf_bud = self.leaf_sum(SB, "upper('${para_scn_bud}')", "'${para_year}'", "'12'")
            leaf_cur = self.leaf_adj(PM)
            tot_py = self.comp_total(SA, "upper('${para_scn_py}')", PYR, PM, 'sa', values_sql)
            tot_bud = self.comp_total(SB, "upper('${para_scn_bud}')", "'${para_year}'", "'12'", 'sb', values_sql)
            tot_cur = self.comp_adj_total(PM, 't2', values_sql)
            row_py = self.comp_row_sum(SA, "upper('${para_scn_py}')", PYR, PM)
            row_bud = self.comp_row_sum(SB, "upper('${para_scn_bud}')", "'${para_year}'", "'12'")
            row_cur = self.comp_row_adj(PM)
        return leaf_py, leaf_bud, leaf_cur, tot_py, tot_bud, tot_cur, row_py, row_bud, row_cur


# ---------------------------------------------------------------- 科目源解析（原型 analyze_source/parse_expr）
def parse_expr(expr, code_set):
    comps, sign, depth, token = [], 1, [1], ''

    def flush(tok, s):
        tok = tok.strip()
        if tok and (re.fullmatch(r'\d{8}', tok) or tok.startswith('PLH') or tok in code_set):
            comps.append((tok, s))

    for ch in expr:
        if ch.isalnum() or ch == '_':
            token += ch
        else:
            flush(token, sign * depth[-1])
            token = ''
            if ch == '(':
                depth.append(depth[-1])
            elif ch == ')' and len(depth) > 1:
                depth.pop()
            elif ch == '-':
                sign = -sign
            elif ch == '+':
                sign = 1
    flush(token, sign * depth[-1])
    seen, out = set(), []
    for c, s in comps:
        if c not in seen:
            seen.add(c)
            out.append((c, s))
    return out


def subject_source_rows(page, sem):
    """从主表 cpt 提取 (行号, c4科目公式, 科目名) —— 对齐原型 analyze_source。"""
    src = (page.get("subject_source") or {}).get("cpt")
    if not src:
        raise SystemExit("COMPILE ERROR: account_drill 需要 subject_source.cpt（主表科目源）")
    path = src if os.path.isabs(src) or ":" in src else os.path.join(
        sem["meta"]["paths"]["reportlets_dir"], src)
    txt = open(path, encoding="utf-8").read()
    rows = {}
    for m in re.finditer(r'<C c="(\d+)" r="(\d+)"[^>]*>((?:(?!</C>).)*)</C>', txt, re.S):
        rows.setdefault(int(m.group(2)), {})[int(m.group(1))] = m.group(3)
    data_rows = []
    for r in sorted(rows):
        if r < 4:
            continue
        c4, c2 = rows[r].get(4, ''), rows[r].get(2, '')
        tx = re.search(r'<!\[CDATA\[([^\]]+)\]\]>', c4)
        if tx and tx.group(1).strip():
            tx2 = re.search(r'<!\[CDATA\[([^\]]+)\]\]>', c2)
            name = tx2.group(1).strip() if tx2 else tx.group(1).strip()
            data_rows.append((r, tx.group(1).strip(), name))
    return data_rows


# ---------------------------------------------------------------- 构件（原型 combo/label/单元格）
def xcombo(name, label_text, dict_name, x, decl=None, formula_value=None):
    dict_xml = ''
    if dict_name:
        deps = ''
        if decl:
            ds = ''.join(f'<Parameter name="{d}" CustomData="false"><O><![CDATA[]]></O></Parameter>'
                         for d in decl)
            deps = f'<Parameters>{ds}</Parameters>'
        dict_xml = ('<Dictionary class="com.fr.data.impl.TableDataDictionary">'
                    '<FormulaDictAttr ki="0" vi="1"/>'
                    '<TableDataDictAttr><TableData class="com.fr.data.impl.NameTableData">'
                    f'<Name><![CDATA[{dict_name}]]></Name>{deps}</TableData></TableDataDictAttr></Dictionary>')
    wv = ('<widgetValue>\n<O t="XMLable" class="com.fr.base.Formula">\n<Attributes>\n'
          f'<![CDATA[{formula_value}]]>\n</Attributes>\n</O>\n</widgetValue>') if formula_value else \
         '<widgetValue>\n<O>\n<![CDATA[]]></O>\n</widgetValue>'
    return (f'<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">'
            f'<InnerWidget class="com.fr.form.ui.ComboBox"><WidgetName name="{name}"/>'
            f'<LabelName name="{label_text}"/>'
            f'<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">'
            f'<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>'
            f'<PrivilegeControl/></WidgetAttr>'
            f'<allowBlank><![CDATA[true]]></allowBlank><DirectEdit><![CDATA[false]]></DirectEdit>'
            f'<CustomData><![CDATA[false]]></CustomData>{dict_xml}{wv}</InnerWidget>'
            f'<BoundsAttr x="{x}" y="12" width="100" height="26"/></Widget>')


def xlabel(name, text, x, w=45):
    return (f'<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">'
            f'<InnerWidget class="com.fr.form.ui.Label"><WidgetName name="{name}"/>'
            f'<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">'
            f'<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>'
            f'<PrivilegeControl/></WidgetAttr>'
            f'<widgetValue><O><![CDATA[{text}]]></O></widgetValue>'
            f'<LabelAttr verticalcenter="true" textalign="0" autoline="true"/>'
            f'<FRFont name="微软雅黑" style="1" size="80" foreground="-13421773"/>'
            f'<border style="0" color="-723724"/></InnerWidget>'
            f'<BoundsAttr x="{x}" y="12" width="{w}" height="26"/></Widget>')


def build_panel_widgets(sem):
    """组织面板（原型 panel_org）。控件名一律 para_*（修复原型 legal/bu 短名缺陷）。"""
    deps = sem["org"]["dict_dependencies"]
    entity_formula = sem["conventions"]["entity_formula"]
    items = [
        ('para_legal', '法人：', 'dict_legal', deps.get('dict_legal') or []),
        ('para_bu', 'BU：', 'dict_bu', deps.get('dict_bu') or []),
        ('para_region', '区域：', 'dict_region', deps.get('dict_region') or []),
        ('para_plant', '工厂：', 'dict_plant', deps.get('dict_plant') or []),
        ('para_entity', 'Entity：', None, None, entity_formula),
    ]
    widgets, x = [], 8
    for it in items:
        pname, ptext, dname, decl = it[0], it[1], it[2], it[3]
        fv = it[4] if len(it) > 4 else None
        widgets.append(xlabel(f'lb_{pname[5:]}' if pname.startswith('para_') else f'lb_{pname}', ptext, x))
        widgets.append(xcombo(pname, ptext, dname, x + 51, decl, fv))
        x += 165
    return '\n'.join(widgets)


def style_block(st, border):
    fg = f' foreground="{st["fg"]}"' if st.get("fg") else ''
    return ('<Style imageLayout="1"><Format class="com.fr.base.TextFormat"/>'
            f'<FRFont name="{st.get("font", "微软雅黑")}" style="1" size="{st["size"]}"{fg}/>'
            f'<Background name="ColorBackground" color="{st["bg"]}"/>'
            f'<Border><Top style="1" color="{border}"/><Bottom style="1" color="{border}"/>'
            f'<Left style="1" color="{border}"/><Right style="1" color="{border}"/></Border></Style>')


def build_styles(sem):
    th = sem["theme"]
    order = ["title", "header", "data", "total", "component"]
    return ''.join(style_block(th["styles"][k], th["border"]) for k in order)


def dscolumn(ds, col):
    return (f'<O t="DSColumn"><Attributes dsName="{ds}" columnName="{col}"/>'
            '<Complex/><RG class="com.fr.report.cell.cellattr.core.group.SummaryGrouper">'
            '<FN><![CDATA[com.fr.data.util.function.SumFunction]]></FN></RG>'
            '<Parameters/></O>')


def formula_cell(c, r, s, expr):
    return (f'<C c="{c}" r="{r}" s="{s}"><O t="XMLable" class="com.fr.base.Formula">'
            f'<Attributes><![CDATA[{expr}]]></Attributes></O><PrivilegeControl/><Expand/></C>')


def text_cell(c, r, s, text):
    return f'<C c="{c}" r="{r}" s="{s}"><O><![CDATA[{text}]]></O><PrivilegeControl/><Expand/></C>'


# ---------------------------------------------------------------- account_drill 展开
def build_account_drill(page, sem):
    frag = Fragments(sem, page)
    conn = ('<Attributes maxMemRowCount="-1"/>'
            '<Connection class="com.fr.data.impl.NameDatabaseConnection">'
            '<DatabaseName><![CDATA[demo_connection]]></DatabaseName></Connection>')
    rows = subject_source_rows(page, sem)
    code_set = set(c for _, c, _ in rows)
    values_rows = []
    for _, expr, _ in rows:
        for comp, sign in parse_expr(expr, code_set):
            if comp != expr:
                values_rows.append((expr, comp, sign))

    def q(s):
        return s.replace("'", "''")

    if values_rows:
        values_sql = ' UNION ALL '.join(
            f"SELECT '{q(expr)}' AS expr, '{q(c)}' AS comp, {s} AS sgn"
            for expr, c, s in values_rows)
    else:  # 空构成兜底：保持 G3 values_union 幅面（UNION ALL 两段同空集）
        values_sql = ("SELECT '' AS expr, '' AS comp, 0 AS sgn WHERE 1=0 "
                      "UNION ALL SELECT '', '', 0 WHERE 1=0")

    leaf_py, leaf_bud, leaf_cur, tot_py, tot_bud, tot_cur, row_py, row_bud, row_cur = \
        frag.cols(values_sql)

    ds_account_sql = (f"SELECT '${{p_code}}' AS acc,\n"
                      f"COALESCE({leaf_py}, {tot_py}, 0) AS py,\n"
                      f"COALESCE({leaf_bud}, {tot_bud}, 0) AS bud,\n"
                      f"COALESCE({leaf_cur}, {tot_cur}, 0) AS cur")
    compose_sql = (f"SELECT o.comp, o.sgn,\n"
                   f"COALESCE(({row_py}), 0) AS py,\n"
                   f"COALESCE(({row_bud}), 0) AS bud,\n"
                   f"COALESCE(({row_cur}), 0) AS cur\n"
                   f"FROM ({values_sql}) o\n"
                   f"WHERE o.expr = '${{p_code}}'\n"
                   f"ORDER BY o.sgn DESC, o.comp")

    def dict_block(name, sql, decl):
        ps = ''.join(f'<Parameter><Attributes name="{d}"/><O><![CDATA[]]></O></Parameter>'
                     for d in decl)
        return (f'<TableData name="{name}" class="com.fr.data.impl.DBTableData">'
                f'<Parameters>{ps}</Parameters>{conn}'
                f'<Query><![CDATA[{sql}]]></Query><PageQuery><![CDATA[]]></PageQuery></TableData>')

    PERM_ALIAS = sem["org"]["perm_exists_alias_template"].replace("{alias}", "f").strip()
    dicts = (
        dict_block('dict_legal',
                   "SELECT DISTINCT legal_code AS v, legal_code AS t FROM demo_ads.fin_demo_auth_base_info f "
                   "WHERE legal_code IS NOT NULL AND legal_code <> '' AND " + PERM_ALIAS + " ORDER BY 1", [])
        + dict_block('dict_bu',
                     "SELECT DISTINCT bu AS v, bu AS t FROM demo_ads.fin_demo_auth_base_info f "
                     "WHERE bu IS NOT NULL AND bu <> '' AND ('${para_legal}'='' OR f.legal_code='${para_legal}') AND "
                     + PERM_ALIAS + " ORDER BY 1", ['para_legal'])
        + dict_block('dict_region',
                     "SELECT DISTINCT region AS v, region AS t FROM demo_ads.fin_demo_auth_base_info f "
                     "WHERE region IS NOT NULL AND region <> '' AND ('${para_bu}'='' OR f.bu='${para_bu}') AND "
                     + PERM_ALIAS + " ORDER BY 1", ['para_legal', 'para_bu'])
        + dict_block('dict_plant',
                     "SELECT DISTINCT plant_code AS v, plant_code AS t FROM demo_ads.fin_demo_auth_base_info f "
                     "WHERE plant_code IS NOT NULL AND plant_code <> '' AND "
                     "(('${para_legal}'<>'' AND f.legal_code='${para_legal}') OR "
                     "('${para_bu}'<>'' AND f.bu='${para_bu}' AND ('${para_region}'='' OR f.region='${para_region}'))) AND "
                     + PERM_ALIAS + " ORDER BY 1", ['para_legal', 'para_bu', 'para_region'])
    )

    param_names = sem["conventions"]["standard_params"]
    params_xml = ''.join(f'<Parameter><Attributes name="{p}"/><O><![CDATA[]]></O></Parameter>'
                         for p in param_names)
    param_guard_sql = ("SELECT ${p_code} AS code, ${para_legal} AS gl, ${para_bu} AS bu, "
                       "${para_region} AS rg, ${para_plant} AS pl, ${para_entity} AS en, "
                       "${para_year} AS y, ${para_month} AS m, ${para_scn_py} AS sp, "
                       "${para_scn_bud} AS sb, ${para_scn_cur} AS sc, ${para_curr} AS c, ${para_unit} AS u")
    param_guard = (f'<TableData name="param_guard" class="com.fr.data.impl.DBTableData">'
                   f'<Parameters>{params_xml}</Parameters>{conn}'
                   f'<Query><![CDATA[{param_guard_sql}]]></Query>'
                   f'<PageQuery><![CDATA[]]></PageQuery></TableData>')
    ds_account = (f'<TableData name="ds_account" class="com.fr.data.impl.DBTableData">'
                  f'<Parameters/>{conn}'
                  f'<Query><![CDATA[{ds_account_sql}]]></Query>'
                  f'<PageQuery><![CDATA[]]></PageQuery></TableData>')
    ds_compose = (f'<TableData name="ds_compose" class="com.fr.data.impl.DBTableData">'
                  f'<Parameters/>{conn}'
                  f'<Query><![CDATA[{compose_sql}]]></Query>'
                  f'<PageQuery><![CDATA[]]></PageQuery></TableData>')

    # ---- 单元格（r→s 映射按交付 cpt 实测：r0→s0 r2→s1 r3→s2 r5→s1 r6→s1 r7→s4 r8→s3）----
    cells = [formula_cell(0, 0, 0, '=CONCATENATE("科目下钻：", $p_name)')]
    for i, h in enumerate(['科目', '上年 YTD', '预算 YTD', '当年 YTD', 'VS LY 差额', 'VS PPL 差额']):
        cells.append(text_cell(i, 2, 1, h))
    cells.append(f'<C c="0" r="3" s="2">{dscolumn("ds_account", "acc")}<PrivilegeControl/><Expand/></C>')
    for ci, col in [(1, 'py'), (2, 'bud'), (3, 'cur')]:
        cells.append(f'<C c="{ci}" r="3" s="2">{dscolumn("ds_account", col)}<PrivilegeControl/><Expand/></C>')
    cells.append(formula_cell(4, 3, 2, '=D4 - B4'))
    cells.append(formula_cell(5, 3, 2, '=D4 - C4'))
    cells.append(text_cell(0, 5, 1, '公式科目构成(小计)'))
    for i, h in enumerate(['组件科目', '符号', '上年小计', '预算小计', '当年小计']):
        cells.append(text_cell(i, 6, 1, h))
    for ci, col in [(0, 'comp'), (1, 'sgn'), (2, 'py'), (3, 'bud'), (4, 'cur')]:
        cells.append(f'<C c="{ci}" r="7" s="4">{dscolumn("ds_compose", col)}<PrivilegeControl/><Expand/></C>')
    cells.append(text_cell(0, 8, 3, '构成合计'))
    for ci, colL in [(2, 'C'), (3, 'D'), (4, 'E')]:
        cells.append(formula_cell(ci, 8, 3, f'=SUM({colL}7)'))

    th = sem["theme"]
    widgets_xml = build_panel_widgets(sem)
    lock_js = sem["conventions"]["lock_js_template"].rstrip('\n')
    doc = f'''<?xml version="1.0" encoding="UTF-8"?>
<WorkBook xmlVersion="20211223" releaseVersion="10.0.0">
<ReportWebAttr><ServerPrinter/></ReportWebAttr>
<ReportFitAttr fitStateInPC="2" fitFont="false"/>
<Report class="com.fr.report.worksheet.WorkSheet" name="{page["page"]}">
<ReportPageAttr><HR/><FR/><HC/><FC/></ReportPageAttr>
<ColumnPrivilegeControl/><RowPrivilegeControl/>
<RowHeight defaultValue="{th["row_height"]["default"]}"><![CDATA[{th["row_height_list"]}]]></RowHeight>
<ColumnWidth defaultValue="2743200"><![CDATA[{th["column_width_list"]}]]></ColumnWidth>
<CellElementList>{''.join(cells)}</CellElementList>
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
<TableDataMap>{ds_account}{ds_compose}{dicts}{param_guard}</TableDataMap>
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
<Background name="ColorBackground" color="{th["panel_bg"]}"/>
<LCAttr vgap="0" hgap="0" compInterval="0"/>
{widgets_xml}
<Listener event="afterinit" name="init1">
<JavaScript class="com.fr.js.JavaScriptImpl">
<Parameters/>
<Content>
<![CDATA[{lock_js}]]></Content>
</JavaScript>
</Listener>
</Layout>
</ParameterUI>
</ReportParameterAttr>
<StyleList>{build_styles(sem)}</StyleList>
<DesignerVersion DesignerVersion="KAA"/>
<PreviewType PreviewType="1"/>
</WorkBook>'''
    return doc


# ---------------------------------------------------------------- panel_org 展开（纯面板页）
def build_panel_org(page, sem):
    """独立组织面板页：面板 + 一格说明文字（面板模块与 account_drill 共用）。"""
    th = sem["theme"]
    widgets_xml = build_panel_widgets(sem)
    lock_js = sem["conventions"]["lock_js_template"].rstrip('\n')
    param_names = sem["conventions"]["standard_params"]
    params_xml = ''.join(f'<Parameter><Attributes name="{p}"/><O><![CDATA[]]></O></Parameter>'
                         for p in param_names)
    note = text_cell(0, 0, 0, page.get("note", "组织面板页（panel_org 原型）"))
    doc = f'''<?xml version="1.0" encoding="UTF-8"?>
<WorkBook xmlVersion="20211223" releaseVersion="10.0.0">
<ReportWebAttr><ServerPrinter/></ReportWebAttr>
<ReportFitAttr fitStateInPC="2" fitFont="false"/>
<Report class="com.fr.report.worksheet.WorkSheet" name="{page["page"]}">
<ReportPageAttr><HR/><FR/><HC/><FC/></ReportPageAttr>
<ColumnPrivilegeControl/><RowPrivilegeControl/>
<RowHeight defaultValue="{th["row_height"]["default"]}"><![CDATA[]]></RowHeight>
<ColumnWidth defaultValue="2743200"><![CDATA[]]></ColumnWidth>
<CellElementList>{note}</CellElementList>
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
<TableDataMap></TableDataMap>
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
<Background name="ColorBackground" color="{th["panel_bg"]}"/>
<LCAttr vgap="0" hgap="0" compInterval="0"/>
{widgets_xml}
<Listener event="afterinit" name="init1">
<JavaScript class="com.fr.js.JavaScriptImpl">
<Parameters/>
<Content>
<![CDATA[{lock_js}]]></Content>
</JavaScript>
</Listener>
</Layout>
</ParameterUI>
</ReportParameterAttr>
<StyleList></StyleList>
<DesignerVersion DesignerVersion="KAA"/>
<PreviewType PreviewType="1"/>
</WorkBook>'''
    return doc


# ---------------------------------------------------------------- compare_main 展开（T2-2b）
# 架构（对齐语义层 archetypes.compare_main.generator 指针「analyze_source() + 主表 cpt 自身」）：
#   页面 DSL + 语义层 → 以线上主表 cpt 为模板基座（subject_source.cpt 自指），经
#   解析(元素级拆解) → 结构模型 → facts 闸/kind 闸/未知偏差 fail-closed 闸 →
#   DSL 选项变换（comments/before_cr 可裁剪） → 规范化重序列化 落盘。
# SQL/单元格载荷源自模板基座（口径事实已由语义层登记），护栏与对拍负责闭合验证。
_TAG_RE = re.compile(r'</?([A-Za-z_][\w.\-]*)')


def _split_elements(s):
    """把连续同级 XML 元素串拆成 [(tag, 原文)]；CDATA 感知（SQL/公式内 '</X>' 不误切）。"""
    parts, i, n = [], 0, len(s)
    while i < n:
        if s[i].isspace():
            i += 1
            continue
        if s[i] != '<':
            raise ValueError(f"compare_main 模板解析：非元素内容 @{i}: {s[i:i+40]!r}")
        if s.startswith('<!--', i):
            i = s.find('-->', i) + 3
            continue
        j = s.index('>', i)
        tag = _TAG_RE.match(s[i:j + 1]).group(1)
        if s[j - 1] == '/':
            parts.append((tag, s[i:j + 1]))
            i = j + 1
            continue
        depth, k, end = 1, j + 1, None
        while depth:
            a = s.find('<', k)
            if a < 0:
                raise ValueError(f"compare_main 模板解析：{tag} 未闭合")
            if s.startswith('<![CDATA[', a):
                k = s.index(']]>', a) + 3
                continue
            b = s.index('>', a)
            t = _TAG_RE.match(s[a:b + 1]).group(1)
            if s[b - 1] == '/':
                pass
            elif s.startswith('</', a):
                depth -= 1
                if depth == 0:
                    end = b + 1
            else:
                depth += 1
            k = b + 1
        parts.append((tag, s[i:end]))
        i = end
    return parts


def _compact(xml):
    """规范化重序列化：元素间空白折叠（含紧邻 CDATA 的边界）、CDATA 内部原样保留。
    哨兵法：段两侧补 '>'/'<' 使 "> ⏎ <![CDATA[" 跨段边界也被折叠——线上 _bdec/_ext 等
    机插数据集 Query 带换行，会使 extract_sql_list 的 CDATA 优先分支失配（提取进 CDATA 标记）。"""
    out, i = [], 0
    while True:
        c = xml.find('<![CDATA[', i)
        seg = xml[i:] if c < 0 else xml[i:c]
        out.append(re.sub(r'>\s+<', '><', '>' + seg.strip() + '<')[1:-1])
        if c < 0:
            break
        e = xml.index(']]>', c)
        out.append(xml[c:e + 3])
        i = e + 3
    return ''.join(out).strip()


def _subject_cpt_path(page, sem):
    src = (page.get("subject_source") or {}).get("cpt")
    if not src:
        raise SystemExit("COMPILE FAIL: compare_main 需要 subject_source.cpt（主表模板基座）")
    return src if os.path.isabs(src) or ":" in src else os.path.join(
        sem["meta"]["paths"]["reportlets_dir"], src)


def build_compare_main(page, sem):
    ref_path = _subject_cpt_path(page, sem)
    ref = open(ref_path, encoding="utf-8").read()
    kind = page["kind"]
    opts = page.get("options") or {}

    # ---- 闸 0：未知偏差 fail-closed —— 用登记豁免后的护栏跑模板基座，仍有错=登记不全，拒编译
    ref_sql = guardrails.extract_sql_list(ref)
    unregistered = [e for e in guardrails.check(ref, sem, ref_sql)
                    if e.get("severity", "error") == "error"]
    if unregistered:
        print(f"COMPILE FAIL — 模板基座存在未登记偏差 {len(unregistered)} 处"
              f"（known_deviations 豁免后仍 FAIL；照实复现原则下拒编译，请先补登记）：")
        for e in unregistered[:20]:
            print(f'  - [{e["gate"]}] {e["rule"]}: {e["message"][:120]}')
        raise SystemExit(1)

    # ---- 解析：顶层 → Report 子块 → CellElementList 逐格
    decl = ref[:ref.find('<WorkBook')]
    wb_open = ref[ref.find('<WorkBook'):ref.index('>', ref.find('<WorkBook')) + 1]
    body = ref[len(decl) + len(wb_open):ref.rindex('</WorkBook>')]
    top = _split_elements(body)
    tops = {}
    for tag, part in top:
        tops.setdefault(tag, []).append(part)
    report = tops['Report'][0]
    rep_open = report[:report.index('>') + 1]
    rep_body = report[len(rep_open):report.rindex('</Report>')]
    rep_children = _split_elements(rep_body)
    cel = next(p for t, p in rep_children if t == 'CellElementList')
    cells = _split_elements(cel[cel.index('>') + 1:cel.rindex('</CellElementList>')])

    # ---- 闸 1：语义层 facts 核对（结构漂移即拒编译；口径以线上现件为准、登记随 snapshot_at）
    cm = (sem.get("archetypes") or {}).get("compare_main") or {}
    counts = ((cm.get("facts") or {}).get("counts") or {}).get(kind) or {}
    links = {}
    for _, cell in cells:
        for ln in re.findall(r'<NameJavaScript name="([^"]+)"', cell):
            links[ln] = links.get(ln, 0) + 1
    data_rows = sorted({int(m.group(1)) for _, cell in cells
                        for m in [re.match(r'<C c="\d+" r="(\d+)"', cell)] if m and int(m.group(1)) >= 4})
    problems = []
    if counts:
        if len(ref_sql) != counts.get("datasets", len(ref_sql)):
            problems.append(f"数据集数 {len(ref_sql)} != facts {counts['datasets']}")
        if len(cells) != counts.get("cells", len(cells)):
            problems.append(f"单元格数 {len(cells)} != facts {counts['cells']}")
        if len(data_rows) != counts.get("data_rows", len(data_rows)):
            problems.append(f"数据行数 {len(data_rows)} != facts {counts['data_rows']}")
        for key, lname in (("links_comments", "填写Comments"), ("links_drill", "科目下钻"),
                           ("links_adj", "调整ADJ")):
            if links.get(lname, 0) != counts.get(key, links.get(lname, 0)):
                problems.append(f"超链[{lname}] {links.get(lname, 0)} != facts {counts[key]}")
    rh = re.search(r'<RowHeight defaultValue="(\d+)">\s*<!\[CDATA\[([\d,]+)', ref, re.S)
    if not rh or rh.group(1) != "723900" or not rh.group(2).startswith("1440000,1440000,1440000,1440000"):
        problems.append("行高族漂移（期望 defaultValue=723900 且 r0~r3=1440000）")
    drill_target = (f"/示例报表工程/明细报表/示例实际表-科目下钻.cpt" if kind == "actual"
                    else f"/示例报表工程/明细报表/示例预算表-科目下钻.cpt")
    if drill_target not in ref:
        problems.append(f"科目下钻超链目标缺失: {drill_target}")
    if kind == "actual":
        if "demo_rates_org_detail_actual_adj_vt" not in ref:
            problems.append("actual 页 ds_fs 应走 ADJ 视图（demo_rates_org_detail_actual_adj_vt）")
        if not any(n == "ds_cr_lta" for n, _ in ref_sql):
            problems.append("actual 页应含 ds_cr_ 基础名族")
    else:
        if not any(n == "ds_cr_lta_bud" for n, _ in ref_sql) or not any(n == "ds_cr_lta_fy" for n, _ in ref_sql):
            problems.append("budget 页应含 ds_cr_*_bud/_fy 变体族")
        if "调整ADJ" in links:
            problems.append("budget 页不应有 调整ADJ 超链族")
    if problems:
        print("COMPILE FAIL — 模板基座与语义层 facts 冲突（以线上现件为准请修 facts 并附 snapshot_at）：")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)

    # ---- 变换 1：DSL 选项裁剪（对拍用默认=线上现状，不触发）
    drop_ds, drop_cell = set(), []
    if opts.get("comments") is False:
        drop_ds.add("ds_comments")
    if opts.get("before_cr") is False:
        drop_ds.update(n for n, _ in ref_sql if n.startswith("ds_cr_"))
    if drop_ds:
        drop_cell = [c for _, c in cells if any(f'dsName="{n}"' in c for n in drop_ds)]
        cells = [(t, c) for t, c in cells if c not in drop_cell]
        print(f"  compare_main 选项裁剪: datasets={sorted(drop_ds)} cells=-{len(drop_cell)}")

    # ---- 变换 2：页面名（Report name ← DSL page）
    rep_open = re.sub(r'name="[^"]*"', 'name="' + page["page"].replace('"', '&quot;') + '"',
                      rep_open, count=1)

    # ---- 重序列化（规范化：元素间空白折叠；CDATA 原样）
    out_cells = '\n'.join(_compact(c) for _, c in cells)
    new_cel = '<CellElementList>' + out_cells + '</CellElementList>'
    new_rep_children = '\n'.join(new_cel if t == 'CellElementList' else _compact(p)
                                 for t, p in rep_children)
    new_report = rep_open + '\n' + new_rep_children + '\n</Report>'
    new_top = []
    for tag, part in top:
        if tag == 'Report':
            new_top.append(new_report)
        elif tag == 'TableDataMap':
            tds = _split_elements(part[part.index('>') + 1:part.rindex('</TableDataMap>')])
            kept = []
            for t, p in tds:
                m = re.search(r'<TableData\b[^>]*?name="([^"]+)"', p)
                if m and m.group(1) in drop_ds:
                    continue
                kept.append((t, p))
            new_top.append('<TableDataMap>' + '\n'.join(_compact(p) for _, p in kept)
                           + '</TableDataMap>')
        else:
            new_top.append(_compact(part))
    return decl + wb_open + '\n' + '\n'.join(new_top) + '\n</WorkBook>\n'


# ---------------------------------------------------------------- 主流程
SMOKE_DEFAULTS = {
    'para_year': '2026', 'para_month': 'Sep', 'para_adj': 'ADJ后',
    'para_legal': '', 'para_bu': '', 'para_region': '', 'para_plant': '',
    'para_scn_py': 'Actual', 'para_scn_bud': 'PPL_R2', 'para_scn_cur': 'PPL_R2',
    'p_code': 'PLH01', 'p_name': 'PLH01 营业收入', 'fine_username': 'frdev1',
    'para_curr': 'CNY Total', 'para_unit': '1000', 'para_month_bud': 'Dec',
    'para_entity': '', 'para_ext1': '', 'para_ext2': '', 'para_ext3': '',
    'para_ext4': '', 'para_ext5': '',
    'para_level': '', 'para_lpvc': '',   # compare_main 主表面板参数（T2-2b）
}
G5_ENV_RULES = {"connect_failed", "no_conn", "psycopg2_missing", "unresolved_param"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="示例项目 FS 报表 DSL 编译器")
    ap.add_argument("page", help="页面 DSL yaml 路径")
    ap.add_argument("--semantic", default=os.path.join(HERE, "semantic_layer.yaml"))
    ap.add_argument("--out", default=None, help="输出 cpt（缺省 dsl/build/<output>）")
    ap.add_argument("--smoke", action="store_true", help="落盘前执行 G5 库上冒烟")
    ap.add_argument("--ext", action="store_true",
                    help="落盘前追加 G6 扩展闸（guardrails R01-R15，默认不开）")
    ap.add_argument("--param", action="append", default=[], metavar="K=V")
    args = ap.parse_args(argv)

    page = load_yaml(args.page)
    sem = load_yaml(args.semantic)

    # ---- G0 前置闸：NEEDS_CLARIFICATION 未消歧→拒绝产出（T11 spec-kit：clarify 未过不能 plan）----
    clar = guardrails.check_clarifications(page, sem)
    if clar:
        print(f"COMPILE BLOCKED — NEEDS_CLARIFICATION 未消歧 {len(clar)} 处，澄清问题清单:")
        for e in clar:
            print(f'  - [{e["detail"]["path"]}] {e["detail"]["question"]}')
        print("COMPILE FAIL — 产物未落盘（退出码 3=存在待澄清歧义；消歧后删除标记重编译）")
        return 3

    errs = ground_check(page, sem)
    if errs:
        print("COMPILE FAIL — schema grounding:")
        for e in errs:
            print("  -", e)
        return 1

    arch = page["archetype"]
    if arch == "account_drill":
        doc = build_account_drill(page, sem)
    elif arch == "panel_org":
        doc = build_panel_org(page, sem)
    elif arch == "compare_main":
        doc = build_compare_main(page, sem)
    else:
        print(f"COMPILE FAIL: archetype [{arch}] 展开器未实现")
        return 1

    # 写前闸：G1-G4 硬闸；G5 仅 --smoke，环境类失败降级为警告（网络不通不阻塞静态产物）
    sql_list = guardrails.extract_sql_list(doc)
    param_values = dict(SMOKE_DEFAULTS)
    for kv in args.param:
        k, _, v = kv.partition("=")
        param_values[k.strip()] = v
    db = (sem.get("meta") or {}).get("db") or {}
    conn = {"host": db.get("host"), "port": db.get("port"), "dbname": db.get("dbname"),
            "user": db.get("user"), "password": db.get("password"), "connect_timeout": 15}
    gerrs = guardrails.check(doc, sem, sql_list, do_smoke=args.smoke,
                             conn=conn if args.smoke else None, param_values=param_values,
                             enable_ext=args.ext)
    blocking, warns = [], []
    for e in gerrs:
        if e.get("severity") == "info":
            warns.append(e)
        elif e["gate"] == "G5" and e["rule"] in G5_ENV_RULES:
            warns.append(e)
        else:
            blocking.append(e)
    for e in blocking:
        print(f'GUARDRAIL BLOCK [{e["gate"]}] {e["rule"]}: {e["message"]}')
    if blocking:
        print("COMPILE FAIL — 产物未落盘（O1 写前闸）")
        return 1

    out = args.out or os.path.join(HERE, "build", page.get("output") or (page["page"] + ".cpt"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        bak = out + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.replace(out, bak)
        print(f"BACKUP: {out} -> {bak}")
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    ET.parse(out)  # 落盘兜底
    print(f"COMPILED: {out}")
    print(f"  archetype={arch} kind={page.get('kind')} datasets={len(sql_list)} "
          f"values_rows={len(re.findall(r'AS sgn', doc))}")
    for e in warns:
        print(f'  WARN [{e["gate"]}] {e["rule"]}: {e["message"][:120]}')
    print("NEXT: python kfgj/fzpy/fr_check.py \"{}\"  # 退出码 1 且仅三族误报 = 基线内".format(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
