# -*- coding: utf-8 -*-
"""panel_skill.py — 标准参数面板生成器（控件清单 spec → 参数面板 XML / 整页 cpt）。

R39 标准组件技能库 ②。全部口径取自 semantic_layer.yaml:
  - para_* 命名铁律（conventions.control_param_rule；G2(c) widget_param_mismatch 是真阳性闸）
  - lb_* 标签命名（compile.py panel_org 同构）
  - 栅格 x 坐标 165px 步进（conventions.archetypes.panel_widgets.layout:
    label(45px)+combo(100px) 一组，组间距 165px，y=12 h=26）
  - entity 只读公式（conventions.entity_formula）
  - lock_js（conventions.lock_js_template，__w 修 context 版）

控件类映射证据: _runs/night/20260904/L2/widget_facts.md（171 类探针，xtype↔class↔XML 全链路断言）
+ dsl/compile.py xcombo/xlabel（设计器实测构件）。
label/combo 为全证据级（compile.py 线上同构）；其余类型按 L2 roundtrip 事实以同构 BoundsWidget
骨架生成（证据级见 README 分级表）。
"""
import datetime
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

from _common import (SkillError, load_semantic, now_stamp, run_guardrails,
                     tabledata_xml, workbook_cpt)

# xtype → 控件类（L2 widget_facts.md 速查表，xml_assert=full 子集）
WIDGET_CLASSES = {
    "label":         "com.fr.form.ui.Label",
    "combo":         "com.fr.form.ui.ComboBox",
    "combocheckbox": "com.fr.form.ui.ComboCheckBox",
    "date":          "com.fr.form.ui.DateEditor",
    "number":        "com.fr.form.ui.NumberEditor",
    "text":          "com.fr.form.ui.TextEditor",
}
FULL_EVIDENCE = {"label", "combo"}      # compile.py 线上同构级
CONTROLS = set(WIDGET_CLASSES) - {"label"}

PARA_RE = re.compile(r"para_[a-z0-9_]+")
LB_RE = re.compile(r"lb_[a-z0-9_]+")


# ---------------------------------------------------------------- 校验
def validate_spec(spec, sem):
    if not isinstance(spec, dict) or not spec.get("widgets"):
        raise SkillError("panel spec 需要 widgets 非空列表")
    names = []
    for w in spec["widgets"]:
        wtype = w.get("type")
        if wtype not in WIDGET_CLASSES:
            raise SkillError(f"控件类型 [{wtype}] 不在支持清单: {sorted(WIDGET_CLASSES)}")
        name = w.get("name")
        if not name:
            raise SkillError("控件缺 name")
        if name in names:
            raise SkillError(f"控件名重复: [{name}]")
        names.append(name)
        if wtype == "label":
            if not LB_RE.fullmatch(name):
                raise SkillError(f"标签名 [{name}] 须以 lb_ 前缀（面板标签命名约定）")
        else:
            if not PARA_RE.fullmatch(name):
                raise SkillError(f"控件名 [{name}] 违反 para_* 命名铁律"
                                 f"（conventions.control_param_rule：控件名必须等于模板参数名，"
                                 f"否则值不绑定；下钻页 v2 违例已酿成锁定失效事故）")
            std = set(sem["conventions"].get("standard_params") or [])
            if name not in std:
                raise SkillError(f"控件参数 [{name}] 不在 semantic standard_params 清单: {sorted(std)}")
            if w.get("dict") and not str(w["dict"]).startswith("dict_"):
                raise SkillError(f"字典名 [{w.get('dict')}] 须 dict_ 前缀（G4 dict_ 豁免口径）")
            if w.get("readonly_formula") and wtype != "combo":
                raise SkillError(f"readonly_formula 仅支持 combo（entity 只读公式场景），得到 [{wtype}]")
        if w.get("dict_deps"):
            controls = {x["name"] for x in spec["widgets"] if x.get("type") != "label"}
            bad = [d for d in w["dict_deps"] if d not in controls]
            if bad:
                raise SkillError(f"dict_deps 引用了面板不存在的控件: {bad}")
    return True


# ---------------------------------------------------------------- 构件（compile.py 同构）
def _widget_attr():
    return ('<WidgetAttr aspectRatioLocked="false" aspectRatioBackup="-1.0" description="">'
            '<MobileBookMark useBookMark="false" bookMarkName="" frozen="false" index="-1" oldWidgetName=""/>'
            '<PrivilegeControl/></WidgetAttr>')


def _bounds(inner_cls, name, x, w, extra_children=""):
    return (f'<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">'
            f'<InnerWidget class="{inner_cls}"><WidgetName name="{name}"/>'
            f'{_widget_attr()}{extra_children}</InnerWidget>'
            f'<BoundsAttr x="{x}" y="12" width="{w}" height="26"/></Widget>')


def _dict_xml(dict_name, deps):
    if not dict_name:
        return ''
    ds = ''.join(f'<Parameter name="{d}" CustomData="false"><O><![CDATA[]]></O></Parameter>'
                 for d in (deps or []))
    deps_xml = f'<Parameters>{ds}</Parameters>' if ds else '<Parameters/>'
    return ('<Dictionary class="com.fr.data.impl.TableDataDictionary">'
            '<FormulaDictAttr ki="0" vi="1"/>'
            '<TableDataDictAttr><TableData class="com.fr.data.impl.NameTableData">'
            f'<Name><![CDATA[{dict_name}]]></Name>{deps_xml}</TableData></TableDataDictAttr></Dictionary>')


def _widget_value(w):
    if w.get("readonly_formula"):
        # entity 只读公式（semantic entity_formula；$para_* 无大括号形态）
        f = w["readonly_formula"] if isinstance(w["readonly_formula"], str) \
            else _ENTITY_FORMULA_REF[0]
        if not f:
            raise SkillError("readonly_formula=true 需要 semantic conventions.entity_formula")
        return ('<widgetValue>\n<O t="XMLable" class="com.fr.base.Formula">\n<Attributes>\n'
                f'<![CDATA[{f}]]>\n</Attributes>\n</O>\n</widgetValue>')
    return '<widgetValue>\n<O>\n<![CDATA[]]></O>\n</widgetValue>'


_ENTITY_FORMULA_REF = [None]   # build_widgets 内注入 semantic entity_formula


def _control_xml(w, x):
    """控件（非 label）BoundsWidget。宽度缺省 100（semantic panel_widgets.layout）。"""
    cls = WIDGET_CLASSES[w["type"]]
    dict_xml = _dict_xml(w.get("dict"), w.get("dict_deps"))
    wv = _widget_value(w)
    extra = (f'<allowBlank><![CDATA[true]]></allowBlank>'
             f'<DirectEdit><![CDATA[false]]></DirectEdit>'
             f'<CustomData><![CDATA[false]]></CustomData>{dict_xml}{wv}')
    return _bounds(cls, w["name"], x, w.get("width", 100), extra)


def _label_xml(w, x):
    text = w.get("text", "")
    return (f'<Widget class="com.fr.form.ui.container.WAbsoluteLayout$BoundsWidget">'
            f'<InnerWidget class="com.fr.form.ui.Label"><WidgetName name="{w["name"]}"/>'
            f'{_widget_attr()}'
            f'<widgetValue><O><![CDATA[{text}]]></O></widgetValue>'
            f'<LabelAttr verticalcenter="true" textalign="0" autoline="true"/>'
            f'<FRFont name="微软雅黑" style="1" size="80" foreground="-13421773"/>'
            f'<border style="0" color="-723724"/></InnerWidget>'
            f'<BoundsAttr x="{x}" y="12" width="{w.get("width", 45)}" height="26"/></Widget>')


def build_widgets(spec, sem=None):
    """spec → 面板 BoundsWidget XML 串。

    布局口径（semantic archetypes.panel_widgets.layout）:
      label(45px) + combo(100px) 一组，组间距 165px，y=12 h=26；起始 x=8。
      实现：label 落 x（宽 45），控件落 x+51（宽 100），每组推进 165px 栅格。
    """
    sem = sem or load_semantic()
    validate_spec(spec, sem)
    _ENTITY_FORMULA_REF[0] = sem["conventions"]["entity_formula"]
    return _layout_linear(spec)


def _layout_linear(spec):
    """165px 栅格：label 槽占 51px（45+6 间隙），控件落组内 +51，组步进恒 165px。"""
    out, x = [], 8
    for w in spec["widgets"]:
        if w["type"] == "label":
            out.append(_label_xml(w, x))
            x += 51
        else:
            out.append(_control_xml(w, x))
            x += 114
    return "\n".join(out)


# ---------------------------------------------------------------- 字典数据集（org 四级联）
def build_org_dict_datasets(sem, names=None):
    """按 semantic org.dict_dependencies 生成 dict_legal/bu/region/plant 四字典集
    （compile.py build_account_drill 的 dict_block 同构；仅 PERM，G4 dict_ 豁免 ORG）。"""
    perm_alias = sem["org"]["perm_exists_alias_template"].replace("{alias}", "f").strip()
    blocks = []

    def dict_block(name, sql):
        return (f'<TableData name="{name}" class="com.fr.data.impl.DBTableData">'
                f'<Parameters/>{_CONN_REF[0]}'
                f'<Query><![CDATA[{sql}]]></Query><PageQuery><![CDATA[]]></PageQuery></TableData>')

    blocks.append(dict_block('dict_legal',
                             "SELECT DISTINCT legal_code AS v, legal_code AS t FROM demo_ads.fin_demo_auth_base_info f "
                             "WHERE legal_code IS NOT NULL AND legal_code <> '' AND " + perm_alias + " ORDER BY 1"))
    blocks.append(dict_block('dict_bu',
                             "SELECT DISTINCT bu AS v, bu AS t FROM demo_ads.fin_demo_auth_base_info f "
                             "WHERE bu IS NOT NULL AND bu <> '' AND ('${para_legal}'='' OR f.legal_code='${para_legal}') AND "
                             + perm_alias + " ORDER BY 1"))
    blocks.append(dict_block('dict_region',
                             "SELECT DISTINCT region AS v, region AS t FROM demo_ads.fin_demo_auth_base_info f "
                             "WHERE region IS NOT NULL AND region <> '' AND ('${para_legal}'='' OR f.legal_code='${para_legal}') "
                             "AND ('${para_bu}'='' OR f.bu='${para_bu}') AND " + perm_alias + " ORDER BY 1"))
    blocks.append(dict_block('dict_plant',
                             "SELECT DISTINCT plant_code AS v, plant_code AS t FROM demo_ads.fin_demo_auth_base_info f "
                             "WHERE plant_code IS NOT NULL AND plant_code <> '' AND "
                             "(('${para_legal}'<>'' AND f.legal_code='${para_legal}') OR "
                             "('${para_bu}'<>'' AND f.bu='${para_bu}' AND ('${para_region}'='' OR f.region='${para_region}'))) AND "
                             + perm_alias + " ORDER BY 1"))
    return blocks


_CONN_REF = [None]   # build_cpt 内注入 connection_xml(sem)


# ---------------------------------------------------------------- 整页产物
def build(spec, sem=None, report_name="panel", out=None):
    """spec → (cpt_text, meta)。org_dicts=True（缺省当面板有 dict_ 引用时自动）补齐四字典集。
    guardrails G1-G4 0 错才返回。"""
    sem = sem or load_semantic()
    validate_spec(spec, sem)
    from _common import connection_xml
    _CONN_REF[0] = connection_xml(sem)
    _ENTITY_FORMULA_REF[0] = sem["conventions"]["entity_formula"]

    widgets_xml = _layout_linear(spec)
    lock_js = sem["conventions"]["lock_js_template"].rstrip("\n") if spec.get("lock_js", True) else None

    control_names = [w["name"] for w in spec["widgets"] if w["type"] != "label"]
    used_dicts = sorted({w["dict"] for w in spec["widgets"] if w.get("dict")})
    tds = ""
    if used_dicts:
        org4 = {"dict_legal", "dict_bu", "dict_region", "dict_plant"}
        missing = [d for d in used_dicts if d not in org4]
        if missing:
            raise SkillError(f"字典集 {missing} 非语义层 org 四级联字典，"
                             f"请用 dataset_skill 生成后以 datasets 传入（本技能只内置 org 四字典）")
        tds = "".join(build_org_dict_datasets(sem))
    doc = workbook_cpt(report_name, _NOTE_CELL, tds, sem, param_names=control_names,
                       widgets_xml=widgets_xml, lock_js=lock_js)
    blocking, _ = run_guardrails(doc, sem)
    if blocking:
        raise SkillError("panel_skill 产物未过 guardrails:\n" +
                         "\n".join(f'  [{e["gate"]}] {e["rule"]}: {e["message"]}' for e in blocking))
    if out:
        dump(out, doc)
    return doc, {"widgets": len(spec["widgets"]), "controls": control_names, "dicts": used_dicts}


_NOTE_CELL = ('<C c="0" r="0" s="0"><O><![CDATA[参数面板页（panel_skill 生成）]]></O>'
              '<PrivilegeControl/><Expand/></C>')


def dump(out, doc):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if os.path.exists(out):
        bak = out + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.replace(out, bak)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    ET.parse(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python panel_skill.py '<spec.json>' [out.cpt]")
        raise SystemExit(2)
    spec = json.loads(sys.argv[1])
    try:
        doc, meta = build(spec)
    except SkillError as e:
        print(f"SKILL REJECT: {e}")
        raise SystemExit(1)
    print(json.dumps(meta, ensure_ascii=False))
    if len(sys.argv) > 2:
        dump(sys.argv[2], doc)
        print(f"WROTE: {sys.argv[2]}  ({now_stamp()})")
