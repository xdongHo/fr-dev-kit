#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fr_lint_write.py — L2 条件驱动写前审计执行器（规则表驱动，乙形态一期）
=====================================================================
设计依据：设计A-事前门禁.md §1/§2（件1/件2）＋设计A-事前门禁-B竞标.md §1.1/§1.2
（22 字段 schema、五型 predicate）＋闸门1裁决清单.md 裁决1/§3。

职责：
    对一个待写目标文件按 lint_rules.json 逐规则判定，出 PASS/WARN/FAIL ＋退出码；
    每条命中(engaged)规则的判定落留痕 KIT3\\_runs\\gate\\<ts>_<rule_id>.json
    （7 attest 字段：rule_id/basis/target/verdict/evidence/ts/operator）。
    本脚本零规则硬编码：全部判据来自规则表（数据/代码分离，供 G07 同源校验）。

用法：
    python fr_lint_write.py --file <目标路径> [--content <预检内容文件>]
                            [--rules <lint_rules.json>] [--registry <doc_id_registry.json>]
                            [--operator <操作者>] [--draft] [--json] [--no-attest]

退出码：0=参与判定规则全 PASS（或无规则命中）  1=存在 FAIL  2=仅 WARN  3=内部错误
（argparse 用法错误按其默认退出 2，与 WARN=2 以 stderr 的 usage 输出区分）
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
import argparse
import datetime
import fnmatch
import json
import os
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RULES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint_rules.json")
DEFAULT_REGISTRY = os.path.join(KIT_ROOT, "ckzl/zsk/gczsk", "doc_id_registry.json")
DEFAULT_RUNS_DIR = os.path.join(KIT_ROOT, "_runs", "gate")

ATTest_FIELDS = ["rule_id", "basis", "target", "verdict", "evidence", "ts", "operator"]


# ----------------------------------------------------------------------------
# 归一化（B 竞标：归一大小写/全半角后精确匹配，禁模糊防误放行）
# ----------------------------------------------------------------------------
def normalize_token(s, steps):
    out = s
    for step in steps or []:
        if step == "nfkc":
            out = unicodedata.normalize("NFKC", out)
        elif step == "lowercase":
            out = out.lower()
    return out


def norm_path(p):
    return os.path.abspath(p).replace("\\", "/")


def path_hit(abspath, patterns):
    """fnmatch 不感知路径分隔符：统一 / 后匹配绝对路径；无 / 的 pattern 再试 basename。"""
    np = norm_path(abspath).lower()
    base = os.path.basename(np)
    for pat in patterns or []:
        lp = pat.lower().replace("\\", "/")
        if fnmatch.fnmatch(np, lp) or (("/" not in lp) and fnmatch.fnmatch(base, lp)):
            return True
    return False


def content_hit(content, regexes):
    for rx in regexes or []:
        try:
            if re.search(rx, content, re.MULTILINE):
                return True
        except re.error:
            return False
    return False


def line_col(content, pos):
    line = content.count("\n", 0, pos) + 1
    col = pos - (content.rfind("\n", 0, pos) + 1) + 1
    return line, col


# ----------------------------------------------------------------------------
# 五型 predicate 判定器：返回 (verdict, evidence_dict)
# ----------------------------------------------------------------------------
def eval_literal_set(rule, content, registry_path):
    params = rule.get("predicate", {}).get("params", {})
    steps = params.get("normalize", ["lowercase"])
    try:
        cands_raw = re.findall(params.get("extract", r"doc-\d+"), content)
    except re.error as e:
        return "FAIL", {"error": "extract 正则非法: %r" % e}
    cands = sorted({normalize_token(c, steps) for c in cands_raw})
    if not cands:
        return "PASS", {"candidates": [], "note": params.get(
            "empty_candidates", "无引用，不加载 registry")}
    if not registry_path or not os.path.isfile(registry_path):
        return "FAIL", {"candidates": cands, "error":
                        "registry 不存在: %s" % registry_path}
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:  # noqa: BLE001
        return "FAIL", {"candidates": cands, "error": "registry 读取失败: %r" % e}
    keys = set(data.get("ids", {}).keys()) if isinstance(data, dict) and "ids" in data \
        else set(data.keys()) if isinstance(data, dict) else set()
    hits = [c for c in cands if c in keys]
    miss = [c for c in cands if c not in keys]
    ev = {"candidates": cands, "hits": hits, "miss": miss,
          "registry": norm_path(registry_path), "match": "exact",
          "boundary": params.get("boundary_note", "")}
    return ("FAIL" if miss else "PASS"), ev


def eval_regex_ban(rule, content, registry_path=None):
    params = rule.get("predicate", {}).get("params", {})
    violations = []
    for pat in params.get("patterns", []):
        try:
            flags = re.MULTILINE
            for name in str(pat.get("flags", "")):
                flags |= getattr(re, name, 0)
            for m in re.finditer(pat.get("regex", r"(?!)"), content, flags):
                ln, cl = line_col(content, m.start())
                violations.append({"line": ln, "col": cl,
                                   "match": m.group(0)[:120],
                                   "hint": pat.get("hint", "")})
        except re.error as e:
            return "FAIL", {"error": "pattern 正则非法: %r" % e,
                            "violations": violations}
    ev = {"violations": violations, "scope_note": params.get("scope_note", "")}
    return ("FAIL" if violations else "PASS"), ev


def eval_struct_seq(rule, content, registry_path=None):
    params = rule.get("predicate", {}).get("params", {})
    kind = params.get("kind", "md_heading_unique")
    if kind != "md_heading_unique":
        return "FAIL", {"error": "未知 struct_seq kind: %s" % kind}
    levels = set(params.get("levels", [2, 3]))
    seen, dups = {}, []
    for m in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", content, re.MULTILINE):
        level = len(m.group(1))
        if level not in levels:
            continue
        text = m.group(2).strip()
        key = (level, text)
        ln, _ = line_col(content, m.start())
        if key in seen:
            dups.append({"level": level, "text": text,
                         "lines": seen[key] + [ln]})
            seen[key].append(ln)
        else:
            seen[key] = [ln]
    ev = {"duplicates": dups, "levels": sorted(levels),
          "normalize": params.get("normalize", "strip")}
    return ("FAIL" if dups else "PASS"), ev


def eval_threshold(rule, content, registry_path=None):
    """threshold 判定器（首批规则未用；供测试夹具旁证与后续铁律如 F3 阈值类落表）。
    语义=禁令：条件成立（如行长>上限）即 FAIL。"""
    params = rule.get("predicate", {}).get("params", {})
    kind = params.get("metric", "")
    value = params.get("value", 0)
    op = params.get("op", ">")
    if kind == "max_line_length":
        actual = max((len(l) for l in content.splitlines()), default=0)
    elif kind == "min_hits":
        rx = params.get("regex", r"(?!)")
        actual = len(re.findall(rx, content, re.MULTILINE))
    else:
        return "FAIL", {"error": "未知 threshold metric: %s" % kind}
    violated = {"<": actual < value, "<=": actual <= value, ">": actual > value,
                ">=": actual >= value, "==": actual == value}.get(op, False)
    ev = {"metric": kind, "op": op, "value": value, "actual": actual,
          "semantics": "禁令条件成立即 FAIL"}
    return ("FAIL" if violated else "PASS"), ev


def eval_exists(rule, content, registry_path=None):
    params = rule.get("predicate", {}).get("params", {})
    kind = params.get("kind", "substring")
    if kind == "substring":
        needle = params.get("needle", "")
        head = content[: params.get("within_chars", len(content))]
        ok = needle in head
        return ("PASS" if ok else "FAIL"), {
            "needle": needle, "within_chars": params.get("within_chars"),
            "found": ok, "judge_note": params.get("judge_note", "")}
    if kind == "regex":
        rx = params.get("regex", r"(?!)")
        m = re.search(rx, content[: params.get("within_chars", len(content))],
                      re.MULTILINE)
        return ("PASS" if m else "FAIL"), {"regex": rx, "found": bool(m)}
    if kind == "any_group":
        ci = params.get("case_insensitive", True)
        hay = content.lower() if ci else content
        needle_fn = (lambda w: w.lower()) if ci else (lambda w: w)
        groups = params.get("groups", {})
        hit_groups, hit_words = [], []
        for gname, words in groups.items():
            g_hits = [w for w in words if needle_fn(w) in hay]
            if g_hits:
                hit_groups.append(gname)
                hit_words.extend(g_hits)
        ok = bool(hit_groups)
        verdict = "PASS" if ok else "WARN"
        return verdict, {"hit_groups": hit_groups, "hit_words": hit_words[:20],
                         "group_source": params.get("group_source", ""),
                         "verdict_semantics": params.get("verdict_semantics", "")}
    return "FAIL", {"error": "未知 exists kind: %s" % kind}


PREDICATE_EVALUATORS = {
    "literal_set": eval_literal_set,
    "regex_ban": eval_regex_ban,
    "struct_seq": eval_struct_seq,
    "threshold": eval_threshold,
    "exists": eval_exists,
}


# ----------------------------------------------------------------------------
# basis 行：每条规则的铁律锚（与规则表同源，此处仅作运行期快照供留痕复用）
# ----------------------------------------------------------------------------
BASIS = {
    "AC5-WIDGETNAME-UPPER": "ckzl/gf/FR_HEADLESS_GUIDE.md:422（### AC「JS 选择器控件名必须 toUpperCase()」）＋ckzl/bb/外部依赖与归档声明.mdmiaoda/notes/铁律改造清单-A.md:150（AC5 前移·生成器统一变换断言）",
    "P2-MD-DUP-HEADING": "ckzl/bb/外部依赖与归档声明.mdmiaoda/闸门1裁决清单.md:25（P-2 立案）＋ckzl/lc/04_参数面板.md:312,317（同名 H2 实证）",
    "G06-KB-INDEX-HEAD": "kfgj/EXEC_CONTRACT.md:43（G06 表行）＋kfgj/guard.py:219-221（gate_kb_index 同判）＋ckzl/bb/外部依赖与归档声明.md知识管理规范-维护流程.md §0.2",
    "R5-DOCID-REGISTRY-GATE": "ckzl/gf/FR_HEADLESS_GUIDE.md:294（### R「无核验节点名禁止伪造 XML」）＋ckzl/bb/外部依赖与归档声明.mdmiaoda/闸门1裁决清单.md:17（裁决1：doc_id_registry 字面量精确比对）＋ckzl/bb/外部依赖与归档声明.mdmiaoda/notes/铁律改造清单-A.md:158-165（§3 白名单门禁设计）",
    "TRIG-4ELEM-CONDITION": "ckzl/bb/外部依赖与归档声明.mdmiaoda/designs/设计A-事前门禁.md:36-37（四要素＝ckzl/bb/外部依赖与归档声明.mdmiaoda/notes/铁律改造清单-A.md §1 L1 三组词＋三路判据合并机械化）",
}


def write_attest(runs_dir, ts, rule_id, target, verdict, evidence, operator):
    os.makedirs(runs_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = os.path.join(runs_dir, "%s_%s.json" % (stamp, rule_id))
    rec = {
        "rule_id": rule_id,
        "basis": BASIS.get(rule_id, "lint_rules.json 规则表 basis 未登记"),
        "target": norm_path(target),
        "verdict": verdict,
        "evidence": evidence,
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "operator": operator,
    }
    assert set(rec.keys()) == set(ATTest_FIELDS)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    return path


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="L2 条件驱动写前审计执行器（规则表驱动）")
    ap.add_argument("--file", required=True, help="待写目标文件路径")
    ap.add_argument("--content", help="预检内容文件（目标未落盘时提供将写入的内容；默认读 --file 本体）")
    ap.add_argument("--rules", default=DEFAULT_RULES, help="规则表路径")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY, help="doc_id_registry 路径")
    ap.add_argument("--operator", default="fr-agent", help="操作者署名（留痕用）")
    ap.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR, help="留痕目录")
    ap.add_argument("--draft", action="store_true", help="草稿模式：deny 规则 FAIL 降级 WARN（留痕，禁连续使用）")
    ap.add_argument("--no-attest", action="store_true", help="不落留痕（仅供试跑）")
    ap.add_argument("--json", action="store_true", help="stdout 输出机器可读 JSON")
    args = ap.parse_args()

    target = os.path.abspath(args.file)
    content_path = os.path.abspath(args.content) if args.content else target
    try:
        with open(args.rules, "r", encoding="utf-8") as f:
            table = json.load(f)
    except Exception as e:  # noqa: BLE001
        print("[ERR] 规则表不可读: %r" % e)
        return 3
    try:
        with open(content_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except FileNotFoundError:
        print("[ERR] 内容文件不存在: %s（目标未落盘时用 --content 提供预检内容）" % content_path)
        return 3
    except Exception as e:  # noqa: BLE001
        print("[ERR] 内容读取失败: %r" % e)
        return 3

    registry_path = os.path.join(KIT_ROOT, args.registry) \
        if args.registry and not os.path.isabs(args.registry) else args.registry

    results = []
    attest_paths = []
    for rule in table.get("rules", []):
        if not rule.get("enabled", True):
            continue
        trig = rule.get("trigger", {})
        tools_hit = True  # CLI 调用面恒为 write/edit，规则 tools 即为其监听面
        pg = path_hit(target, trig.get("path_glob"))
        cr = content_hit(content, trig.get("content_regex"))
        engaged = tools_hit and (pg or cr)
        rid = rule.get("rule_id", "?")
        if not engaged:
            results.append({"rule_id": rid, "status": "SKIP",
                            "detail": "触发未命中(path_glob=%s content_regex=%s)"
                                      % (pg, cr)})
            continue
        ptype = rule.get("predicate", {}).get("type")
        evaluator = PREDICATE_EVALUATORS.get(ptype)
        if not evaluator:
            verdict, evidence = "FAIL", {"error": "未知 predicate 类型: %s" % ptype}
        else:
            verdict, evidence = evaluator(rule, content, registry_path)
        action = rule.get("action", "deny")
        status = verdict
        if verdict == "FAIL" and action == "log":
            status = "WARN"  # 遥测规则永不 FAIL
        elif verdict == "FAIL" and args.draft:
            status = "WARN"  # 草稿降级（留痕在案，正式交付禁止连续使用）
        if not args.no_attest:
            attest_paths.append(write_attest(
                args.runs_dir, None, rid, target, status, evidence, args.operator))
        results.append({"rule_id": rid, "status": status,
                        "detail": rule.get("message", ""),
                        "evidence": evidence})

    gate = [r for r in results if r["status"] in ("PASS", "WARN", "FAIL")]
    n_fail = sum(1 for r in gate if r["status"] == "FAIL")
    n_warn = sum(1 for r in gate if r["status"] == "WARN")
    n_pass = sum(1 for r in gate if r["status"] == "PASS")
    n_skip = sum(1 for r in results if r["status"] == "SKIP")
    exit_code = 1 if n_fail else (2 if n_warn else 0)

    if args.json:
        print(json.dumps({"target": norm_path(target), "exit_code": exit_code,
                          "pass": n_pass, "warn": n_warn, "fail": n_fail,
                          "skip": n_skip, "results": results,
                          "attests": attest_paths},
                         ensure_ascii=False, indent=2))
    else:
        icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[SKIP]"}
        print("=" * 62)
        print("  fr_lint_write 写前审计  目标=%s%s" % (norm_path(target),
              "  [draft]" if args.draft else ""))
        print("=" * 62)
        for r in results:
            print("%s %s" % (icon[r["status"]], r["rule_id"]))
            print("       %s" % r["detail"])
            ev = r.get("evidence") or {}
            for k in ("miss", "violations", "duplicates", "hit_groups"):
                if ev.get(k):
                    print("       %s: %s" % (k, ev[k]))
            if ev.get("error"):
                print("       error: %s" % ev["error"])
        print("-" * 62)
        print("  结果: %s   (PASS=%d WARN=%d FAIL=%d SKIP=%d)  退出码=%d"
              % ("❌ 存在 FAIL" if n_fail else
                 ("⚠️ 仅 WARN" if n_warn else "✅ 通过"),
                 n_pass, n_warn, n_fail, n_skip, exit_code))
        if attest_paths:
            print("  留痕: %s （%d 件）" % (args.runs_dir, len(attest_paths)))
        print("=" * 62)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
