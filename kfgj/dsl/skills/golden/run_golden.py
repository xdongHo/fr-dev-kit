# -*- coding: utf-8 -*-
"""run_golden.py — R39 三生成器 golden 用例运行器。

每用例流程: spec → 技能构建 → guardrails G1-G4 独立复核（0 错）→ ET 合法 → 回读断言
（assert_contains / assert_not_contains / assert_regex）→ 产物落 golden/out/。
坏 spec 用例: expect=reject，技能必须抛 SkillError 且消息含 reject_contains 关键词。

用法:
  python golden/run_golden.py [--smoke]     # --smoke 附带 G5 库上冒烟（VPN 不通时降级 SKIP_G5）
输出:
  golden/out/<case>.cpt + _runs/night/R39/results.jsonl（及 golden/out/results.jsonl 副本）
"""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(os.path.dirname(SKILLS_DIR))
sys.path.insert(0, SKILLS_DIR)

import dataset_skill  # noqa: E402
import panel_skill    # noqa: E402
import chart_skill    # noqa: E402
from _common import SkillError, load_semantic, now_stamp, run_guardrails  # noqa: E402

import yaml  # noqa: E402

SKILLS = {"dataset": dataset_skill, "panel": panel_skill, "chart": chart_skill}
OUT_DIR = os.path.join(HERE, "out")
RUNS_DIR = os.path.join(REPO_ROOT, "_runs", "night", "R39")

# G5 冒烟参数基线（compile.py SMOKE_DEFAULTS 子集，覆盖 ORG/PERM/period 引用）
SMOKE_PARAMS = {
    "para_year": "2026", "para_month": "Sep", "para_month_bud": "Dec",
    "para_legal": "", "para_bu": "", "para_region": "", "para_plant": "",
    "para_entity": "", "para_adj": "ADJ后",
    "para_scn_py": "Actual", "para_scn_bud": "PPL_R2", "para_scn_cur": "PPL_R2",
    "para_curr": "CNY Total", "para_unit": "1000",
    "p_code": "PLH01", "p_name": "PLH01 营业收入",
    "fine_username": "frdev1",
}


def run_case(path, sem, do_smoke=False):
    case = yaml.safe_load(open(path, encoding="utf-8").read())
    name = case.get("name") or os.path.basename(path).rsplit(".", 1)[0]
    skill = SKILLS[case["skill"]]
    rec = {"case": name, "skill": case["skill"], "expect": case.get("expect", "ok"),
           "ts": now_stamp()}
    try:
        if rec["expect"] == "reject":
            try:
                skill.build(case["spec"], sem)
                rec["status"], rec["detail"] = "FAIL", "坏 spec 未被拒绝（未抛 SkillError）"
            except SkillError as e:
                kw = case.get("reject_contains", "")
                if kw and kw not in str(e):
                    rec["status"] = "FAIL"
                    rec["detail"] = f"拒绝消息缺关键词 [{kw}]: {e}"
                else:
                    rec["status"], rec["detail"] = "PASS", f"rejected: {str(e)[:160]}"
            return rec, None

        doc, meta = skill.build(case["spec"], sem)
        # ---- 独立复核（不信任技能内建闸）：guardrails + ET ----
        blocking, warns = run_guardrails(doc, sem)
        if blocking:
            rec["status"] = "FAIL"
            rec["detail"] = "; ".join(f'[{e["gate"]}] {e["rule"]}' for e in blocking)
            return rec, doc
        try:
            ET.fromstring(doc.encode("utf-8"))
        except ET.ParseError as e:
            rec["status"], rec["detail"] = "FAIL", f"ET parse: {e}"
            return rec, doc
        # ---- 回读断言 ----
        for s in case.get("assert_contains", []):
            if s not in doc:
                rec["status"], rec["detail"] = "FAIL", f"assert_contains 未命中: {s!r}"
                return rec, doc
        for s in case.get("assert_not_contains", []):
            if s in doc:
                rec["status"], rec["detail"] = "FAIL", f"assert_not_contains 命中: {s!r}"
                return rec, doc
        for rx in case.get("assert_regex", []):
            if not re.search(rx, doc, re.S):
                rec["status"], rec["detail"] = "FAIL", f"assert_regex 未命中: {rx!r}"
                return rec, doc
        # ---- 产物落盘 ----
        out_cpt = os.path.join(OUT_DIR, name + ".cpt")
        skill.dump(out_cpt, doc)
        rec["status"], rec["detail"] = "PASS", json.dumps(meta, ensure_ascii=False)
        rec["product"] = out_cpt
        # ---- G5 冒烟（可选；环境类失败降级；0 行 = 不通过，对齐 verify_sql 闭环纪律）----
        if do_smoke:
            blocking5, warns5 = run_guardrails(doc, sem, do_smoke=True,
                                               param_values=dict(SMOKE_PARAMS))
            g5_errs = [e for e in blocking5 if e["gate"] == "G5"]
            env_down = any(e["rule"] in ("connect_failed", "no_conn", "psycopg2_missing")
                           for e in g5_errs)
            rec["g5"] = ("SKIP_ENV" if env_down else ("FAIL" if g5_errs else "OK"))
            rows = {}
            for e in warns5:
                if e.get("rule") == "smoke_ok":
                    m5 = re.search(r", (\d+) 行", e["message"])
                    rows[e.get("detail", {}).get("ds", "?")] = int(m5.group(1)) if m5 else -1
            rec["g5_rows"] = rows
            if not env_down and not g5_errs and not case.get("allow_zero_rows") \
                    and any(v == 0 for v in rows.values()):
                rec["status"], rec["detail"] = "FAIL", f"G5 冒烟 0 行: {rows}"
            elif rec["g5"] == "FAIL":
                rec["status"], rec["detail"] = "FAIL", "G5 冒烟失败: " + \
                    "; ".join(e["message"][:80] for e in g5_errs)
        return rec, doc
    except SkillError as e:
        rec["status"], rec["detail"] = "FAIL", f"SkillError: {str(e)[:300]}"
        return rec, None
    except Exception as e:                       # noqa: BLE001 —— 单用例崩溃不拖垮整批
        rec["status"], rec["detail"] = "FAIL", f"EXC {type(e).__name__}: {e!r}"[:300]
        return rec, None


def main():
    do_smoke = "--smoke" in sys.argv
    sem = load_semantic()
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(RUNS_DIR, exist_ok=True)
    recs = []
    for path in sorted(glob.glob(os.path.join(HERE, "cases", "*.yaml"))):
        rec, _ = run_case(path, sem, do_smoke=do_smoke)
        recs.append(rec)
        mark = "PASS" if rec["status"] == "PASS" else rec["status"]
        print(f"[{mark:8s}] {rec['case']:28s} {rec.get('detail', '')[:120]}")
    n_pass = sum(1 for r in recs if r["status"] == "PASS")
    summary = {"total": len(recs), "pass": n_pass,
               "fail": sum(1 for r in recs if r["status"] == "FAIL"),
               "ts": now_stamp(), "smoke": do_smoke}
    print(f"GOLDEN SUMMARY: {json.dumps(summary, ensure_ascii=False)}")
    for out in (os.path.join(RUNS_DIR, "results.jsonl"),
                os.path.join(OUT_DIR, "results.jsonl")):
        with open(out, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.write(json.dumps({"summary": summary}, ensure_ascii=False) + "\n")
    return 0 if n_pass == len(recs) else 1


if __name__ == "__main__":
    sys.exit(main())
