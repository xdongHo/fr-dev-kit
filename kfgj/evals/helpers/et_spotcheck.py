# -*- coding: utf-8 -*-
"""E-REBUILD-ET-SPOT: 重建产物 XML 抽检（确定性抽样 3 件, ET 解析全过才放行）。

抽样规则（确定性, 不随机）: 对目录下 .cpt/.frm 按文件名排序, 取第 1 件、中间 1 件、
最后 1 件。任何一件解析失败或目录不足 3 件 → 退出码 1。
用法: python evals/helpers/et_spotcheck.py [rebuild目录]
      缺省 _runs/night/campaign/rebuild（campaign 战役重建产物, CAR-014 数据源）
"""
import os
import sys
import xml.etree.ElementTree as ET

DEFAULT_DIR = os.path.join("_runs", "night", "campaign", "rebuild")
EXTS = (".cpt", ".frm")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    if not os.path.isdir(root):
        print("[FAIL] rebuild 目录不存在: %s" % root)
        return 1
    names = sorted(n for n in os.listdir(root) if n.lower().endswith(EXTS))
    if len(names) < 3:
        print("[FAIL] 可抽检产物不足 3 件(实际 %d): %s" % (len(names), root))
        return 1
    picks = [names[0], names[len(names) // 2], names[-1]]
    bad = []
    for n in picks:
        p = os.path.join(root, n)
        try:
            ET.parse(p)
            print("  OK  %s" % p)
        except Exception as e:  # noqa: BLE001
            bad.append((n, str(e)[:120]))
            print("  BAD %s -> %s" % (n, str(e)[:120]))
    if bad:
        print("[FAIL] ET 解析通过: %d/3" % (3 - len(bad)))
        return 1
    print("[PASS] ET 解析通过: 3/3 (抽样: 首件/中位件/末件, 共 %d 件产物)" % len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
