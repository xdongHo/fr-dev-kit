# -*- coding: utf-8 -*-
"""E-W915-LEDGER-JSON-FULL 助手: ckzl/bb/外部依赖与归档声明.md 全量 JSON 行校验（W915 A8_eval）。

断言(比 E-ROUTER-LEDGER 的两条抽检更强):
  1. 全部以 { 起始的行 json.loads 可解析(bad=0)
  2. 登记条数 ≥6
  3. id 形如 R-\\d{4} 且全局唯一
  4. 每条必填字段齐: id / date / task / result
全过 → rc 0 并打印「台账 JSON 行全解析: N/N」。
用法: python evals/fixtures/w915/ledger_json_check.py [台账路径]
"""
import io
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

DEFAULT_LEDGER = "ckzl/bb/外部依赖与归档声明.md"
REQUIRED_FIELDS = ("id", "date", "task", "result")
PLACEHOLDER_TASK = "任务一句话"


def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LEDGER
    bad, main_rows, aux_rows = 0, [], 0
    with io.open(ledger, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            s = line.strip()
            if not s.startswith("{"):
                continue
            try:
                o = json.loads(s)
            except ValueError as e:
                bad += 1
                print("  BAD 第%d行 JSON 不可解析: %s" % (lineno, e))
                continue
            # 主登记行: 真实 task 且非增补行("+1":true)。格式模板行(task=任务一句话)
            # 与「+1 同类摩摩 +1」增补行合法复用 id, 只要求可解析, 不参与唯一性/必填校验。
            if str(o.get("task") or "") and str(o.get("task")) != PLACEHOLDER_TASK \
                    and not o.get("+1"):
                main_rows.append((lineno, o))
            else:
                aux_rows += 1
    n = len(main_rows)
    ids = [str(o.get("id", "")) for _ln, o in main_rows]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    badid = [i for i in ids if not re.match(r"^R-\d{4}$", i)]
    missfield = [(ln, [k for k in REQUIRED_FIELDS if not str(o.get(k, "")).strip()])
                 for ln, o in main_rows if any(not str(o.get(k, "")).strip()
                                               for k in REQUIRED_FIELDS)]
    print("  JSON 行: 主登记 %d + 模板/增补 %d | 不可解析: %d | id 重复: %s | "
          "id 形态异常: %s | 必填字段缺失: %s"
          % (n, aux_rows, bad, dup or "无", badid or "无", missfield or "无"))
    if bad == 0 and n >= 6 and not dup and not badid and not missfield:
        print("[PASS] 台账 JSON 行全解析: %d/%d 主登记, id 唯一且形态合法, 必填字段齐"
              % (n, n))
        return 0
    print("[FAIL] 台账校验未过")
    return 1


if __name__ == "__main__":
    sys.exit(main())
