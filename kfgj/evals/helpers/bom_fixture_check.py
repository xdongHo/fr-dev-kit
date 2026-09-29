# -*- coding: utf-8 -*-
"""E-BOM-* 助手: build_template_bom 悬挂检测/计数口径/高频统计 夹具回归。

三种模式(均确定性, 只读原库代码不建库):
  dangling <cpt>            用 ckzl/zsk/gczsk/build_template_bom.py 的 TemplateParser 求悬挂,
                            断言 FS408 形态(cell->dataset)与 sql->param 命中 → rc 0/1
  counting <cpt>            同一夹具上 orig 口径 vs v2 口径(LMIX SOP-0904 接入 H3 分类器的副本)
                            的 sql->param 悬挂对照, 断言 orig=3 / v2=1(引号内列名误报被剔) → rc 0/1
  highfreq <dir>            递归收集目录 cpt/frm, 按文件名精确匹配定位高频夹具对
                            (HIGHFREQ_FIXTURES), 断言共享数据集 ds_ok 跨 2 件频次=2 → rc 0/1
                            (目录布局平铺/子目录均适用, 其余无关夹具增删不影响判定;
                             A24 已知坑②加固: 原非递归 listdir+len==2 硬断言已退役)

用法: python evals/helpers/bom_fixture_check.py <mode> <path>
"""
import importlib.util
import os
import sys

try:  # Windows 控制台中文输出(与 evals/run_evals.py 同款保护)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ORIG_BUILDER = os.path.join(ROOT, "ckzl/zsk/gczsk", "build_template_bom.py")
V2_BUILDER = os.path.join(ROOT, "_runs", "night", "R74_night", "LMIX_build_template_bom_v2.py")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_with(builder, path, name):
    tp = builder.TemplateParser(0, path, "evals")
    ok = tp.parse()
    return tp, ok


def mode_dangling(cpt):
    b = _load(ORIG_BUILDER, "bom_orig")
    tp, ok = parse_with(b, cpt, "d")
    if not ok:
        print("[FAIL] 夹具解析失败: %s" % tp.error)
        return 1
    d = tp.dangling()
    for row in d:                      # v2 dangling() 5元组(+classification/basis), 位置式取前3列
        typ, who, tgt = row[0], row[1], row[2]
        print("  dangling: %s %s -> %s" % (typ, who, tgt))
    has_cell = any(t == "cell->dataset" and g == "ds_ghost" for t, _, g in
                   ((r[0], r[1], r[2]) for r in d))
    has_sql = any(t == "sql->param" and g == "p_ghost" for t, _, g in
                  ((r[0], r[1], r[2]) for r in d))
    if has_cell and has_sql:
        print("[PASS] FS408 形态命中: cell->dataset(ds_ghost) + sql->param(p_ghost), 共 %d 条" % len(d))
        return 0
    print("[FAIL] FS408 形态未命中 cell=%s sql=%s" % (has_cell, has_sql))
    return 1


def mode_counting(cpt):
    bo = _load(ORIG_BUILDER, "bom_orig_c")
    bv = _load(V2_BUILDER, "bom_v2_c")
    to, ok1 = parse_with(bo, cpt, "o")
    tv, ok2 = parse_with(bv, cpt, "v")
    if not (ok1 and ok2):
        print("[FAIL] 夹具解析失败 orig=%s v2=%s" % (to.error, tv.error))
        return 1
    so = {r[2] for r in to.dangling() if r[0] == "sql->param"}
    sv = {r[2] for r in tv.dangling() if r[0] == "sql->param"}
    print("  sql->param orig=%d %s" % (len(so), sorted(so)))
    print("  sql->param v2  =%d %s" % (len(sv), sorted(sv)))
    # 口径断言: orig 把引号内 SQL 标识符(t1/col_ghost)当宏 → 3 条; v2 剔除后只剩真实 p_ghost → 1 条
    if len(so) == 3 and len(sv) == 1 and sv == {"p_ghost"} and set(so) == {"t1", "col_ghost", "p_ghost"}:
        print("[PASS] dangling 计数口径对照: orig=3(含引号内误报) → v2=1(真悬挂)")
        return 0
    print("[FAIL] 口径对照不符")
    return 1


HIGHFREQ_FIXTURES = ("bom_second.cpt", "fs408_like.cpt")  # 高频统计夹具对(按文件名精确匹配)


def mode_highfreq(root):
    """高频统计(加固版): 递归收集 root 下全部 cpt/frm, 但判定只看按文件名精确
    定位的夹具对 HIGHFREQ_FIXTURES —— 平铺/子目录布局均可命中, 其余无关夹具
    (无论平铺还是子目录)的增删均不影响 freq 与件数判定。"""
    b = _load(ORIG_BUILDER, "bom_orig_h")
    found = {}                     # basename(小写) -> 命中路径(排序遍历, 命中唯一且确定)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            if fn.lower().endswith((".cpt", ".frm")):
                found.setdefault(fn.lower(), os.path.join(dirpath, fn))
    freq = {}
    n_parsed = 0
    missing = []
    for name in HIGHFREQ_FIXTURES:
        p = found.get(name.lower())
        if p is None:
            missing.append(name)
            continue
        n_parsed += 1
        tp, ok = parse_with(b, p, "h" + name)
        if ok:
            for ds in tp.datasets:
                freq[ds] = freq.get(ds, 0) + 1
    for k in sorted(freq):
        print("  freq[%s]=%d" % (k, freq[k]))
    if missing:
        print("[FAIL] 高频夹具缺失: %s" % ", ".join(missing))
        return 1
    if freq.get("ds_ok") == 2 and n_parsed == 2:
        print("[PASS] 高频统计: ds_ok 跨 2 件频次=2")
        return 0
    print("[FAIL] 高频统计不符: ds_ok=%d files=%d" % (freq.get("ds_ok", 0), n_parsed))
    return 1


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    mode, path = sys.argv[1], sys.argv[2]
    if mode == "dangling":
        return mode_dangling(path)
    if mode == "counting":
        return mode_counting(path)
    if mode == "highfreq":
        return mode_highfreq(path)
    print("未知模式: %s" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())
