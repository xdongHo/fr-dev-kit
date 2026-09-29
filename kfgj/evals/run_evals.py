# -*- coding: utf-8 -*-
"""evals/run_evals.py — fr_dev_kit 内部评估集顺序执行 runner（CAR-019 起步版）。

用法（仓库根执行）:
  python evals/run_evals.py                 # 全量(以 cases.jsonl 实际条数为准), PASS/FAIL 矩阵 + 汇总
  python evals/run_evals.py --kind capability|regression
  python evals/run_evals.py --case E-DSL-CLEAN
退出码: 0=无 FAIL(SKIP 不算)  1=存在 FAIL(含 setup 失败/异常)  2=--case/--kind 过滤后无匹配用例

用例定义: evals/cases.jsonl（字段口径见 evals/README.md）。
harness 冻结纪律: 评估口径依赖 工具版本+本用例命令, 改工具输出文案/退出码语义时
必须同步改 cases.jsonl 并在 README 登记评估口径断裂点。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
CASES_FILE = os.path.join(HERE, "cases.jsonl")
DEFAULT_TIMEOUT = 300

try:  # Windows 控制台中文矩阵输出
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass


def decode_output(raw):
    """子进程字节流解码: utf-8 → gbk → replace，保证中文断言可匹配。"""
    for enc in ("utf-8", "gbk"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def run_shell(cmd, timeout):
    try:
        p = subprocess.run(cmd, shell=True, cwd=REPO_ROOT, timeout=timeout,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.returncode, decode_output(p.stdout or b""), None
    except subprocess.TimeoutExpired:
        return None, "", "超时(>%ds)" % timeout
    except Exception as e:  # noqa: BLE001
        return None, "", "执行异常: %r" % e


def check_case(case, rc, out, err):
    """返回 (ok, 失败原因列表)。expect_exit 支持 int / list(any-of) / null(跳过)。"""
    fails = []
    exp = case.get("expect_exit")
    if exp is not None:
        allowed = exp if isinstance(exp, list) else [exp]
        if rc not in allowed:
            fails.append("expect_exit %s != 实际 %s" % (exp, rc))
    for s in case.get("expect_contains") or []:
        if s not in out:
            fails.append("contains 未命中: %r" % s)
    for pat in case.get("expect_regex") or []:
        if not re.search(pat, out):
            fails.append("regex 未命中: %r" % pat)
    if err:
        fails.append(err)
    return (not fails), fails


def main():
    ap = argparse.ArgumentParser(description="fr_dev_kit 内部评估集 runner")
    ap.add_argument("--kind", choices=["capability", "regression"], default=None)
    ap.add_argument("--case", default=None, help="只跑指定 id")
    ap.add_argument("--list", action="store_true", help="只列出用例不执行")
    args = ap.parse_args()

    cases = []
    with io.open(CASES_FILE, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except ValueError as e:
                print("[FAIL] cases.jsonl 第%d行 JSON 坏: %s" % (lineno, e))
                return 1
    n_total = len(cases)

    if args.kind:
        cases = [c for c in cases if c.get("kind") == args.kind]
    if args.case:
        cases = [c for c in cases if c.get("id") == args.case]

    if args.list:
        for c in cases:
            print("%-22s [%s] %s" % (c["id"], c.get("kind", "?"), c.get("title", "")))
        return 0

    # BG-EV-03: 显式 --case/--kind 过滤后无匹配 → 拒绝"0/0 PASS 且 rc=0"的守门假绿
    if (args.case or args.kind) and not cases:
        print("无匹配用例: --case=%s --kind=%s (核对拼写或先 --list 查看; cases.jsonl 共 %d 条)"
              % (args.case or "-", args.kind or "-", n_total))
        return 2

    results = []
    for c in cases:
        cid = c.get("id", "?")
        print("-" * 70)
        print("[%s] %s" % (cid, c.get("title", "")))

        # 环境前置（P0-1 主线补位 2026-09-14）: requires_modules 缺失时 SKIP, 不计入 FAIL
        missing = []
        for _m in c.get("requires_modules") or []:
            try:
                __import__(_m)
            except Exception:
                missing.append(_m)
        if missing:
            print("  SKIP 缺模块: %s (当前环境未安装, 用例未执行)" % ",".join(missing))
            results.append((cid, c.get("kind", "?"), "SKIP", "缺模块: " + ",".join(missing)))
            continue

        # setup: 任一失败即判 FAIL(不跑主命令, 防脏状态误判)
        setup_err = None
        for sc in c.get("setup") or []:
            src, sout, serr = run_shell(sc, DEFAULT_TIMEOUT)
            if src not in (0, None) or serr:
                setup_err = "setup 失败(rc=%s): %s | %s" % (src, sc, (sout or serr or "")[-200:])
                break
        if setup_err:
            print("  SETUP-FAIL %s" % setup_err)
            results.append((cid, c.get("kind", "?"), "FAIL", setup_err))
            continue

        rc, out, err = run_shell(c["command"], int(c.get("timeout_s") or DEFAULT_TIMEOUT))
        ok, fails = check_case(c, rc, out, err)
        tail = " | ".join(out.strip().splitlines()[-1:]) if out.strip() else ""
        print("  rc=%s  %s" % (rc, tail[:110]))
        for m in fails:
            print("  ✗ %s" % m)
        results.append((cid, c.get("kind", "?"), "PASS" if ok else "FAIL",
                        "; ".join(fails) if fails else ""))

    # 矩阵 + 汇总
    print("=" * 70)
    print("  %-22s %-11s %s" % ("id", "kind", "result"))
    n_pass = 0
    for cid, kind, status, note in results:
        n_pass += (status == "PASS")
        print("  %-22s %-11s %s%s" % (cid, kind, status, ("  " + note) if note else ""))
    total = len(results)
    print("-" * 70)
    n_skip = sum(1 for _, _, s, _ in results if s == "SKIP")
    print("  汇总: %d/%d PASS, SKIP=%d (capability=%d, regression=%d)"
          % (n_pass, total, n_skip,
             sum(1 for _, k, s, _ in results if k == "capability" and s == "PASS"),
             sum(1 for _, k, s, _ in results if k == "regression" and s == "PASS")))
    print("=" * 70)
    # SKIP = 环境前置不满足, 不构成回归; 仅 FAIL 判非零 (P0-1 主线补位 2026-09-14)
    return 0 if all(s != "FAIL" for _, _, s, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main())
