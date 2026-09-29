# -*- coding: utf-8 -*-
"""rules_ext.py — [DEPRECATED 2026-09-05] G6 扩展闸已合入 guardrails.py。

本模块由 L5 泳道（2026-09-04）产出（R01-R15 外挂 G6）；晨间收口卡 R25（2026-09-05）
已将全部 15 条规则**原样迁入** guardrails.py（模块 docstring 含与 G1-G5 的重复判定
评审结论与「强化版」标注），本文件降级为兼容 shim：既有调用方
（如 _runs/night/L5/run_fixtures.py 的 `rules_ext.check_rules_ext(...)`）无需改动。

公开接口（均为 guardrails 同名对象别名）
--------
check_rules_ext(doc_xml, semantic, sql_list) -> list[dict]   # 只跑 G6（R01-R15）
check_with_base(doc_xml, semantic, sql_list, ...) -> list[dict]  # G1-G5+G6 联检
                                                             # = guardrails.check(enable_ext=True)
GATE = "G6"

CLI（行为与合入前一致）
--------
python rules_ext.py <cpt路径> [--semantic <yaml>] [--with-base]
    默认只跑 G6；--with-base 连跑 G1-G5+G6。有错 exit 1。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guardrails as gr  # noqa: E402

__all__ = ["check_rules_ext", "check_with_base", "GATE"]

GATE = gr.GATE

check_rules_ext = gr.check_rules_ext
check_with_base = gr.check_with_base


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="示例项目 cpt 护栏扩展闸 G6（R01-R15；已合入 guardrails.py，本 CLI 为兼容入口）")
    ap.add_argument("cpt", help="待检 cpt 路径")
    ap.add_argument("--semantic", default=None, help="semantic_layer.yaml 路径（缺省用内置 conventions）")
    ap.add_argument("--with-base", action="store_true", help="连跑 guardrails G1-G5（挂载演示）")
    args = ap.parse_args(argv)

    try:
        with open(args.cpt, "r", encoding="utf-8") as f:
            doc = f.read()
    except OSError as e:
        print(f"G6 ERROR: 无法读取 cpt: {e}", file=sys.stderr)
        return 2
    semantic = {}
    if args.semantic:
        try:
            import yaml
        except ImportError:
            print("G6 ERROR: --semantic 需要 PyYAML（pip install pyyaml）；"
                  "或省略 --semantic 用内置 conventions", file=sys.stderr)
            return 2
        try:
            with open(args.semantic, "r", encoding="utf-8") as f:
                semantic = yaml.safe_load(f.read()) or {}
        except (OSError, yaml.YAMLError) as e:
            print(f"G6 ERROR: semantic yaml 读取/解析失败: {e}", file=sys.stderr)
            return 2

    sql_list = gr.extract_sql_list(doc)
    errs = (check_with_base(doc, semantic, sql_list) if args.with_base
            else check_rules_ext(doc, semantic, sql_list))
    for e in errs:
        line = f'[{e["gate"]}] {e["rule"]}: {e["message"]}'
        if e.get("detail"):
            line += f"  detail={e['detail']}"
        print(line)
    if errs:
        print(f"G6: {len(errs)} errors")
        return 1
    print("G6: 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
