# -*- coding: utf-8 -*-
"""E-ROUTER-LEDGER: 任务路由台账完整性抽检。

校验 ckzl/bb/外部依赖与归档声明.md 中 R-0001 / R-0002 两条真实登记:
  - 行为合法 JSON（json.loads 通过）
  - 属真实登记而非文件头格式模板（task 字段存在且 != 模板占位「任务一句话」）
两条都在且可解析 → 退出码 0, 否则 1。
用法: python evals/helpers/router_ledger_check.py [台账路径]
"""
import io
import json
import os
import sys

DEFAULT_LEDGER = os.path.join("ckzl/bb/外部依赖与归档声明.md")
PLACEHOLDER_TASK = "任务一句话"
REQUIRED_IDS = ("R-0001", "R-0002")


def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LEDGER
    if not os.path.isfile(ledger):
        print("[FAIL] 台账不存在: %s" % ledger)
        return 1
    found = {}
    with io.open(ledger, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            s = line.strip()
            if not s.startswith("{"):
                continue
            try:
                obj = json.loads(s)
            except ValueError:
                print("  BAD 第%d行: JSON 不可解析: %.80s" % (lineno, s))
                continue
            rid = str(obj.get("id") or "")
            task = str(obj.get("task") or "")
            if rid in REQUIRED_IDS and task and task != PLACEHOLDER_TASK:
                found[rid] = obj
    ok = True
    for rid in REQUIRED_IDS:
        if rid in found:
            print("  OK  %s 存在且 JSON 可解析 (task: %.50s...)" % (rid, found[rid].get("task", "")))
        else:
            print("  MISS %s: 无真实登记(缺失/JSON坏/或只剩格式模板)" % rid)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
