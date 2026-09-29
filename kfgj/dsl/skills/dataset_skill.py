# -*- coding: utf-8 -*-
"""dataset_skill.py — 标准数据集生成器（spec → DBTableData XML / 整页 cpt）。

R39 标准组件技能库 ①。spec 契约见 _common.build_fact_sql docstring；
硬约束（不可绕过）:
  - numeric 转换: 事实集必须 ≥1 个 numeric_cols，生成 COALESCE(NULLIF(col,'')::numeric,0)
  - ORG+PERM:    permission=full 时从 semantic org 模板织入（entity 四段并集 + 角色旁路/用户映射）
  - period CASE: period_param=para_month|para_month_bud 时自动织入 CASE upper('${..}') 换算
  - 产物必须过 guardrails G1-G4（0 错）才视为构建成功（build 内建自检）

口径来源: dsl/semantic_layer.yaml（org 模板/conventions/standard_params/meta.fr_connection_name）。
"""
import datetime
import json
import os
import sys
import xml.etree.ElementTree as ET

from _common import (SkillError, build_fact_sql, cascade_params, load_semantic,
                     now_stamp, run_guardrails, tabledata_xml, workbook_cpt)

DEFAULT_REPORT_NAME = "detail"


def validate_spec(spec, sem):
    """spec 校验（违例 SkillError，坏 spec 标准出口）。"""
    from _common import validate_dataset_spec
    return validate_dataset_spec(spec, sem)


def declared_params(spec, sem):
    """cpt 级声明参数 = spec.params ∪ ORG 级联参数（ORG 织入时）∪ period 参数。"""
    names = list(spec.get("params") or [])
    perm = spec.get("permission") or "full"
    if perm == "full":
        for p in cascade_params(sem):
            if p not in names:
                names.append(p)
    if spec.get("period_param") and spec["period_param"] not in names:
        names.append(spec["period_param"])
    return names


def build_sql(spec, sem=None):
    """仅取 SQL（verify_sql.py 验证闭环用）。"""
    return build_fact_sql(spec, sem or load_semantic())


def build_tabledata(spec, sem=None):
    """spec → (<TableData> XML 片段, sql)。仅数据集本体，不落 cpt。"""
    sem = sem or load_semantic()
    sql = build_fact_sql(spec, sem)
    return tabledata_xml(spec["name"], sql, sem, params=spec.get("params") or []), sql


def build(spec, sem=None, report_name=DEFAULT_REPORT_NAME, do_smoke=False):
    """spec → (cpt_text, sql)；guardrails G1-G4 任一错误 → SkillError（不出产物）。"""
    sem = sem or load_semantic()
    validate_spec(spec, sem)
    td, sql = build_tabledata(spec, sem)
    names = declared_params(spec, sem)
    doc = workbook_cpt(report_name, "", td, sem, param_names=names)
    blocking, _ = run_guardrails(doc, sem, do_smoke=do_smoke)
    if blocking:
        raise SkillError("dataset_skill 产物未过 guardrails:\n" +
                         "\n".join(f'  [{e["gate"]}] {e["rule"]}: {e["message"]}' for e in blocking))
    return doc, sql


def dump(out, doc):
    """落盘（既有文件自动备份）+ ET 兜底解析。"""
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    if os.path.exists(out):
        bak = out + ".bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        os.replace(out, bak)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    ET.parse(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python dataset_skill.py '<spec.json>' [out.cpt]")
        raise SystemExit(2)
    spec = json.loads(sys.argv[1])
    try:
        doc, sql = build(spec)
    except SkillError as e:
        print(f"SKILL REJECT: {e}")
        raise SystemExit(1)
    print(sql)
    if len(sys.argv) > 2:
        dump(sys.argv[2], doc)
        print(f"WROTE: {sys.argv[2]}  ({now_stamp()})")
