# -*- coding: utf-8 -*-
"""test_needs_clarification.py — CAR-012 G0 前置闸测试（独立可跑，零网络零服务器）

运行: python dsl/tests/test_needs_clarification.py        # 全过退出码 0，有 FAIL 退出码 1
覆盖:
  T1 无标记正常编译（rc=0 且产物落盘）
  T2 page 同级键标记 → 拒编译（rc=3 + 澄清清单含路径与问题 + 不落盘）
  T3 page 值内联标记 [NEEDS CLARIFICATION: ...] → 拒编译（rc=3）
  T4 语义层标记（datasources 槽位）→ check_clarifications 命中且路径正确
  T5 约定声明节点（conventions.needs_clarification）不自杀：真实 semantic_layer.yaml 扫描=0
  T6 嵌套槽位路径正确性（list 下标 [i] 形态）
"""
import contextlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DSL = os.path.dirname(HERE)
sys.path.insert(0, DSL)

import guardrails  # noqa: E402
import compile as compiler  # noqa: E402  (dsl/compile.py)
import yaml  # noqa: E402

FAILS = []


def _write_page(tmp, name, mutate=None, inline_note=None):
    page = {
        "page": name,
        "archetype": "panel_org",
        "filters": {},
        "blocks": [],
        "options": {},
        "output": name + ".cpt",
    }
    if mutate:
        mutate(page)
    if inline_note:
        page["note"] = inline_note
    p = os.path.join(tmp, name + ".yaml")
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(page, f, allow_unicode=True)
    return p


def _run_compile(page_path, out_path):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = compiler.main([page_path, "--out", out_path])
    return rc, buf.getvalue()


def check(name, cond, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def main():
    sem_path = os.path.join(DSL, "semantic_layer.yaml")
    with open(sem_path, encoding="utf-8") as f:
        sem = yaml.safe_load(f.read())

    with tempfile.TemporaryDirectory() as tmp:
        # ---- T1 无标记正常编译 ----
        p = _write_page(tmp, "g0_clean")
        out = os.path.join(tmp, "clean", "out.cpt")
        rc, stdout = _run_compile(p, out)
        check("T1 无标记编译 rc=0", rc == 0, f"rc={rc} stdout={stdout[:200]}")
        check("T1 产物已落盘", os.path.exists(out))

        # ---- T2 page 同级键标记 → rc=3 不落盘 ----
        def mark(page):
            page["filters"] = {"org": {"cascade": ["/legal/bu/region/plant"]},
                               "needs_clarification": "四级联锁定范围待业务确认"}
        p = _write_page(tmp, "g0_marked", mutate=mark)
        out2 = os.path.join(tmp, "marked", "out.cpt")
        rc, stdout = _run_compile(p, out2)
        check("T2 有标记 rc=3", rc == 3, f"rc={rc}")
        check("T2 清单含槽位路径 page.filters", "page.filters" in stdout, stdout[:300])
        check("T2 清单含澄清问题", "四级联锁定范围待业务确认" in stdout, stdout[:300])
        check("T2 产物未落盘", not os.path.exists(out2))

        # ---- T3 值内联标记 → rc=3 ----
        p = _write_page(tmp, "g0_inline",
                        inline_note="列宽 [NEEDS CLARIFICATION: 用 2200000 还是 fs_main 族?] 待定")
        out3 = os.path.join(tmp, "inline", "out.cpt")
        rc, stdout = _run_compile(p, out3)
        check("T3 内联标记 rc=3", rc == 3, f"rc={rc}")
        check("T3 清单含内联问题", "2200000" in stdout, stdout[:300])
        check("T3 产物未落盘", not os.path.exists(out3))

        # ---- T4 语义层标记命中 + 路径正确 ----
        sem_marked = yaml.safe_load(yaml.safe_dump(sem))
        sem_marked["datasources"]["org_sum_budget"]["needs_clarification"] = \
            "2027~2031 预算缺数是否阻塞上线"
        got = guardrails.check_clarifications({"page": "x", "archetype": "panel_org"}, sem_marked)
        check("T4 命中 1 条", len(got) == 1, repr(got))
        check("T4 路径=semantic.datasources.org_sum_budget",
              got and got[0]["detail"]["path"] == "semantic.datasources.org_sum_budget", repr(got))
        check("T4 gate=G0 rule=needs_clarification",
              got and got[0]["gate"] == "G0" and got[0]["rule"] == "needs_clarification", repr(got))

        # ---- T6 嵌套槽位路径（list 下标） ----
        page_nested = {"blocks": [{"kind": "panel", "needs_clarification": "面板要不要隐藏?"}]}
        got6 = guardrails.scan_clarifications(page_nested, "page")
        check("T6 嵌套路径含 [0]", got6 and got6[0]["path"] == "page.blocks[0]", repr(got6))

    # ---- T5 真实 semantic_layer.yaml 声明节点不自杀 ----
    got5 = guardrails.check_clarifications({}, sem)
    check("T5 真实语义层扫描=0（声明节点被跳过）", len(got5) == 0, repr(got5))

    print(f"\n{'ALL PASS' if not FAILS else 'FAILED: ' + ', '.join(FAILS)}"
          f"（{6 - len(set(f.split()[0] for f in FAILS))}/6 组通过）")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
