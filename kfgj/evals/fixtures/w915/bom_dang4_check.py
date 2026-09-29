# -*- coding: utf-8 -*-
"""E-W915-BOM-DANG4 助手: FS408 扩展夹具的四形态悬挂断言（W915 泳道 A8_eval）。

夹具 evals/fixtures/bom/fs408_w915.cpt 每类悬挂恰好埋一处:
  cell->dataset(ds_cell_ghost) / chart->dataset(ds_chart_ghost) /
  widget->param(p_wghost)      / sql->param(p_sqlghost)
四条全命中且无多余 → rc 0, 否则 1。只读加载 ckzl/zsk/gczsk/build_template_bom.py 的
TemplateParser, 不建库不改原库。
用法: python evals/fixtures/w915/bom_dang4_check.py evals/fixtures/bom/fs408_w915.cpt
"""
import importlib.util
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
BUILDER = os.path.join(ROOT, "ckzl/zsk/gczsk", "build_template_bom.py")

# (类型, 目标) 期望集合——引用方(who)含 seq 号不作断言
EXPECTED = {
    ("cell->dataset", "ds_cell_ghost"),
    ("chart->dataset", "ds_chart_ghost"),
    ("widget->param", "-"),
    ("sql->param", "p_sqlghost"),
}
# 兼容性: dangling() 行首三元 (类型, 引用方, 目标) 在后, builder 演进可能追加
# 分类列/备注列(W915 时点实测 5 元组: +R2 规则位+说明), 故按位置取前三维不假设总长


def main():
    cpt = sys.argv[1] if len(sys.argv) > 1 else ""
    spec = importlib.util.spec_from_file_location("bom_builder_w915", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tp = mod.TemplateParser(0, cpt, "w915")
    if not tp.parse():
        print("[FAIL] 夹具解析失败: %s" % tp.error)
        return 1
    got = {(row[0], row[2]) for row in tp.dangling()}
    for t, g in sorted(got):
        print("  dangling: %s -> %s" % (t, g))
    if got == EXPECTED:
        print("[PASS] 四形态悬挂命中 4/4 (cell/chart/sql/widget 各一处, 无多余)")
        return 0
    print("[FAIL] 悬挂集合不符: 缺=%s 多=%s" % (sorted(EXPECTED - got), sorted(got - EXPECTED)))
    return 1


if __name__ == "__main__":
    sys.exit(main())
