#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_defaults.py — 默认自动档编排器（P0, Stage 11 §2.2）

按 Stage 2→3→4→6 顺序串接默认格式化脚本（机械自动化"默认参数表"同构）:
  1. sql    Stage 2  format_dataset_sql.py   数据集 SQL 美化(sqlglot)
  2. detail Stage 3  fmt_detail_cells.py     类型化明细样式(数值右/百分比右/日期/序号/文本)
  3. freeze Stage 3  freeze_header.py        冻结表头
  4. panel  Stage 4  auto_layout_watermark.py  参数面板区块模型布局(LAYOUT_SPEC Ver0.7 权威; 2026-09-29 起,
            原 fmt_panel_safe.py 为 Ver0.5 旧实现已弃用)
  5. css    Stage 6  add_css_import.py       CSS 引用注入
  6. btns   Stage 6  add_export_btn.py + add_query_btn.py  导出/查询按钮补齐

默认全开; --skip a,b 显式关闭单项(留痕); --verify 末尾跑真引擎渲染验证(T+L 断言)。
单步失败不停线(机械流水线原则: 报警汇总), exit code = 失败步骤数(0=全绿)。

用法:
  python run_defaults.py <cpt路径...> [--skip sql,panel] [--numeric-labels 标签1,标签2]
                         [--freeze-rows 2] [--verify] [--timeout 120]
"""
import argparse
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))          # .../kfgj/tygs/CPT模板/默认格式
V2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))  # repo 根(3 层上)

STEPS = [  # (key, Stage, 脚本相对 HERE, argv 模板)
    ("sql", "2", os.path.join("4.模板数据集sql格式美化", "format_dataset_sql.py"), ["{cpt}"]),
    ("detail", "3", "fmt_detail_cells.py", ["{cpt}"]),
    ("freeze", "3", "freeze_header.py", ["{cpt}", "--rows", "{rows}"]),
    ("panel", "4", os.path.join("2.参数面板控件布局", "auto_layout_watermark.py"), ["{cpt}"]),
    ("css", "6", os.path.join("2.参数面板控件布局", "add_css_import.py"), ["{cpt}"]),
    ("btns", "6", None, None),  # 双脚本特殊处理
]


def xml_ok(fp):
    """每步后良构校验(编排器级防线: 任何步骤弄坏文件立即报警)"""
    import xml.etree.ElementTree as ET
    try:
        ET.parse(fp)
        return True, ""
    except ET.ParseError as e:
        return False, str(e)


def run_one(script, argv, cwd):
    p = os.path.join(HERE, script)
    if not os.path.isfile(p):
        return False, "脚本不存在: %s" % p
    cmd = [sys.executable, p] + argv
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=cwd, timeout=300)
    except subprocess.TimeoutExpired:
        return False, "超时(>300s)"
    tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
    ok = r.returncode == 0
    return ok, (tail[-1][:120] if tail else ("exit=0" if ok else "exit=%d" % r.returncode))


def main():
    ap = argparse.ArgumentParser(description="默认自动档编排器(Stage 2→3→4→6)")
    ap.add_argument("cpts", nargs="+", help="cpt 路径(可多个)")
    ap.add_argument("--skip", default="", help="跳过步骤(逗号分隔): sql,detail,freeze,panel,css,btns")
    ap.add_argument("--numeric-labels", default="", help="数值列标签清单(传给 fmt_detail_cells)")
    ap.add_argument("--freeze-rows", default="2", help="冻结行数(默认2)")
    ap.add_argument("--verify", action="store_true", help="末尾跑 render_check 真引擎验证")
    ap.add_argument("--timeout", type=int, default=120, help="verify 渲染超时秒")
    a = ap.parse_args()

    skip = {s.strip() for s in a.skip.split(",") if s.strip()}
    unknown = skip - {k for k, *_ in STEPS}
    if unknown:
        print("❌ 未知步骤: %s (可用: %s)" % (unknown, ",".join(k for k, *_ in STEPS)))
        return 2
    if skip:
        print("⚠ 跳过步骤(留痕): %s" % ",".join(sorted(skip)))

    n_fail = 0
    for cpt in a.cpts:
        cpt = os.path.abspath(cpt)
        if not os.path.isfile(cpt):
            print("❌ 文件不存在: %s" % cpt)
            n_fail += 1
            continue
        print("═══ %s ═══" % os.path.basename(cpt))
        extra = []
        for key, stage, script, argv_tpl in STEPS:
            if key in skip:
                print("  [SKIP] %-6s Stage %s" % (key, stage))
                continue
            if key == "btns":
                oks = []
                for sub in ("add_export_btn.py", "add_query_btn.py"):
                    ok, msg = run_one(os.path.join("2.参数面板控件布局", sub), ["{cpt}"], HERE)
                    oks.append(ok)
                    if not ok:
                        print("  [FAIL] btns/%s: %s" % (sub.split('_')[1], msg))
                good, why = xml_ok(cpt)
                if not good:
                    print("  [FAIL] btns   Stage 6  步骤后 XML 不良构: %s" % why)
                    n_fail += 1
                elif all(oks):
                    print("  [ OK ] %-6s Stage 6  导出+查询按钮" % key)
                else:
                    n_fail += 1
                continue
            argv = [x.format(cpt=cpt, rows=a.freeze_rows) for x in argv_tpl]
            if key == "detail" and a.numeric_labels:
                argv += ["--numeric-labels", a.numeric_labels]
            ok, msg = run_one(script, argv, HERE)
            # 已知"无料"返回(裸模板无数据行/无SQL) → 流水线语义: 该工位无料, 非缺陷
            if not ok and key == "detail" and "未找到" in msg:
                print("  [EMPTY] %-6s Stage %s  无数据行(裸模板), 跳过 — %s" % (key, stage, msg))
                continue
            if ok:  # 步骤成功 → 复核文件仍良构(编排器级防线)
                good, why = xml_ok(cpt)
                if not good:
                    print("  [FAIL] %-6s Stage %s  步骤后 XML 不良构: %s(备份在 _backup_*)" % (key, stage, why))
                    n_fail += 1
                    continue
            tag = "OK" if ok else "FAIL"
            print("  [%s] %-6s Stage %s  %s" % (tag, key, stage, msg))
            if not ok:
                n_fail += 1

    # 可选: 真引擎验证(T+L 断言)
    if a.verify:
        rc = os.path.join(V2, "kfgj/xlyl", "render_check.py")
        print("═══ verify(真引擎渲染) ═══")
        r = subprocess.run([sys.executable, rc] + [os.path.abspath(c) for c in a.cpts]
                           + ["--backend", "injected", "--html-dir",
                              os.path.join(V2, "kfgj/xlyl", "out"), "--timeout", str(a.timeout)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        for ln in out.strip().splitlines()[:8]:
            print("  " + ln)
        if r.returncode not in (0,):
            n_fail += 1
            print("  [FAIL] render_check exit=%d" % r.returncode)

    print("═══ 汇总: %s ═══" % ("全绿 ✅" if n_fail == 0 else "失败 %d 步 ❌(不停线, 详见上)" % n_fail))
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
