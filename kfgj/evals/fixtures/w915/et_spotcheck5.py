# -*- coding: utf-8 -*-
"""E-W915-ET-SPOT5 助手: 重建产物 XML 抽检加强版——5 件分位点抽样（W915 A8_eval）。

与 evals/helpers/et_spotcheck.py(3 件: 首/中/末)互补: 对 .cpt/.frm 按名排序取
第 1 / 25% / 50% / 75% / 末位 共 5 个分位点(去重), ET.parse 全过且 ≥5 件 → rc 0。
用法: python evals/fixtures/w915/et_spotcheck5.py [rebuild目录]
      缺省 _runs/night/campaign/rebuild
"""
import os
import sys
import xml.etree.ElementTree as ET

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

DEFAULT_DIR = os.path.join("_runs", "night", "campaign", "rebuild")
EXTS = (".cpt", ".frm")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    if not os.path.isdir(root):
        print("[FAIL] rebuild 目录不存在: %s" % root)
        return 1
    names = sorted(n for n in os.listdir(root) if n.lower().endswith(EXTS))
    if len(names) < 5:
        print("[FAIL] 可抽检产物不足 5 件(实际 %d): %s" % (len(names), root))
        return 1
    idx = sorted({0, len(names) // 4, len(names) // 2, len(names) * 3 // 4, len(names) - 1})
    bad = 0
    for i in idx:
        p = os.path.join(root, names[i])
        try:
            ET.parse(p)
            print("  OK  [%d/%d] %s" % (i + 1, len(names), names[i]))
        except Exception as e:  # noqa: BLE001
            bad += 1
            print("  BAD [%d/%d] %s -> %s" % (i + 1, len(names), names[i], str(e)[:120]))
    if bad:
        print("[FAIL] ET 解析通过: %d/5" % (5 - bad))
        return 1
    print("[PASS] ET 解析通过: 5/5 (分位点抽样 首/25%%/50%%/75%%/末, 共 %d 件产物)" % len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
