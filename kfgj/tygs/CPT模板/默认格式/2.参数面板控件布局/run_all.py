"""
参数面板一键全量优化 — 执行目录下所有独立脚本。

用法:
    python run_all.py <cpt路径> [cpt路径...]

执行顺序:
    1. cancel_params_template.py — 取消常用参数组合
    2. add_query_btn.py          — 缺 Query 自动补
    3. add_export_btn.py         — 缺 Export 自动补
    4. add_css_import.py         — CSSImport 外部样式引用
    5. add_para_init_event.py    — CSS 注入
    6. set_write_no_toolbar.py   — 填报无工具栏
    7. fix_styles.py             — 字体 + padding
    8. fix_row_heights.py        — 行高分类
    9. widen_all.py              — 布局分行 + 跨列对齐
"""
import sys, os, subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name, args):
    """运行一个脚本，传递剩余参数"""
    path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(path):
        print(f"⚠️  跳过（不存在）: {script_name}")
        return True
    cmd = [sys.executable, path] + args
    print(f"\n{'='*60}")
    print(f"▶ {script_name}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    return result.returncode == 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("示例: python run_all.py FS实际.cpt FS预算.cpt")
        sys.exit(1)

    targets = sys.argv[1:]
    print(f"目标文件: {targets}")
    print(f"脚本目录: {SCRIPT_DIR}\n")

    steps = [
        ("cancel_params_template.py", "取消常用参数组合"),
        ("add_query_btn.py",          "缺 Query 自动补"),
        ("add_export_btn.py",         "缺 Export 自动补"),
        ("add_css_import.py",         "CSSImport 外部样式"),
        ("add_para_init_event.py",    "CSS 注入"),
        ("set_write_no_toolbar.py",   "填报无工具栏"),
        ("fix_styles.py",             "字体 + padding"),
        ("fix_row_heights.py",        "行高分类"),
        ("widen_all.py",              "布局分行 + 跨列对齐"),
    ]

    failed = []
    for script, desc in steps:
        ok = run_script(script, targets)
        if not ok:
            failed.append(script)

    print(f"\n{'='*60}")
    if failed:
        print(f"❌ 失败: {', '.join(failed)}")
    else:
        print("✅ 全部完成")


if __name__ == '__main__':
    main()
